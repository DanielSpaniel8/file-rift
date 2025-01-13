![fr_logo](fileriftlogo0.png)

## Overview
File Rift is a decoder/recoder for Swordigo's Protocol Buffers (pb) files. These files include:
- `*.scene`: level data
- `*.scl`: libraries containing objects that can be used in `.scene` files
- `*.fnt`: font mapping files
- `*.gdata`: definitions for collectibles, spells, quests etc.
- `*.gstate`: default state for newgames
- `*.gopt`: names for music tracks, as well as the default touch controls layout
- `*.sounds`: names for sound effect tracks
- `*.scmap`: in-game map layout
- `*.atlas`: texture mapping files

File Rift has two modes: decode and recode. In decode mode, File Rift will convert Swordigo binary files into a custom plain text format, which looks similar to a markup language. In recode mode, File Rift will convert those plain text files back into binary files which can be added into the game. Normally, File Rift will decode the original game files, however it can decode or recode any Swordigo files you give it.

## Usage
Clone the repo or download a release. Run `FileRiftx.x.py` using Python 3.
```bash
python3 FileRiftx.x.py
```
To change the rift mode, open FileRiftx.x.py in an editor and change the value of the string `rift_mode`. Valid options are `"decode"`, `"recode"`, `"both"` and `"custom"`. `"custom"` mode is the same as decode, but it only searches the `/de_in/custom` folder.  
All files in `/de_in` are used as input files for the decoder. The folders `all`, `scene` and `scl` are intended for the original game files. Any folders you make will be scanned when rifting, and all output files will be placed in `/de_out`.  
All files in `/re_in` are used as input files for the recoder. Any folders you make will be scanned when rifting, and all output files will be placed in `/re_out`.  

## syntax
File Rift decodes files into a custom format, which looks similar to a markup language.

```
# comment
a : 12 # integer
b : 15.9 # float
c : 'abc' # string
d{ # sub-section
    a : 1 # sub-item
}
```

The files are split up into records, with each record following the pattern of tag, delimiter, data.
The tag is the key for a record, and specifies what information that record represents. Tags should be surrounded by whitespace, but not quotes.  
The delimiter can be either `:` or `=`, but it is intirely optional.
There are three main types of record: integer, float and string. These work the same as in pretty much any markup language.

Integers are all decimal digits, no decimal points allowed. `0` `1500`  
Floats may have decimal points, but they don't have to. `0.0` `20`  
Strings are surrounded by single quotes `'` or double quotes `"`.  

## Lua Chunks

scene and scl files often contain Lua chunks, which are represented like this:
```
main_chunk : $
-- some lua here
$end
```

A Lua chunk always comes in a pair, with a 64-bit chunk and a 32-bit copy:
```
lua_chunk{
    main_chunk : $ ... $end    # 64-bit
    secondary_chunk : ''  # 32-bit
}
```
The secondary chunk is always pre-compiled, which makes it practically impossible to edit. This means that mods that utilize Lua chunks usually only work on 64-bit devices. File Rift can compile the main chunk for you, and add the output of the compilation to the secondary chunk. To trigger this, use `@comp`:
```
main_chunk : $ ... $end
secondary_chunk : @comp
```
As File Rift runs through your files, it keeps content of the last chunk, and when it finds `@comp`, it compiles the last chunk and adds it to that record. Be careful, if you use `@comp` in the wrong place, it will add the content of a random chunk to your record.  
> Note: this feature currently only works on Linux.

## Sourcing

File Rift has two methods for bringing the contents of an external file into a recode file. You can source any file in the `/source` folder, and put its contents anywhere in a recode file.
The purpose of the sourcing feature is to make modding a bit faster and easier by moving some parts of a file to an external file, which means you don't have to hunt for the correct line every time you need to make a change.

- `$source`
```
# this example will bring all the fire dragon info from dragons/fire.txt in to dragons.scl

file >> /re_in/dragons.scl:

library_item{
    object{
        $source[dragons/fire.txt]
    }
}
...


file >> /source/dragons/fire.txt:

        name : 'dragon_fire'
        component{
            component_type : 'EntityInfo'
...
```

- `$lua`

`$lua` is the same as the `$source`, but adds a comment with the sourced filename. I usually use it in Lua chunks, hence the name. It doesn't actually have to be used for Lua though.
```
file >> /re_in/dash_mod.scl:

        main_chunk : $
        $lua[dash.lua]
        $end
...


file >> /source/dash.lua:

Scene.Find("hero"):setVelocity(v)
...


 >> recode output:
        main_chunk : $
-- dash.scl
Scene.Find("hero"):setVelocity(v)
...
        $end
...
```

## Templates

The purpose of templates is to make writting re_in files easier by abstracting common things.

Here's how a template looks:
```yaml
# templates/obj.fr
object{
    name : '$1',
    identifier : '$2',
    position{
        x_position : $3,
        y_position : $4,
    }
    z_position : $5,
    rotation : $6,
    scale : $7,
    hidden : 0,
}
```


And this is how you would use that template:
```yaml
$obj[statue_knight; knight1; -256; 128; 0; 0; 1]
```


That would be the same as writing:
```yaml
object{
    name : 'statue_knight',
    identifier : 'knight1',
    position{
        x_position : -256,
        y_position : -128,
    }
    z_position : 0,
    rotation : 0,
    scale : 1,
    hidden : 0,
}
```


Templates are placed in `/templates`. The name of the file defines how it will be referenced, for instance if you name your template file `chunk` or `chunk.fr` it can be referenced as `$chunk[...]`.  
The filename must be made up of lower case letters and dots. Note that the extension .fr will be removed automatically, but not any other extension.  
You can use directories for template files, but the path to the file is not used in the reference, e.g. `/templates/nt/proj/npc` is referenced as `$npc[...]`. This means that `/templates/a` is the same as `/templates/d/a`.  
The template itself just uses a $ dollar sign and one or two decimal digits to indicate things to replace.