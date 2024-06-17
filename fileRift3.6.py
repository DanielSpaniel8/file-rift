# --- file rift v3.6 ---

# display code chunks properly

import os
from struct import unpack
from pygments import highlight
from pygments.lexers import LuaLexer
from pygments.formatters import Terminal256Formatter

from riftOptions import writeOutPut, enclose, colourize, delimiter, indentLevel, techInfo, techHex

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
        print(f'\n{cr +tagname} / off = {hex(sum(offsets)-1)} / met = {metalevel} / file = {gameFile.name}\n{cg +formNames} / files done = {filesDone}')
        quit()

    if not n in formats[metalevel]:
        print(f'\n{cr}unnamed / off = {hex(sum(offsets)-1)} / met = {metalevel}\n{formNames}')
        quit()

    # --- handle different wire types ---

    # prepare indentation and subs
    subs = 'sub-' * metalevel
    indent = ' ' * (indentLevel*metalevel)

    tech = ''
    if techInfo:
        tech = f'{cdb}({tagname} @ {hex( sum(offsets) )[2:]}){cg}'
        if not techHex:
            tech = f'{cdb}({int(tagname) // 8}@{sum(offsets)}){cg}'

    if typeVarInt:
        if writeOutPut:
            outLines.append(indent+ form[tagname]+ delimiter + str(varInt()) + tech + '\n')
        else:
            print(f'{indent+ cG +form[tagname]+ cg} : {str(varInt())} {tech}')

    if typeInt64:
        if writeOutPut:
            outLines.append(indent +form[tagname]+ delimiter +inbytes[ sum(offsets) : (sum(offsets) +8) ]+ 'i6' +tech+ '\n')
        else:
            print(f'{indent+ cG +form[tagname]+ cg} : {inbytes[ sum(offsets) : (sum(offsets) +8) ]} i6 {tech}')
        offsets[metalevel] += 8

    if typeLen:

        pointer = varInt()
        pointers[metalevel] = pointer   # store pointer

        if str(type(form[tagname])) == "<class 'str'>":   # if there is a plain string:
            if writeOutPut:
                outLines.append(indent+ form[tagname]+ delimiter + str(inbytes[ sum(offsets) : sum(offsets) + pointer])[2:-1] +' '+tech+ '\n')
            else:
                print(indent+ cG +form[tagname]+ cg + delimiter + str(inbytes[ sum(offsets) : sum(offsets) + pointer])[2:-1] + ' ' +tech)
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
                chunk = str(inbytes[sum(offsets) : sum(offsets) + pointer])[2:-1].replace('\\r','').replace('\\n', '\n' + indent).replace('\\t','\t') 

                if colourize:
                    chunk = highlight(chunk, LuaLexer(), Terminal256Formatter())

                if writeOutPut:
                    outLines.append(indent+ form[tagname][1]+ delimiter + 'chunk >')
                    outLines.append(f'\n\n{indent}=== lua =============\n')
                    outLines.append(indent + chunk)
                    outLines.append(f'\n\n{indent}=====================\n')
                else:
                    print(indent+ cG + form[tagname][1]+ cg + delimiter + cy + 'chunk >')
                    print(cg+f'\n\n{indent}=== lua =============\n')
                    print(indent + chunk)
                    print(   f'\n\n{indent}=====================\n')

                offsets[metalevel] += pointer
                
        if str(type(form[tagname])) == "<class 'dict'>":   # if there are subblocks:
            brace = ''
            if enclose:
                brace = cc+' {'+cg
            if writeOutPut:
                outLines.append(f"\n{indent}{form[tagname]['name']} {subs}block{brace} {tech}\n\n")
            else:
                print(f"\n{cy +indent}{form[tagname]['name']} {cg +subs}block{brace} {tech}\n")
            
            # push and get new format
            metalevel +=1

            formats[metalevel] = form[tagname]
            
    if typeInt32:
        # print(f'{indent+ cG +form[tagname]+ cg} : {inbytes[ sum(offsets) : sum(offsets) +4 ]} i3')
        if writeOutPut:
            outLines.append((indent+ form[tagname]+ delimiter + int32()) +' '+tech+ '\n')
        else:
            print(indent+ cG +form[tagname]+ cg + delimiter + int32() +' '+tech)
        offsets[metalevel] +=4



    # --- pop if neccesary and recall handler function ---

    for i in offsets:
        
        if offsets[metalevel] >= pointers[metalevel -1]:   # pop if so

            if metalevel != 0:

                # print(f'{cr}pop {offsets[metalevel]} / {pointers[metalevel -1]}{cg}')#--- debugging

                metalevel -=1

                # close curly braces if requested
                if writeOutPut:
                    if enclose:
                        tabs = '\t'*metalevel
                        outLines.append(tabs+'}'+'\n')
                    else:
                        outLines.append('\n')

                else:
                    if enclose:
                        tabs = ' '* (metalevel*indentLevel)
                        print(tabs+cc+'}'+cg)
                    else:
                        print()

                # reset format
                formats[metalevel+1] = {'name':'-'}

                # reset pointer and offset
                pointers[metalevel +1] = 0

                offsets[metalevel] += offsets[metalevel +1]
                offsets[metalevel +1] = 0

    # print(f'{cr +str(metalevel)+ cg} : offset {hex(sum(offsets))}\n{offsets}\n{pointers}')#--- debugging
    

# --- define colours

cg, cG, cc, cr, cy, cdb = '','','','','',''
if colourize:
    cg = '\033[0;37m'
    cG = '\033[1;32m'
    cc = '\033[1;36m'
    cr = '\033[3;31m'
    cy = '\033[1;33m'
    cdb = '\033[2;34m'

filesDone = 0

outLines = ['']

os.system('clear')

# --- loop through all files and decompile them ---

for folder in os.scandir('./gameFiles'):
    if folder.is_dir():
        for gameFile in os.scandir(folder):

            # if j.name in skipFiles:
                # continue

            # if gameFile.name[-3:] != 'scl':
            # if gameFile.name[-3:] == 'scl' or gameFile.name[-5:] == 'scene':
                # continue
            
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

            print(cG,'\n----------\n\nfile : ',cg,gameFile.name)

            while sum(offsets) < len(inbytes):

                handleData()

            openString = 'x'
            if gameFile.name in os.scandir('./outFiles/'+folder.name):
                openString = 'w'

            with open(('./outFiles/'+folder.name+'/'+gameFile.name), 'w') as file:
                for line in outLines:
                    file.write(line)
            
            outLines = []

            print('\n', gameFile.name, ' done')
                
print(f'\n\n{cG}file rift {cr}v3.6{cg} by {cG}Daniel Spaniel{cg}')