'''from matrix import Matrix
from hashlib import pbkdf2_hmac
from hmac import new as create_hmac
from os import urandom
from itertools import chain
'''
rcon = [0x00,0x01,0x02,0x04,0x08,0x10,
        0x20,0x40,0x80,0x1B,0x36] #added 0x00 at start so that do not need to decrement i

sbox = [0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
        0xca, 0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
        0xb7, 0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
        0x04, 0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
        0x09, 0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
        0x53, 0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
        0xd0, 0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
        0x51, 0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
        0xcd, 0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
        0x60, 0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
        0xe0, 0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
        0xe7, 0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
        0xba, 0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
        0x70, 0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
        0xe1, 0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
        0x8c, 0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16]

invsbox = [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
           0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
           0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
           0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
           0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
           0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
           0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
           0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
           0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
           0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
           0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
           0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
           0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
           0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
           0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
           0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d]
'''
class AES:
    def __init__(self,key):
        self.master_keys = self.define_roundKeys(key)
        #self.iterations = len(self.plaintext)//16 + 1; remainder = 16-len(self.plaintext)%16;
        # for iteration in range(self.iterations):
        #     if iteration == self.iterations -1:
        #         pass
        #     else:
        #         bytes = Matrix(4,4)
        #         bytes.add_data(self.plaintext[iteration*16:iteration*16+16])
        #         pass

    def encrypt(self,plaintext):
        #print('init',state.Matrix,'\n'
        state = Matrix(4,4)
        state.add_data(plaintext)
        self.add_round_key(self.master_keys.Matrix[0],state)
        #print('0',state.Matrix,'\n')
        for round in range(1,10):
            self.subbytes(state)
            #print(round,state.Matrix,'\n')
            self.shiftrows(state)
            #print(round,state.Matrix,'\n')
            self.mixcolumns(state)
            #print(round,state.Matrix,'\n')
            self.add_round_key(self.master_keys.Matrix[round],state)
            #print(round,state.Matrix,'\n')
        self.subbytes(state)
        self.shiftrows(state)
        self.add_round_key(self.master_keys.Matrix[-1],state)
        return bytes(state.unload())

    def decrypt(self,ciphertext):
        state = Matrix(4,4)
        state.add_data(ciphertext)
        self.add_round_key(self.master_keys.Matrix[-1],state)
        self.invshiftrows(state)
        self.invsubbytes(state)
        for round in range(9,0,-1):
            self.add_round_key(self.master_keys.Matrix[round],state)
            self.invmixcolumns(state)
            self.invshiftrows(state)
            self.invsubbytes(state)
        self.add_round_key(self.master_keys.Matrix[0],state)
        return bytes(state.unload())        

    def encrypt_mode_cbc(self,plaintext,iv):
        plaintext = self.pad(plaintext)
        cipher_text = []
        for block in range(len(plaintext)//16):
            encrypted_block = self.encrypt(self.XOR(plaintext[16*block:16*(block+1)],iv))
            cipher_text.append(encrypted_block)
            iv = encrypted_block
        return b''.join(cipher_text)

    def decrypt_mode_cbc(self,ciphertext,iv):
        plaintext = []
        for block in range(len(ciphertext)//16):
            decrypted_block = self.decrypt(ciphertext[16*block:16*(block+1)])
            plaintext_block = self.XOR(decrypted_block,iv)
            plaintext.append(plaintext_block)
            iv = ciphertext[16*block:16*(block+1)]
        return self.remove_padding(b''.join(plaintext))


    def define_roundKeys(self,key):
        roundkeys = Matrix(11,4)
        roundkeys.Column_Major = False
        data = [list(key[byte:byte+4]) for byte in range(0,len(key),4)]
        i = 1
        for key in range(0,40):
            t_key = list(data[-1])
            if len(data)%4 == 0:
                t_key.append(t_key.pop(0))
                for bit in range(len(t_key)):
                    t_key[bit] = sbox[t_key[bit]]
                t_key[0] ^= rcon[i]
                i+=1
            new_word = self.XOR(t_key,data[-4])
            data.append(new_word)
            
            # Rkey = []
            # for word in range(4):
            #     previous = data[-1][word]
            #     print(previous)
            #     if word == 0:
            #         last = data[-1][-1]
            #         last.append(last.pop(0))
            #         last[0] ^= rcon[i]
            #         new_word = self.XOR(previous,last)
            #     else:
            #         new_word = self.XOR(previous,(Rkey[-1]))
            #     Rkey.append(new_word)
            # i+=1
            # data.append(Rkey)
        roundkeys.add_data(data)
        return roundkeys

   
    def pad(self,plaintext):
        padding_dif = 16 - len(plaintext)%16
        added_bytes = bytes([padding_dif]*padding_dif)
        return plaintext+added_bytes
        # padding = b''
        # if len(plaintext)%16 != 0:
        #     padlen = 16 - len(plaintext)%16
        #     padding = bytes([0x0]*padlen)
        # return plaintext+padding
    
    def remove_padding(self,plaintext):
        padding_dif = plaintext[-1]
        added_bytes = plaintext[-1*padding_dif:0]
        plaintext = plaintext[:len(plaintext)-padding_dif]
        return plaintext

    def XOR(self,v1,v2):
        return bytes(a^b for a,b in zip(v1,v2))

    def subbytes(self,state):
        for column in range(state._columns):
            for row in range(state._rows):
                state.Matrix[row][column] = sbox[state.Matrix[row][column]]

    def invsubbytes(self,state):
        for column in range(state._columns):
            for row in range(state._rows):
                state.Matrix[row][column] = invsbox[state.Matrix[row][column]]


    def shiftrows(self,state):
        for row in range(1,state._rows):
            state.rotateLeft(row)

    def invshiftrows(self,state):
        for row in range(1,state._rows):
            state.rotateRight(row)

    def mixcolumns(self,state):
        for column in range(state._columns):
            state.mix_column(column)

    def invmixcolumns(self,state):
        for column in range(state._columns):
            state.inv_mix_column(column)
            

    def add_round_key(self,round_key,state):
        for i in range(4):
            for j in range(4):
                state.Matrix[i][j] ^= round_key[j][i]


SALTSIZE = KEYSIZE = IVSIZE = 16

def create_keys(password,salt):
    digest = pbkdf2_hmac('sha256',password,salt,100000)
    key2 = digest[0:KEYSIZE]
    key3 = digest[KEYSIZE:]
    return key2,key3


def encrypt(password,plaintext):
    if isinstance(password,str):
        password = password.encode('utf-8')
    if isinstance(plaintext,str):
        plaintext = plaintext.encode('utf-8')
    key1 = urandom(KEYSIZE); print('k1',key1)
    IV = urandom(IVSIZE); print('IV',IV)
    salt = urandom(SALTSIZE); print('salt',salt)
    key2, key3 = create_keys(password,salt); print('k2',key2,'k3',key3)
    ciphertext = AES(key1).encrypt_mode_cbc(plaintext,IV)
    encrypted_key = AES(key2).encrypt_mode_cbc(key1,IV); print('encK1',encrypted_key)
    return encrypted_key+key3+salt+IV+ciphertext
 

    # key = key.encode('utf-8')
    # plaintext = plaintext.encode('utf-8')
    # salt = b');W\x85\x93\xa3\xa7\xe6KJ\xf4\xd1\x85\x11-$' #urandom(16)
    # print(salt,'s')
    # key = b'\xd6\xf6 ?\xebG\x00\x05\x88\xa5\xf5\x92\x13\xeb\xd1\x83'
    # iv = b'\xac\xe0\x84\xf0xEQ\xa71\xb2(\xd1\xe7\xb1\xfda'
    # #key,iv = create_keys(key,salt)
    # ciphertext = AES(key).encrypt_mode_cbc(plaintext,iv)
    # return ciphertext

def decrypt(password,ciphertext):
    if isinstance(password,str):
        password = password.encode('utf-8')
    if isinstance(ciphertext,str):
        plaintext = ciphertext.encode('utf-8')
    encrpyted_key, ciphertext = ciphertext[:2*KEYSIZE],ciphertext[2*KEYSIZE:] ;print('enck1',encrpyted_key) #2*keysize becuase padding adds extra 16bytes on
    key3, ciphertext = ciphertext[:KEYSIZE],ciphertext[KEYSIZE:] ; print('k3',key3)
    salt, ciphertext = ciphertext[:SALTSIZE],ciphertext[SALTSIZE:] ; print('salt',salt)
    IV, ciphertext = ciphertext[:IVSIZE],ciphertext[IVSIZE:] ; print('IV',IV)
    key2, expected_key3 = create_keys(password,salt) ; print('exk3',expected_key3,'k2',key2)
    if expected_key3 != key3:
        return None
    key1 = AES(key2).decrypt_mode_cbc(encrpyted_key,IV)
    plaintext = AES(key1).decrypt_mode_cbc(ciphertext,IV)
    return plaintext
    
    
    t
    # if isinstance(key,str):
    #     key = key.encode('utf-8')
    # if isinstance(ciphertext,str):
    #     ciphertext = ciphertext.encode('utf-8')
    # #salt = ciphertext[:16]
    # #ciphertext = ciphertext[16:]
    # #key,iv = create_keys(key,salt)
    # key = b'\xd6\xf6 ?\xebG\x00\x05\x88\xa5\xf5\x92\x13\xeb\xd1\x83'
    # iv = b'\xac\xe0\x84\xf0xEQ\xa71\xb2(\xd1\xe7\xb1\xfda'
    # return AES(key).decrypt_mode_cbc(ciphertext,iv)
    
        
        

if __name__ == '__main__':
    # text = b'Fusce tincidunt.'
    # key = b'Curabitur justo.'
    # encrypt = AES(key)
    # print(encrypt.encryption(text))
    ciphertext = encrypt('abcdefg','ABCDEFGHIJKLMNOPQRSTUV')
    print(ciphertext)
    pt= decrypt('abcdefg',ciphertext)
    print(str(pt,'utf-8'))
    # print(f'TESTING CBC DECRYPTION, KEY=abcdefg, CT={CT}')
    # PT = decrypt('abcdefg',CT)
    # print('PT',PT)

    for i in range(11):
        if i == 0:
            print(encrypt.master_keys.Matrix[i])
        else:
            line = []
            for j in range(4):
                line.append(list(hex(a) for a in encrypt.master_keys.Matrix[i][j]))
            print(line)'''

 
# def XOR2(v1,v2):
#         tuple_list = zip(v1,v2)
#         print(tuple_list)
#         byte_list = []
#         for byte_tuple in tuple_list:
#             byte_list.append(byte_tuple[0]^byte_tuple[1])
#         return bytes(byte_list)
    
# def XOR1(v1,v2):
#         return bytes(a^b for a,b in zip(v1,v2))
    

# print(XOR1([109,78,45,88,96],[108,79,65,69,230]))
# print(XOR2([109,78,45,88,96],[108,79,65,69,230]))

'''
from matrix import Matrix
from hashlib import pbkdf2_hmac, sha256
from os import urandom
#Matrix class from matrix.py

padding_bit = 0x1

class AES:
    def __init__(self,key):
        self.master_keys = self.define_roundKeys(key)#calls the define_roundKeys() to expand the keys



    def define_roundKeys(self,key):
        #Expansion of a 128-bit key
        roundkeys = Matrix(11,4)#produce a matrix of 11*4 
        roundkeys.Column_Major = False#set matrix to row matrix
        expanded_keys = [list(key[byte:byte+4]) for byte in range(0,len(key),4)]
        #splits the initial key into 4 lots of 4 bytes and appends it to a list
        i = 1#sets the initial value for the r_con index

        for key in range(0,40):#range of 40 to get all 10 remaining round keys
            t_key = list(expanded_keys[-1])#set the temporary key to the last 4 bytes

            if len(expanded_keys)%4 == 0:#for the first 4 bytes of an expanded key only

                t_key.append(t_key.pop(0))#rotate the 4 bytes left by 1 byte
                for byte in range(len(t_key)):#apply sbox to each byte in t_key
                    t_key[byte] = sbox[t_key[byte]]
                t_key[0] ^= rcon[i]#xor rcon with first byte
                i+=1#increment rcon index

            new_word = self.XOR(t_key,expanded_keys[-4])#for all of the 4 bytes in an expanded key, XOR with byte 16 bytes before current key
            expanded_keys.append(new_word)#append the new 4 bytes to the expanded keys
            
            
        roundkeys.add_data(expanded_keys)#add expanded keys to the matrix object
        return roundkeys#returns all the round keys as a matrix object

    def encrypt(self,plaintext):
        state = Matrix(4,4) #create state matrix of 16 bytes
        plaintext = bytes(plaintext.encode()) #encode plaintext into byte object
        state.add_data(plaintext) #add data to state matrix
        for i in state.Matrix:
            print(i)
        self.add_round_key(self.master_keys.Matrix[0],state) #adds initial key to state matrix
        for round in range(1,10): #iterates 1-9 included
            self.subbytes(state) #calls subbytes method
            self.shiftrows(state) #calls shiftrows method
            self.mixcolumns(state) #calls mixcolumns method
            self.add_round_key(self.master_keys.Matrix[round],state) #passes the rounds round key
        #final round encryption - no mixcolumns
        self.subbytes(state) 
        self.shiftrows(state)
        self.add_round_key(self.master_keys.Matrix[-1],state) #adds final round key
        return bytes(state.unload()) #returns a bytes object of the unloaded state


    def decrypt(self,ciphertext):
        state = Matrix(4,4)
        state.add_data(ciphertext)

        self.add_round_key(self.master_keys.Matrix[-1],state) #adds the last round key in the master keys
        self.invshiftrows(state) #shifts the rows right
        self.invsubbytes(state) #subs bytes from inv s-box


        for round in range(9,0,-1): #iterates from 9 to 1 inclusive with a step of -1
            self.add_round_key(self.master_keys.Matrix[round],state) #adds appropriate round key
            self.invmixcolumns(state) #calls inverse mix columns
            self.invshiftrows(state) #calls inverse shift rows
            self.invsubbytes(state) #calls invsers sub bytes


        self.add_round_key(self.master_keys.Matrix[0],state) #adds initial key (i.e. the first round key)
        return bytes(state.unload()) #unloads the plaintext and returns as a bytes object

    def invshiftrows(self,state):
        for row in range(1,state._rows): #iterates through each row number
            state.rotateRight(row) #calls the matrix.rotateRight method to rotate each row

    def invsubbytes(self,state):
        for column in range(state._columns): #iterates through each column  
            for row in range(state._rows): #nested loop to iterate through each row
                state.Matrix[row][column] = invsbox[state.Matrix[row][column]] #subs the new value in based on the old value

    def invmixcolumns(self,state):
        for column in range(state._columns): #iterates through each column position
            state.inv_mix_column(column) #passes the column index for each column position


    def encrypt_mode_cbc(self,plaintext,iv):
        plaintext = self.pad(plaintext) #calls pad to make the plaintext a multiple of 16

        cipher_text = b''
        for block in range(len(plaintext)//16): #iterates through the number of blocks
            block_to_be_encrypted = self.XOR(plaintext[16*block:16*(block+1)],iv) #XOR's the current IV with the plaintext block
            encrypted_block = self.encrypt(block_to_be_encrypted) #encrypts the block 
            cipher_text+=encrypted_block #appends the new encrypted block to the cipher text list
            iv = encrypted_block #sets the new IV as the encrypted block
        return cipher_text

    def decrypt_mode_cbc(self,ciphertext,iv):
        plaintext = b'' #creates empty bytes object

        for block in range(len(ciphertext)//16): #iterates through number of blocks
            decrypted_block = self.decrypt(ciphertext[16*block:16*(block+1)]) #calls decrypt block for the appropriate ciphertext block
            plaintext_block = self.XOR(decrypted_block,iv) #XOR is the same each way so this turns decrypted XORd block into plaintext
            plaintext+= plaintext_block #adds plaintext block to plaintext bytes object
            iv = ciphertext[16*block:16*(block+1)] #iv is the next encrypted block


        return self.remove_padding(plaintext) #removes the padding from the start


    def add_round_key(self,round_key,state): #passed the round key to be XOR and the whole state
        for row in range(4): #iterates through each row
            for column in range(4): #iterates through each column
                state.Matrix[row][column] ^= round_key[column][row] #XORs with corresponding round key


    def subbytes(self,state):
        for column in range(state._columns): 
            for row in range(state._rows):
                state.Matrix[row][column] = sbox[state.Matrix[row][column]]
        

    def mixcolumns(self,state):
        for column in range(state._columns):
            state.mix_column(column)

    def shiftrows(self,state):
        for row in range(1,state._rows): #goes through each row, skips first row
            state.rotateLeft(row) #calls the matrix method rotateLeft


    def XOR(self,v1,v2):
        return bytes(a^b for a,b in zip(v1,v2))

    def pad(self,plaintext):
        padding_dif = 16 - len(plaintext)%16 #adds a block of padding if the plaintext is already 16
        bytes_to_be_added = bytes([padding_bit] + [0x0]*(padding_dif-1)) #adds one padding bit followed by a number of 0's
        return plaintext+bytes_to_be_added #concatenates the plaintext and the padding

    def remove_padding(self,plaintext):
        for i in range(len(plaintext)-1,0,-1): #iterates through object from end to start
            if plaintext[i] == padding_bit: #checks if the byte is the padding bit (i.e. 0x01)
                plaintext = plaintext[0:i] #if it is the padding bit, the plaintext is the plaintext from the start to that point
                break #it breaks the loop to keep the plaintext in tact
        return plaintext #it returns the plaintext

        # padding_dif = plaintext[-1]
        # added_bytes = plaintext[-1*padding_dif:0]
        # plaintext = plaintext[:len(plaintext)-padding_dif]
        #return plaintext

SALTSIZE = KEYSIZE = IVSIZE = 16

def create_keys(password,salt):
    digest = pbkdf2_hmac('sha256',password,salt,100000)
    key2 = digest[0:KEYSIZE]
    key3 = digest[KEYSIZE:]
    return key2,key3

def encrypt(password,plaintext):
    if isinstance(password,str):
        password = password.encode('utf-8')
    if isinstance(plaintext,str):
        plaintext = plaintext.encode('utf-8')

        
    key1 = urandom(KEYSIZE); #creates a random key1 from keysize                                                               #print('k1',key1)
    IV = urandom(IVSIZE); # creates random IV from IV size                                                               #print('IV',IV)
    salt = urandom(SALTSIZE); #creates random salt value from salt size                                                              #print('salt',salt)
    key2, key3 = create_keys(password,salt); #called to create keys2 and keys3 from the password and salt                                                            #print('k2',key2,'k3',key3)
    
    
    ciphertext = AES(key1).encrypt_mode_cbc(plaintext,IV)
    encrypted_key = AES(key2).encrypt_mode_cbc(key1,IV);                                                     #print('encK1',encrypted_key)
    return encrypted_key+key3+salt+IV+ciphertext



def decrypt(password,ciphertext):
    if isinstance(password,str):
        password = password.encode('utf-8')
    if isinstance(ciphertext,str):
        plaintext = ciphertext.encode('utf-8')
    encrpyted_key, ciphertext = ciphertext[:2*KEYSIZE],ciphertext[2*KEYSIZE:] ;print('enck1',encrpyted_key) #2*keysize becuase padding adds extra 16bytes on
    key3, ciphertext = ciphertext[:KEYSIZE],ciphertext[KEYSIZE:] ; print('k3',key3)
    salt, ciphertext = ciphertext[:SALTSIZE],ciphertext[SALTSIZE:] ; print('salt',salt)
    IV, ciphertext = ciphertext[:IVSIZE],ciphertext[IVSIZE:] ; print('IV',IV)
    key2, expected_key3 = create_keys(password,salt) ; print('exk3',expected_key3,'k2',key2)
    if expected_key3 != key3:
        return None
    key1 = AES(key2).decrypt_mode_cbc(encrpyted_key,IV)
    plaintext = AES(key1).decrypt_mode_cbc(ciphertext,IV)
    return plaintext

'''

class Matrix:
    def __init__(self,rows,columns):
        self._rows = rows
        self._columns = columns
        self.Matrix = [['' for column in range(columns)] for row in range(rows)]
        self.Column_Major = True
        

    def add_data(self,data):
        if self.Column_Major: #selection statement 
            for column in range(self._columns): #iterates through the column number
                for row in range(self._rows): #iterates through the row number
                    self.Matrix[row][column] = data[row + self._rows*column]
                    #sets the value in the matrix to the equivalent value in the data array
        else:
            for row in range(self._rows): #iterates through row number
                for column in range(self._columns): #iterates through column number
                    self.Matrix[row][column] = data[column + self._columns*row]
                    #sets the value to equivalent value 


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
        arr = [] #empty list 


        if self.Column_Major: #checks if matrix used column major
            for i in range(self._columns): #loops each column
                for j in range(self._rows): #loops each row
                    arr.append(self.Matrix[j][i]) #appends data


        else:
            for i in range(self._rows):
                for j in range(self._columns):
                    arr.append(self.Matrix[i][j])
        return arr


def Galois_Mult(a,b): #a and b are values of state and linear transform
        product = 0 #return value
        carry = 0 #states if msb of a is 1 or 0
        for i in range(8):
            if b&1 == 1: #checks if lsb of b is 1
                product ^= a #XOR product and a
            carry = a&128 #tracks if msb of a is 1 or not
            a <<=1 #rotates a one bit left
            a &= 255 #ands a and 011111111 which discards msb
            if carry == 128: #if msb of a is set to 1
                a ^= 0x1b #XOR a and 27
            b >>=1 #b rotated right and lsb discarded
        return product  


D = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]


M = Matrix(4,4)
M.add_data(D)

print('[',end='')
for i in range(len(M.Matrix)):
    if i == len(M.Matrix)-1:
        print(str(M.Matrix[i])+']')
    else:
        print(M.Matrix[i])
    
print()