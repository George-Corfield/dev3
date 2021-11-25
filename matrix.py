mc = [[2,3,1,1],
    [1,2,3,1],
    [1,1,2,3],
    [3,1,1,2]]

class Matrix:
    def __init__(self,rows,columns):
        self.Matrix = [['' for column in range(columns)] for row in range(rows)]
        self.Column_Major = True
        self._columns = columns
        self._rows = rows

    def add_data(self,data):
        if self.Column_Major:
            for column in range(self._columns):
                for row in range(self._rows):
                    self.Matrix[row][column] = data[row + self._rows*column]
        else:
            for row in range(self._rows):
                for column in range(self._columns):
                    self.Matrix[row][column] = data[column + self._columns*row]


    def rotateLeft(self,rotation_num):
        #rotation_num is the number of times a row needs to be rotated
        #rotation_num is also the index of the row to be rotated
        for rotation in range(rotation_num): #iterated between 0 and rotation num
            self.Matrix[rotation_num].append(self.Matrix[rotation_num].pop(0))
            #this takes the first value and removes it from the row
            #then the value removed by pop is appended onto the end giving the impression it has been rotated

        
    def rotateRight(self,rotation_num):
        #again rotation_num is the number of rotations and the row index
        for rotation in range(rotation_num):#iterates between 0 and number of rotations to be carried out
            self.Matrix[rotation_num].insert(0,self.Matrix[rotation_num].pop(-1))
            #the last value is popped from the row
            #this value is inserted at the start of the row


    def mix_column(self,col_num):
        a = [0,0,0,0] #creates a new array
        for c in range(4):
            a[c] = self.Matrix[c][col_num] #sets each value of the column to the new array
        
        self.Matrix[0][col_num] = Galois_Mult(a[0],2)^Galois_Mult(a[1],3)^Galois_Mult(a[2],1)^Galois_Mult(a[3],1)
        self.Matrix[1][col_num] = Galois_Mult(a[0],1)^Galois_Mult(a[1],2)^Galois_Mult(a[2],3)^Galois_Mult(a[3],1)
        self.Matrix[2][col_num] = Galois_Mult(a[0],1)^Galois_Mult(a[1],1)^Galois_Mult(a[2],2)^Galois_Mult(a[3],3)
        self.Matrix[3][col_num] = Galois_Mult(a[0],3)^Galois_Mult(a[1],1)^Galois_Mult(a[2],1)^Galois_Mult(a[3],2)



    def inv_mix_column(self,col_num):
        a = [0,0,0,0]
        for c in range(4):
            a[c] = self.Matrix[c][col_num]
        self.Matrix[0][col_num] = Galois_Mult(a[0],14)^Galois_Mult(a[1],11)^Galois_Mult(a[2],13)^Galois_Mult(a[3],9 )
        self.Matrix[1][col_num] = Galois_Mult(a[0],9 )^Galois_Mult(a[1],14)^Galois_Mult(a[2],11)^Galois_Mult(a[3],13)
        self.Matrix[2][col_num] = Galois_Mult(a[0],13)^Galois_Mult(a[1],9 )^Galois_Mult(a[2],14)^Galois_Mult(a[3],11)
        self.Matrix[3][col_num] = Galois_Mult(a[0],11)^Galois_Mult(a[1],13)^Galois_Mult(a[2],9 )^Galois_Mult(a[3],14)

        

    def unload(self):
        arr = []
        if self.Column_Major:
            for i in range(self._columns):
                for j in range(self._rows):
                    arr.append(self.Matrix[j][i])
        else:
            for i in range(self._rows):
                for j in range(self._columns):
                    arr.append(self.Matrix[i][j])
        return arr

        
        


def Galois_Mult(a,b):
        p = 0
        carry = 0
        for i in range(8):
            if b&1 == 1:
                p ^= a
            carry = a&128
            a <<=1
            a &= 255
            if carry == 128:
                a ^= 0x1b
            b >>=1
        return p  



            
                

        

