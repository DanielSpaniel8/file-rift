# --- block formats for file rift v3.2 and later

# --- for .gopt files




formatList = {

'name' : 'root',

'0a' : {   # music definition
    'name' : 'music definition',
    '0a' : 'name',
    '12' : {
        'name' : 'file',
        '0a' : 'filename',
        '15' : 'u0',
    }
},

'32' : {
    'name' : 'button positions',
    '12' : {
        'name' : 'button',
        '0a' : 'name',
        '1a' : {
            'name' : 'position',
            '0d' : 'left',
            '15' : 'right',
            '1d' : 'bottom',            
            '25' : 'top',
        },
    },
},

'3a' : {
    'name' : 'buttons',
    '12' : {
        'name' : 'button',
        '0a' : 'name',
        '1a' : {
            'name' : 'position',
            '0d' : 'left',
            '15' : 'right',
            '1d' : 'bottom',            
            '25' : 'top',
        },
    }
}

}



# 0 / 000 varint

# 2 / 010 string / subBlock with pointer

# 5 / 101 four bytes

