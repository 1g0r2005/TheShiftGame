import glob
from tokenize import group
from pprint import pprint
import pygame
import random
import threading
import configparser
import yaml

PLAYER_COLOR = (255,0,0)
WALL_COLOR =(255,191,128)
FL_COLOR = (255,217,179)
BLACK = (0,0,0)
WHITE = (255,255,255)

with open("config.yaml", 'r') as f:
    config_temp = yaml.safe_load(f)
    version = config_temp['version']
    log_lev = config_temp['logger']['level']
    screenWidth,screenHeight = config_temp['screendef'].values()
    fps = config_temp['fpslock']

config = configparser.ConfigParser()
config.read("cellrules.ini")
ruleForAlive,ruleForDead = [int(el) for el in list(config['cells']['rule_alive'])], [int(el) for el in list(config['cells']['rule_dead'])]
cellsInLine = int(config['cells']['cellinline'])

cellSize = screenWidth//cellsInLine,screenHeight//cellsInLine

pygame.init()

currentUsedItems = []
cellsList = []
cellsColors = []

clock = pygame.time.Clock()

class Screen(pygame.Surface):
    '''
    Screen class - additional layers based on pygame.Surface
    
    __init__(self,screenWidth,screenHeight)
        screenWidth,screenHeight - size of app screen
    '''
    def __init__(self,screenWidth,screenHeight):
        super().__init__((screenWidth,screenHeight))

class Entity(pygame.Surface):
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
    SPEED = 1 #cells per tick
    
    def __init__(self,x,y,color=WHITE):
        super().__init__((cellSize[0],cellSize[1]))
        
        self.x,self.y = x,y
        self.color = color
        self.fill(color)
        
    def draw(self,surf):
        surf.blit(self,[self.x*cellSize[0],self.y*cellSize[1]])

    def move(self,dir,cellmap):
        x0,y0 = self.x,self.y
        dx,dy = self.SPEED,self.SPEED
        if dir[0]==1: #down
            if y0!=cellsInLine-1:
                if cellmap[x0][y0+dy]==0:
                    self.y+=1
        elif dir[0]==-1: #up
            if y0!=0:
                if cellmap[x0][y0-dy]==0:
                    self.y-=1
        if dir[1]==1: #right
            if x0!=cellsInLine-1:
                if cellmap[x0+dx][y0]==0:
                    self.x+=1
        elif dir[1]==-1: #left
            if x0!=0:
                if cellmap[x0-dx][y0]==0:
                    self.x-=1

class Player(Entity):
    '''
    Player subclass - entity controlled by person

    __init__(self,x,y,color=WHITE,inventory_set={'StatLight':3})
        x,y - initial pos
        color - color of rect(now all ent are rects)
        inventory_set - dictionary with player's items
    '''
    HP = 100
    inventory = {}
    def __init__(self,x,y,color=WHITE,inventory_set={"DotLight":3}):
        super().__init__(x,y,color)
        self.inventory=inventory_set
  
    def use(self,unit):
        if self.inventory[unit]>0:
           match unit:
               case 'DotLight':
                   currentUsedItems.append(DotLight(self.x,self.y,1,20,temp=True))
                   self.inventory["DotLight"]-=1
               case _:
                   pass
        else:
            print(f"Don't have any {unit}")

class DotLight():
    '''
    DotLight class - small circle of light (for ex. around player)
    
    def __init__(self,x,y,I,r,temp):
        I - intensivity (0,1)
        x,y - position of dot
        r - maximum radius of light
        temp - flag for fading light
        lifetime - time when temp light works in ticks (1/60 sec)
    def use(self):
        draw spot of light on light layer (screenLight) by x,y,I,r
    
    def move(self,new_x,new_y)
        change coord of spot
        new_x,new_y - updated coords
    '''
    def __init__(self,x,y,I,r,temp=False,lifetime=random.randint(300,400)):
        self.I = I
        self.x = x
        self.y = y
        self.r = r
        self.temp = temp
        self.lifetime = lifetime
    def use(self):
        if self.temp:
            self.lifetime-=1
        for x0 in range(max(0,self.x-self.r),min(self.x+self.r,cellsInLine)):
            for y0 in range(max(0,self.y-self.r),min(self.y+self.r,cellsInLine)):
                d = (x0-self.x)**2+(y0-self.y)**2
                attenuation = max(0,1-(d/self.r))
                alpha = self.I*attenuation*60
                oldColor = screenLight.get_at((x0*cellSize[0],y0*cellSize[1]))[0]
                checkWallBetw = sum(cellsList[x][y] for x in range(min(x0,self.x),max(x0,self.x)+1) for y in range(min(y0,self.y),max(y0,self.y)+1))
                if cellsList[x0][y0]==0 and checkWallBetw==0:
                        newColorAll = max(oldColor,alpha)
                        if not self.temp:
                            newColorR = newColorAll*random.randint(80,100)/100
                            newColorG = newColorAll*random.randint(80,100)/100
                            newColorB = newColorAll*random.randint(50,60)/100
                        else:
                            newColorR,newColorG,newColorB = newColorAll,newColorAll,newColorAll
                        pygame.draw.rect(screenLight,[newColorR,newColorG,newColorB],[x0*cellSize[0],y0*cellSize[1],cellSize[0],cellSize[1]])
                
    def move(self,new_x,new_y):
        self.x = new_x
        self.y = new_y
        
screenMain = pygame.display.set_mode((screenWidth, screenHeight)) # main screen (static, in_cycle)
screenBack = Screen(screenWidth,screenHeight) # surface for background (static, out_cycle)
screenEntity = Screen(screenWidth,screenHeight) # surface for entities (animated)
screenLight = Screen(screenWidth,screenHeight) # surface for light
screenEntity.set_colorkey(BLACK)
screenLight.set_alpha(240)

def initial_generation(N,min_shift,max_shift,min_size,max_size):
    '''
    gen_main start cell states
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

def check_neighbors(matrix):
    '''
    return matrix with count of alive neibours of cell
    matrix - bitmap of cells states
    '''
    nb_matrix = [[0]*cellsInLine for i in range(cellsInLine)]
    for x in range(cellsInLine):
        for y in range(cellsInLine):
            start_x, start_y = x-1,y-1
            end_x, end_y = x+1,y+1
            if x == 0:
                start_x = 0
            elif x == cellsInLine-1:
                end_x = 0
            if y == 0:
                start_y = y
            elif y == cellsInLine-1:
                end_y = y
            nb = sum([matrix[xcell][ycell] for xcell in range(start_x,end_x+1) for ycell in range(start_y,end_y+1)])
            if nb!=0 and matrix[x][y]==1:
                nb-=1
            nb_matrix[x][y] = nb  
    return nb_matrix

def main_generation(cell_matrix,nb_matrix,alive,dead):
    '''
    gen_main next state of cell matrix with rules connected with cell and her check_nb
    cell_matrix - bitmap of cells states
    nb_matrix - matrix of cells neibours
    alive - when cell continue live (count of alive neibours)
    dead - when cell become alive (count of alive neibours)
    '''
    for x in range(cellsInLine):
        for y in range(cellsInLine):
            state = cell_matrix[x][y]
            neibour = nb_matrix[x][y]
            if state == 0: # dead cell
                if neibour in dead: #0 to 1 (air to wall)
                    cell_matrix[x][y] = 1
            else:
                if neibour in alive: #1 to 0 (wall to air)
                    cell_matrix[x][y] = 0        
                
def post_generation(cell_matrix,color_matrix):
    '''
    fix generation artefacts
    cell_matrix - bitmap of cells states
    color_matrix - map of cells colors
    '''
    for x in range(cellsInLine):
        for y in range(cellsInLine):
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
            if x==cellsInLine-1:
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
            if y==cellsInLine-1:
                if cell_matrix[x][y-1]==1:
                    cell_matrix[x][y]=1
                    if color_matrix[x][y-1]==8:
                        color_matrix[x][y] = 8
                    else:
                        color_matrix[x][y] = color_matrix[x][y-1]+1
                        
def cell_drawing(screen,matrix,color_matrix=screenMain):
    '''
    draw new state of cells by matrix
    screen - pygame screen object
    matrix - bitmap of cells states
    color - map of cells colors
    light - light for whole map
    '''
    for x in range(cellsInLine):
        for y in range(cellsInLine):
            if matrix[x][y] == 1:
                color = list(map(lambda single_color: single_color*(1-color_matrix[x][y]/10),WALL_COLOR))#255*(1-color_matrix[x][y]/8)
            else:
                color = list(map(lambda single_color: single_color,FL_COLOR))
            pygame.draw.rect(screen,color,[x*cellSize[0],y*cellSize[1],(x+1)*cellSize[0],(y+1)*cellSize[1]])     
            
def terrain_thread_func():
    global cellsList,cellsColors
    '''map generation'''
    cellsList = initial_generation(cellsInLine,5,10,0,8)
    maxtick = 4
    for i in range(maxtick):
        main_generation(cellsList,check_neighbors(cellsList),ruleForAlive,ruleForDead)
    cellsColors = check_neighbors(cellsList)
    post_generation(cellsList,cellsColors)
    
def screen_thread_func():
    global currentUsedItems
    
    player = Player(player_x,player_y,color=PLAYER_COLOR)
    player_light = DotLight(player_x,player_y,1,10)
    

    fixed_light = []
    running = True
    motion = [0,0]

    '''init screen'''
    cell_drawing(screenBack,cellsList,color_matrix=cellsColors)
    screenMain.blit(screenBack,(0,0))
    screenMain.blit(screenLight,(0,0))
    f_light = 1 #flag for player light
    f_update_items = False #flag for updating persons items
    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a: #left
                    motion[1] = -1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d: #right
                    motion[1] = 1
                elif event.key == pygame.K_UP or event.key == pygame.K_w: #up
                    motion[0] = -1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s: #down
                    motion[0] = 1
                elif event.key == pygame.K_f: #flashlight
                    f_light *= -1
               
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a: motion[1] = 0
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d: motion[1] = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_w: motion[0] = 0
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s: motion[0] = 0
                elif event.key == pygame.K_t: #place light
                    player.use(unit='DotLight')
                    f_update_items=True
                    
        
        player.move(motion,cellsList)
        player_light.x = player.x
        player_light.y = player.y
        if f_light==1:
            player_light.use()
        else:
            pass
        for item in currentUsedItems:
             
             try:
                 if item.lifetime==0:
                     del item
                 item.use()
             except:
                 pass
        
        screenMain.blit(screenBack,(0,0))
        player.draw(screenMain)
        screenMain.blit(screenLight,(0,0))
        screenLight.fill(BLACK)
        pygame.display.update()
        
terrain_thread_func()
'''initial player pos'''
flag = True
while flag:
    player_x,player_y = random.randint(0,cellsInLine-1),random.randint(0,cellsInLine-1)
    if cellsList[player_x][player_y]==0:
        flag = False

screen_thread_func()
