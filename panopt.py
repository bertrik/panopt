#!/usr/bin/env python

# Shows several JPG camera snapshots tiled into a bigger image.
#
# requires python2, ppython-sdl2 !
#
# Possible improvements:
# - write optional label ("CAM1") for each image (and use a clunky "camera" font)
# - read layout from a config file instead of hardcoding it
# - allow some tiles to be bigger than others
# - make quit work better by using smaller loops

import time
import sys
import ctypes
import urllib2
from sdl2 import *
from sdl2.sdlimage import *

# screen and tile dimensions
SCREEN_W = 1280
SCREEN_H = 960
TILE_W = SCREEN_W / 3
TILE_H = SCREEN_H / 3

# reads one image from the source
def readframe(url):
    response = urllib2.urlopen(url)
    return response.read()

# updates the main screen with one image
def update(window, x, y, url):
    image = readframe(url)
    rwops = SDL_RWFromMem(image, sys.getsizeof(image))
    image = IMG_LoadTyped_RW(rwops, True, "JPG")
    rect = SDL_Rect(TILE_W * x, TILE_H * y, TILE_W, TILE_H)
    SDL_BlitScaled(image, None, SDL_GetWindowSurface(window), rect)
    SDL_FreeSurface(image)
    SDL_UpdateWindowSurface(window)

def main():
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b"Panopticon",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              SCREEN_W, SCREEN_H, SDL_WINDOW_SHOWN)
    
    event = SDL_Event()
    iterations = 0
    starttime = time.time()
    file = 0

    while True:
        # draw all rectangles into buffer
        update(window, 0, 0, "http://localhost:8000/cgi-bin/nph-mjgrab?2")
        update(window, 1, 0, "http://localhost:8000/cgi-bin/nph-mjgrab?4")
        update(window, 2, 0, "http://localhost:8000/cgi-bin/nph-mjgrab?6")
        update(window, 0, 1, "http://localhost:8000/cgi-bin/nph-mjgrab?7")
        update(window, 1, 1, "http://localhost:8000/cgi-bin/nph-mjgrab?8")
        update(window, 2, 1, "http://localhost:8000/cgi-bin/nph-mjgrab?9")
        update(window, 0, 2, "http://localhost:8000/cgi-bin/nph-mjgrab?10")
    
        # calculate fps
        iterations = iterations + 1
        delta_t = (time.time() - starttime)
        if (delta_t > 0):
            fps = iterations / delta_t
            print(fps)
        
        # check for quit button
        while SDL_PollEvent(ctypes.byref(event)):
            if event.type == SDL_QUIT:
                break
    
    SDL_DestroyWindow(window)
    SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())

