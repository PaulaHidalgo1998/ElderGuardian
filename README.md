# ElderGuardian
Intelligent Robotic Device for Elderly Assistance and Monitoring

**Author:** Paula Hidalgo Cerezo  
**University:** Universitat Politècnica de Catalunya (UPC)  
**Master's Program:** Master's degree in Automatic Control and Robotics  
**Academic Year:** 2025  

---

## 🧠 Abstract

The progressive aging of the population is generating a growing demand for technological solutions that allow elderly people to live safely and independently in their homes. This Master's Thesis presents the development of a prototype of an autonomous assistive robot designed to detect falls and generate alerts in emergency situations.

The system is based on a Raspberry Pi 5 as the central processing unit. It uses a connected camera for computer vision and applies the YOLOv11n-Pose algorithm for person detection and pose estimation, enabling it to identify whether a person is standing, sitting, or has fallen. The robot is capable of moving thanks to motorized wheels, and both its structure and wheels have been designed and fabricated using 3D printing technology.

When a fall is detected, the system triggers an emergency communication intended to alert a caregiver or relevant service. This functionality makes the robot a valuable tool for teleassistance, reducing response time to potential domestic accidents.

This work demonstrates the feasibility of developing an affordable and functional prototype of a robotic system for monitoring elderly individuals, laying the groundwork for future enhancements such as the integration of new features or increased system autonomy.

---

## 🗂️ Repository Structure

This repository contains the source code and resources developed for my Master's Thesis project. The folder structure is as follows:

- `vision/`: Person and posture detection algorithms based on YOLOv11n-Pose.
- `mobile/`: Script for controlling servomotors using the PCA9685 module.
- `alerts/`: Code that creates and sends alert messages to the caregiver’s smartphone.  
- `videos/`: Recordings and visual tests demonstrating the robot's functionality. (Note: GitHub does not support video playback. Please download the files to view them).

---

## 🤖 Robot in Action

![Robot demo](robot_demo_3D.gif)


---

## 🛠️ Installation & Requirements

```bash
# Clone the repository
git clone https://github.com/PaulaHidalgo1998/ElderGuardian.git
cd ElderGuardian

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

