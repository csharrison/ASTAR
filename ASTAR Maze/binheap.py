#binary heap

class BinHeap(object):
        def __init__(self):
                #first index is not used for math purposes
                self.l = [None]

        def __repr__(self):
                #what shows up when you type the object in the interpreter
                return str(self.l[1:])

        def __len__(self):#called by the len() function
                return len(self.l)-1

        def __getitem__(self, key):#called by heap[key]
                return self.l[key+1]
        
        def index(self,value):
                #returns the index of a particular item in the heap
                return self.l.index(value)-1

        def add(self, value):
                "appends a value to the heap"
                self.l.append(value)
                pos = len(self.l)-1 #start at the last position
        
                if pos != 1:
                        #as long as the value is less than its parent (value index /2, rounded down)
                        #we bubble it up in the list
                        while value < self.l[pos/2]:
                                self.l[pos] , self.l[pos/2] = self.l[pos/2] , self.l[pos] #switcheroo (bubble)
                                pos /= 2

        def pop(self):
                "Deletes and returns the smallest element in the heap"
                
                #switch the root and the last element
                self.l[1], self.l[len(self.l)-1] = self.l[len(self.l)-1] , self.l[1]
                
                retval = self.l.pop() # remove the element that used to be the root

                pos = 1#current position of the appended value
                while True:
                        if pos*2 > len(self.l)-1: break # no children
                        
                        elif pos *2+1 > len(self.l) -1:#no right child
                                
                                #the root is less than its only child, break
                                if self.l[pos] < self.l[pos * 2]: break
                                
                                else: #root greater than single child
                                        self.l[pos] , self.l[pos * 2] = self.l[pos * 2] , self.l[pos] #switcheroo (bubble)
                                        pos *= 2

                        elif self.l[pos] < self.l[pos *2] and self.l[pos] < self.l[pos *2 + 1]:
                                #if the root is less than its children, break
                                break

                        else:# root is greater than children
                                if self.l[pos * 2] < self.l[pos * 2 + 1]:
                                        self.l[pos] , self.l[pos * 2] = self.l[pos * 2] , self.l[pos] #switcheroo (bubble)
                                        pos *= 2
                                else:
                                        self.l[pos] , self.l[pos * 2+1] = self.l[pos * 2+1] , self.l[pos] #switcheroo (bubble)
                                        pos = pos * 2 + 1
                return retval

        def get_min(self):
                "returns the smallest item in the heap, without deleting it"
                return self.l[1]


if __name__ == "__main__":#if we run the program as a standalone program
        heap = BinHeap()
        heap.add(4)
        heap.add(5)
        heap.add(15)
        heap.add(-5)
        print heap
        heap.add(100)
        heap.add(-100)
        heap.add(-1000)
        heap.add(-100)
        print heap
        print heap.pop()
        print heap.pop()
        print heap.pop()
        print heap.pop()
        print heap.pop()
        print heap.pop()
        print heap.pop()
        print heap
