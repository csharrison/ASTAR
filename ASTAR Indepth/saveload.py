#saving and loading
def write_to_file(grid, dim, path):
    "writes the current map to a file"
    f = open(path,'w')
    f.write (str(dim[0])+" "+str(dim[1]) + " ")
    for x in xrange(len(grid)):
        for y in xrange(len(grid[x])):
            f.write(str(int(grid[x][y]))+" ")
    f.close()

def load_from_file(path):
    "loads the current map from a file"
    t = open(path,'r').read().split()
    dim = int(t[0]),int(t[1])
    row ,grid, t = [],[], t[2:]
    for i in xrange(len(t)):
        if i>0 and i % ((dim[1])/10) == 0: grid.append(row); row = []
        row.append(bool(int(t[i])))
    grid.append(row)
    return grid, dim
