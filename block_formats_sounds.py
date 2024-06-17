# --- block formats for file rift v3.2 and later

# --- for .sounds files




formatList = {

'name' : 'root',

'0a' : {
    'name' : 'sound',
    '0a' : 'name',
    '12' : 'file',
    '1d' : 'u0',
    '25' : 'u1',
}

}



# 0 / 000 varint

# 2 / 010 string / subBlock with pointer

# 5 / 101 four bytes

