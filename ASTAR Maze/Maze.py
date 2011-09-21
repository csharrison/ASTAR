import pygame
import sys
import eztext
from pygame.locals import *

from astar import create_path
from math import acos,atan,sin,cos
from saveload import write_to_file,load_from_file
from smoothit import walkable, make_smooth
"""
TODO:
We have two choices for our guy's movement
when a guys rounded real (pixel) location is a nodes location:
    1.  make the real location = the nodes location
        this causes jerkyness and makes the guy travel faster on adjacent nodes
        they jerk him along the path, not allowing him to fully travel there
        
    2. only calculate position based on the pixel location
        this method gives smooth paths, but causes clipping

2 is used now, but a balance between the two would be nice


add enemies, a game or something
make some tiles worth differently (e.g. roads and mountains)
implement time splicing to let the algorith run for >1 frames

optimize A* search, maybe without the node class and just with a fixed matrix

add more complexity to the path function: 
    different sprite (car or something)
    turning with fixed angles
    Directional A*
    impoved smoothing pass
    Directional 24 or 48 search?
"""
class Guy(object):
    def __init__(self, loc, image, speed, dim):
        self.rloc = (loc[0]*10, loc[1]*10)#'real' location
        self.loc, self.speed, self.path = loc, speed, []
        self.image = pygame.image.load(image)
        self.known_walkability = creategrid(dim)
        self.goal = ()
        self.theta = self.changex = self.changey = 0
        self.all_knowing = True
        
    def calculate_direction(self):
        "calculates the direction the guy needs to go to reach the next node"
        if self.rloc[0] - self.path[0][0]*10 == 0:#completely vertical path
            self.changex = 0#no x change (vertical movement)
            self.theta = acos(0)# used to calculate y change

            #if the guy is below the path, you need to multiply it by -1 (I don't know why)
            if self.rloc[1]<self.path[0][1]*10:
                self.changey = sin(self.theta)*self.speed*.1
            else:
                self.changey = sin(self.theta)*self.speed*.1 *-1

        else:
            #calculate the changex and changey by finding the atan of the change of x and y
            self.theta = atan((self.rloc[1]-self.path[0][1]*10.)/(self.rloc[0]-self.path[0][0]*10.))
            self.changex = cos(self.theta) *self.speed*.1
            self.changey = sin(self.theta) *self.speed*.1

        #strange, I don't know why this is needed either, but it is, stupid polar coordinate system
        if self.rloc[0]-self.path[0][0]*10.>0:self.changex*=-1; self.changey*=-1
        
    def set_path(self, screen, grid, end, timelimit = .5):
        "sets a path for the guy to follow"
        self.goal = end # reset the goal
        
        #create a path using A* and smooth it up with the smoothing function
        if self.all_knowing == True:
            self.path = make_smooth(screen, self.loc,create_path(self.loc,end,grid,timelimit),grid)
        else:
            self.path = make_smooth(screen, self.loc,create_path(self.loc,end,self.known_walkability,timelimit),grid)

        #sometimes the path will be empty
        if len(self.path)>0:
            self.calculate_direction()#calculate the initial direction
        
    def traverse_path(self):
        #update the 'real' location and the rounded grid location
        self.rloc = (self.rloc[0]+self.changex, self.rloc[1] + self.changey)
        self.loc = (int(round((self.rloc[0]/10.))), int(round(self.rloc[1]/10.)))

        #if the grid location matches with our target...
        if self.loc == self.path[0]:
            #reset the 'real' location to the grid location
            #uncomment this out in order to get no clipping, but jerkier paths
            #speeding up the guys speed helps sorta mask it
            #self.rloc = (self.loc[0]*10.,self.loc[1]*10.)
            
            self.path.pop(0)#delete that node from our path

            #if we still have a path, recalculate our new direction
            if len(self.path)>0: self.calculate_direction()

    def draw_guy(self, screen):
        #blit the dude on the screen, based on his 'real' coordinates
        screen.blit(self.image, (self.rloc[0], self.rloc[1]))
        
def creategrid(dim):
    "creates a walled in grid"
    x,y = dim[0]/10-2, dim[1]/10-2
    grid = []
    for gx in xrange(x+2):
        row = []
        for gy in xrange(y+2):
            if gx == 0 or gy == 0 or gx == x+1 or gy == y+1:
                row.append(False)
            else: row.append(True)
        grid.append(row)
    return grid

def update(screen, grid, guy, r):
    "Updates around the guy, depending on his sight range"   
    for x in xrange(guy.loc[0]-r,guy.loc[0]+r+1):
        for y in xrange(guy.loc[1]-r, guy.loc[1]+r+1):
            if x>=0 and y>=0 and x<len(grid) and y<len(grid[0]):
                
                if grid[x][y] == False:
                    pygame.draw.rect(screen,(150,100,50),(x*10,y*10,10,10))

                elif grid[x][y] == True:
                    pygame.draw.rect(screen,(100,255,100),(x*10,y*10,10,10))

                guy.known_walkability[x][y] = grid[x][y]
                    
    guy.draw_guy(screen)
    #update all of the squares that the guy is 'seeing'
    pygame.display.update((guy.loc[0]-r)*10,(guy.loc[1]-r)*10,
                          (1+2*r)*10,(1+2*r)*10)

def draw_all(screen, grid, guy):
    "Draws the entire screen"
    for x in xrange(len(grid)):
        for y in xrange(len(grid[x])):
            if grid[x][y] == True:
                pygame.draw.rect(screen, (100,255,100), (x*10, y * 10, 10, 10))
            elif grid[x][y] == False:
                pygame.draw.rect(screen, (150,100,50) , (x*10, y * 10, 10, 10))
    guy.draw_guy(screen)
    pygame.display.flip()

def change(screen, grid, deleting, mx, my):
    "either draws or erases a wall"
    grid[mx][my] = deleting
    if deleting: pygame.draw.rect(screen,(100,255,100),(mx*10, my*10,10,10))
    else       : pygame.draw.rect(screen,(150,100,50) ,(mx*10, my*10,10,10))
    pygame.display.update(mx*10, my * 10, 10, 10)
    return grid

def main(dim):

    import psyco
    psyco.full()
    
    #initialize pygame, the display caption, and the screen
    pygame.init(); pygame.display.set_caption("A* Maze")
    grid = creategrid(dim)
    #reset the screen to the dimensions in the new map
    screen = pygame.display.set_mode((dim[0], dim[1]))

    guy = Guy((10,15),"smiley x 10.bmp",.8, dim)
    r = 2#the guys sight range

    '''
    guy.all_knowing : this guy knows everything
    True -> guy and user can see everything, deleting/adding walls allowed
    False -> guy has a sight radius and updates his knowledge of the map (deleting/adding walls not allowed)
    pressing m will switch modes
    '''
    drawing = deleting = False
    draw_all(screen,grid,guy)


    save = eztext.Input(maxlength=60, color=(255,0,0), prompt='Input save path: ')
    load = eztext.Input(maxlength=60, color=(255,0,0), prompt='Input load path: ')
    loading = saving = False

    while True:#main game loop
        events = pygame.event.get()#get the inputs
        if saving == True:
            #fill the screen black where we type
            screen.fill((0,0,0),(0,0,1000,25))
            save.update(events)#update the text
            save.draw(screen)#draw the text
            pygame.display.update((0,0,1000,25))#update the screen

        elif loading == True:
            screen.fill((0,0,0),(0,0,1000,25))
            load.update(events)
            load.draw(screen)
            pygame.display.update((0,0,1000,25))

        for e in events: #processes key/mouse inputs
            mousex = (pygame.mouse.get_pos()[0])/10
            mousey = (pygame.mouse.get_pos()[1])/10

            #right click will draw a wall,
            #left click will move the guy to your mouse cursor
            if e.type == MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[2] == 1:
                    #can only draw if the guy knows about it, or it will mess with his head
                    if guy.all_knowing == True: 
						if grid[mousex][mousey] == True:
							drawing = True
						else: deleting = True
                    
                elif grid[mousex][mousey]!= False and (mousex,mousey)!=guy.loc:
                    guy.set_path(screen, grid,(mousex,mousey))
            elif e.type == MOUSEBUTTONUP:drawing = deleting = False


            #ESC:quit; hold d: delete walls; s : save map;  l : load map
            #q deletes the entire map; m: change guy settings
            elif e.type == KEYDOWN:
                
                if e.key == K_ESCAPE: pygame.quit();  sys.exit()#quit
                
                elif e.key == K_RETURN:
                    #saving and loading reset the guy so he knows everything
                   if saving == True:
                       write_to_file(grid,dim, save.value)
                       saving = False
                       draw_all(screen,grid,guy)
                       pygame.display.flip()
                       guy.all_knowing = True
                       
                   elif loading == True:
                       try:#'try' to load the file
                           grid,dim = load_from_file(load.value)
                           screen = pygame.display.set_mode((dim[0], dim[1]))
                           draw_all(screen, grid, guy)
                           guy.all_knowing = True
                           loading = False
                       except:#if we can't, raise and exception
                           load.prompt = "Please try again: "
                           load.value = ''
                       
                if not(saving or loading):#we don't want any interferece while we type
                    if e.key == K_s: saving = True
                    elif e.key == K_l: loading = True
                           
                    #erases the map and replaces it with an empty one    
                    elif e.key == K_q:
                        grid = creategrid(dim)
                        draw_all(screen, grid,guy)
                        guy.all_knowing = True
                    elif e.key == K_m:
                        guy.all_knowing = not guy.all_knowing
                        if guy.all_knowing == True:
                            draw_all(screen,grid,guy)
                        else:
                            screen.fill((0,0,0))
                            pygame.display.flip()
                            guy.known_walkability = creategrid(dim)
                            update(screen,grid,guy,r)
                                    
        if len(guy.path) > 0 :#if the guy has a path
            #if the next step in the path isn't a wall
            if grid[guy.path[0][0]][guy.path[0][1]] != False:
                guy.traverse_path()

            #else if he hits a wall, he recalculates the path
            else: guy.set_path(screen, grid,guy.goal, .07)
            
        #if the guy's time limit runs out for finding a path, he can try again
        elif len(guy.path)>0 and guy.loc != guy.goal and len(guy.goal)>0:
            guy.set_path(screen, grid,guy.goal)

        update(screen, grid, guy,r)
        
        if   drawing  == True: grid = change(screen, grid,False, mousex,mousey)
        elif deleting == True: grid = change(screen, grid, True, mousex,mousey)
        
            
if __name__ == "__main__": main((1000,700))
