# Slide Puzzle
# Further ideas: Create menu, grey out buttons, change tile colour option (DONE),
# game difficulty (change number of original scrambles, timer? - lace it with menu), add score
#
# *********************************************************
# USAGE: python slidePuzzle.py <difficulty>
# where difficuilty is 0, 1, or 2 (default 1)
# *********************************************************

import pygame, sys, random
from pygame.locals import *

TILESIZE = 80
WINDOWWIDTH = 720
WINDOWHEIGHT = 580
FPS = 30
BLANK = None

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)
RED = (204, 0, 0)
BLUE = (0, 0, 204)
YELLOW = (204, 204, 0)
GRAY = (180, 180, 180)

BGCOLOR = DARKTURQUOISE
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# difficulties
EASY = 0
NORMAL = 1
HARD = 2

# Initialize the starting board, then perform animations to scramble the board
# for user to solve. Instead of using an algorithm to piece together the
# solution, just retrace the steps to scramble to return to original position
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT
    global NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT
    global BOARDWIDTH, BOARDHEIGHT, XMARGIN, YMARGIN, TILECOLOR

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Tile Sliding Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    BASICFONT2 = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE-4)
    
    music = "Lost.mp3" # ***can add own music file (.mp3, .mid, .ogg)
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1, 0.0)
    musicOn = True
    
    difficulty = NORMAL
    if len(sys.argv) == 1: # no difficulty argument specified
        pass
    elif len(sys.argv) == 2:
        difficulty = int(sys.argv[1])
    else:
        print("USAGE: python slidePuzzle.py <difficulty>")
        return
    
    if difficulty == EASY:
        BOARDWIDTH, BOARDHEIGHT = 3, 3
        numScrambles = 40
    elif difficulty == NORMAL:
        BOARDWIDTH, BOARDHEIGHT = 4, 4
        numScrambles = 80
    else:
        BOARDWIDTH, BOARDHEIGHT = 5, 5
        numScrambles = 160

    XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH-1))) / 2)
    YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT-1))) / 2)
    tileColors = [GREEN, RED, BLUE, YELLOW]
    TILECOLOR = random.choice(tileColors)
    
    # Store the option buttons and their rectangles in OPTIONS
    RESET_SURF, RESET_RECT = makeText('Reset', BUTTONTEXTCOLOR, GRAY, \
                                      WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    NEW_SURF, NEW_RECT = makeText('New Game', BUTTONTEXTCOLOR, GRAY, \
                                      WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = makeText('Solve', BUTTONTEXTCOLOR, GRAY, \
                                      WINDOWWIDTH - 120, WINDOWHEIGHT - 30)
    COLOR_RECT = pygame.Rect(WINDOWWIDTH - 60, 20, 40, 40)
    
    mainBoard, solutionSeq = generateNewPuzzle(numScrambles)
    SOLVEDBOARD = getStartingBoard()
    allMoves = [] # list of moves made from the solved configuration
    numSlides = 0
    
    while True: # main game loop
        slideTo = None # the direction, if any, a tile should slide
        msg = 'Click tile or press arrow keys to slide' # text shown in upper left corner
        if mainBoard == SOLVEDBOARD:
            msg = 'Puzzle solved!'
            
        drawBoard(mainBoard, msg)
        # Record number of slides made
        slideSurf = BASICFONT2.render('Slides made: ' + str(numSlides), 1, WHITE)
        slideRect = slideSurf.get_rect()
        slideRect.topleft = (10, WINDOWHEIGHT-25)
        DISPLAYSURF.blit(slideSurf, slideRect)
        pygame.draw.rect(DISPLAYSURF, tileColors[1], COLOR_RECT)

        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == KEYUP:
                # check if user pressed a key to slide a tile
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN
                # check if user mute/unmuted sound
                elif event.key == K_m:
                    if musicOn == True:
                        pygame.mixer.music.pause()
                        musicOn = False
                    else:
                        pygame.mixer.music.unpause()
                        musicOn = True
            elif event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if user clicked an option button
                    if RESET_RECT.collidepoint(event.pos): # undo all moves
                        resetAnimation(mainBoard, allMoves)
                        allMoves = []
                        numSlides = 0
                    elif NEW_RECT.collidepoint(event.pos): # new game
                        mainBoard, solutionSeq = generateNewPuzzle(numScrambles)
                        allMoves = []
                        numSlides = 0
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSeq+allMoves)
                        allMoves = []
                    elif COLOR_RECT.collidepoint(event.pos):
                        tileColors.append(tileColors[0])
                        del tileColors[0]
                        TILECOLOR = tileColors[0]
                else: # user clicked a tile
                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx-1 and spoty == blanky:
                       slideTo = RIGHT # tile to left
                    elif spotx == blankx+1 and spoty == blanky:
                       slideTo = LEFT # tile to right
                    elif spotx == blankx and spoty == blanky-1:
                       slideTo = DOWN # tile above
                    elif spotx == blankx and spoty == blanky+1:
                        slideTo = UP # tile below
                        

        if slideTo:
            slideAnimation(mainBoard, slideTo, \
                           'Click tile or press arrow keys to slide', 10)
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo) # record the move
            numSlides += 1
            
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all events of type
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key in (K_ESCAPE, K_q): # q or esc quit the game
            terminate()
        pygame.event.post(event) # put other KEYUP events back


def getStartingBoard():
    # Return a board data structure with tiles in solved state
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH # maintain board structure [1][2][3]/[4][5][6]
        board.append(column)
        counter -= (BOARDWIDTH * (BOARDHEIGHT-1)) + BOARDWIDTH - 1
        # we added BOARDWIDTH an extra time in inner for loop

    board[BOARDWIDTH-1][BOARDHEIGHT-1] = None # empty tile
    return board


def getBlankPosition(board):
    # Return x,y board coordinates of the blank space
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == None:
                return (x, y)


def makeMove(board, move):
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        # performing swaps this way allows you to forego a temp variable
        board[blankx][blanky], board[blankx][blanky+1] = \
        board[blankx][blanky+1], board[blankx][blanky]
    if move == DOWN:
        board[blankx][blanky], board[blankx][blanky-1] = \
        board[blankx][blanky-1], board[blankx][blanky]
    if move == LEFT:
        board[blankx][blanky], board[blankx+1][blanky] = \
        board[blankx+1][blanky], board[blankx][blanky]
    if move == RIGHT: 
        board[blankx][blanky], board[blankx-1][blanky] = \
        board[blankx-1][blanky], board[blankx][blanky] 

        
def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
            (move == DOWN and blanky != 0) or \
            (move == LEFT and blankx != len(board) - 1) or \
            (move == RIGHT and blankx != 0)
# if the blank space is in the left-most column, you cannot move a tile to it
# by moving right (as there is no tile to its left)


def getRandomMove(board, lastMove=None):
    # start with a full list of all four moves
    validMoves = [UP, DOWN, LEFT, RIGHT]

    # remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        # don't undo your previous move
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    # return a random move from the list of remaining moves
    # At worst, if blank space is in corner (so two movements are restricted)
    # and a lastMove is passed, there is ONE valid move left
    return random.choice(validMoves)

    
def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1) # 1 pixel gap between tiles
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    # from the (x, y) pixel coordinates, get board coordinates
    for i in range(len(board)):
        for j in range(len(board[0])):
            left, top = getLeftTopOfTile(i, j)
            currentRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if currentRect.collidepoint(x, y):
                return (i, j)

    return (None, None)

            
def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    # draw a tile at board coordinates tilex and tiley, optionally a few pixels
    # over (determined by adjx, adjy)
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left+adjx, top+adjy, \
                                              TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE/2) + adjx, top + int(TILESIZE/2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, message):
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    # draw board border
    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE 
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left-5, top-5, \
                                                width+11, height+11), 4)

    # draw option buttons
    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)
    

def slideAnimation(board, direction, message, animationSpeed):
    
    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx # location of tile to move
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    # prepare the base surface
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    # tile to be moved "disappears" from its original area (on baseSurf)
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        # animate tile sliding over
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

    
def generateNewPuzzle(numSlides):
    # Scramble the board for user to solve (ie. return to original configuration)
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500)
    
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Please wait, generating new puzzle...', int(TILESIZE/2))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move

    return (board, sequence)


def resetAnimation(board, allMoves):
    # get all of the slides in allMoves in reverse
    revAllMoves = allMoves[:] # gets a copy of the list
    revAllMoves.reverse()

    for move in revAllMoves:
        if move == UP:
            oppMove = DOWN
        elif move == DOWN:
            oppMove = UP
        elif move == LEFT:
            oppMove = RIGHT
        elif move == RIGHT:
            oppMove = LEFT

        slideAnimation(board, oppMove, '', int(TILESIZE/2))
        makeMove(board, oppMove)

        
if __name__ == '__main__':
    main()
        
