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
import json
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *

# screen and tile dimensions
SCREEN_W = 1280
SCREEN_H = 960
TILE_W = SCREEN_W / 3
TILE_H = SCREEN_H / 3

class Camera(object):
    def __init__(self, x, y, label, url):
        self.x = x
        self.y = y
        self.label = label
        self.url = url

# reads one image from the source
def readframe(url):
    try:
        response = urllib2.urlopen(url)
        return response.read()
    except Exception:
        return None

def renderText(text, size):
    font = TTF_OpenFont("VCR_OSD_MONO_1.001.ttf", size)
    surface = TTF_RenderText_Shaded(font, text, SDL_Color(255,255,255), SDL_Color(0,0,0))
    TTF_CloseFont(font);
    
    return surface

# renders one camera onto the window
def renderCamera(window, camera):
    # get JPG
    jpeg = readframe(camera.url)
    if jpeg is None:
        return
    rwops = SDL_RWFromMem(jpeg, sys.getsizeof(jpeg))
    image = IMG_LoadTyped_RW(rwops, True, "JPG")

    # blit scaled JPG
    rect = SDL_Rect(TILE_W * camera.x, TILE_H * camera.y, TILE_W, TILE_H)
    SDL_BlitScaled(image, None, SDL_GetWindowSurface(window), rect)
    SDL_FreeSurface(image)
    
    # draw text over it
    SDL_BlitSurface(camera.osd, None, SDL_GetWindowSurface(window), rect)

    SDL_UpdateWindowSurface(window)

def main():
    SDL_Init(SDL_INIT_VIDEO)
    TTF_Init()

    window = SDL_CreateWindow(b"Panopticon",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              SCREEN_W, SCREEN_H, SDL_WINDOW_SHOWN)
    
    event = SDL_Event()
    iterations = 0
    starttime = time.time()
    lasttime = starttime
    file = 0

    cameras = list()
    cameras.append(Camera(0, 0, "KEUKEN", "http://localhost:8000/cgi-bin/nph-mjgrab?2"))
    cameras.append(Camera(1, 0, "WERKPLAATS", "http://localhost:8000/cgi-bin/nph-mjgrab?6"))
    cameras.append(Camera(2, 0, "ACHTERDEUR", "http://localhost:8000/cgi-bin/nph-mjgrab?7"))

    cameras.append(Camera(0, 1, "SPACE", "http://localhost:8000/cgi-bin/nph-mjgrab?3"))
    cameras.append(Camera(1, 1, "SPACE", "http://localhost:8000/cgi-bin/nph-mjgrab?4"))
    cameras.append(Camera(2, 1, "3D-PRINTER", "http://localhost:8000/cgi-bin/nph-mjgrab?1"))

    cameras.append(Camera(0, 2, "INRIT", "http://localhost:8000/cgi-bin/nph-mjgrab?10"))
    cameras.append(Camera(1, 2, "PARKEER", "http://localhost:8000/cgi-bin/nph-mjgrab?9"))
    cameras.append(Camera(2, 2, "PARKEER", "http://localhost:8000/cgi-bin/nph-mjgrab?8"))
    
    # prerender OSD
    for camera in cameras:
        camera.osd = renderText(camera.label, 30)
    
    running = True
    while running:
        for camera in cameras:
            if not running:
                break;

            # draw one cam
            renderCamera(window, camera);
    
            # check for quit button
            while SDL_PollEvent(ctypes.byref(event)):
                if event.type == SDL_QUIT:
                    running = False
    
        # calculate fps
        iterations = iterations + 1
        delta_t = (time.time() - starttime)
        if (delta_t > 0):
            fps = iterations / delta_t
            print(fps)

    SDL_DestroyWindow(window)
    SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())

