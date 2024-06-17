# --- block formats for file rift v3.2 and later

# --- for .gstate files




formatList = {

'name' : 'root',

'0a' : {
    'name' : 'inventory',
    '28' : 'soul shards',
    '5a' : {
        'name' : 'item',
        '0a' : 'name',
    },
    '7a' : 'skill',
    '82' : 'selected skill',
    '8a' : 'sword trinket',
},
'1a' : 'spawn level',
'22' : 'spawnpoint',
'4a' : 'u1',

}



# 0 / 000 varint

# 2 / 010 string / subBlock with pointer

# 5 / 101 four bytes

