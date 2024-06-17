# --- file rift v4 ---

# write output so that it can be interpreted as jsonl

import os
from struct import unpack

def varInt():

    value  = 0   # value of the pointer, to be returned
    offset = 0   # how many bytes were in the varInt, to be advanced later

    b = inbytes[sum(offsets)]
    value = b

    while b > 127:   # continue until lack of continuation bit

        offset +=1
        value -= 128 ** offset   # subtract the value of the last byte's continuation bit

        b = inbytes[sum(offsets) +offset]
        value += b * (128 ** offset)

    offsets[metalevel] += offset +1
    return value

def int32():

    data = inbytes[ sum(offsets) : sum(offsets) +4 ]

    output = unpack('<f', data)[0]   # "<" for little endian, "f" for float. it returns a tuple, so we take the first item

    return str(output)

def handleData():

    global metalevel
    global outLines

    # --- get the tag and detect wire type ---

    tagbyte = varInt()
    tagname = hex(tagbyte)[2:] .zfill(2)

    typeVarInt, typeInt64, typeLen, typeInt32 = False, False, False, False

    typeVarInt = tagbyte %8 == 0   # 000 = 0
    typeInt64  = tagbyte %8 == 1   # 001 = 0
    typeLen    = tagbyte %8 == 2   # 010 = 2
    typeInt32  = tagbyte %8 == 5   # 101 = 5

    form = formats[metalevel]
    
    # --- check for unlisted tags and unnamed blocks ---

    n = 'name'
    formNames = ''
    for i in formats:
        formNames += i[n] + '/'

    if not tagname in form:
        print(f'\nunrecognized tag "{tagname}". offset = {hex(sum(offsets)-1)}\nmetalevel = {metalevel} in file {gameFile.name}\nblock format path = {formNames}')
        quit()

    if not n in formats[metalevel]:
        print(f'\nunnamed / off = {hex(sum(offsets)-1)} / met = {metalevel}\n{formNames}')
        quit()

    # --- handle different wire types ---

    # prepare indentation and subs
    subs = 'sub-' * metalevel
    indent = '\t' * (metalevel)

    if typeVarInt:
        outLines.append(indent+'"'+ form[tagname]+ '" : ' + str(varInt()) + ',\n')

    if typeInt64:
        outLines.append(indent +'"'+form[tagname]+ ' : ' +inbytes[ sum(offsets) : (sum(offsets) +8) ]+ 'i6,' + '\n')
        offsets[metalevel] += 8

    if typeLen:

        pointer = varInt()
        pointers[metalevel] = pointer   # store pointer

        if str(type(form[tagname])) == "<class 'str'>":   # if there is a plain string:
            outLines.append(indent+'"'+form[tagname]+ '" : "' + str(inbytes[ sum(offsets) : sum(offsets) + pointer])[2:-1].replace('\\', '\\\\').replace('"','\\"').replace("'","\\'") +'",\n')
            offsets[metalevel] += pointer

        if str(type(form[tagname])) == "<class 'list'>":   # if there is an alternative action:

            k = form[tagname]

            if k[0] ==0:   # link to another format

                path = []
                path = k[1].rsplit('/')

                thisForm = formats[0]
                for l in path:
                    thisForm = thisForm[l]

                form[tagname] = thisForm

            if k[0] ==1:   # lua chunk
                # remove carriage returns, replace line break and tab representations with the actual character
                chunk = str(inbytes[sum(offsets) : sum(offsets) + pointer])[2:-1].replace('\\r','').replace('\\n', '\n' + indent).replace('\\t','\t').replace('"', '\\"')

                outLines.append(indent+'"'+ form[tagname][1]+ '" : "' + 'chunk >')
                outLines.append(f'\n\n{indent}=== lua =============\n')
                outLines.append(indent + chunk)
                outLines.append(f'\n\n{indent}=====================",\n')

                offsets[metalevel] += pointer
                
        if str(type(form[tagname])) == "<class 'dict'>":   # if there are subblocks:
            brace = ' {'
            outLines.append('\n'+indent +'"'+form[tagname]['name']+subs+'block " : '+brace+'\n\n')
            
            # push and get new format
            metalevel +=1

            formats[metalevel] = form[tagname]
            
    if typeInt32:
        outLines.append((indent+'"'+ form[tagname]+ '" : ' + int32()) +',\n')
        
        offsets[metalevel] +=4



    # --- pop if neccesary and recall handler function ---

    for i in offsets:
        
        if offsets[metalevel] >= pointers[metalevel -1]:   # pop if so

            if metalevel != 0:

                metalevel -=1

                # close curly braces if requested
                tabs = '\t'*metalevel
                outLines.append(tabs+'},'+'\n')

                # reset format
                formats[metalevel+1] = {'name':'-'}

                # reset pointer and offset
                pointers[metalevel +1] = 0

                offsets[metalevel] += offsets[metalevel +1]
                offsets[metalevel +1] = 0


filesDone = 0

outLines = ['']

os.system('clear')

# --- loop through all files and decompile them ---

for folder in os.scandir('./gameFiles'):
    if folder.is_dir():
        for gameFile in os.scandir(folder):

            filesDone +=1

            # --- define starting variables ---

            offsets = [0]*10
            pointers = [0]*10

            metalevel = 0   # how many layers of nested data deep we are

            filetype = gameFile.name.rsplit('.')[-1]

            match filetype:
                case 'scene':
                    from block_formats_scene import formatList
                case 'scl':
                    from block_formats_scl import formatList
                case 'scmap':
                    from block_formats_scmap import formatList
                case 'gdata':
                    from block_formats_gdata import formatList
                case 'gstate':
                    from block_formats_gstate import formatList
                case 'gopt':
                    from block_formats_gopt import formatList
                case 'sounds':
                    from block_formats_sounds import formatList
                    

            inpath = './gameFiles/'+folder.name+'/'+gameFile.name

            formats = [{'name':'-'}]*10
            formats[0] = formatList

            with open(inpath, 'rb') as file:
                inbytes = file.read()

            print('\n----------\n\nfile : ',gameFile.name)

            outLines.append('data = {\n')

            while sum(offsets) < len(inbytes):

                handleData()

            outLines.append('\n}')

            openString = 'x'
            if gameFile.name in os.scandir('./outFilesTesting/'+folder.name):
                openString = 'w'

            with open(('./outFilesTesting/'+folder.name+'/'+gameFile.name+'.jsonl'), 'w') as file:
                for line in outLines:
                    file.write(line)
            
            outLines = []

            print('\n', gameFile.name, ' done')
                
print(f'\n\nfile rift v4 by Daniel Spaniel')
