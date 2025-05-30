# Deer_Cam
DeerCam is a field-deployable system for automated infrared thermography of wildlife, designed to function like a camera trap. This repository contains all code and documentation needed to build and operate DeerCam—a Raspberry Pi–based platform that captures thermal images using a FLIR A325sc camera via the FLIR Spinnaker SDK. The README includes detailed instructions for assembling the system, configuring hardware, and processing the resulting thermal imagery.

![thermal_images](images/deer.png)


## Description
DDeerCam is designed to function similarly to a camera trap. When an animal passes in front of the system, a passive infrared (PIR) motion sensor connected to the Raspberry Pi triggers a relay that supplies power to the thermal camera. Once powered on and connected to the Raspberry Pi, the camera begins capturing images at user-defined intervals for a user-specified duration. After this period, the system checks for continued motion. If no motion is detected, the camera is powered off. To operate the DeerCam System autonomously in the field, the researcher must provide a 12V power supply and a waterproof housing for the Raspberry Pi, PIR sensor, and thermal camera.

![deercam_1](images/DeerCam_1.png)
![deercam_2](images/DeerCam_2.png)
 

## Getting Started

### Hardware

