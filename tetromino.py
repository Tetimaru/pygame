import random, time, pygame, sys
from pygame.locals import *

# constants
FPS = 10
WIN_WIDTH = 640
WIN_HEIGHT = 480
BOX_SIZE = 20
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLANK = '.'

# if the user continues to hold left/right, how often the piece moves one space (delay)
MOVE_HORIZ_FREQ = 0.15
MOVE_VERT_FREQ = 0.1

X_MARGIN = int((WIN_WIDTH - (BOARD_WIDTH * BOX_SIZE)) / 2)
TOP_MARGIN = WIN_HEIGHT - (BOARD_HEIGHT * BOX_SIZE) - 5

#                R    G    B
WHITE        = (255, 255, 255)
GRAY         = (185, 185, 185) 
BLACK        = (0, 0, 0)
RED          = (155, 0, 0)
LIGHT_RED     = (175, 20, 20)
GREEN        = (0, 155, 0)
LIGHT_GREEN   = (20, 175, 20)
BLUE         = (0, 0, 155)
LIGHT_BLUE    = (20, 20, 175)
YELLOW       = (155, 155, 0)  
LIGHT_YELLOW  = (175, 175, 20)

BORDER_COLOR = (135, 206, 250)
BG_COLOR = BLACK
TEXT_COLOR = WHITE
TEXT_SHADOW_COLOR = GRAY
COLORS = (BLUE, GREEN, RED, YELLOW)
LIGHT_COLORS = (LIGHT_BLUE, LIGHT_GREEN, LIGHT_RED, LIGHT_YELLOW)

assert len(COLORS) == len(LIGHT_COLORS) # each color must have light color

TEMPLATE_WIDTH = 5
TEMPLATE_HEIGHT = 5

BORDER_WIDTH = 3
NEXT_PIECE_RECT_TOPLEFT = (BOX_SIZE * 2, BOX_SIZE * 2)

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..00.',
                     '.00..',
                     '.....'],
                    ['.....',
                     '..0..',
                     '..00.',
                     '...0.',
                     '.....']] # rotations of S shape piece

SHAPES = {'S': S_SHAPE_TEMPLATE}

SONG1 = '[AMFS][AMV] Ichinen Nikagetsu Hatsuka (1-2--20-) - BRIGHT (Vietsub).mp3'
SONG2 = 'AMV - Au Tabi Suki ni Natte - Bright.mp3'
SONG3 = 'AMV Sayaka Shionoya - Calling Out.mp3'
SONG4 = 'Arigatou.AishitetaHito.mp3'
SONG5 = 'Kirai Demo Suki Aishiteru- BRIGHT [Vietsub].mp3'

SONGS = [SONG1, SONG2, SONG3, SONG4, SONG5]

def main():
    global FPS_CLOCK, DISPLAY_SURF, BASIC_FONT, BIG_FONT
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', 18)
    BIG_FONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetris')
    showTextScreen('Tetris')

    while True: # game loop
        runGame()
        

def runGame():
    # setup variables for start of game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False
    movingLeft = False
    movingRight = False
    score = 0
    level = 0
    fallFreq = MOVE_VERT_FREQ

    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()

    currentSong = 0
    pygame.mixer.music.load(SONGS[currentSong])
    pygame.mixer.music.play(-1, 0.0)
    musicON = True
    
    while True:     # main game loop
        if None == fallingPiece:
            # start a new piece at the top
            fallingPiece = nextPiece
            nextPiece = getNewPiece()
            lastFallTime = time.time() # reset lastFallTime

            if not isValidPosition(board, fallingPiece):
                return # can't fit new piece on board, so game over
            
        checkForQuit()
        for event in pygame.event.get():    # event handling loop
            if KEYUP == event.type:
                if K_m == event.key: # mute
                    if True == musicON:
                        pygame.mixer.music.pause()
                        musicON = False
                    else:
                        pygame.mixer.music.unpause()
                        musicON = True
                elif (K_LSHIFT == event.key or K_RSHIFT == event.key):
                    # change songs
                    currentSong = (currentSong + 1) % len(SONGS)
                    pygame.mixer.music.load(SONGS[currentSong])
                    pygame.mixer.music.play(-1, 0.0)
                elif (K_LEFT == event.key or K_a == event.key): # stop moving in direction 
                    movingLeft = False
                elif (K_RIGHT == event.key or K_d == event.key):
                    movingRight = False
                elif (K_DOWN == event.key or K_s == event.key):
                    movingDown = False
            elif KEYDOWN == event.type:
                # move left
                if (K_LEFT == event.key or K_a == event.key) and \
                   isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                    movingLeft = True
                    movingRight = False # to make sure not both are true
                    lastMoveSidewaysTime = time.time()
                # move right
                elif (K_RIGHT == event.key or K_d == event.key) and \
                   isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                    movingRight = True
                    movingLeft = False
                    lastMoveSidewaysTime = time.time()
                # rotate the block
                elif (K_UP == event.key or K_w == event.key):
                    fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % \
                                               len(SHAPES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        # modulo works with negative numbers
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % \
                                                   len(SHAPES[fallingPiece['shape']])
                        
                #elif (K_DOWN == event.key or K_s == event.key):
                 #   movingDown = False

        # move the block according to user input
        if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVE_HORIZ_FREQ:
            if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
                fallingPiece['x'] -= 1
            elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
                fallingPiece['x'] += 1
            lastMoveSidewaysTime = time.time()

        # piece falls by itself
        if time.time() - lastFallTime > fallFreq:
            # see if piece has landed
            if not isValidPosition(board, fallingPiece, adjY=1):
                # set it on the board
                addToBoard(board, fallingPiece)
                fallingPiece = None
            else:
                # move block down
                fallingPiece['y'] += 1
                lastFallTime = time.time()

        # draw everything onto the screen
        DISPLAY_SURF.fill(BG_COLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        if fallingPiece != None:
            drawPiece(fallingPiece)
        
        pygame.display.update()
        FPS_CLOCK.tick(FPS)

    
def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()
    
    
def checkForKeyPress():
    checkForQuit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if KEYDOWN == event.type:
            continue    # remove KEYDOWN events from event queue
        return event.key
    return None


def showTextScreen(text):
    # This function displays large text in the center of
    # the screen until a key is pressed
    titleSurf, titleRect = makeTextObjs(text, BIG_FONT, TEXT_SHADOW_COLOR) # text shadow
    titleRect.center = (WIN_WIDTH/2, WIN_HEIGHT/2)
    DISPLAY_SURF.blit(titleSurf, titleRect)
    
    titleSurf, titleRect = makeTextObjs(text, BIG_FONT, TEXT_COLOR) # text
    titleRect.center = (WIN_WIDTH/2 - 3, WIN_HEIGHT/2 - 3)
    DISPLAY_SURF.blit(titleSurf, titleRect) # wow! 3D effect!!

    pressKeySurf, pressKeyRect = makeTextObjs('Press any key to start playing', BASIC_FONT, \
                                              TEXT_COLOR)
    pressKeyRect.center = (WIN_WIDTH/2, WIN_HEIGHT/2 + 100)
    DISPLAY_SURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() == None:
        pygame.display.update()
        FPS_CLOCK.tick()
        

def checkForQuit():
    for event in pygame.event.get(QUIT):
        terminate()


def getNewPiece():
    # return a random new piece in a random rotation and color  
    shape = random.choice(list(SHAPES.keys()))

    # piece data structure ********************************
    newPiece = {'shape': shape,
                'rotation': random.randint(0, len(SHAPES[shape])-1),
                # (x, y) coordinates of top left of template
                'x': int(BOARD_WIDTH/2) - int(TEMPLATE_WIDTH/2), 
                'y': -2, # start it above the board (i.e. less than 0)
                'color': random.randint(0, len(COLORS)-1)}
    return newPiece


def addToBoard(board, piece):
    for x in range(TEMPLATE_WIDTH):
        for y in range(TEMPLATE_HEIGHT):
            if SHAPES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']

                
def getBlankBoard():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARD_WIDTH):
        board.append([BLANK] * BOARD_HEIGHT)
    return board


def isOnBoard(x, y):
    return x >= 0 and x < BOARD_WIDTH and y < BOARD_HEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if piece is within board and not colliding
    # adjX, i.e. adjustedX, allows us to check the validity of piece's position if it was
    # moved adjX spaces horizontally
    for x in range(TEMPLATE_WIDTH):
        for y in range(TEMPLATE_HEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or BLANK == SHAPES[piece['shape']][piece['rotation']][y][x]:
                continue

            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK: # collision
                return False
    return True


def convertToPixelCoords(board_x, board_y):
    # map board (x, y) coordinates to pixel (x, y) coordinates
    return (X_MARGIN + BOX_SIZE*board_x, TOP_MARGIN + BOX_SIZE*board_y) 


def drawStatus(score, level):
    # draw the score text
    scoreSurf = BASIC_FONT.render('Score: %s' % score, True, TEXT_COLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WIN_WIDTH - 150, 20)
    DISPLAY_SURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = BASIC_FONT.render('Level: %s' % level, True, TEXT_COLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WIN_WIDTH - 150, 50)
    DISPLAY_SURF.blit(levelSurf, levelRect)

    
def drawUnit(board_x, board_y, color):
    # Unit = one grid space
    # A tetris block is composed of 4 units
    if color == BLANK:
        return  
    
    pixel_x, pixel_y = convertToPixelCoords(board_x, board_y)
    pygame.draw.rect(DISPLAY_SURF, COLORS[color], (pixel_x + 1, pixel_y + 1, \
                                                   BOX_SIZE - 1, BOX_SIZE - 1))
    pygame.draw.rect(DISPLAY_SURF, LIGHT_COLORS[color], (pixel_x + 1, pixel_y + 1, \
                                                         BOX_SIZE - 4, BOX_SIZE - 4))
    

def drawPiece(piece):
    shapeToDraw = SHAPES[piece['shape']][piece['rotation']] # 2D array, piece[''] is a dict entry

    # draw each of the blocks that make up the piece
    for x in range(TEMPLATE_WIDTH):
        for y in range(TEMPLATE_HEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawUnit(piece['x'] + x, piece['y'] + y, piece['color'])


def drawNextPiece(piece):
    # draw the text
    textSurf = BASIC_FONT.render('Next', True, TEXT_COLOR)
    textRect = textSurf.get_rect()
    textRect.center = (NEXT_PIECE_RECT_TOPLEFT[0] + TEMPLATE_WIDTH/2 * BOX_SIZE, \
                       NEXT_PIECE_RECT_TOPLEFT[1] - 18)
    DISPLAY_SURF.blit(textSurf, textRect)
    # draw the piece
    shapeToDraw = SHAPES[piece['shape']][piece['rotation']] 

    for x in range(TEMPLATE_WIDTH):
        for y in range(TEMPLATE_HEIGHT):
            if shapeToDraw[y][x] != BLANK:
                pixel_x, pixel_y = (NEXT_PIECE_RECT_TOPLEFT[0]+x*BOX_SIZE, \
                                    NEXT_PIECE_RECT_TOPLEFT[1]+y*BOX_SIZE)
                pygame.draw.rect(DISPLAY_SURF, COLORS[piece['color']], (pixel_x + 1, pixel_y + 1, \
                                                               BOX_SIZE - 1, BOX_SIZE - 1))
                pygame.draw.rect(DISPLAY_SURF, LIGHT_COLORS[piece['color']], \
                                 (pixel_x + 1, pixel_y + 1, BOX_SIZE - 4, BOX_SIZE - 4))
    # draw the border
    pygame.draw.rect(DISPLAY_SURF, BORDER_COLOR, (NEXT_PIECE_RECT_TOPLEFT[0], \
        NEXT_PIECE_RECT_TOPLEFT[1], TEMPLATE_WIDTH * BOX_SIZE, TEMPLATE_HEIGHT * BOX_SIZE), \
                     BORDER_WIDTH)

        
def drawBoard(board):
    # draw border & fill board
    pygame.draw.rect(DISPLAY_SURF, BORDER_COLOR, (X_MARGIN - 3, TOP_MARGIN - 7, \
                            BOARD_WIDTH*BOX_SIZE + 8, BOARD_HEIGHT*BOX_SIZE + 8), BORDER_WIDTH)
    pygame.draw.rect(DISPLAY_SURF, BG_COLOR, (X_MARGIN, TOP_MARGIN, BOX_SIZE * BOARD_WIDTH, \
                                              BOX_SIZE * BOARD_HEIGHT))
    
    # draw grid
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            drawUnit(x, y, board[x][y])

            
if __name__ == '__main__':
    main()
