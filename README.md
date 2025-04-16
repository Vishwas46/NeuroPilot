# NeuroPilot Project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) This repository, **NeuroPilot**, originally started as a fork of [nvidia-research/gpudrive](https://github.com/nvidia-research/gpudrive). It is now evolving to explore autonomous driving concepts, currently focusing on an **Automatic Emergency Braking (AEB)** proof-of-concept using the **CARLA Simulator** and **YOLOv8** object detection.

Future work may involve integrating Reinforcement Learning (RL) techniques, potentially leveraging aspects of the original GPUDrive framework. See [PROGRESS.md](PROGRESS.md) for a detailed breakdown of planned steps and current status.

## Current Focus: CARLA AEB Proof-of-Concept (PoC)

Located in the `carla_aeb_poc/` directory, this PoC demonstrates a basic AEB system:

1.  **Connects** to a running CARLA Simulator instance.
2.  **Spawns** an ego vehicle (Tesla Model 3 by default).
3.  **Attaches** an RGB camera sensor to the vehicle.
4.  **Captures** camera images.
5.  **Processes** images using a YOLOv8 model (`yolov8n.pt` by default) to detect relevant objects (people, cars).
6.  **Estimates** the distance to the closest relevant obstacle in front (using a *very basic* visual estimation method).
7.  **Calculates** a simple Time-to-Collision (TTC) assuming the obstacle is stationary.
8.  **Triggers** emergency braking if the TTC falls below a predefined threshold.
9.  **Visualizes** the camera feed with bounding boxes using OpenCV.

### Key Limitations of Current PoC:

* **Distance Estimation:** Highly inaccurate, based on simple bounding box height assumptions. Requires significant improvement (e.g., using Lidar/Radar sensors in CARLA, stereo vision, or ground truth data for development).
* **TTC Calculation:** Assumes obstacles are stationary. Needs relative velocity for accurate prediction with moving objects.
* **Obstacle Filtering:** Basic check for objects within the center of the camera view.

## Prerequisites & Setup

Ensure the following are installed before running the AEB PoC:

1.  **CARLA Simulator:**
    * Download and install CARLA from the official repository: [CARLA Releases](https://github.com/carla-simulator/carla/releases) or follow the [Build instructions](https://carla.readthedocs.io/en/latest/build_linux/) (Linux) / [Build instructions](https://carla.readthedocs.io/en/latest/build_windows/) (Windows) / [Build instructions](https://carla.readthedocs.io/en/latest/build_macos/) (macOS).
    * **Crucially, you need to start the CARLA Simulator executable before running the Python script.** On macOS, this is typically done via:
        ```bash
        # Navigate to the directory where you extracted CARLA
        cd /path/to/your/CARLA_folder/
        ./CarlaUE4.sh
        ```
        Wait for the simulation map to load.

2.  **Python 3.x:** (Python 3.11 recommended based on original `nextSteps.txt`). Check with `python3 --version`. If needed, install from [python.org](https://www.python.org/) or using a package manager like [Homebrew](https://brew.sh/) on macOS (`brew install python`).

3.  **Git:** Needed to clone this repository. Install from [git-scm.com](https://git-scm.com/downloads) or using a package manager (`brew install git`).

4.  **Python Libraries:**
    * It's highly recommended to use a virtual environment:
        ```bash
        python3 -m venv venv
        source venv/bin/activate # On macOS/Linux
        # venv\Scripts\activate # On Windows
        ```
    * Install required libraries using pip:
        ```bash
        pip install carla-client ultralytics opencv-python numpy torch torchvision torchaudio
        ```
        * `carla-client`: The official Python API for CARLA.
        * `ultralytics`: Provides YOLOv8 implementation.
        * `opencv-python`: For image processing and visualization.
        * `numpy`: For numerical operations.
        * `torch`, `torchvision`, `torchaudio`: PyTorch libraries. YOLOv8 uses PyTorch. The command installs versions compatible with your system (including potentially MPS for Apple Silicon).

5.  **PyTorch MPS Support (for Apple Silicon Macs):**
    * The command above should install a compatible PyTorch version. To verify MPS (Metal Performance Shaders) is available and being used:
        ```python
        import torch

        if torch.backends.mps.is_available():
            mps_device = torch.device("mps")
            x = torch.ones(1, device=mps_device)
            print("MPS is available. Using MPS device.")
            # print(x) # Optional: Print tensor on MPS device
        else:
            print ("MPS device not found.")

        # Ultralytics usually detects MPS automatically if available.
        # You can sometimes explicitly pass device='mps' to the YOLO model if needed.
        ```

## How to Run the AEB PoC

1.  **Start CARLA Simulator** (as described in Prerequisites).
2.  **Clone this repository:**
    ```bash
    git clone [https://github.com/Vishwas46/NeuroPilot.git](https://github.com/Vishwas46/NeuroPilot.git)
    cd NeuroPilot
    ```
3.  **Set up Python environment and install libraries** (as described in Prerequisites, using a virtual environment is recommended).
4.  **Navigate to the PoC directory:**
    ```bash
    cd carla_aeb_poc
    ```
5.  **Run the script:**
    ```bash
    python aeb_runner.py
    ```
    * You can adjust parameters like CARLA host/port, camera resolution, YOLO model path, and TTC threshold via command-line arguments. Use `python aeb_runner.py --help` to see options.
6.  An OpenCV window titled 'Camera Feed' should appear, showing the simulation view. Detected objects will have boxes drawn, turning red if the crude TTC calculation indicates a potential collision. Console output will provide more details.
7.  Press **'q'** in the OpenCV window to stop the script gracefully.

## Future Plans

Refer to [PROGRESS.md](PROGRESS.md) for detailed steps regarding:
* Refining the AEB PoC (improving perception and control).
* Exploring the original GPUDrive components.
* Integrating Reinforcement Learning.
* Improving documentation.

## Original GPUDrive

For information about the original GPUDrive project this repository was forked from, please refer to [nvidia-research/gpudrive](https://github.com/nvidia-research/gpudrive).

## Contributing

*(Optional: Add contribution guidelines if you plan for others to contribute)*

## License

*(Optional: Specify your chosen license, e.g., MIT License)*
This project is licensed under the MIT License - see the LICENSE.md file for details (if you add one).