# Introduction

The GÖKBAĞ Drone Project aims to enhance drone functionalities in military applications by incorporating advanced object detection, autonomous and manual control systems, and robust communication frameworks. This README file provides essential information about the project structure, system requirements, installation procedures, and basic usage.
## System Requirements

Python 3.8 or higher \
Libraries: djitellopy, cv2, numpy, PIL, customtkinter, ultralytics\
Compatible hardware: DJI Tello drone



## Installation
Clone the repository
```bash
git clone https://github.com/ahmetselimkaraca/drone
```
Navigate to the project directory
```bash
cd GokbagDrone
```

Install required Python libraries
```bash
pip install -r requirements.txt
```

# Project Structure
DroneController.py: Main module controlling drone operations, including takeoff, landing, and image capturing.\
keypressmodule.py: Handles keyboard inputs for manual drone control.\
coord_csv_module.py: Manages CSV file operations for logging flight data.\
utilities.py: Provides utility functions like password hashing and user data management.\
models: Directory containing trained YOLO models for object detection.

# Usage
__Starting the Drone Controller:__
```bash
python main.py
```
__Manual Control:__
Use the keyboard to control the drone manually. Key mappings include arrow keys for navigation and specific keys for takeoff ('T') and landing ('L').

__Object Detection:__
Toggle object detection features to enable real-time object tracking during the flight.

__Flight Data Logging:__
Flight paths are automatically saved in CSV format in the flight_logs directory for post-flight analysis.

# Additional Information
For detailed API documentation and advanced configuration, refer to the docs folder.\
The project's progress and updates are regularly pushed to the repository, so keep an eye on the latest commits for new features and improvements.


## Contact

For more information or to report issues, please contact the project team at\
 aselim.karaca@tedu.edu.tr\
 berkay.babayigit@tedu.edu.tr\
 burak.bilgi@tedu.edu.tr\
 eren.alsan@tedu.edu.tr