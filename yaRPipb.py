#!/usr/bin/env python

import os
from time import sleep, strftime
import sys
import ConfigParser

import RPi.GPIO as GPIO
import picamera                                                             # http://picamera.readthedocs.org/en/release-1.4/install2.html
import pygame

#################
### Functions ###
#################

### setup ###
# clean up running programs as needed when main program exits
def cleanup():
    print('\nBye')
    pygame.quit()
    GPIO.cleanup()
    sys.exit()

def setupGPIO(led_pin, btn_start_pin, btn_exit_pin):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(led_pin, GPIO.OUT)                                           # LED
    GPIO.setup(btn_start_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)            # Start-Button
    GPIO.add_event_detect(btn_start_pin, GPIO.RISING, bouncetime = 300)
    GPIO.setup(btn_exit_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)             # Exit-Button
    GPIO.add_event_detect(btn_exit_pin, GPIO.RISING, bouncetime = 300)
    GPIO.output(led_pin,False)
    print('GPIO setup successful.')

def setupPygame(monitor_w, monitor_h):
    pygame.init()
    pygame.display.set_mode((monitor_w, monitor_h))
    screen = pygame.display.get_surface()
    pygame.display.set_caption('Yet Another Pi Photobooth')
    pygame.mouse.set_visible(False)
    pygame.display.toggle_fullscreen()

    return screen

### camera ###
def setupCamera(saturation, iso, resolution_w, resolution_h):   #TODO: Use tuple for resolution
    print('Get Ready')
    GPIO.output(led_pin, False)

    camera = picamera.PiCamera()
    camera.vflip = False
    camera.saturation = saturation
    camera.iso = iso
    camera.resolution = (resolution_w, resolution_h)

    return camera

def takePictures(camera, file_path, total_pics, monitor_w, monitor_h, capture_delay):
    print('Taking Picture')
    now = strftime("%Y_%m_%d_%H_%M_%S")
    taken_pictures = []
    for i in range(1, total_pics + 1):
        clear_screen()
        show_image(real_path + "/images/instructions.png")
        sleep(instructions_delay)

        filename = file_path + now + '__' + str(i) + '.jpg'
        
        clear_screen()
        camera.hflip = True # preview a mirror image
        camera.start_preview(resolution=(640, 480))
        sleep(warmup_delay) # warm up camera
        camera.stop_preview()

        GPIO.output(led_pin, True)
        camera.hflip = False # flip back for photo
        camera.capture(filename)
        taken_pictures.append(filename)
        GPIO.output(led_pin, False)

        show_image(filename)
        sleep(capture_delay)
        clear_screen()

    camera.close()

    return taken_pictures

### GraphicsMagick ###
def create_four_grid(taken_pictures, file_path):
    if len(taken_pictures) != 4:
        pass
    else:
        now = strftime("%Y_%m_%d_%H_%M_%S")
        filename = file_path + now + '__montage.jpg'

        gmagick = []
        gmagick.append('gm montage')
        gmagick.append('-geometry 640x480')
        gmagick.append('-tile 2x2')
        gmagick.append('-quality 100')
        for i in taken_pictures:
            gmagick.append(i)
        gmagick.append(filename)

        graphicsmagick = ' '.join(gmagick)
        os.system(graphicsmagick)

        show_image(filename)
        sleep(6)        

### pygame ###
def set_demensions(img_w, img_h):
    # courtesy of drumminhands photobooth
    # https://github.com/drumminhands/drumminhands_photobooth

    # Note this only works when in booting in desktop mode.
    # When running in terminal, the size is not correct (it displays small). Why?

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (monitor_w * img_h) / img_w

    if (ratio_h < monitor_h):
        #Use horizontal black bars
        #print "horizontal black bars"
        transform_y = ratio_h
        transform_x = monitor_w
        offset_y = (monitor_h - ratio_h) / 2
        offset_x = 0
    elif (ratio_h > monitor_h):
        #Use vertical black bars
        #print "vertical black bars"
        transform_x = (monitor_h * img_w) / img_h
        transform_y = monitor_h
        offset_x = (monitor_w - transform_x) / 2
        offset_y = 0
    else:
        #No need for black bars as photo ratio equals screen ratio
        #print "no black bars"
        transform_x = monitor_w
        transform_y = monitor_h
        offset_y = offset_x = 0

    # uncomment these lines to troubleshoot screen ratios
#    print str(img_w) + " x " + str(img_h)
#     print "ratio_h: "+ str(ratio_h)
#     print "transform_x: "+ str(transform_x)
#     print "transform_y: "+ str(transform_y)
#     print "offset_y: "+ str(offset_y)
#     print "offset_x: "+ str(offset_x)

def show_image(image_path):
    screen.fill((0, 0, 0)) # clear the screen

    img = pygame.image.load(image_path)
    img = img.convert()
    set_demensions(img.get_width(), img.get_height()) # set pixel dimensions based on image

    # rescale the image to fit the current display
    img = pygame.transform.scale(img, (transform_x,transfrom_y))
    #print('Image Scale:\n ' + str(img.get_width()) + 'x' + str(img.get_height()))      # uncomment for debugging
    screen.blit(img,(offset_x,offset_y))
    pygame.display.flip()

def clear_screen():
    screen.fill((0, 0, 0))
    pygame.display.flip()


########################
### Variables Config ###
########################

try:
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
except:
    print('Error: config.ini not found')
    sys.exit()

# Environment
real_path = os.path.dirname(os.path.realpath(__file__))
total_pics = config.getint('Environment', 'total_pics')
file_path = config.get('Environment', 'file_path')
monitor_w = config.getint('Environment', 'monitor_w')
monitor_h = config.getint('Environment', 'monitor_h')

# GPIO
led_pin = config.getint('GPIO', 'led_pin')
btn_start_pin = config.getint('GPIO', 'btn_start_pin')
btn_exit_pin = config.getint('GPIO', 'btn_exit_pin')

# Camera
saturation = config.getint('Camera', 'saturation')
iso = config.getint('Camera', 'iso')
resolution_w = config.getint('Camera', 'resolution_w')
resolution_h = config.getint('Camera', 'resolution_h')
instructions_delay = config.getfloat('Camera', 'instructions_delay')
warmup_delay = config.getfloat('Camera', 'warmup_delay')
capture_delay = config.getfloat('Camera', 'capture_delay')
finished_delay = config.getfloat('Camera', 'finished_delay')

# pygame
transform_x = monitor_w         # how wide to scale the jpg when replaying
transfrom_y = monitor_h         # how high to scale the jpg when replaying
offset_x = 0                    # how far off to left corner to display photos
offset_y = 0                    # how far off to left corner to display photos

####################
### Main Program ###
####################

setupGPIO(led_pin, btn_start_pin, btn_exit_pin)
screen = setupPygame(monitor_w, monitor_h)

print('App is running...')
for x in range(0,5):                                                        # blink LED to show app is running
    GPIO.output(led_pin, True)
    sleep(0.5)
    GPIO.output(led_pin, False)
    sleep(0.5)

show_image(real_path + "/images/intro.png")

try:
    while True:
        GPIO.output(led_pin, True)                                          # turn on LED to show users they can push the button
        if GPIO.event_detected(btn_start_pin):                              # Take Pictures!
            camera = setupCamera(saturation, iso, resolution_w, resolution_h)
            taken_pictures = takePictures(camera, file_path, total_pics, monitor_w, monitor_h, capture_delay)
            create_four_grid(taken_pictures, file_path)
            show_image(real_path + "/images/finished2.png")
            sleep(finished_delay)
            show_image(real_path + "/images/intro.png")
        if GPIO.event_detected(btn_exit_pin):                               # Exit App
            cleanup()
        sleep(0.001)
except KeyboardInterrupt:
    cleanup()
    print "\nBye"


