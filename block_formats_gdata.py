# --- block formats for file rift v3.2 and later

# --- for .gdata files




formatList = {

'name' : 'root',


'0a' : {   # collectable item

    'name' : 'collectable item',
    '12' : 'name',
    '1a' : 'title',
    '22' : 'subTitle',
    '2a' : 'info',
    # item types : 1=non-collectable,2=sword,3=armour,4=trinket,5=collectable
    '08' : 'item type',
    '30' : 'can have multiple',
    '38' : 'min damage',
    '40' : 'max damage',
    '48' : 'sequence position'

},
'12' : {   # skill

    'name' : 'skill',
    '0a' : 'name',
    '12' : 'title',
    '1a' : 'subtitle',
    '20' : 'u0',
    '28' : 'min damage',
    '30' : 'max damage'

},
'1a' : {   # quest

    'name' : 'quest',
    '0a' : 'name',
    '12' : 'title',
    '22' : 'target level'
    
},
'22' : {   # entity info

    'name' : 'entity info',
    '0a' : 'name',
    '12' : 'title',
    '18' : 'u0',
    '20' : 'u1',
    '28' : 'u2',
    '30' : 'u3',
    '3d' : 'u4',
    '45' : 'u5',
    
},
'2a' : {   # compass info

    'name' : 'compass info',
    '08' : 'u0',
    '12' : 'name',
    '1a' : 'target level',
    '22' : 'target object',
    '2a' : 'u1',
    '30' : 'u2',
    '3a' : {   # waypoints

        'name' : 'waypoint',
        '0a' : 'target level',
        '12' : 'target object',

    },
    
},


}



# 0 / 000 varint

# 2 / 010 string / subBlock with pointer

# 5 / 101 four bytes

