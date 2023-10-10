import pygame
import random
N = 50
WIDTH,HEIGHT = 600,600
FPS = 60

alive = [0,1,2,3]
dead = [5,6,7,8]

cellsize = WIDTH//N,HEIGHT//N
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

PLAYER_COLOR = (255,0,0)

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


class Entity():
    '''
    Entity class - moving objects

    __init__(self,x,y,color=(255,255,255))
        x,y - initial pos
        color - color of rect(now all ent are rects)
    draw(self,surf)
        surf - pygame surface object
    move(self,dx,dy)
        dx,dy - change coords of object
    '''
    speed = 1 #cells per tick

    def __init__(self,x,y,color=(255,255,255)):
        self.x,self.y = x,y
        self.color = color
    def draw(self,surf):
        #now all ent are sq
        pygame.draw.rect(surf,self.color,[self.x*cellsize[0],self.y*cellsize[1],cellsize[0],cellsize[1]])

    def move(self,dir,cellmap):
        x0,y0 = self.x,self.y
        dx,dy = self.speed,self.speed
        if dir[0]==1: #down
            if y0!=N-1:
                if cellmap[x0][y0+dy]==0:
                    self.y+=1
        elif dir[0]==-1: #up
            if y0!=0:
                if cellmap[x0][y0-dy]==0:
                    self.y-=1
        if dir[1]==1: #right
            if x0!=N-1:
                if cellmap[x0+dx][y0]==0:
                    self.x+=1
        elif dir[1]==-1: #left
            if x0!=0:
                if cellmap[x0-dx][y0]==0:
                    self.x-=1
        
class Player(Entity):  #заготовка
    HP = 100 #percent

    def __init__(self,x,y,color=(255,255,255)):
        super().__init__(x,y,color)

class Dot_Light(): #переписать!
    def __init__(self,x,y,I,r):
        self.I = I
        self.x = x
        self.y = y
        self.r = r
    def light(self,light_map):
        for x0 in range(max(0,self.x-self.r),min(self.x+self.r,N)):
            for y0 in range(max(0,self.y-self.r),min(self.y+self.r,N)):
                d = (x0-self.x)**2+(y0-self.y)**2
                attenuation = max(0.05,1-(d/self.r))
                light_map[x0][y0] = self.I*attenuation
    def move(self,new_x,new_y):
        self.x = new_x
        self.y = new_y

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
    player_x,player_y = random.randint(0,N-1),random.randint(0,N-1)
    if cells[player_x][player_y]==0:
        flag = False

player = Player(player_x,player_y,color=PLAYER_COLOR)
player_light = Dot_Light(player_x,player_y,1,20)
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
                motion[1] = -1
            elif event.key == pygame.K_RIGHT: #right
                motion[1] = 1
            elif event.key == pygame.K_UP: #up
                motion[0] = -1
            elif event.key == pygame.K_DOWN: #down
                motion[0] = 1
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT: motion[1] = 0
            elif event.key == pygame.K_RIGHT: motion[1] = 0
            elif event.key == pygame.K_UP: motion[0] = 0
            elif event.key == pygame.K_DOWN: motion[0] = 0

    draw_cell(screen,cells,color_matrix=color_cells,light=light_matrix)

    player_light.x = player.x
    player_light.y = player.y
    player.move(motion,cells)
    player_light.light(light_matrix)
    player.draw(screen)
    

    pygame.display.flip()