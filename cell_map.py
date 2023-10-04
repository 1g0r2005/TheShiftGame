import pygame
import random
from copy import copy
N = 50
WIDTH,HEIGHT = 600,600
FPS = 60

alive = [0,1,2,3]
dead = [5,6,7,8]

cells = [[random.choice([0,1]) for j in range(N)] for i in range(N)]

cellsize = WIDTH//N,HEIGHT//N
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def draw_cell(screen,matrix,color_matrix=screen):
    '''
    draw new state of cells by matrix
    screen - pygame screen object
    matrix - bitmap of cells states
    color - map of cells colors
    '''
    for x in range(N):
        for y in range(N):
            if matrix[x][y] == 1:
                single_color = 255*(1-color_matrix[x][y]/8)
                color = (single_color,single_color,single_color)
            else:
                color = (255*(7/8),255*(7/8),255*(7/8))
            pygame.draw.rect(screen,color,[x*cellsize[0],y*cellsize[1],(x+1)*cellsize[0],(y+1)*cellsize[1]])
def neibourhood(matrix):
    '''
    return matrix with count of alive neibours of cell
    matrix - bitmap of cells states
    '''
    nb_matrix = [[0]*N for i in range(N)]
    for x in range(N):
        for y in range(N):
            start_x, start_y = x-1,y-1
            end_x, end_y = x+1,y+1
            if x == 0:
                start_x = 0
            elif x == N-1:
                end_x = 0
            if y == 0:
                start_y = y
            elif y == N-1:
                end_y = y
            #print('####',x,y,'###',start_x,start_y,end_x,end_y)
            nb = sum([matrix[xcell][ycell] for xcell in range(start_x,end_x+1) for ycell in range(start_y,end_y+1)])
            if nb!=0 and matrix[x][y]==1:
                nb-=1
            nb_matrix[x][y] = nb  
    return nb_matrix
def generate(cell_matrix,nb_matrix,alive,dead):
    '''
    generate next state of cell matrix with rules connected with cell and her neibourhood
    cell_matrix - bitmap of cells states
    nb_matrix - matrix of cells neibours
    alive - when cell continue live (count of alive neibours)
    dead - when cell become alive (count of alive neibours)
    '''
    for x in range(N):
        for y in range(N):
            state = cell_matrix[x][y]
            neibour = nb_matrix[x][y]
            if state == 0: # dead cell
                if neibour in dead: #0 to 1 (air to wall)
                    cell_matrix[x][y] = 1
            else:
                if neibour in alive: #1 to 0 (wall to air)
                    cell_matrix[x][y] = 0
                    
def generate_post(cell_matrix):
    for x in range(N):
        for y in range(N):
            if (x<1 or y<1)or((x>N-2) or (y>N-2)):
                cell_matrix[x][y]=1
                color_cells[x][y]=1
                


running = True

##gen map
maxtick = 4
for i in range(maxtick):
    generate(cells,neibourhood(cells),alive,dead)
    
color_cells = neibourhood(cells)

generate_post(cells)

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    draw_cell(screen,cells,color_matrix=color_cells)
    pygame.display.flip()
