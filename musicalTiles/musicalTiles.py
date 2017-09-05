# Musical Tiles

import pygame, sys, time, random
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 640

FLASHSPEED = 500 # in milliseconds
FLASHDELAY = 120

TILESIZE = 200
TILEGAP = 20
TIMEOUT = 5 # seconds before game over if no button is pushed

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRIGHTRED = (255, 0, 0)
RED = (155, 0, 0)
BRIGHTGREEN = (0, 255, 0)
GREEN = (0, 155, 0)
BRIGHTBLUE = (0, 0, 255)
BLUE = (0, 0, 155)
BRIGHTYELLOW = (255, 255, 0)
YELLOW = (155, 155, 0)
DARKGRAY = (40, 40, 40)

bgColor = BLACK

XMARGIN = int((WINDOWWIDTH - (2*TILESIZE + TILEGAP)) / 2) 
YMARGIN = int((WINDOWHEIGHT - (2*TILESIZE + TILEGAP)) / 2) 

# Rect objects for each of the four buttons
YELLOW_RECT = pygame.Rect(XMARGIN, YMARGIN, TILESIZE, TILESIZE)
BLUE_RECT = pygame.Rect(XMARGIN+TILESIZE+TILEGAP, YMARGIN, \
                       TILESIZE, TILESIZE)
RED_RECT = pygame.Rect(XMARGIN, YMARGIN+TILESIZE+TILEGAP, \
                      TILESIZE, TILESIZE)
GREEN_RECT = pygame.Rect(XMARGIN+TILESIZE+TILEGAP, YMARGIN+TILESIZE+TILEGAP, \
                        TILESIZE, TILESIZE)

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BEEP1, BEEP2, BEEP3, BEEP4

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Musical Tiles')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 16)

    # message (floating text)
    infoSurf = BASICFONT.render('Match the pattern by clicking on the tiles \
or the A, S, Z, X keys', 1, DARKGRAY)
    infoRect = infoSurf.get_rect()
    infoRect.topleft = (10, WINDOWHEIGHT-25)

    # load the sound files
    BEEP1 = pygame.mixer.Sound('beep1.ogg')
    BEEP2 = pygame.mixer.Sound('beep2.ogg')
    BEEP3 = pygame.mixer.Sound('beep3.ogg')
    BEEP4 = pygame.mixer.Sound('beep4.ogg')

    # initialize other game variables
    pattern = [] # stores pattern of colors
    currentStep = 0 # color player should push next
    lastClickTime = 0 # timestamp of player's last tile push
    patternLen = 1
    timeLeft = TIMEOUT
    waitingForInput = False # set true when waiting for user's input sequence
    
    while True: # main game loop
        clicked = None # stores tile clicked
        DISPLAYSURF.fill(bgColor)
        drawButtons()
        # keep track of player score
        scoreSurf = BASICFONT.render('Pattern length: ' + str(patternLen), 1, WHITE)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH-140, 10)
        # keep track of time remaining
        timeSurf = BASICFONT.render('Time remaining: ' + str(timeLeft), 1, WHITE)
        timeRect = timeSurf.get_rect()
        timeRect.topleft = (10, 10)
        
        DISPLAYSURF.blit(scoreSurf, scoreRect)
        DISPLAYSURF.blit(timeSurf, timeRect)
        DISPLAYSURF.blit(infoSurf, infoRect)
        
        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                clicked = getTileClicked(mousex, mousey)
            elif event.type == KEYUP:
                if event.key == K_a:
                    clicked = YELLOW
                elif event.key == K_s:
                    clicked = BLUE
                elif event.key == K_z:
                    clicked = RED
                elif event.key == K_x:
                    clicked = GREEN
                    
        if not waitingForInput:
            # play pattern
            pygame.display.update()
            pygame.time.wait(1000)
            pattern.append(random.choice((RED, GREEN, BLUE, YELLOW)))
            for tile in pattern:
                flashAnimate(tile)
                pygame.time.wait(FLASHDELAY)
            waitingForInput = True
            
        else:
            if currentStep != 0:
                timeLeft = int(TIMEOUT - (time.time() - lastClickTime))
                
            # wait for player inputs
            if clicked and clicked == pattern[currentStep]:
                # pushed correct tile
                flashAnimate(clicked)
                currentStep += 1
                lastClickTime = time.time()

                if currentStep == len(pattern):
                    # correctly followed pattern; increase total steps
                    patternLen += 1
                    waitingForInput = False
                    currentStep = 0
                    # flash pattern length
                    scoreSurf = BASICFONT.render('Pattern length: ' + str(patternLen), 1, BRIGHTRED)
                    DISPLAYSURF.blit(scoreSurf, scoreRect)
                    timeLeft = TIMEOUT
            elif(clicked and clicked != pattern[currentStep]) or \
(currentStep != 0 and time.time() - lastClickTime > TIMEOUT):
                # incorrect tile, or timeout
                gameOverAnimation()
                # restart
                pattern = []
                currentStep = 0
                waitingForInput = False
                patternLen = 1
                timeLeft = TIMEOUT
                pygame.time.wait(1000)
                    
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key in (K_ESCAPE, K_q):
            terminate()
        pygame.event.post(event)


def flashAnimate(color, animationSpeed=50):
    if color == RED:
        sound = BEEP1
        flashColor = BRIGHTRED
        rectangle = RED_RECT
    elif color == GREEN:
        sound = BEEP2
        flashColor = BRIGHTGREEN
        rectangle = GREEN_RECT
    elif color == BLUE:
        sound = BEEP3
        flashColor = BRIGHTBLUE
        rectangle = BLUE_RECT
    elif color == YELLOW:
        sound = BEEP4
        flashColor = BRIGHTYELLOW
        rectangle = YELLOW_RECT

    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface((TILESIZE, TILESIZE))
    flashSurf = flashSurf.convert_alpha() # allows drawing of transparent colors
    r, g, b = flashColor
    sound.play()
    
    # outer loop loops twice, once for 0->255, once for 255->0
    for start, end, step in ((0, 255, 1), (255, 0, -1)):
        for alpha in range(start, end, animationSpeed * step):
            checkForQuit()
            DISPLAYSURF.blit(origSurf, (0, 0))
            flashSurf.fill((r, g, b, alpha))
            DISPLAYSURF.blit(flashSurf, rectangle.topleft)
            pygame.display.update()
            FPSCLOCK.tick(FPS)

    DISPLAYSURF.blit(origSurf, (0, 0))

    
def getTileClicked(x, y):
    if RED_RECT.collidepoint(x, y):
        return RED
    elif GREEN_RECT.collidepoint(x, y):
        return GREEN
    elif BLUE_RECT.collidepoint(x, y):
        return BLUE
    elif YELLOW_RECT.collidepoint(x, y):
        return YELLOW
    else:
        return None
    
    
def drawButtons():
    pygame.draw.rect(DISPLAYSURF, RED, RED_RECT)
    pygame.draw.rect(DISPLAYSURF, GREEN, GREEN_RECT)
    pygame.draw.rect(DISPLAYSURF, BLUE, BLUE_RECT)
    pygame.draw.rect(DISPLAYSURF, YELLOW, YELLOW_RECT)

    
def gameOverAnimation(color=WHITE, animationSpeed=50):
    # play all beeps at once, then flash background
    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface(DISPLAYSURF.get_size())
    flashSurf = flashSurf.convert_alpha()
    BEEP1.play()
    BEEP2.play()
    BEEP3.play()
    BEEP4.play()
    r, g, b = color
    for i in range(3):
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            for alpha in range(start, end, animationSpeed * step):
                checkForQuit()
                flashSurf.fill((r, g, b, alpha))
                DISPLAYSURF.blit(origSurf, (0, 0))
                DISPLAYSURF.blit(flashSurf, (0, 0))
                drawButtons()
                pygame.display.update()
                FPSCLOCK.tick(FPS)

    
if __name__ == '__main__':
    main()
    
