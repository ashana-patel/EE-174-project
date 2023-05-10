from __future__ import print_function
from __future__ import division

import platform
import numpy as np
import config

elif config.DEVICE == 'pi':
    from rpi_ws281x import *
    strip = Adafruit_NeoPixel(config.N_PIXELS, config.LED_PIN,
                                       config.LED_FREQ_HZ, config.LED_DMA,
                                       config.LED_INVERT, config.BRIGHTNESS)
    strip.begin()
elif config.DEVICE == 'blinkstick':
    from blinkstick import blinkstick
    import signal
    import sys
    #Will turn all leds off when invoked.
    def signal_handler(signal, frame):
        all_off = [0]*(config.N_PIXELS*3)
        stick.set_led_data(0, all_off)
        sys.exit(0)

    stick = blinkstick.find_first()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

_gamma = np.load(config.GAMMA_TABLE_PATH)

_prev_pixels = np.tile(253, (3, config.N_PIXELS))

pixels = np.tile(1, (3, config.N_PIXELS))

_is_python_2 = int(platform.python_version_tuple()[0]) == 2

def _update_pi():
    global pixels, _prev_pixels
    # Truncate values and cast to integer
    pixels = np.clip(pixels, 0, 255).astype(int)
    # Optional gamma correction
    p = _gamma[pixels] if config.SOFTWARE_GAMMA_CORRECTION else np.copy(pixels)
    # Encode 24-bit LED values in 32 bit integers
    r = np.left_shift(p[0][:].astype(int), 8)
    g = np.left_shift(p[1][:].astype(int), 16)
    b = p[2][:].astype(int)
    rgb = np.bitwise_or(np.bitwise_or(r, g), b)
    for i in range(config.N_PIXELS):
        if np.array_equal(p[:, i], _prev_pixels[:, i]):
            continue
            
        strip._led_data[i] = int(rgb[i])
    _prev_pixels = np.copy(p)
    strip.show()

def _update_blinkstick():
    global pixels
    
    # Truncate values and cast to integer
    pixels = np.clip(pixels, 0, 255).astype(int)
    p = _gamma[pixels] if config.SOFTWARE_GAMMA_CORRECTION else np.copy(pixels)
    # Read the rgb values
    r = p[0][:].astype(int)
    g = p[1][:].astype(int)
    b = p[2][:].astype(int)

    #create array in which we will store the led states
    newstrip = [None]*(config.N_PIXELS*3)

    for i in range(config.N_PIXELS):
        # blinkstick uses GRB format
        newstrip[i*3] = g[i]
        newstrip[i*3+1] = r[i]
        newstrip[i*3+2] = b[i]
    #send the data to the blinkstick
    stick.set_led_data(0, newstrip)


def update():
    """Updates the LED strip values"""
    if config.DEVICE == 'esp8266':
        _update_esp8266()
    elif config.DEVICE == 'pi':
        _update_pi()
    elif config.DEVICE == 'blinkstick':
        _update_blinkstick()
    else:
        raise ValueError('Invalid device selected')


# Execute this file to run a LED strand test
# If everything is working, you should see a red, green, and blue pixel scroll
# across the LED strip continously
if __name__ == '__main__':
    import time
    # Turn all pixels off
    pixels *= 0
    pixels[0, 0] = 255  # Set 1st pixel red
    pixels[1, 1] = 255  # Set 2nd pixel green
    pixels[2, 2] = 255  # Set 3rd pixel blue
    print('Starting LED strand test')
    while True:
        pixels = np.roll(pixels, 1, axis=1)
        update()
        time.sleep(.1)
