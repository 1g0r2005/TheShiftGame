import pygame
import random
N = 50
WIDTH,HEIGHT = 600,600
FPS = 60

alive = [0,1,2,3]
dead = [5,6,7,8]

cellsize = WIDTH//N,HEIGHT//N
print(cellsize)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def init_gen(N,min_shift,max_shift,min_size,max_size):
    '''
    generate start cell states
    N - size of matrix(N*N)
    min_shift - minimal shift for of enter
    max_shift - maximal shift for of enter
    min_size - minimal size of x_enter
    max_size - maximal size of y_enter
    '''
    cells = [[random.choice([0,1]) for j in range(N)] for i in range(N)]

    entupx1 = random.randrange(min_shift,N-max_shift)
    entupx2 = random.randrange(entupx1+min_size,entupx1+max_size)
    entdnx1 = random.randrange(min_shift,N-max_shift)
    entdnx2 = random.randrange(entupx1+min_size,entupx1+max_size)
    entlfy1 = random.randrange(min_shift,N-max_shift)
    entlfy2 = random.randrange(entupx1+min_size,entupx1+max_size)
    entrty1 = random.randrange(min_shift,N-max_shift)
    entrty2 = random.randrange(entupx1+min_size,entupx1+max_size)
    for x in range(N):
        for y in range(N):
            if y < 2:
                if x>=entupx1 and x<=entupx2:
                    cells[x][y]=0
                else:
                    cells[x][y]=1
            if y > N-3:
                if x>=entdnx1 and x<=entdnx2:
                    cells[x][y]=0
                else:
                    cells[x][y]=1
            if x < 2:
                if y>=entlfy1 and y<=entlfy2:
                    cells[x][y]=0
                else:
                    cells[x][y]=1
            if x > N-3:
                if y>=entrty1 and y<=entrty2:
                    cells[x][y]=0
                else:
                    cells[x][y]=1
    return cells
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
def post_gen(cell_matrix,color_matrix):
    '''
    fix generation artefacts
    cell_matrix - bitmap of cells states
    color_matrix - map of cells colors
    '''
    for x in range(N):
        for y in range(N):
            if x==0:
                if cell_matrix[x+1][y]==1:
                    cell_matrix[x][y]=1
                    if color_matrix[x+1][y]==8:
                        color_matrix[x][y] = 8
                    else:
                        color_matrix[x][y] = color_matrix[x+1][y]+1
            if y==0:
                if cell_matrix[x][y+1]==1:
                    cell_matrix[x][y]=1
                    if color_matrix[x][y+1]==8:
                        color_matrix[x][y] = 8
                    else:
                        color_matrix[x][y] = color_matrix[x][y+1]+1
            if x==N-1:
                if cell_matrix[x-1][y]==1:
                    cell_matrix[x][y]=1
                    if color_matrix[x-2][y]<7:
                        color_matrix[x-1][y] =  color_matrix[x-2][y]+1
                        if color_matrix[x-2][y]<8:
                            color_matrix[x][y] = color_matrix[x-1][y]+1
                        else:
                            color_matrix[x][y] = 8
                    else:
                        color_matrix[x-1][y] =  8
                        color_matrix[x][y] = 8
            if y==N-1:
                if cell_matrix[x][y-1]==1:
                    cell_matrix[x][y]=1
                    if color_matrix[x][y-1]==8:
                        color_matrix[x][y] = 8
                    else:
                        color_matrix[x][y] = color_matrix[x][y-1]+1


def draw_cell(screen,matrix,color_matrix=screen,light=[[1]*N for i in range(N)]):
    '''
    draw new state of cells by matrix
    screen - pygame screen object
    matrix - bitmap of cells states
    color - map of cells colors
    light - light for whole map
    '''
    for x in range(N):
        for y in range(N):
            if matrix[x][y] == 1:
                color = list(map(lambda single_color: single_color*(1-color_matrix[x][y]/10)*light[x][y],[255,191,128]))#255*(1-color_matrix[x][y]/8)
            else:
                color = list(map(lambda single_color: single_color*light[x][y],(255,217,179)))
            color = color
            pygame.draw.rect(screen,color,[x*cellsize[0],y*cellsize[1],(x+1)*cellsize[0],(y+1)*cellsize[1]])     

def draw_player(screen,x,y):
    '''
    draw position of player
    screen - pygame screen object
    x,y - coords of player cell
    '''
    PLAYER_COLOR = (255,0,0)
   
    pygame.draw.rect(screen,PLAYER_COLOR,[x*cellsize[0],y*cellsize[1],cellsize[0],cellsize[1]])

def move_player(x0,y0,dir,cellmap):
    '''
    return new position of player
    use keyboard events
    x0,y0 - coords of player
    dir - direction of movement
    [left = [-1,0]]
    [right = [1,0]]
    [up = [0,-1]]
    [down = [0,1]]
    cellmap - bitmap of cells states (1=wall,0=air)
    '''
    x1,y1 = x0,y0
    if dir[0]==1: #down
        if y0!=N-1:
            if cellmap[x0][y0+1]==0:
                y1+=1
    elif dir[0]==-1: #up
        if y0!=0:
            if cellmap[x0][y0-1]==0:
                y1-=1
    if dir[1]==1: #right
        if x0!=N-1:
            if cellmap[x0+1][y0]==0:
                x1+=1
    elif dir[1]==-1: #left
        if x0!=0:
            if cellmap[x0-1][y0]==0:
                x1-=1
    return x1,y1

def dot_light(light,x,y,I,r):#demo
    '''
    create new spot from dot light
    light - light for whole map
    x, y - coords of new dot light
    I - intens of new dot light (0-1)
    r - max distance where dot light affect cells
    '''
    for x0 in range(max(0,x-r),min(x+r,N)):
        for y0 in range(max(0,y-r),min(y+r,N)):
            d = (x0-x)**2+(y0-y)**2
            attenuation = max(0.05,1-(d/r))
            light[x0][y0] = I*attenuation

'''map generation'''
cells = init_gen(N,5,10,0,8)
maxtick = 4
for i in range(maxtick):
    generate(cells,neibourhood(cells),alive,dead)
color_cells = neibourhood(cells)
post_gen(cells,color_cells)
'''initial player pos [temp]'''
flag = True
while flag:
    x,y = random.randint(0,N-1),random.randint(0,N-1)
    if cells[x][y]==0:
        flag = False
        print(x,y)
        
running = True
motion = [0,0]
light_matrix = [[0.05]*N for i in range(N)]
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: #left
                motion = [0,-1]
            elif event.key == pygame.K_RIGHT: #right
                motion = [0,1]
            elif event.key == pygame.K_UP: #up
                motion = [-1,0]
            elif event.key == pygame.K_DOWN: #down
                motion = [1,0]
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT,
                         pygame.K_RIGHT,pygame.K_UP,pygame.K_DOWN]:
                motion = [0,0]
    x,y = move_player(x,y,motion,cells)
    dot_light(light_matrix,x,y,1,20)
    draw_cell(screen,cells,color_matrix=color_cells,light=light_matrix)
    
    draw_player(screen,x,y)

    
    pygame.display.flip()
