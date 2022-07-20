# C:/Users/BADUNGS/AppData/Local/Programs/Python/Python37/argon
import pygame
from pygame.locals import *
from gameobjects.vector2 import Vector2
from sys import exit
from random import *
from logging import *
from itertools import combinations

basicConfig(
    level=WARNING,
    format='%(asctime)s - %(message)s'
)
disable(level=WARNING)

# Initialise
pygame.init()
pygame.mixer.init()
pygame.font.init()

# Constants
WIDTH = 480; HEIGHT = 600
SCREEN_SIZE = (WIDTH+1, HEIGHT+1)
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
pygame.display.set_caption('Connect Four')

GRID_SIDE = 80
TOP_SCREEN_SIZE = (WIDTH, 120)

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,0,100)
YELLOW = (250,255,0)
RED = (255,0,50)
WINNERFONT = pygame.font.SysFont('comicsans', 80)

COL_IND = {}

class Matrix(object):
    ''' This creates a matrix of a list where each row is a list of numbers'''
    def __init__(self, array):
        self.array = array
        try:
            for n in range(len(array)):
                if len(array[n]) != len(array[n+1]):
                    raise Exception('Inconsistent Dimensions: Item ' + str(n+1))
        except IndexError:
            pass
                    
        for n in self.array:
            for m in n:
                # print(type(m))
                is_correct_type = type(m)==int or type(m)==float
                if not is_correct_type:
                    raise Exception('Incorrect Type')
        
        self.r = len(self.array[0])
        self.c = len(self.array)
        self.size = (self.r, self.c)
        self.diags = self.diagonals()
        # self.diag = self.diags[1]

    def diagonals(self):
        '''Return list of all diagonals'''
        diags = []
        cols = list(range(self.c))
        rows = list(range(self.r))
        all_forms = [self.array, self.flipUD(self.array[:]), 
            self.flipLR(self.array[:]), self.flipLR(self.flipUD(self.array[:]))]
        # get diagonal of every transformation of self.array
        for form in all_forms:
            cols = list(range(self.c))
            rows = list(range(self.r))
            for c in range(self.c):
                try:
                    while len(rows)<=len(cols):
                        hold = []
                        for i,j in zip(rows, cols):
                            try:
                                hold.append(form[i][j])
                            except IndexError:
                                continue

                        diags.append(hold)
                        cols.remove(cols[0])
                    rows.remove(rows[-1])

                except IndexError:
                    continue
        return self.trimDiags(diags)

    def flipLR(self, array):
        ''' flip the matrix elements left to right '''
        for i in range(len(array)):
            array[i] = list(array[i].__reversed__())
        return array

    def flipUD(self, array):
        ''' flip the matrix upside down '''
        array = list(array.__reversed__())
        return array

    def transpose(self, array=None):
        ''' return the transpose of the matrix '''
        if not array:
            array = self.array
        transpose = []
        for c in range(self.c):
            hold = []
            for r in range(self.r):
                hold.append(array[r][c])
            transpose.append(hold)
        return transpose

    def trimDiags(self, array):
        ''' sort arrays and remove empty arrays and repeated arrays '''
        sorted_array = [sorted(arr) for arr in array]
        # Remove empty lists
        for n in sorted_array[:]:
            if not n:
                sorted_array.remove(n)
        # Remove list repititions
        for n in sorted_array[:]:
            while sorted_array.count(n)>1 or not (sorted_array.count(n)):
                sorted_array.remove(n)
        return sorted(sorted_array)

    def disp(self, array=None):
        if not array:
            for n in self.array:
                print(n)
        else:
            for n in array:
                print(n)


class Player(object):

    def __init__(self):
        self.moves = []

    def getQuads(self):
        # return all possible groups of fours from moves made
        quads = list(combinations(self.moves, 4))
        return quads

    def clearMoves(self):
        self.moves = []
        

GRID = Matrix([list(range(1,7)), list(range(7,13)), 
            list(range(13,19)), list(range(19,25)), 
            list(range(25,31)), list(range(31,37))])

ROWS = [5,5,5,5,5,5]

def getPos(col_ind):
    # This function returns the pos in the grid, given the col_ind
    global ROWS
    # GRID.disp()
    try:
        if ROWS[col_ind-1] >= 0:
            r = ROWS[col_ind-1]; c = col_ind-1
            info('r, c: ' + str(r) + " " + str(c))
            pos = GRID.array[r][c]
            # pos = GRID.array[ROWS[6-col_ind]][col_ind-1]
            ROWS[col_ind-1] -= 1
            return pos

        else: 
            debug('END OF COLUMN REACHED')
            return None

    except IndexError:
        pass

def createColourIndex():
    # create a global dictionary where keys are positions and values
    # are colours
    global COL_IND
    i = 1
    for n in range(0,WIDTH,GRID_SIDE):
        for m in range(0,WIDTH,GRID_SIDE):
            COL_IND[i] = WHITE
            i += 1

def checkForWinner(gamer1, gamer2):
    diags = GRID.diags
    valid_diags = [diag for diag in diags if len(diag) > 3]
    diag_quads = inQuads(valid_diags)
    row_quads = inQuads(GRID.array)
    col_quads = inQuads(GRID.transpose())
    wins = inQuads(diag_quads) + row_quads + col_quads
    q1 = gamer1.getQuads(); q2 = gamer2.getQuads()
    for quad in q1:
        if sorted(list(quad)) in wins:
            pygame.event.set_blocked(MOUSEBUTTONDOWN)
            return 'Gamer 1'
    for quad in q2:
        if sorted(list(quad)) in wins:
            pygame.event.set_blocked(MOUSEBUTTONDOWN)
            return 'Gamer 2'
    return

def declareWinner(winner=None):
    # draw rect background
    top_rect = pygame.Rect(0, 0, *TOP_SCREEN_SIZE)
    pygame.draw.rect(screen, BLACK, top_rect)

    if winner:
        # blit text
        winner = WINNERFONT.render(winner.upper() + ' WINS', 1, YELLOW)
        screen.blit(winner, (20,20))

    pygame.display.update()
    pygame.time.delay(1500)

def inQuads(array):
    # return array in groups of fours
    hold = []
    for arr in array:
        n = len(arr)-4
        ind = 0
        try:
            while ind<=n: 
                hold.append(arr[ind:ind+4])
                ind+=1
        except IndexError:
            continue

    return hold

def drawGridCircles():    
    # draw circles
    # col_pos = {}
    ind = 1
    for n in range(0,WIDTH,GRID_SIDE):
        for m in range(0,WIDTH,GRID_SIDE):
            # screen_surface, colour, position, radius, thickness
            pos = (40+m, 40+n+TOP_SCREEN_SIZE[1])
            # col_pos[pos] = []
            pygame.draw.circle(screen, COL_IND[ind], pos, 39, 0)
            ind += 1

def drawTopCircle(mouse_pos, col):
    # draw rect background
    top_rect = pygame.Rect(0, 0, *TOP_SCREEN_SIZE)
    pygame.draw.rect(screen, BLACK, top_rect)
    # draw circle
    pos = (40,60)
    for n in range(0,WIDTH,GRID_SIDE):
        if n <= mouse_pos.x <= n+GRID_SIDE:
            pos = (n+GRID_SIDE/2, 60)
            # debug('Getting pos: ' + str(pos))
    pygame.draw.circle(screen, col, pos, 39, 0)
    pygame.display.update()
    return pos

def drawWindow():
    screen.fill(BLUE)
    drawGridCircles()

def main():
    global ROWS

    ROWS = [5,5,5,5,5,5]
    turn = 1
    colours = [None, RED, YELLOW]
    gamer1 = Player(); gamer2 = Player()
    players = [None, gamer1, gamer2]
    winner = None
    pos = drawTopCircle(Vector2(40,60), colours[turn])
    createColourIndex()

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == QUIT:
                # running = False
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONDOWN:
                col = colours[turn]
                pos = drawTopCircle(Vector2(pygame.mouse.get_pos()), col)
                debug('Gotten pos: ' + str(pos))
                col_ind = int((pos[0]+40)/80)

                pos = getPos(col_ind)
                if pos:
                    gamer = players[turn]
                    gamer.moves.append(pos)
                
                COL_IND[pos] = colours[turn]

                if ROWS[col_ind-1] <= -1 and not pos:   #This fixes the problem of colour not changing 
                    pass                                # when you click a filled column
                else: turn *= -1        

                winner = checkForWinner(gamer1, gamer2)
                warning(ROWS)

        drawWindow()
        col = colours[turn]
        pos = drawTopCircle(Vector2(pygame.mouse.get_pos()), col)

        # if grid is full
        if ROWS == [-1,-1,-1,-1,-1,-1]:
                declareWinner()
                winner = None
                createColourIndex()
                gamer1.clearMoves()
                gamer2.clearMoves()
                ROWS = [5,5,5,5,5,5]

        # check for winner
        if winner: 
            info('Winner is ' + winner)
            declareWinner(winner)
            pygame.event.set_allowed(MOUSEBUTTONDOWN)

            main()

if __name__ == "__main__":
    main()

