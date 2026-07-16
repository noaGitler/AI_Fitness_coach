# AI Fitness Coach: Real-Time Biomechanical Tracker

## Project Overview
The **AI Fitness Coach** is a real-time computer vision system designed to provide biomechanical feedback and enhance safety during physical training. By leveraging advanced AI models, the system monitors user movement, tracks exercise repetition, and ensures correct posture to prevent injury. In case of emergency or detected falls, the system initiates a safety protocol to alert designated contacts.

## Core Capabilities
* **Real-Time Biomechanical Analysis:** Utilizing **MediaPipe** to extract skeletal landmarks and calculate joint angles, the system provides live visual feedback (color-coded status: Green for correct, Red for correction) alongside text and audio cues.
* **Fall Detection & Safety Mechanism:** A robust safety layer powered by **YOLOv8** that monitors the user's center of gravity (Y-axis analysis) and inactivity timers. If a fall is detected, the system triggers an emergency protocol, simulating an automated alert with the user's pre-defined location.
* **Intuitive GUI:** Built with **PyQt**, the interface provides a clean, modern dashboard with real-time tracking, rep counting, and exercise status monitoring.

## Tech Stack
* **Language:** Python
* **Computer Vision & AI:** OpenCV, MediaPipe, YOLOv8 (Deep Learning)
* **Data Management:** SQLite
* **GUI:** PyQt

## Development & AI Integration
This project was developed through an iterative process involving critical evaluation of model performance and logical flow. We utilized AI tools to assist in architecture troubleshooting, logical refinement, and Git version control management. 

## Key Features for Evaluation
* **High-Complexity Logic:** The system employs a multi-threaded approach to handle simultaneous pose estimation and object detection without compromising real-time performance.
* **Robust Error Handling:** Implemented a frame-buffer counter to prevent "noise" in tracking and ensure the system remains stable even if the user temporarily exits the camera frame.
