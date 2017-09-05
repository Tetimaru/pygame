# adapted from https://inventwithpython.com/makinggames.pdf
#
# the game world can be considered an infinite space
# the portion of the space shown on the game screen is defined by the camera Rect


import random, time, sys, math, pygame
from pygame.locals import *

FPS = 30
WIN_WIDTH = 640
WIN_HEIGHT = 480

GRASS_COLOR = (24, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

CAMERA_SLACK = 90 # how far from the center the squirrel moves before moving the camera
MOVE_RATE = 9
BOUNCE_RATE = 6 # larger = slower
BOUNCE_HEIGHT = 30
START_SIZE = 25
WIN_SIZE = 300 # target size to win
INVULN_TIME = 2 # invulnerability in seconds after being hit
MAX_HEALTH = 3

NUM_GRASS_TYPES = 3
NUM_GRASS = 80 # number of grass "objects" in the active area
NUM_SQUIRRELS = 30 # "
SQUIRREL_MIN_SPEED = 3
SQUIRREL_MAX_SPEED = 7
DIR_CHANGE_FREQ = 2 # % chance of direction change per frame

LEFT = 'left'
RIGHT = 'right'


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    cameraRect = pygame.Rect(camerax, cameray, WIN_WIDTH, WIN_HEIGHT)
    while True:
        # create a Rect object with random coords within the "active area"
        # objects should not be spawned directly within the camera view (they would be
        # rendered immediately in the next frame and look weird), but they also should
        # not be spawned too far away as the probability of encountering them in future
        # camera views would be extremely low
        x = random.randint(camerax - WIN_WIDTH, camerax + (2 * WIN_WIDTH))
        y = random.randint(cameray - WIN_HEIGHT, cameray + (2 * WIN_HEIGHT))
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y

        
def makeNewGrass(camerax, cameray):
    ###############################
    # Grass object
    #   grassImage (num): there are NUM_GRASS_TYPES forms of grass
    #   width
    #   height
    #   x
    #   y : coords of topleft
    #   rect: Rect of grassObj
    ###############################
    gr = {}
    gr['grassImage'] = random.randint(0, NUM_GRASS_TYPES - 1)
    gr['width'] = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']) )
    return gr


def runGame():
    invulnerableMode = False # if player is invulnerable
    invulnerableStartTime = 0
    gameOverMode = False # if the player has lost
    gameOverStartTime = 0
    winMode = False # if the player has won

    camerax = 0
    cameray = 0 # coordinates of top left of the camera Rect 

    grassObjs = [] # stores all grass "objects" in the game
    squirrelObjs = [] # " (non-player squirrels)
    playerObj = {'surface': pygame.transform.scale(L_SQUIR_IMG, (START_SIZE, START_SIZE)),
                 'facing': LEFT,
                 'size': START_SIZE,
                 'x': WIN_WIDTH / 2,
                 'y': WIN_HEIGHT / 2,
                 # bounce: (standing) 0 -----------> BOUNCE_RATE (completion of bounce)
                 'bounce': 0 
                 'health': MAX_HEALTH}

    moveLeft = False
    moveRight = False
    moveUp = False
    moveDown = False

    # add random grass to field
    for i in range(10):
        grassObjs.append(makeNewGrass(camerax, cameray))
        grassObjs[i]['x'] = random.randint(0, WIN_WIDTH)
        grassObjs[i]['y'] = random.randint(0, WIN_HEIGHT)
    
    while True:
        DISPLAYSURF.fill(GRASS_COLOR)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_SQUIR_IMG, R_SQUIR_IMG, GRASSIMAGES
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('gameicon.jpg'))
    DISPLAYSURF = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('Squirrel')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    L_SQUIR_IMG = pygame.image.load('squirrel.png')
    R_SQUIR_IMG = pygame.transform.flip(L_SQUIR_IMG, True, False)
    GRASSIMAGES = []
    for i in range(1, NUM_GRASS_TYPES):
        GRASSIMAGES.append(pygame.image.load('grass%s.png' % i))

    while True:
        runGame()


if __name__ == '__main__':
    main()

    
