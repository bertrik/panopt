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

class Camera(object):
    def __init__(self, x, y, scale, label, url):
        self.x = x
        self.y = y
        self.scale = scale
        self.label = label
        self.url = url

# reads one image from the source
def readframe(url):
    try:
        response = urllib2.urlopen(url)
        return response.read()
    except Exception:
        return None

# returns a surface with the text rendered in white with a black outline in the specified size
def renderText(text, size):
    font = TTF_OpenFont("VCR_OSD_MONO_1.001.ttf", size)
    
    TTF_SetFontOutline(font, 2)
    outline = TTF_RenderText_Blended(font, text, SDL_Color(0, 0, 0))
    TTF_SetFontOutline(font, 0)
    surface = TTF_RenderText_Blended(font, text, SDL_Color(255,255,255))
    TTF_CloseFont(font)

    SDL_BlitSurface(surface, None, outline, SDL_Rect(2,2,0,0))
    return outline

# renders one camera onto the window
def renderCamera(window, camera):
    # get window properties
    cw = ctypes.c_int()
    ch = ctypes.c_int()
    SDL_GetWindowSize(window, ctypes.byref(cw), ctypes.byref(ch))
    w,h = cw.value,ch.value

    # get JPG
    jpeg = readframe(camera.url)
    if jpeg is None:
        return
    rwops = SDL_RWFromMem(jpeg, sys.getsizeof(jpeg))
    image = IMG_LoadTyped_RW(rwops, True, "JPG")

    # blit scaled JPG
    x = w * camera.x / 4
    y = h * camera.y / 3
    rect = SDL_Rect(x, y, w * camera.scale / 4, h * camera.scale / 3)
    SDL_BlitScaled(image, None, SDL_GetWindowSurface(window), rect)
    SDL_FreeSurface(image)
    
    # draw text over it
    SDL_BlitSurface(camera.osd, None, SDL_GetWindowSurface(window), rect)

    SDL_UpdateWindowSurface(window)

def main():
    SDL_Init(SDL_INIT_VIDEO)
    TTF_Init()

    window = SDL_CreateWindow(b"Panopticon",
                              SDL_WINDOWPOS_CENTERED, 
                              SDL_WINDOWPOS_CENTERED,
                              1024, 
                              768, 
                              SDL_WINDOW_SHOWN)
    SDL_SetWindowFullscreen(window, SDL_WINDOW_FULLSCREEN_DESKTOP)
    
    event = SDL_Event()
    iterations = 0
    starttime = time.time()
    lasttime = starttime
    file = 0

    cameras = list()
    cameras.append(Camera(0, 0, 1, "ACHTERDEUR", "http://localhost:8000/cgi-bin/nph-mjgrab?7"))
    cameras.append(Camera(0, 1, 1, "WERKPLAATS", "http://localhost:8000/cgi-bin/nph-mjgrab?6"))
    cameras.append(Camera(0, 2, 1, "KEUKEN", "http://localhost:8000/cgi-bin/nph-mjgrab?2"))

    cameras.append(Camera(1, 0, 2, "SPACE", "http://localhost:8000/cgi-bin/nph-mjgrab?4"))
    cameras.append(Camera(1, 2, 1, "SPACE", "http://localhost:8000/cgi-bin/nph-mjgrab?3"))

    cameras.append(Camera(2, 2, 1, "3D-PRINTER", "http://localhost:8000/cgi-bin/nph-mjgrab?1"))

    cameras.append(Camera(3, 0, 1, "PARKEER", "http://localhost:8000/cgi-bin/nph-mjgrab?9"))
    cameras.append(Camera(3, 1, 1, "PARKEER", "http://localhost:8000/cgi-bin/nph-mjgrab?8"))
    cameras.append(Camera(3, 2, 1, "INRIT", "http://localhost:8000/cgi-bin/nph-mjgrab?10"))
    
    # prerender OSD
    for camera in cameras:
        camera.osd = renderText(camera.label, 30)
    
    running = True
    while running:
        for camera in cameras:
            if not running:
                break

            # draw one cam
            renderCamera(window, camera)
    
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

