# Memory Puzzle (1)
# from http://inventwithpython.com/makinggames.pdf

import random, pygame, sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
REVEALSPEED = 4 # speed boxes' sliding reveals and covers
BOXSIZE = 40 # box height/width
GAPSIZE = 10 # size of gap between boxes

BOARDWIDTH = 2 # number of columns of icons
BOARDHEIGHT = 2 # number of rows of icons
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Noneven number of boxes'

# pixels from edge of screen to board
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, \
"Board is too big for the number of shapes/colors defined."

def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0
    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # stores (x, y) coordinates of first box clicked
    
    music = 'Arigatou.AishitetaHito.mp3' # ***can add own music file (.mp3, .mid, .ogg)
    pygame.mixer.music.load(music) 
    pygame.mixer.music.play(-1, 0.0)
    musicON = True
    
    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True: # main game loop
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and \
                (event.key == K_ESCAPE or event.key == K_q)):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_m: # mute/unmute
                if musicON == True:
                    pygame.mixer.music.pause()
                    musicON = False
                else:
                    pygame.mixer.music.unpause()
                    musicON = True
            elif event.type == KEYUP and event.key == K_r: # restart
                mainBoard, revealedBoxes = restart()
                continue
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP: # mouse clicked (and released)
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # The mouse is currently over a box
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True

                if firstSelection == None: # current box is first clicked
                    firstSelection = (boxx, boxy)
                else:
                    # check if there is a match between the two icons
                    if getShapeAndColor(mainBoard, boxx, boxy) != \
                    getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1]):
                        # re-cover the tiles
                        pygame.time.wait(1000) # 1 second
                        coverBoxesAnimation(mainBoard, [(boxx, boxy), \
                                (firstSelection[0], firstSelection[1])])
                        revealedBoxes[boxx][boxy] = False
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                    elif hasWon(revealedBoxes): # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)
                        mainBoard, revealedBoxes = restart()
                        
                    firstSelection = None
                    
            
        # redraw the screen and wait a clock tick
        pygame.display.update()
        FPSCLOCK.tick(FPS)


# initializes data structure representing which boxes are covered
def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val] * BOARDHEIGHT) # list of boolean values
    return revealedBoxes


# returns data structure representing state of the board    
def getRandomizedBoard():
    # Get a list of every possible shape in every possible order
    icons = []
    for color in ALLCOLORS:
        for shape in ALLSHAPES:
            icons.append((shape, color))

    random.shuffle(icons)
    numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2)
    # list slice the number of icons we need, then duplicate for pair 
    icons = icons[:numIconsUsed] * 2 
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
        
    return board


def splitIntoGroupsOf(groupsize, theList):
    # splits a list into a list of lists, where the inner lists have at most
    # groupsize number of items
    result = []
    for i in range(0, len(theList), groupsize):
        result.append(theList[i:i + groupsize])
    return result
        

def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)


def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            # check if Box[x][y] contains the pixel (x,y)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def drawIcon(shape, color, boxx, boxy):
    quarter = int(BOXSIZE * 0.25)
    half = int(BOXSIZE * 0.5)

    left, top = leftTopCoordsOfBox(boxx, boxy) # get pixel coordinates

    # Draw the shapes
    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF, color, (left+half, top+half), half-5)
        pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left+half, top+half), quarter-5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF, color, (left+quarter, top+quarter, \
                                              half, half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF, color, ((left+half, top), \
        (left+BOXSIZE-1, top+half), (left+half, top+BOXSIZE-1), (left, top+half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top+i), (left+i, top))
            pygame.draw.line(DISPLAYSURF, color, (left+i, top+BOXSIZE-1), \
                             (left+BOXSIZE-1, top+i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top+quarter, BOXSIZE, half))

        
def getShapeAndColor(board, boxx, boxy):
    # board[x][y] = (shape, color)
    return board[boxx][boxy][0], board[boxx][boxy][1]

    
def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed
    # The parameter "boxes" is a list of two-item tuples, each containing the
    # (x,y) location of a box
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])

        if coverage > 0: # draw the cover
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))

    pygame.display.update()
    FPSCLOCK.tick(FPS)

        
def revealBoxesAnimation(board, boxesToReveal):
    # Do the "box reveal" animation
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, - REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    # Do the "box cover" animation
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if revealed[boxx][boxy]:
                # Draw the icon
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)
            else: # Draw a covered box
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, \
                     (left-5, top-5, BOXSIZE+10, BOXSIZE+10), 4)

def startGameAnimation(board):
    # Randomly reveal the boxes 8 at a time
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x,y))
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        DISPLAYSURF.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)

        
def hasWon(revealedBoxes):
##    for x in range(BOARDWIDTH):
##        for y in range(BOARDHEIGHT):
##            if revealedBoxes[x][y] == False:
##                return False
    for i in revealedBoxes:
        if False in i:
            return False # there are still boxes covered
    return True

def restart():
    # Reset the board
    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    drawBoard(mainBoard, revealedBoxes)
    pygame.display.update()
    pygame.time.wait(1000)

    startGameAnimation(mainBoard)
    return mainBoard, revealedBoxes

if __name__ == '__main__': # execute main if program is being run (and not imported)
    main()
