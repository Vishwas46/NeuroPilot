# NeuroPilot Project Progress

This document tracks the development progress of the NeuroPilot project, incorporating elements from the original GPUDrive goals and the CARLA AEB Proof-of-Concept.

## Phase 1: GPUDrive Setup & Initial Exploration (Based on original `nextSteps.txt`)

- [ ] **Fork and Clone:**
    - [x] Fork the GPUDrive repository on GitHub. *(Marked as done since you've forked it)*
    - [ ] Clone your fork locally: `git clone https://github.com/Vishwas46/NeuroPilot.git`
    - [ ] `cd NeuroPilot`
- [ ] **Environment Setup (GPUDrive Focus):**
    - [ ] **Local Build (CPU Mode):**
        - [ ] Ensure dependencies (CMake, Python 3.11) are installed.
        - [ ] Create a build directory: `mkdir build && cd build`
        - [ ] Run CMake: `cmake .. -DCMAKE_BUILD_TYPE=Release`
        - [ ] Build: `make -j`
        - [ ] Go back: `cd ..`
        - [ ] Install package locally: `pip install -e .`
    - [ ] **Using Docker (Recommended for ARM Mac):**
        - [ ] Modify the Dockerfile if needed for ARM compatibility.
        - [ ] Build Docker image: `docker build -t gpudrive:arm .`
        - [ ] Run Docker container: `docker run -it --rm -v $(pwd):/workspace gpudrive:arm /bin/bash`
- [ ] **Set Up Python Environment for RL:**
    - [ ] Create virtual environment: `python3 -m venv rl_env`
    - [ ] Activate virtual environment: `source rl_env/bin/activate`
    - [ ] Install RL libraries: `pip install stable-baselines3[extra] gymnasium opencv-python matplotlib`
- [ ] **Develop RL Training Script:**
    - [ ] Create a script (e.g., `train_agent.py`).
    - [ ] Import GPUDrive environment.
    - [ ] Initialize vectorized environment (Gymnasium).
    - [ ] Define and train an RL agent (e.g., PPO).
    - [ ] Evaluate and visualize agent performance.
    - [ ] Use provided sample code as a starting point.
- [ ] **Test and Iterate (RL):**
    - [ ] Run training script (`python train_agent.py`).
    - [ ] Monitor logs and rewards.
    - [ ] Tweak hyperparameters, rewards, environment settings.

## Phase 2: CARLA AEB Proof-of-Concept (Current Focus)

- [x] **Setup PoC Directory:** *(Assuming you created carla_aeb_poc)*
    - [x] Create directory: `mkdir carla_aeb_poc`
- [x] **Develop AEB Script (`aeb_runner.py`):** *(Assuming you created the script)*
    - [x] Basic CARLA connection and setup.
    - [x] Spawn ego vehicle.
    - [x] Add RGB camera sensor.
    - [x] Implement camera callback and image queue.
    - [x] Load YOLOv8 model.
    - [x] Implement main loop:
        - [x] Get camera image.
        - [x] Perform YOLOv8 inference.
        - [x] Basic obstacle detection (target classes, confidence).
        - [x] **(Needs Improvement)** Simple distance estimation.
        - [x] **(Needs Improvement)** Simple Time-to-Collision (TTC) calculation (assumes stationary obstacle).
        - [x] Implement basic AEB logic (brake on low TTC).
        - [x] Add visualization (OpenCV window with bounding boxes).
    - [x] Implement basic cleanup logic.
- [ ] **Refine AEB PoC:**
    - [ ] Improve distance estimation (e.g., use CARLA ground truth, add Lidar/Radar, stereo vision).
    - [ ] Improve TTC calculation (use relative velocity).
    - [ ] Implement more robust obstacle filtering/tracking.
    - [ ] Test different YOLOv8 models (e.g., `yolov8s.pt`, `yolov8m.pt`).
    - [ ] Implement CARLA synchronous mode for deterministic results.
    - [ ] Add configuration options (e.g., config file, more arguments).
    - [ ] Improve error handling.

## Phase 3: Integration & Documentation

- [ ] **Integrate Approaches (Optional):**
    - [ ] Explore using GPUDrive environment structure with CARLA backend.
    - [ ] Train RL agent within the CARLA+YOLO AEB scenario.
- [ ] **Documentation and Showcase:**
    - [x] Create `PROGRESS.md`. *(This file!)*
    - [ ] Update `README.md` with project focus, setup, and PoC details. *(See below)*
    - [ ] Add detailed documentation on methodology and results.
    - [ ] Push all changes to GitHub.
    - [ ] Highlight the project in portfolio/CV.