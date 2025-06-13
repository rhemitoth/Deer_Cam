# ======================== Notes ===========================================

## The intended use of FLIR_A325sc_Controller_Complete.py is automate the control a FLIR A3xx series camera using a raspberry pi.
## Before running this script, you will need to download and install the FLIR Spinnaker SDK for python on your raspberry pi. 
## Additionally, you will need a FLIR A3xx camera, a PIR sensor, a raspberry pi, an waveshare e-ink display hat, and a relay hat for the raspberry pi.
## The relay hat is used to automate the powering on/off of the camera based on input from the PIR sensor.
## When the script is first run, the relay will be switched off and no power will be supplied to the camera.
## After motion is detected by the PIR sensor, the relay is switched on and power is supplied to the camera.
## Once a telnet connection is established between the camera and the pi, the pi sends a signal over telnet to focus the camera.
## Once the camera is focused, a burst of three images are saved at a specified frequency (e.g. every 5 seconds) for a specified durtation (e.g. 5 minutes).
## After images have been collected for a specified duration of time, the relay will be switched off and the camera will power down.
## While the program is running, statements are printed to the e-ink display hat to describe what the system is doing.
## Please consult the README file for a description of how to assemble the system. 

# ======================== Import  Modules ==================================

#Modules for establishing telnet connection between FLIR and pi
import telnetlib # for establishing telnet connection to focus camera

# Modules for working with GPIO input
from gpiozero import MotionSensor # for reading PIR input
import gpiozero # for controlling relay

# Modules for capturing and saving images with the FLIR
import datetime # for creating image filenames with datetime of image capture
import PySpin # FLIR spinnaker SDK

# Modules for controlling the e-paper display
import os # for checking if directory for image export exists (avoids errors while swapping SD cards) and working with the e-ink display
import sys 
from waveshare_epd import epd2in7_V2 # Using the 2.7 inch Waveshare e-paper HAT
from PIL import Image,ImageDraw,ImageFont

# Other modules
from time import sleep # for pausing code
import time
import subprocess # used to check if SD card is connected

# ======================== Connect to Camera and Grab Image ==================================
# The function 'save_images_spinnaker' uses the PySpin library from the FLIR Spinnaker SDK to connect to the camera and grab images
# Argument 'directory' specifies directory on the raspberry pi where the image will be saved 
# Argument 'filetype' specifies filetype of image to be saved ('png', 'jpg', 'tiff', etc). I recommend using tiff since this datatype can easily be converted to a numpy array for analysis in python. 
# Argument 'burst' specifies whether a single image or a burst of images will be saved. The default is burst = True and is ideal for capturing images of free ranging animals.
# Argument 'burst_num' specifies the number of images that are captured as a part of the burst. The default is 3. 

def save_image_spinnaker(directory, filetype, burst = False, burst_num = 3):
    # Argument 'directory' specifies directory where image will be saved
    # Argument 'filetype' specifies filetype of image to be saves ('png', 'jpg', 'tiff', etc)
    
    # Initalize the system
    system = PySpin.System.GetInstance()

    # Get the camera
    cam = system.GetCameras()[0]
    
    try:
        if burst == False:
            # Initialize the camera
            cam.Init()

            # Start aquisition
            cam.BeginAcquisition()

            # Grab image
            image_result = cam.GetNextImage()
        
            # Save image
            filename = directory + 'file-' + str(datetime.utcnow.now().strftime('%Y%m%d-%H%M%S')) + "." + filetype
            if os.path.exists(directory):
                image_result.Save(filename)

            # Release image
            image_result.Release()

            # Stop Acquisition
            cam.EndAcquisition()

            # Deinitalize camera
            cam.DeInit()
        else:
            # Initialize the camera
            cam.Init()

            # Start aquisition
            cam.BeginAcquisition()

            for i in range(0,burst_num):

                # Grab image
                image_result = cam.GetNextImage()
        
                # Save image
                filename = directory + "file-" + str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')) +  "_burst" + str(i+1) + "." + filetype
                if os.path.exists(directory):
                    image_result.Save(filename)

                # Release image
                image_result.Release()

            # Stop Acquisition
            cam.EndAcquisition()

            # Deinitalize camera
            cam.DeInit()

    finally:
        # Release system instance
        system.ReleaseInstance()


# ======================= Check for camera connection ========================================
# The function 'check_connection' generates a list of  cameras that are connected to the raspberry pi using the FLIR spinnaker SDK 
# The function returns 'False' if no cameras are connected
# The function returns 'Returns' 'True' if a camera is connected

def check_connection():
    # Initalize the system
    system = PySpin.System.GetInstance()

    # Get the list of connected cameras
    cam_list = system.GetCameras()

    # Get length of camera list
    numcams = len(cam_list)

    # Return true if the camera is connected. Return false is no camera is connected.
    if numcams > 0:
        return True
    else:
        return False

# ======================== Establishing Telnet Connection ==============================
# The function 'establish_telnet_connection' establishes a telnet connection between the camera and the raspberry pi using the telnetlib module
# Argument 'cam_ip' is the ip address of the camera.
# In order for the raspberry pi to recognize the camera, the camera and the raspberry pi must be on the same subnet.
# The easiest way to ensure that the pi and the camera are on the same subnet is to change the ip address of the raspberry pi to align with the ip address of the camera. 

def establish_telnet_connection(cam_ip):
    telnet_connection = telnetlib.Telnet(cam_ip)
    return telnet_connection

# ======================== Focusing the camera via telnet ==============================
# The function 'focus' focuses the camera via a telent connection between the camera and the pi
# Argument 'telnet connection' is the telnet connection object that is generated by the function 'establish_telent_connection'

def focus(telnet_connection):
    telnet_connection.read_until(b'>')
    telnet_connection.write(b'rset .system.focus.autofull true\n') # telnet command to focus the camera
    sleep(5)

# ======================== Drawing an image on the e-ink display ========================
# The function 'print_to_display' is used to send images to the waveshare e-ink dipslay hat for the raspberry pi
# Argument 'deer_on' specifies whether the message will be printed in a speech bubble coming from a cartoon deer. The default is set to 'True' and is recommended because it looks very cute :). Consult the README file for an example image of the display.
# Argument 'deer_path' specifies where the background image of the deer is saved on the raspberry pi. If 'deer_on' = False, this argument is not utilized
# Argument 'message' specifies that message that will be printed to the e-ink display hat
# Argument 'textX' specifies the X position where text is drawn
# Argument 'textY' specifies the Y position where the text is drawn
# Agument 'fontPath' specifies the font that you would like to use for the message. You can get a list of paths of fonts that are installed on your PI by typing "fc-list" in the terminal. 

def print_to_display(deer_on = True, deer_path = "/home/moorcroftlab/Documents/FLIR/FLIR_A325sc_Controller/raspi_text_background_wlogo.bmp", message = "hello deer",textX = 20,textY = 60,fontPath = "/usr/share/fonts/X11/Type1/NimbusMonoPS-Bold.pfb",fontSize = 18):
    # This function is used to print out messages describing what the system is doing to the e-paper display
    # deer_on = True, the messages will appear as text inside of a speech bubble coming from a cartoon of a roe deer (I'm using this system to capture images of roe deer and I thought it would be cute ¯\_(ツ)_/¯)
    # deer_on = False, the message will appear as plain text 
    # deer_path = location on your Pi where the deer image is saved
    # message = "the text you want to display on the screen"
    # textX = X position to draw text
    # textY = Y position to draw text
    # fontPath = Path to the font you want to use. You can get a list of paths of fonts installed on your Pi by typing "fc-list" in the terminal

    if deer_on == True:
        epd = epd2in7_V2.EPD()
        epd.init()
        epd.Clear()
        
        #Create a blank image for drawing
        canvas = Image.new('1',(epd.width,epd.height),255)
        draw = ImageDraw.Draw(canvas)

        # Load the bitmap image
        image_path = deer_path
        bmp_image = Image.open(image_path)
        bw_image = bmp_image.convert('1')
        bmp_width,bmp_height = bw_image.size

        # Position to paste the bitmap image
        x_offset = 0
        y_offset = 0

        # Paste the bitmap image onto the canvas
        canvas.paste(bw_image,(x_offset,y_offset))

        # Load a font
        font_path = fontPath
        txt_font = ImageFont.truetype(font_path,fontSize)

        # Define the text to display
        text = message

        # Position to draw the text
        text_x = textX
        text_y = textY

        # Draw the text on the canvas
        draw.text((text_x, text_y),text,font=txt_font,fill=0)

        # Display the image on the e-Paper display
        epd.display_Fast(epd.getbuffer(canvas))
    else:
        epd = epd2in7_V2.EPD()
        epd.init()
        epd.Clear()
        
        #Create a blank image for drawing
        canvas = Image.new('1',(epd.width,epd.height),255)
        draw = ImageDraw.Draw(canvas)
        
        # Load a font
        font_path = fontPath
        txt_font = ImageFont.truetype(font_path,fontSize)
    
        # Define the text to display
        text = message
        
        # Position to draw the text
        text_x = textX
        text_y = textY
        
        # Draw the text on the canvas
        draw.text((text_x, text_y),text,font=txt_font,fill=0)
        
        # Display the image on the e-Paper display
        epd.display_Fast(epd.getbuffer(canvas))

# =================== Clear the e-ink display ======================================
# The function 'clear_display' clears the e-ink display 

def clear_display():
    epd = epd2in7_V2.EPD()
    epd.init()
    epd.Clear()
    
# ================= Check if SD card is connected ====================================
# The function 'is_sd_card_connected' is used to check if an SD card is connected to the raspberry pi
# For this project, I connected the SD card to the raspberry pi using a USB SD card reader

def is_sd_card_connected():
    def list_block_devices():
        # Execute lsblk command to list block devices
        result = subprocess.run(['lsblk', '-o', 'NAME,TYPE'], capture_output=True, text=True)
        return result.stdout

    def find_sd_card(devices_info):
        # Parse the output of lsblk to find the SD card
        lines = devices_info.strip().split('\n')
        for line in lines:
            if 'sd' in line:  # Typically, SD cards will be named /dev/sdX where X is a letter
                parts = line.split()
                device_name = parts[0]
                device_type = parts[1]
                
                if device_type == 'disk':
                    return True
        return False

    devices_info = list_block_devices()
    return find_sd_card(devices_info)

# ====================== Find SD Mount Point ==========================================
# The function 'find_sd_card_mount_point' identifies the mount point of the SD Card.
# The mount point is the directory associated with the SD Card where images will be saved.

def find_sd_card_mount_point():
    try:
        # Use the 'df' command to list all mounted filesystems
        output = subprocess.check_output(['df', '-h']).decode('utf-8')
        print(output)
        # Split the output into lines and iterate over them
        for line in output.splitlines():
            # Check if the line contains '/media' or '/mnt'
            if '/media' in line or '/mnt' in line:
                # Split the line into columns and get the mount point
                columns = line.split()
                mount_point = columns[-1]
                # You can add further checks to identify the SD card specifically
                print(f"Possible SD card mount point: {mount_point}")
                return(mount_point)
                
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        
# ======================= Save pictures ==================================================
# The function 'collect_data' is used to pull images from the camera and save them to the SD card.
# Argument 'duration' sets the duration (in minutes) of data collection.
# Argument 'frequency' sets the frequency (in seconds) at which images (or burst of images) are grabbed from the camera.

def collect_data(fpath = "/media/moorcroftlab/9016-4EF82/",duration = 2, frequency = 5):
    # f_path = "directory where images will be saved"
    # duration = duration in minutes of data collection
    # frequency = frequency at which image bursts are captured
    start_time = time.time()
    elapsed_time = 0
    check_sd_count = 0
    image_capture_count = 0
    sd_mnt_pt = find_sd_card_mount_point()
    while elapsed_time < duration * 60:
        if is_sd_card_connected() == False:
            image_capture_count = 0 # reset image capture count 
            print("WARNING: SD Card missing.")
            if check_sd_count == 0:
                print_to_display(message = "WARNING.\nNo SD card \ndetected.")
            check_sd_count += 1
            sd_missing = True
            while sd_missing == True:
                sd_missing = os.path.exists(fpath)
                sleep(1)
        elif is_sd_card_connected() == True and check_connection() == True:
            check_sd_count = 0 # reset check SD count
            fpath = find_sd_card_mount_point()+"/"
            if image_capture_count == 0:
                print_to_display(message = "Capturing \nimages.")
            print("Capturing image . . .")
            save_image_spinnaker(directory = fpath, filetype = "tiff")
            print ("Image saved.")
            sleep(frequency)
            image_capture_count += 1
        elapsed_time = time.time() - start_time
         
# ============== Main Code =============================================

def main():

    # Define PIR sensor GPIO pins on Raspberry Pi
    pir = MotionSensor(20)
    relay = gpiozero.OutputDevice(21, active_high = True, initial_value = False)

    # Main code 

    count = 0 # used to check if while loop is on first iteration
    
    previous_motion = False
    
    while True: 
        # Check if motion is detected
        current_motion = pir.motion_detected
        
        if current_motion == True and previous_motion == False:

            # Turn on camera
            print("Motion detected. Turning on camera")
            relay.on()
            
            # Pause code until camera is connected
            print("Connecting to camera . . .")
            print_to_display(message = "Connecting\nto camera.")
            not_connected = True
            start_time = time.time()
            while not_connected == True:
                connection_status = check_connection()
                if connection_status == True:
                    not_connected = False
                else:
                    current_time = time.time()
                    if current_time - start_time > 60:
                        print("Camera frozen. Restarting . . . ")
                        print_to_display(message = "No cam\ndetected.\nRestarting\nsystem.", fontSize = 16)
                        relay.off()
                        sleep(60)
                        relay.on()
                        print("Connecting to camera . . .")
                        print_to_display(message = "Connecting\nto camera.")
                        sleep(1)
                        start_time = time.time()
                    else:
                        sleep(1)
            print("Camera connected.")

            # Focus the camera
            if check_connection() == True:
                flir_ip = '169.254.0.0' 
                tn = establish_telnet_connection(flir_ip)
                print("Focusing camera . . .")
                print_to_display(message = "Focusing\ncamera.")
                focus(tn)
                print("Camera is focused.")

            # Collect and image every 5 seconds for 1 minute
            collect_data(duration = 1)
            sleep(1)
            
            # Update global count variable
            count = 0
            
        elif current_motion == True and previous_motion == True:
            
            # Refocus the camera
            print_to_display(message = "Re-focusing\ncamera.")
            focus(tn)
            sleep(1)
            
            # Collect a burst of images every 5 seconds for 1 minute
            collect_data(duration = 1)
            sleep(1)
            
            # Update global count variable
            count = 0


        elif current_motion == False:
            relay.off() # turn off relay/power off camera
            print("No motion detected. Camera off.")
            if count == 0:
                print_to_display(message = "No motion\ndetected.\nCamera off.")
            sleep(1) # prevents the camera from freezing from turning on/off to quickly
            # This prevents the display from constantly refreshing when there is no motion
            count +=1
            if count == 2:
                count -= 1
                
        # Update previous motion
        previous_motion = current_motion
            
if __name__ == '__main__':
    main()




