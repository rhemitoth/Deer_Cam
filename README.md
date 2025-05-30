# Deer_Cam
DeerCam is a field-deployable system for automated infrared thermography of wildlife, designed to function like a camera trap. This repository contains all code and documentation needed to build and operate DeerCam—a Raspberry Pi–based platform that captures thermal images using a FLIR A325sc camera via the FLIR Spinnaker SDK. The README includes detailed instructions for assembling the system, configuring hardware, and processing the resulting thermal imagery.

For questions regarding the DeerCam system, please contact the developer, Rhemi Toth, at [rhemitoth@g.harvard.edu](mailto:rhemitoth@g.harvard.edu).


![thermal_images](images/deer.png)


## Description
DeerCam is designed to function similarly to a camera trap. When an animal passes in front of the system, a passive infrared (PIR) motion sensor connected to the Raspberry Pi triggers a relay that supplies power to the thermal camera. Once powered on and connected to the Raspberry Pi, the camera begins capturing images at user-defined intervals for a user-specified duration. After this period, the system checks for continued motion. If no motion is detected, the camera is powered off. To operate the DeerCam System autonomously in the field, the researcher must provide a 12V power supply and a waterproof housing for the Raspberry Pi, PIR sensor, and thermal camera.

![deercam_1](images/DeerCam_1.png)
![deercam_2](images/DeerCam_2.png)
 

## Getting Started

### Hardware

- Power:
    - **12V power supply.** In the field, we use a car battery to power the system, but any reliable 12V power source will work.
    - **DC to DC Converter.** To power the Raspberry Pi from the 12V supply, we use a DC-to-DC converter by Klunoxj, which accepts 12V or 24V input and outputs 5V at 5A via a USB-C connector.
    - **2-pin screw terminal connector and wiring.** The FLIR A325sc camera is powered by connecting wires fitted to a compatible 2-pin screw terminal connector, which then connects directly to the 12 V power supply.

- Camera Parts:
    - **FLIR A3xx Camera.** The DeerCam system is designed for use with the FLIR A325sc, but other FLIR A3xx models may also be compatible. However, we have not tested compatibility with other models.
    - **Ethernet cable.** FLIR A3xx series cameras transmit data via Gigabit Ethernet (GigE). In the DeerCam system, the Raspberry Pi also uses Telnet commands over the Ethernet connection to control the camera's autofocus.

- Raspberry Pi Parts:
    - **Raspberry Pi 5.** Currently, DeerCam must be run on a Raspberry Pi 5 and is not compatible with earlier models. Running DeerCam on an older Pi would require modifying some of the code (e.g., how the GPIO pins are configured).
    - **USB SD card reader.** After retrieving images from the camera, DeerCam saves them to an SD card connected to the Raspberry Pi via a USB SD card reader.
    - **PIR sensor and wiring.** To detect motion, DeerCam uses input from a PIR sensor connected to one of the GPIO pins.
    - **Relay switch.** A relay switch controls power to the camera, ensuring the camera is only powered when needed. This design choice helps conserve battery life by preventing the camera from drawing power continuously when no animals are present.
    - **DS3231 Real-Time Clock.** The Raspberry Pi normally retrieves time from the internet. For field deployments without connectivity, an RTC module is required so the device can maintain accurate time.
    - **e-Paper display.** System status messages (e.g., "Connecting to camera", "Focusing camera", "Collecting images", "WARNING: No SD card") are shown on a 2.7-inch e-Paper Display HAT from Waveshare. Because it doesn't use backlighting, the e-Paper display is ideal for providing status updates without disturbing animals.
    - **Prototyping HAT.** The PIR sensor, RTC module, and e-Paper display are connected via a prototyping HAT. DeerCam is designed to work with the Perma-Proto HAT from Adafruit.
    - **Stacking headers and standoffs.** To physically attach the relay, prototyping HAT, and e-Paper display to the Raspberry Pi, stacking headers and standoffs are used.

- Materials for Field Deployment:
    - **Camera housing and Germanium window.** To protect the thermal camera from environmental exposure, we modified a BOSCH UHO-POE-10 outdoor housing by replacing the front glass with a Germanium window. Since thermal radiation cannot pass through glass, it’s essential that the housing window is made from a material like Germanium that transmits infrared radiation.
    - **Raspberry Pi housing.** The Raspberry Pi is enclosed in an IP67-rated waterproof electrical junction box to shield it from moisture and dust in the field.
    - **PIR sensor housing.** The PIR sensor and its wiring are enclosed in a waterproof plastic box. We modified the box by cutting a hole to match the diameter of the PIR sensor's globe and sealed it with waterproof sealant to ensure durability in outdoor conditions.


### Assembly

The DeerCam System is composed of four primary "layers," listed below from bottom to top:

#### **Layer 1: Raspberry Pi**

![raspi](images/raspberry_pi.png)

#### **Layer 2: Relay**

In the DeerCam System, the positive wire connecting the battery to the camera is routed through a relay switch to allow the Raspberry Pi to control camera power.

![relay1](images/relay_1.png)  
![relay2](images/relay_2.png)

#### **Layer 3: Prototyping HAT**

The RTC module and PIR sensor wiring are soldered directly onto the prototyping HAT. The e-paper display (Layer 4) connects to the HAT by attaching directly to its GPIO pins.

![pb1](images/protoboard_1.png)  
![pb2](images/protoboard_2.png)

#### **Layer 4: e-Paper Display**

![hat1](images/ehat_1.png)  
![hat2](images/ehat_2.png)

### Automatically Running DeerCam on Startup

To ensure the DeerCam system starts automatically when the Raspberry Pi powers on, we use a `systemd` service called `run_on_startup.service`.

### The Startup Script

This service runs the `run_on_startup.sh` script, which:

- Initializes the Conda environment (`flir.env`)
- Launches the FLIR camera controller script
- Logs output to a file for debugging

Here’s what the `run_on_startup.sh` script looks like:

```bash
#!/bin/bash

# Load conda
source /home/moorcroftlab/miniforge3/etc/profile.d/conda.sh

# Activate the environment
conda activate /home/moorcroftlab/miniforge3/envs/flir.env

# Run the Python script and log output
python /home/moorcroftlab/Documents/FLIR/FLIR_A325sc_Controller/FLIR_A325sc_Controller_Complete.py > /home/moorcroftlab/Documents/FLIR/FLIR_A325sc_Controller/run_on_startup.log 2>&1
```

#### Setting Up the Startup Service

If you're setting this up on a new device, follow these steps:

1. Create the service file
Save the following content to `/etc/systemd/system/run_on_startup.service`:

```ini
[Unit]
Description=Run DeerCam at startup
After=network.target

[Service]
Type=simple
ExecStart=/home/USERNAME/path/to/run_on_startup.sh
User=USERNAME
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Make the script executable
```bash
chmod +x /home/USERNAME/path/to/run_on_startup.sh
```

3. Enable and start the service
```bash
sudo systemctl enable run_on_startup.service
sudo systemctl start run_on_startup.service
```
```