# --- block formats for file rift v3.2 and later

# --- for .scmap files




formatList = {

'name' : 'root',

'12' : {   # zone

'name' : 'zone',
'0a' : 'name',
'12' : 'title',
'1a' : {   # scene

    'name' : 'scene',
    '12' : 'name',
    '1a' : {   # connected scene
    
        'name' : 'connected scene',
        '0a' : 'name',
        # directions: 1=right 2=top-right 3=top 3=top-left etc.
        '10' : 'direction',
        '18' : 'unknown1',
        '20' : 'unknown2'
        },

    # features: 1=town 2=??? 3=boss
    '20' : 'feature',
    '28' : 'unknown1',
    '30' : 'unknown2',
    '3a' : 'music',
    '40' : 'unknown3 a',
    '48' : '? treasures',
    '52' : 'title',
    '58' : 'unknown5',
    },

'20' : 'sequence',
'2a' : 'default music',
}
}



# 0 / 000 varint

# 2 / 010 string / subBlock with pointer

# 5 / 101 four bytes

