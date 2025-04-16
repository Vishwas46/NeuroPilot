import carla
import random
import time
import numpy as np
import cv2
from ultralytics import YOLO
import argparse
import queue # For handling sensor data

# --- Configuration ---
CARLA_HOST = 'localhost'
CARLA_PORT = 2000
CAMERA_IMG_WIDTH = 800
CAMERA_IMG_HEIGHT = 600
AEB_THRESHOLD_TTC = 2.0 # Seconds - Trigger brake if Time To Collision is less than this
TARGET_CLASSES = [0, 2] # COCO classes for 'person' (0) and 'car' (2) - Adjust if needed! YOLOv8 COCO classes
YOLO_MODEL_PATH = 'yolov8n.pt' # Path to YOLO model weights (e.g., yolov8n.pt)

# --- Global Variables ---
ego_vehicle = None
camera_sensor = None
image_queue = queue.Queue() # Queue to store images from camera

# --- Helper Functions ---
def process_img(image):
    """Callback function for camera sensor."""
    # print(f"Received image {image.frame}")
    # Store the image in the queue for processing in the main loop
    image_queue.put(image)

def estimate_distance_simple(box_height_pixels, known_height_meters, focal_length_pixels):
    """
    VERY rough distance estimation based on object height in pixels.
    Assumes object is upright and fully visible. Highly inaccurate!
    Replace with better methods (radar, lidar, stereo, ground truth) for real use.
    """
    if box_height_pixels <= 0:
        return float('inf')
    # This formula is a simplification of the pinhole camera model projection
    # distance = (known_height * focal_length) / object_height_in_pixels
    # Focal length needs calibration! Using a guess here.
    return (known_height_meters * focal_length_pixels) / box_height_pixels

def main(args):
    global ego_vehicle, camera_sensor

    client = None # Initialize client to None
    world = None

    try:
        # --- 1. Connect to CARLA ---
        client = carla.Client(args.host, args.port)
        client.set_timeout(10.0) # seconds
        world = client.get_world()
        print(f"Connected to CARLA: {client.get_client_version()}")

        # Optional: Load a specific map if needed
        # world = client.load_world('Town04')
        # world.wait_for_tick() # Ensure map is loaded

        # --- 2. Get World Objects & Spawn Ego Vehicle ---
        blueprint_library = world.get_blueprint_library()
        vehicle_bp = random.choice(blueprint_library.filter('vehicle.tesla.model3')) # Find a vehicle blueprint
        spawn_points = world.get_map().get_spawn_points()
        spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()

        ego_vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
        if ego_vehicle is None:
            print("Error: Could not spawn ego vehicle!")
            return

        print(f"Spawned Ego Vehicle: {ego_vehicle.type_id} (id: {ego_vehicle.id})")
        world.wait_for_tick() # Let the server catch up

        # --- 3. Add Camera Sensor ---
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(args.width))
        camera_bp.set_attribute('image_size_y', str(args.height))
        # Estimate focal length (rough guess based on typical FOV ~90 deg for width)
        # f = image_width / (2 * tan(FOV/2)) => FOV 90 -> tan(45)=1 -> f=width/2
        focal_length_pixels = args.width / 2.0
        print(f"Estimated camera focal length (pixels): {focal_length_pixels:.2f}")

        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4)) # Position relative to vehicle
        camera_sensor = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)
        camera_sensor.listen(process_img) # Register callback
        print(f"Spawned Camera Sensor: {camera_sensor.type_id} (id: {camera_sensor.id})")

        # --- 4. Load YOLO Model ---
        print(f"Loading YOLO model: {args.model}")
        # Specify device='mps' if needed and available, though ultralytics often detects automatically
        # model = YOLO(args.model, device='mps') # or just YOLO(args.model)
        model = YOLO(args.model)
        print("YOLO model loaded.")

        # --- 5. Main Loop (Control, Perception, AEB Logic) ---
        # Start vehicle moving slowly
        ego_vehicle.apply_control(carla.VehicleControl(throttle=0.3))
        time.sleep(1) # Give it a sec to start moving

        braking = False # AEB state flag

        while True:
            world.wait_for_tick() # Sync with simulation tick

            # Get latest image from queue
            try:
                image = image_queue.get(block=True, timeout=0.1) # Wait max 0.1s
            except queue.Empty:
                print("Warning: Image queue empty, skipping frame.")
                continue

            # Convert CARLA image to NumPy array (BGRA -> RGB)
            img_bgra = np.reshape(np.copy(image.raw_data), (image.height, image.width, 4))
            img_rgb = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2RGB)

            # --- YOLO Inference ---
            results = model(img_rgb, verbose=False) # verbose=False to reduce console spam

            # Find closest relevant obstacle in front
            min_distance = float('inf')
            closest_obstacle_box = None
            potential_collision = False

            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])

                    # Check if detected class is relevant (car or person) and confidence is high enough
                    if cls_id in TARGET_CLASSES and confidence > 0.5:
                        xyxy = box.xyxy[0].cpu().numpy() # Get coordinates [x1, y1, x2, y2]
                        box_center_x = (xyxy[0] + xyxy[2]) / 2
                        box_height = xyxy[3] - xyxy[1]

                        # Simple check: Is the obstacle roughly in front? (center within middle 50% of image width)
                        if args.width * 0.25 < box_center_x < args.width * 0.75:
                            # VERY ROUGH Distance Estimation!
                            # Use known heights (average estimates) - TUNE THESE!
                            known_height = 1.6 if cls_id == 0 else 1.5 # Approx height for person/car
                            distance = estimate_distance_simple(box_height, known_height, focal_length_pixels)

                            print(f"  Detected {result.names[cls_id]} (conf: {confidence:.2f}) at ~{distance:.2f}m")

                            if distance < min_distance:
                                min_distance = distance
                                closest_obstacle_box = xyxy # Store box coords for drawing

                            # --- Basic AEB Logic ---
                            # Get ego vehicle speed (m/s)
                            velocity = ego_vehicle.get_velocity()
                            speed_mps = np.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)

                            # VERY Simple TTC calculation (assuming obstacle is stationary!)
                            # Replace with relative speed if obstacle velocity is known/estimated
                            ttc = min_distance / speed_mps if speed_mps > 0.5 else float('inf') # Avoid division by zero/low speed instability

                            print(f"  Speed: {speed_mps*3.6:.1f} km/h, Min Dist: {min_distance:.2f}m, TTC: {ttc:.2f}s")

                            if ttc < args.ttc:
                                potential_collision = True
                                break # Found imminent collision, act immediately
                if potential_collision:
                    break

            # --- Apply Control ---
            if potential_collision and not braking:
                print(f"!!! AEB TRIGGERED !!! TTC: {ttc:.2f}s < {args.ttc:.2f}s. Applying full brakes.")
                ego_vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0, steer=0.0))
                braking = True
            # Optional: Add logic to release brake later if desired

            # --- Visualization (Optional) ---
            # Draw bounding box of closest obstacle on the image
            img_display = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR) # Convert back for OpenCV display
            if closest_obstacle_box is not None:
                pt1 = (int(closest_obstacle_box[0]), int(closest_obstacle_box[1]))
                pt2 = (int(closest_obstacle_box[2]), int(closest_obstacle_box[3]))
                color = (0, 0, 255) if potential_collision else (0, 255, 0) # Red if collision imminent
                cv2.rectangle(img_display, pt1, pt2, color, 2)
                # Put distance text
                cv2.putText(img_display, f"~{min_distance:.1f}m", (pt1[0], pt1[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            cv2.imshow('Camera Feed', img_display)
            if cv2.waitKey(1) & 0xFF == ord('q'): # Allow quitting by pressing 'q'
                break


    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # --- Cleanup ---
        print("Cleaning up actors...")
        if client and world:
             # Access settings via the world object
            settings = world.get_settings()
            settings.synchronous_mode = False # Disable sync mode
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)
            print("Disabled synchronous mode.")

        if camera_sensor is not None:
            camera_sensor.stop()
            camera_sensor.destroy()
            print("Destroyed camera sensor.")
        if ego_vehicle is not None:
            ego_vehicle.destroy()
            print("Destroyed ego vehicle.")
        cv2.destroyAllWindows()
        print("Cleaned up actors and closed windows.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CARLA AEB Demo with YOLOv8")
    parser.add_argument('--host', default=CARLA_HOST, help="CARLA server host")
    parser.add_argument('--port', default=CARLA_PORT, type=int, help="CARLA server port")
    parser.add_argument('--width', default=CAMERA_IMG_WIDTH, type=int, help="Camera image width")
    parser.add_argument('--height', default=CAMERA_IMG_HEIGHT, type=int, help="Camera image height")
    parser.add_argument('--model', default=YOLO_MODEL_PATH, help="Path to YOLOv8 model file (e.g., yolov8n.pt)")
    parser.add_argument('--ttc', default=AEB_THRESHOLD_TTC, type=float, help="Time-to-Collision threshold for AEB (seconds)")

    args = main_args() # Corrected function call
    main(args) # Pass the parsed arguments to main