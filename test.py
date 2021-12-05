
# class Matrix:
#     def __init__(self,rows,columns):
#         self._rows = rows
#         self._columns = columns
#         self.Matrix = [['' for column in range(columns)] for row in range(rows)]
#         self.Column_Major = True
        

#     def add_data(self,data):
#         if self.Column_Major: #selection statement 
#             for column in range(self._columns): #iterates through the column number
#                 for row in range(self._rows): #iterates through the row number
#                     self.Matrix[row][column] = data[row + self._rows*column]
#                     #sets the value in the matrix to the equivalent value in the data array
#         else:
#             for row in range(self._rows): #iterates through row number
#                 for column in range(self._columns): #iterates through column number
#                     self.Matrix[row][column] = data[column + self._columns*row]
#                     #sets the value to equivalent value 


#     def mix_column(self,col_num):
#             a = [0,0,0,0] #creates a new array
#             for c in range(4):
#                 a[c] = self.Matrix[c][col_num] #sets each value of the column to the new array
            
#             self.Matrix[0][col_num] = Galois_Mult(a[0],2)^Galois_Mult(a[1],3)^Galois_Mult(a[2],1)^Galois_Mult(a[3],1)
#             self.Matrix[1][col_num] = Galois_Mult(a[0],1)^Galois_Mult(a[1],2)^Galois_Mult(a[2],3)^Galois_Mult(a[3],1)
#             self.Matrix[2][col_num] = Galois_Mult(a[0],1)^Galois_Mult(a[1],1)^Galois_Mult(a[2],2)^Galois_Mult(a[3],3)
#             self.Matrix[3][col_num] = Galois_Mult(a[0],3)^Galois_Mult(a[1],1)^Galois_Mult(a[2],1)^Galois_Mult(a[3],2)


#     def inv_mix_column(self,col_num):
#         a = [0,0,0,0]
#         for c in range(4):
#             a[c] = self.Matrix[c][col_num]
#         self.Matrix[0][col_num] = Galois_Mult(a[0],14)^Galois_Mult(a[1],11)^Galois_Mult(a[2],13)^Galois_Mult(a[3],9 )
#         self.Matrix[1][col_num] = Galois_Mult(a[0],9 )^Galois_Mult(a[1],14)^Galois_Mult(a[2],11)^Galois_Mult(a[3],13)
#         self.Matrix[2][col_num] = Galois_Mult(a[0],13)^Galois_Mult(a[1],9 )^Galois_Mult(a[2],14)^Galois_Mult(a[3],11)
#         self.Matrix[3][col_num] = Galois_Mult(a[0],11)^Galois_Mult(a[1],13)^Galois_Mult(a[2],9 )^Galois_Mult(a[3],14)


#     def unload(self):
#         arr = [] #empty list 


#         if self.Column_Major: #checks if matrix used column major
#             for i in range(self._columns): #loops each column
#                 for j in range(self._rows): #loops each row
#                     arr.append(self.Matrix[j][i]) #appends data


#         else:
#             for i in range(self._rows):
#                 for j in range(self._columns):
#                     arr.append(self.Matrix[i][j])
#         return arr


# def Galois_Mult(a,b): #a and b are values of state and linear transform
#         product = 0 #return value
#         carry = 0 #states if msb of a is 1 or 0
#         for i in range(8):
#             if b&1 == 1: #checks if lsb of b is 1
#                 product ^= a #XOR product and a
#             carry = a&128 #tracks if msb of a is 1 or not
#             a <<=1 #rotates a one bit left
#             a &= 255 #ands a and 011111111 which discards msb
#             if carry == 128: #if msb of a is set to 1
#                 a ^= 0x1b #XOR a and 27
#             b >>=1 #b rotated right and lsb discarded
#         return product  


# D = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]


# M = Matrix(4,4)
# M.add_data(D)

# print('[',end='')
# for i in range(len(M.Matrix)):
#     if i == len(M.Matrix)-1:
#         print(str(M.Matrix[i])+']')
#     else:
#         print(M.Matrix[i])
    
# print()

message ='the quick brown fox jumps over the lazy dog'
message = bytearray(message,'utf-8')
message.append(0x80)
print(list(message))