#https://medium.com/@sadatnazrul/diffie-hellman-key-exchange-explained-python-8d67c378701c
#https://searchsecurity.techtarget.com/definition/end-to-end-encryption-E2EE
#http://etutorials.org/Networking/802.11+security.+wi-fi+protected+access+and+802.11i/Appendixes/Appendix+A.+Overview+of+the+AES+Block+Cipher/Steps+in+the+AES+Encryption+Process/
from matrix import Matrix
from hashlib import pbkdf2_hmac
from os import pipe, urandom
from itertools import chain
from math import sin, floor

padding_bit = 1

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

class AES:
    def __init__(self,key):
        self.master_keys = self.define_roundKeys(key)

    def encrypt(self,plaintext):
        state = Matrix(4,4)
        state.add_data(plaintext)
        self.add_round_key(self.master_keys.Matrix[0],state)
        for round in range(1,10):
            self.subbytes(state)
            self.shiftrows(state)
            self.mixcolumns(state)
            self.add_round_key(self.master_keys.Matrix[round],state)
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
            
        roundkeys.add_data(data)
        return roundkeys

    
    def pad(self,plaintext):
        padding_dif = 16 - len(plaintext)%16
        bytes_to_be_added = bytes([padding_bit] + [0x0]*(padding_dif-1))
        return plaintext+bytes_to_be_added
    
    def remove_padding(self,plaintext):
        for i in range(len(plaintext)-1,0,-1):
            if plaintext[i] == padding_bit:
                plaintext = plaintext[0:i]
                break
        return plaintext

    def XOR(self,v1,v2):
        tuple_list = zip(v1,v2)
        byte_list = []
        for byte_tuple in tuple_list:
            byte_list.append(byte_tuple[0]^byte_tuple[1])
        return bytes(byte_list)
        #return bytes(a^b for a,b in zip(v1,v2))

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
    key1 = urandom(KEYSIZE)
    IV = urandom(IVSIZE)
    salt = urandom(SALTSIZE)
    key2, key3 = create_keys(password,salt)
    ciphertext = AES(key1).encrypt_mode_cbc(plaintext,IV)
    encrypted_key = AES(key2).encrypt_mode_cbc(key1,IV)
    return encrypted_key+key3+salt+IV+ciphertext
 


def decrypt(password,ciphertext):
    if isinstance(password,str):
        password = password.encode('utf-8')
    if isinstance(ciphertext,str):
        plaintext = ciphertext.encode('utf-8')
    encrpyted_key, ciphertext = ciphertext[:2*KEYSIZE],ciphertext[2*KEYSIZE:]  #2*keysize becuase padding adds extra 16bytes on
    key3, ciphertext = ciphertext[:KEYSIZE],ciphertext[KEYSIZE:]
    salt, ciphertext = ciphertext[:SALTSIZE],ciphertext[SALTSIZE:]
    IV, ciphertext = ciphertext[:IVSIZE],ciphertext[IVSIZE:]
    key2, expected_key3 = create_keys(password,salt)
    if expected_key3 != key3:
        return None
    key1 = AES(key2).decrypt_mode_cbc(encrpyted_key,IV)
    plaintext = AES(key1).decrypt_mode_cbc(ciphertext,IV)
    return plaintext.decode('utf8')


# def rightrotate(a,b):
#     return (a>>b)|(a<<(32-b)) & 0xFFFFFFFF
    

# def rightshift(a,b):
#     return a>>b

# def leftrotate(a,b):
#     return (a<<b)|(a>>(32-b)) & 0xFFFFFFFF

# def leftshift(a,b):
#     return a<<b

def leftrotate(a, b):
    return ((a << b) | (a >> (32 - b))) & 0xFFFFFFFF

def rightrotate(a, b):
    return ((a >> b) | (a << (32 - b))) & 0xFFFFFFFF

def leftshift(a, b):
    return a << b

def rightshift(a, b):
    return a >> b

class Hashing_algorithm():
    def __init__(self):
        self.h = [0x6a09e667,
                  0xbb67ae85,
                  0x3c6ef372,
                  0xa54ff53a,
                  0x510e527f,
                  0x9b05688c,
                  0x1f83d9ab,
                  0x5be0cd19]
        self.k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
   0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
   0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
   0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
   0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
   0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
   0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
   0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

    def update(self,Message):
        #pre processing (padding)
        Message = bytearray(Message,'utf-8')
        L = len(Message)* 8
        Message.append(0x80)
        while (len(Message)*8+64)%512 !=0:
            Message.append(0x00)
        Message += int.to_bytes(L,8,'big')

        #process the message in successive 512-bit chunks
        for each_chunk in range(len(Message)//64):
            chunk = Message[64*each_chunk:64*(each_chunk+1)]
            w = [0 for i in range(64)]
            for word in range(16):
                w[word] = int.from_bytes(chunk[4*word:4*(word+1)],'big')

            #Extend the first 16 words into remaining 48 words
            #W[16..63] of the message schedule array
            for word in range(16,64):
                s0 = (rightrotate(w[word-15],7)^rightrotate(w[word-15],18)^rightshift(w[word-15],3))&0xFFFFFFFF 
                s1 = (rightrotate(w[word-2],17)^rightrotate(w[word-2],19)^rightshift(w[word-2],10))&0xFFFFFFFF
                w[word] = (w[word-16] + s0 + w[word-7] + s1)&0xFFFFFFFF 
            
            #initialize working variables
            a = self.h[0]
            b = self.h[1]
            c = self.h[2]
            d = self.h[3]
            e = self.h[4]
            f = self.h[5]
            g = self.h[6]
            h = self.h[7]

            for i in range(64):
                S1 = (rightrotate(e,6)^rightrotate(e,11)^rightrotate(e,25))&0xFFFFFFFF #S1 = (rightrotate(e, 6) ^ rightrotate(e, 11) ^ rightrotate(e, 25)) & 0xFFFFFFFF
                ch = ((e & f) ^ ((~e) & g)) &0xFFFFFFFF
                temp1 = (h + S1 + ch + self.k[i] + w[i])&0xFFFFFFFF
                S0 = (rightrotate(a,2)^rightrotate(a,13)^rightrotate(a,22))&0xFFFFFFFF #(rightrotate(a, 2) ^ rightrotate(a, 13) ^ rightrotate(a, 22)) & 0xFFFFFFFF
                maj = ((a&b)^(a&c)^(b&c))&0xFFFFFFFF #maj = ((a & b) ^ (a & c) ^ (b & c)) & 0xFFFFFFFF
                temp2 = (S0 + maj)&0xFFFFFFFF 
                

                h = g
                g = f
                f = e
                e = (d+temp1)&0xFFFFFFFF
                d = c
                c = b
                b = a
                a = (temp1+temp2)&0xFFFFFFFF

            self.h[0] = (self.h[0] + a)&0xFFFFFFFF
            self.h[1] = (self.h[1] + b)&0xFFFFFFFF
            self.h[2] = (self.h[2] + c)&0xFFFFFFFF
            self.h[3] = (self.h[3] + d)&0xFFFFFFFF
            self.h[4] = (self.h[4] + e)&0xFFFFFFFF
            self.h[5] = (self.h[5] + f)&0xFFFFFFFF
            self.h[6] = (self.h[6] + g)&0xFFFFFFFF
            self.h[7] = (self.h[7] + h)&0xFFFFFFFF
        
    def digest(self):
        digest = self.hexdigest()
        digest = int(digest,16)
        return digest


    def hexdigest(self):
        digest = ''
        for i in range(len(self.h)):
            digest+= '{:08x}'.format(self.h[i])
        return digest
        


if __name__ == '__main__':
    c = Hashing_algorithm()
    Message = '''dpnacsuwpiwsrxbioaxelwqbgbrnqgpbjmtxvtcurodyjnuxhwkkbuxxyopjvbvdh
lfkvistewlnokqyordxbqicdnhuosxorvppqbwbpvqncligvthftloixywcpebufe
hmywzdnviibqjryyhsqmteohygquxdchpgapzoryuzpxcqvydcrbnglwxrwktpjmz
cnvsudafnoirgcafflvivkwyfwjrkuyknvwctvuivqjknzhiccadddjsnmkvxortt
jkrhbmbdffmjcxzkrynmyfqwagkipfofdeaphwyxxaestzwolzsqvxqrwbmtsamxk
'''
    c.update(Message)
    x1 = c.hexdigest()
    print(x1)






    
     



            
