#a star
import time
from binheap import BinHeap

class node(object):
    #a very simple class simply used to store information
    def __init__(self, loc, parent, gscore, fscore):
        self.loc = loc
        self.parent = parent
        self.gscore, self.fscore = gscore, fscore

def getdircost(loc1,loc2):    
    if loc1[0] - loc2[0] != 0 and loc1[1] - loc2[1] != 0:
        return 14 # diagnal movement
    else:
        return 10 # horizontal/vertical movement

def get_h_score(start,end):
    """Gets the estimated length of the path from a node
    using the Manhatten Method."""
    #return 0 #used if you want dijkstras algorith
    return (abs(end[0]-start[0])+abs(end[1]-start[1])) * 10


def create_path(s, end, grid,timelimit):
    "Creates the shortest path between s (start) and end."
    runtime = 0
    
    # yay nested list comprehension
    # the ons list is a 2d list of node status
    # None means the node has not been checked yet
    # a node object for a value means it is on the open list
    # a False value means that it is on the closed list
    ons = [[None for y in xrange(len(grid[x]))] for x in xrange(len(grid))]

    #n is the current best node on the open list, starting with the initial node
    n = node(s, None ,0, 0)

    #we store the fscores of the nodes and the nodes themselves in a binary heap
    openl = BinHeap()

    #local functions accessed faster than global functions
    get_time = time.clock
    geth = get_h_score
    while n.loc != end:
        t = get_time()

        #search adjacent nodes
        #if the node is already on the open list, then
        #and change their pointer the the current node
        #if their path from current node is shorter than their
        #previous path from previous parent
        #if the node is not on the open list and is not a wall,
        #add it to the open list
        for x in xrange(n.loc[0] -1, n.loc[0] +2):
            for y in xrange(n.loc[1] -1 , n.loc[1] + 2):
                #the checked node can't be our central node
                if (x,y) != n.loc:
                        
                    #if the node is not on the closed list or open list
                    if ons[x][y] != None and ons[x][y] != False:
                        #get cost of the new path made from switching parents
                        new_cost = getdircost(n.loc,(x,y)) + n.gscore

                        # if the path from the current node is shorter
                        if new_cost < ons[x][y].gscore:
                            #find the index of the node
                            #to change in the open list
                            index = openl.index([ons[x][y].fscore,ons[x][y]])

                            #update the node to include this new change
                            openl[index][1] = node((x,y), n, new_cost,
                                                   geth((x,y),end) + new_cost)
                            
                            #update the ons list and the fscore list in the heap
                            openl[index][0] = openl[index][1].fscore
                            ons[x][y] = openl[index][1]

                    #if the node is not a wall and not on the closed list
                    #then simply add it to the open list
                    elif grid[x][y] == True and ons[x][y] != False:
                        h = geth((x,y),end)
                        
                        #movement score gets the direction cost
                        #added to the parent's directional cost
                        g = getdircost(n.loc,(x,y)) + n.gscore

                        ons[x][y] = node((x, y), n, g, g+h)#turn it on baby
                        openl.add([g+h, ons[x][y]])




        #if the length of the open list is zero(all nodes on closed list)
        #then return an empty path list
        if len(openl) == 0:
            print runtime
            return []

        #pop from the binary heap (the zeroth index stores fscore only)
        #this will give the node with the smallest fscore, hopefully closer
        #to the goal
        n = openl.pop()[1]

        #remove from the 'closed' list
        ons[n.loc[0]][n.loc[1]] = False

        runtime += get_time()-t
        if runtime > timelimit:
            print runtime
            break


    #Now we have our path, we just need to trace it
    #trace the parent of every node until the beginning is reached
    moves = []
    while n.loc != s:
        moves.insert(0,n.loc)
        n = n.parent
    print runtime
    return moves 
