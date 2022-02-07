from pydoc import plain


pt = 89

x = pt^0b101100100
print(bin(pt).removeprefix('0b'))
print(bin(x).removeprefix('0b'))
print(bin(x^0b101100100).removeprefix('0b'))



