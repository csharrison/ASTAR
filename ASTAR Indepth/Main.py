import pygame
import sys
import eztext
from pygame.locals import *

from astarcolor import create_path
from math import acos,atan,sin,cos
from saveload import write_to_file,load_from_file


#This file gives a much more indepth look at the A* algorithm, allowing
#the user to see exacly how a search is made, and how paths are traced
#When a path is created:
#Blue squares: nodes on the open list
#Red squares: nodes on the closed list
#Grey squares: shows the best path

#after the best path is found, it passes through a smoothing function
#black squares indicate path nodes that have been removed from the path
#yellow squares are nodes that have stayed

#each square has an arrow pointing to its parent square

class Guy(object):
    def __init__(self, loc, image, screen):
        self.rloc = (loc[0]*10, loc[1]*10)#'real' location
        self.loc, self.path = loc, []
        self.image = pygame.image.load(image)
        self.goal = ()
        self.theta = self.changex = self.changey = 0
        self.wait = 0
        self.screen = screen

    def user_control(self,direction, grid):
        #wait to slow things down a bit
        self.wait+=1
        if self.wait == 50:

            #draw a rect over the guy, 'erasing' him
            pygame.draw.rect(self.screen,(100,255,100),
                             (self.rloc[0],self.rloc[1],10,10))
            
            #if the  guy can go the direction we choose, move there
            if grid[self.loc[0]+direction[0]][self.loc[1]+direction[1]]==True:
                self.loc = (self.loc[0]+direction[0],self.loc[1]+direction[1])

            #else only move which direction he can go in
            #this is done to create fluid movment next to walls
            elif grid[self.loc[0]+ direction[0]][self.loc[1]] == True:
                self.loc = (self.loc[0] + direction[0],self.loc[1])
                
            elif grid[self.loc[0]][self.loc[1]+direction[1]] == True:
                self.loc = (self.loc[0],self.loc[1] + direction[1])

            #make the pixel location line up with the grid
            self.rloc = (float(self.loc[0]*10),float(self.loc[1]*10))
            self.wait = 0
            
    def calculate_direction(self):
        "calculates the direction the guy needs to go to reach the next node"

        #completely vertical path
        if self.rloc[0] - self.path[0][0]*10 == 0:
            #no x change
            self.changex = 0

            #used to calculate y change
            self.theta = acos(0)

            #if the guy is below the path, you need to
            #multiply it by -1 (I don't know why)
            if self.rloc[1]<self.path[0][1]*10:
                self.changey = sin(self.theta)*.1
            else:
                self.changey = sin(self.theta)*.1 *-1

        else:#not a vertical path
            
            #calculate the changex and changey
            #by finding the atan of the change of x and y
            self.theta = atan((self.rloc[1]-self.path[0][1]*10.)/
                              (self.rloc[0]-self.path[0][0]*10.))
            
            self.changex = cos(self.theta) *.1
            self.changey = sin(self.theta) *.1

        #strange, I don't know why this is needed either,
        #but it is, stupid polar coordinate system
        #if the path node is left of the start, reverse it
        if self.rloc[0]-self.path[0][0]*10.>0:
            self.changex*=-1
            self.changey*=-1
        
    def set_path(self, grid, end):
        "sets a path for the guy to follow"
        self.goal = end # reset the goal
        
        #create a path using A* and smooth it up with the smoothing function
        #draw stuff as well in these functions
        self.path = create_path(self.loc,end,grid,self.screen)
        #self.path = make_smooth(self.loc, self.path, grid, self.screen)
        
        #sometimes the path will be empty
        if len(self.path)>0:
            self.calculate_direction()#calculate the initial direction
        pygame.display.flip()#update the screen
        
    def traverse_path(self):
        #update the 'real' location and the rounded grid location
        self.rloc = (self.rloc[0]+self.changex, self.rloc[1] + self.changey)
        self.loc = (int(round((self.rloc[0]/10.))),
                     int(round(self.rloc[1]/10.)))

        #if the grid location matches with our target...
        if self.loc == self.path[0]:
            #reset the 'real' location to the grid location
            #uncomment this out in order to get no clipping, but jerkier paths
            #speeding up the guys speed helps sorta mask it
            #self.rloc = (self.loc[0]*10.,self.loc[1]*10.)
            
            self.path.pop(0)#delete that node from our path

            #if we still have a path, recalculate our new direction
            if len(self.path)>0: self.calculate_direction()
            
            else:#path is nonexistent
                #'erase' the guy and update the location
                #'fix' the guy to the grid basically
                pygame.draw.rect(self.screen,(100,255,100),
                                 (self.rloc[0],self.rloc[1],10,10))
                
                self.rloc = (float(self.loc[0]*10),float(self.loc[1]*10))

    def draw_guy(self):
        #blit the dude on the screen, based on his 'real' coordinates
        self.screen.blit(self.image, (self.rloc[0], self.rloc[1]))
        
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

def update(screen, grid, guy):
    #'erase' the guy, draw him, then update the screen
    pygame.draw.rect(screen, (100,255,100),(guy.rloc[0],guy.rloc[1],10,10))
    guy.draw_guy()
    pygame.display.update((guy.rloc[0]-20),(guy.rloc[1]-20),40, 40)

def draw_all(screen, grid, guy):
    "Draws the entire screen"
    for x in xrange(len(grid)):
        for y in xrange(len(grid[x])):
            #draw either walls or grass
            if grid[x][y] == True:
                pygame.draw.rect(screen, (100,255,100), (x*10, y * 10, 10, 10))
            elif grid[x][y] == False:
                pygame.draw.rect(screen, (150,100,50) , (x*10, y * 10, 10, 10))

    #draw the guy and update the entire screen
    guy.draw_guy()
    pygame.display.flip()

def change(screen, grid, deleting, mx, my):
    "either draws or erases a wall"
    grid[mx][my] = deleting
    if deleting: pygame.draw.rect(screen,(100,255,100),(mx*10, my*10,10,10))
    else       : pygame.draw.rect(screen,(150,100,50) ,(mx*10, my*10,10,10))
    pygame.display.update(mx*10, my * 10, 10, 10)
    return grid

def main(dim):
    #initialize pygame, the display caption, and the screen
    pygame.init(); pygame.display.set_caption("A* Maze")
    grid = creategrid(dim)
    screen = pygame.display.set_mode((dim[0], dim[1]))

    guy = Guy((10,15),"smiley x 10.bmp", screen)


    save = eztext.Input(maxlength=60, color=(255,0,0),
                        prompt='Input save path: ')
    load = eztext.Input(maxlength=60, color=(255,0,0),
                        prompt='Input load path: ')

    #we arent loading or saving
    loading = saving = False
    #we aren't drawing or deleting
    drawing = deleting = False

    #guy moving on a path
    moving = False
    
    #user control direction booleans
    direction = [0,0]
    #user movment
    userm = False

    #draw everything on the screen
    draw_all(screen,grid,guy)

    clock = pygame.time.Clock()#
    while True:#main game loop
        clock.tick(1000)#limits the speed of the game

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

            #right click will draw a wall or delete
            #left click will move the guy to your mouse cursor
            if e.type == MOUSEBUTTONDOWN:
                #right mouse button pressed
                if pygame.mouse.get_pressed()[2] == 1:
                    #if we start by seleting a wall, then we are deleting
                    #else we start drawing
                    if grid[mousex][mousey] == True:
                        drawing = True
                    else:
                        deleting = True

                #set a new path for the guy
                elif grid[mousex][mousey]!= False and (mousex,mousey)!=guy.loc:
                    draw_all(screen, grid,guy)#redraw everythin
                    moving = False#the guy stops moving
                    guy.set_path(grid,(mousex,mousey))
                    #no user movement possible at this point
                    userm = False

            #stop deleting/drawing walls
            elif e.type == MOUSEBUTTONUP:drawing = deleting = False


            #ESC->quit; s ->save map;  l -> load map
            #q -> deletes the entire map
            #SPACE -> moves guy once a path is known
            elif e.type == KEYDOWN:

                #escape to quit
                if e.key == K_ESCAPE: pygame.quit();  sys.exit()

                #sends in the text input for map I/O
                elif e.key == K_RETURN:
                   if saving == True:
                       write_to_file(grid,dim, save.value)
                       draw_all(screen,grid,guy)
                       pygame.display.flip()
                       saving = False
                       
                   elif loading == True:
                       try:#'try' to load the file
                           grid,dim = load_from_file(load.value)
                           screen = pygame.display.set_mode((dim[0], dim[1]))
                           draw_all(screen, grid, guy)
                           loading = False
                       except:#if we can't, raise an exception
                           load.prompt = "Please try again: "
                           load.value = ''
                       
                if not(saving or loading):
                    #we don't want any interferece while we type
                    if e.key == K_s: saving = True
                    elif e.key == K_l: loading = True
                    elif e.key == K_SPACE: moving = True
                        
                    #erases the map and replaces it with an empty one    
                    elif e.key == K_q:
                        grid = creategrid(dim)
                        draw_all(screen, grid,guy)

                    #controls the guys direction
                    elif e.key == K_RIGHT: direction[0] =  1
                    elif e.key == K_LEFT:  direction[0] = -1
                    elif e.key == K_UP  :  direction[1] = -1
                    elif e.key == K_DOWN:  direction[1] =  1

                    #if we are inputing movement and we 'can' move
                    if direction!=[0,0] and userm == False and moving == False:
                        draw_all(screen,grid,guy)
                        userm = True

            elif e.type == KEYUP:
                #reset arrow keys to say we dont won't to go in that direction
                if e.key == K_RIGHT: direction[0] = 0
                elif e.key == K_LEFT: direction[0] = 0
                elif e.key == K_UP: direction[1] = 0
                elif e.key == K_DOWN: direction[1] = 0
                
        if len(guy.path) > 0 :#if the guy has a path
            #if the next step in the path isn't a wall
            if grid[guy.path[0][0]][guy.path[0][1]] != False:
                if moving == True: guy.traverse_path()
            
        elif len(guy.path) == 0: moving = False
        
        if moving == False and userm == True:
            guy.user_control(direction, grid)
            
        update(screen, grid, guy)
        
        if   drawing  == True: grid = change(screen, grid,False, mousex,mousey)
        elif deleting == True: grid = change(screen, grid, True, mousex,mousey)
        
            
if __name__ == "__main__": main((1000,700))
