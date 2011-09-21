from math import sin,cos,atan, acos
def calculate_direction(start,end):
    "calculates the direction the guy needs to go to reach the next node"
    start = [i*10 for i in start]
    end = [i*10 for i in end]
    
    theta = 0
    speed = 2

    
    if start[0] - end[0] == 0:#completely vertical path
        changex = 0#no x change (vertical movement)
        theta = acos(0)# used to calculate y change

        #if the guy is below the path, you need to multiply it by -1 (I don't know why)
        if start[1]<end[1]:
            changey = sin(theta) * speed * .1
        else:
            changey = sin(theta) * speed * .1 * -1

    else:
        #calculate the changex and changey by finding the atan of the change of x and y

        theta = atan((start[1]-end[1])/(start[0]-end[0]))

        changex = cos(theta) * speed* .1
        
        changey = sin(theta) * speed* .1

    #strange, I don't know why this is needed either, but it is, stupid polar coordinate system
    if start[0]-end[0]>0:
        changex *= -1
        changey *= -1

    return changex, changey

#makes A* paths pretty
import pygame
def walkable(screen, point, nextpoint, grid, width):
    "Checks to see if two nodes on a grid are walkable in a straight line"

    #changex, changey = calculate_direction(point,nextpoint)
    #print changex, changey
    changex = (nextpoint[0] - point[0])/100.
    changey = (nextpoint[1] - point[1])/100.
    #print point,nextpoint
    x = point[0] + changex
    y = point[1] + changey
    #print changex,changey
    
    #for i in xrange(50):#go through the path and see if there are any walls that the guy would hit

    while (round(x),round(y)) != nextpoint:
        #pygame.draw.circle(screen, (0,0,0), (x*10,y*10),0)
        #pygame.display.flip()#update((x*10,y*10,2,2))
        #these grid values are where the guy will 'clip' a wall
        if grid[int(round(x+width/15.))][int(round(y))] == False: return False
        if grid[int(round(x-width/15.))][int(round(y))] == False: return False
        if grid[int(round(x))][int(round(y+width/15.))] == False: return False
        if grid[int(round(x))][int(round(y-width/15.))] == False: return False

        x += changex
        y += changey
    return True

def make_smooth(screen, start,path, grid):
    "Takes an A* path and allows for <45 degree turns"
    #goes through each node and sees if the node in front of it
    #can be removed while still traveling in a straight line to the next node
    checkpoint = start
    curi = 0#current node
    while curi+1 < len(path):
        if walkable(screen, checkpoint, path[curi+1], grid, 5) ==True:
            #pygame.draw.rect(screen, (255,0,0),(path[curi][0]*10,path[curi][1]*10,10,10))
            #pygame.display.flip()
            path.remove(path[curi])#remove unneeded paths
        else:
            #pygame.draw.rect(screen, (0,0,0),(path[curi][0]*10,path[curi][1]*10,10,10))
            #pygame.display.flip()
            checkpoint = path[curi]
            curi+=1

    return path
