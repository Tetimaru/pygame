# Grow longer by eating fruits
# Don't crash into the wall or yourself

import pygame, random, sys
from pygame.locals import *

WINDOWWIDTH = 480
WINDOWHEIGHT = 480
GRIDSIZE = 20
assert WINDOWWIDTH%GRIDSIZE == 0, "Window width must be multiple of cell size"
assert WINDOWHEIGHT%GRIDSIZE == 0, "Window height must be multiple of cell size"
GRIDWIDTH = int(WINDOWWIDTH/GRIDSIZE)
GRIDHEIGHT = int(WINDOWHEIGHT/GRIDSIZE)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (60, 60, 60)
BGCOLOR = BLACK
TITLEFONTSIZE = 72

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # index of worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, TITLEFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    TITLEFONT = pygame.font.SysFont('batangbatangchegungsuhgungsuhche', 72)
    pygame.display.set_caption('Snake')
    
    showStartScreen()
    
    
    while True:
        checkForQuit()
        showDifficultySelect()
        runGame()
        gameOver()


def runGame():
    # Set a random start point
    startx = random.randint(5, GRIDWIDTH-6)
    starty = random.randint(5, GRIDHEIGHT-6)
    direction = RIGHT
    
    wormCoords = [{'x': startx, 'y': starty},
                  {'x': startx-1, 'y': starty},
                  {'x': startx-2, 'y': starty}] # starting length = 3
    
    length = 3
    # Set a random position for the fruit
    apple = getRandomLocation()

    DISPLAYSURF.fill(BGCOLOR)
    drawGrid()
    drawApple(apple)
    drawWorm(wormCoords)
    drawScore(length)
    
    while True:
        checkForQuit()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key in (K_RIGHT, K_d) and direction != LEFT:
##                    for i in range(len(wormCoords), 1, -1):
##                        wormCoords[i-1]['x'] = wormCoords[i-2]['x']
##                        wormCoords[i-1]['y'] = wormCoords[i-2]['y']
##                    wormCoords[HEAD]['x'] += 1
                    direction = RIGHT
                elif event.key in (K_LEFT, K_a) and direction != RIGHT:
                    direction = LEFT
                elif event.key in (K_UP, K_w) and direction != DOWN:
                    direction = UP
                elif event.key in (K_DOWN, K_s) and direction != UP:
                    direction = DOWN

        # to simulate worm movement, add where its head moved to
        # at the beginning and delete the end
        if wormCoords[HEAD] == apple:
            apple = getRandomLocation()
            length += 1
        else:
            del wormCoords[-1]
        
        if direction == RIGHT:
            # how dictionary assignments work:
            # red = dict(...)
            # yellow = red (yellow is like a pointer to red, will change on
            # updates to red)
            # tl;dr: to not track another dictionary's changes, you must
            # reference one key at a time, not the whole structure
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}

        wormCoords.insert(0, newHead)

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawApple(apple)
        drawWorm(wormCoords)
        drawScore(length)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
        if checkCollision(wormCoords): # game over
            return
            


def getRandomLocation():
    return {'x': random.randint(0, GRIDWIDTH-1), \
            'y': random.randint(0, GRIDHEIGHT-1)}


def checkCollision(location):
    # check if worm hit window edge
    if location[HEAD]['x'] < 0 or location[HEAD]['x'] >= GRIDWIDTH:
        return True
    if location[HEAD]['y'] < 0 or location[HEAD]['y'] >= GRIDHEIGHT:
        return True

    # check if worm hit iself
    for wormBody in location[1:]:
        if location[HEAD]['x'] == wormBody['x']:
            if location[HEAD]['y'] == wormBody['y']:
                return True
        

def showDifficultySelect():
    global FPS
    DISPLAYSURF.fill(BLACK)
    
    easySurf = TITLEFONT.render('Easy', 1, DARKGREEN, GREEN)
    easyRect = easySurf.get_rect()
    easyRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/4)
    DISPLAYSURF.blit(easySurf, easyRect)
    
    normalSurf = TITLEFONT.render('Normal', 1, DARKGREEN, GREEN)
    normalRect = normalSurf.get_rect()
    normalRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
    DISPLAYSURF.blit(normalSurf, normalRect)
    
    hardSurf = TITLEFONT.render('Hard', 1, DARKGREEN, GREEN)
    hardRect = hardSurf.get_rect()
    hardRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT*3/4)
    DISPLAYSURF.blit(hardSurf, hardRect)

    pygame.display.update()
    
    while True:
        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                x, y = event.pos
                if easyRect.collidepoint(x, y):
                    FPS = 5
                    return
                elif normalRect.collidepoint(x, y):
                    FPS = 10
                    return
                elif hardRect.collidepoint(x, y):
                    FPS = 15
                    return
    
    
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
        

def drawMsg(message):
    pressKeySurf = BASICFONT.render(message, True, WHITE)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.bottomright = (WINDOWWIDTH - 20, WINDOWHEIGHT - 10)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key in (K_ESCAPE, K_q):
        terminate()
    return keyUpEvents[0].key

        
def showStartScreen():

    titleSurf1 = TITLEFONT.render('Snake', True, WHITE, DARKGREEN)
    titleSurf2 = TITLEFONT.render('Snake', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    
    while True:
        checkForQuit()
        DISPLAYSURF.fill(BGCOLOR)
        
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawMsg('Press any key to continue')

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        
        pygame.display.update()
##        FPSCLOCK.tick(FPS)
##        degrees1 += 3
##        degrees2 += 7
        

def drawGrid():
    for x in range(GRIDSIZE, WINDOWWIDTH, GRIDSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x,0), (x, WINDOWHEIGHT))
    for y in range(GRIDSIZE, WINDOWHEIGHT, GRIDSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0,y), (WINDOWWIDTH,y))


def drawWorm(location):
##    for i in range(len(location)):
##        x = location[i]['x'] * GRIDSIZE
##        y = location[i]['y'] * GRIDSIZE
    for wormBlock in location:
        x = wormBlock['x'] * GRIDSIZE
        y = wormBlock['y'] * GRIDSIZE
        wormRect = pygame.Rect(x, y, GRIDSIZE, GRIDSIZE)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormRect)
        wormBorderRect = pygame.Rect(x, y, GRIDSIZE, GRIDSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormBorderRect, \
                         int(GRIDWIDTH/7))
         

def drawScore(length):
    scoreSurf = BASICFONT.render('Length: ' + str(length), 1, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topright = (WINDOWWIDTH-20, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    
def drawApple(location):
    x = location['x'] * GRIDSIZE
    y = location['y'] * GRIDSIZE
    appleRect = pygame.Rect(x, y, GRIDSIZE, GRIDSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def gameOver():
    gameSurf = TITLEFONT.render('Game', 1, WHITE)
    gameRect = gameSurf.get_rect()
    gameRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/3)
    DISPLAYSURF.blit(gameSurf, gameRect)

    gameSurf = TITLEFONT.render('Over', 1, WHITE)
    gameRect = gameSurf.get_rect()
    gameRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/3+108)
    DISPLAYSURF.blit(gameSurf, gameRect)

    drawMsg('Press R to restart')
    pygame.display.update()
    
    while True:
        checkForQuit()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_r:
                    return
    
    
if __name__ == '__main__':
    main()
