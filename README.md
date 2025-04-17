<h3 align="center">
    <img src="fileriftlogo0.png" alt="fr_logo" width="300">
</h3>

## Overview
File Rift is a decoder/recoder for Swordigo's Protocol Buffers (pb) files. These files include:
- `*.scene`: level data
- `*.scl`: libraries containing objects that can be used in `.scene` files
- `*.fnt`: font mapping files
- `*.gdata`: definitions for collectibles, spells, quests etc.
- `*.gstate`: default state for newgames
- `*.gplayer`: savegames
- `*.gopt`: names for music tracks, as well as the default touch controls layout
- `*.sounds`: names for sound effect tracks
- `*.scmap`: in-game map layout
- `*.atlas`: texture mapping files

File Rift has two modes: decode and recode. In decode mode, File Rift will convert Swordigo binary files into a custom plain text format, which looks similar to a markup language. In recode mode, File Rift will convert those plain text files back into binary files which can be added into the game. Normally, File Rift will decode the original game files, however it can decode or recode any Swordigo files you give it.

## Usage
Clone the repo or download a release. Run `FileRift.py` using Python 3.
```bash
python3 FileRift.py
```
To change the rift mode, open config.py in an editor and change the value of the string `rift_mode`. Valid options are `"decode"`, `"recode"`, `"both"` and `"user"`. `"user"` mode is the same as decode, but it only searches the `/de_in/user` folder.  
All files in `/de_in` are used as input files for the decoder. The folders `all`, `scene` and `scl` are intended for the original game files. Any folders you make will be scanned when rifting, and all output files will be placed in `/de_out`.  
All files in `/re_in` are used as input files for the recoder. Any folders you make will be scanned when rifting, and all output files will be placed in `/re_out`.  

To get a list of command line flags, use `python3 FileRift.py --help`. Example output:

```bash
usage: FileRift [-h] [-r] [-d] [-u] [-b] [-f] [-a] [-i INFO] [-p PATH] [-n]

options:
  -h, --help            show this help message and exit
  -r, --recode          Run in recode mode
  -d, --decode          Run in decode mode
  -u, --user            Decode file in /de_in/user, unless otherwise specified
  -b, --both            Run in decode then recode mode
  -f, --force           Run in recode mode with allways_recode turned on
  -a, --audit           Ask before recoding each directory in re_out
  -i INFO, --info INFO  Ask before recoding each directory in re_out
  -p PATH, --path PATH  Recode a file for a given filepath
  -n, --no-colour       Disable output colouring
```

When recoding, Rift will check the contents of every file against a checksum stored in `lib/.manifest`. If the checksum matches, the file will be skipped, saving a lot of time when recoding. To turn off this behaviour, use the `--force` flag, or set `allways_recode` to True in `config.py`.

## Configuration

Configuring FileRift is done using `config.py`. Most of the settings have comments explaining them.

## Syntax
File Rift decodes files into a custom format, which looks similar to a markup language.

```
# comment
a : 12 # integer
b : 15.9 # float
c : 'abc' # string
d{ # message
    a : 1
}
```

The files are split up into records, with each record a tag and some data.
The tag is the key for a record, and specifies what information that record represents. Tags should be surrounded by whitespace, but not quotes.  
There are four main types of record: integer, float, string and message. The first three work the same as in pretty much any markup language, and messages simply contain other records.
If you put a `d` after a float, it will be automatically converted from degrees to radians. `90d`

Integers are all decimal digits, no decimal points allowed. `0` `1500`  
Floats may have decimal points, but they don't have to. `0.0` `20`  
Strings are surrounded by single quotes `'` or double quotes `"`.  
Messages begin and end with braces. `{}`

## Lua Chunks

scene and scl files often contain Lua chunks, which are represented like this:
```
String : $
-- some lua here
$end
```

A Lua chunk always comes in a pair, with a 64-bit chunk and a 32-bit copy:
```
Program{
    String : $ ... $end    # 64-bit
    Bytes : ''  # 32-bit
}
```
The Bytes chunk is always pre-compiled, which makes it practically impossible to edit. This means that mods which utilize Lua chunks usually only work on 64-bit devices. File Rift can compile the String chunk for you, and add the output of the compilation to the secondary chunk. To trigger this, use `@compile` or `@comp`:
```
String : $ ... $end
Bytes : @comp
```
As File Rift runs through your files, it keeps content of the last chunk, and when it finds `@comp`, it compiles the last chunk and adds it to that record. Be careful, if you use `@comp` in the wrong place, it will add the content of a random chunk to your record.  
> Note: this feature currently only works on Linux.

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

## Tag Info

Tag info helps you to write Swordigo files quickly, by showing what record tags are allowed in a message. Run rift with the `-i` flag, and pass a block_formats path like so:

```
python3 FileRift.py -i scene/Object/Position

Position (message)
   0d : X (float)
   15 : Y (float)
```

This tells you that the Position Message contains two records, `X` and `Y`, both floats.
You can also pass a filename and line number like this:

```
python3 FileRift.py -i re_in/testing/beyond_graveyard.scene:4

Object (message)
   0a : TemplateName (str)  [optional] reference to a template to initialize the object from
   12 : Identifier (str)  used to refer to this object
   1a : Component (message)
   22 : Position (message)
   2d : Depth (float)
   35 : Rotation (float)
   3d : Scaling (float)
   42 : LocalAabb (message)
   48 : Hidden (int)
   52 : OnLoad (message)
```

## Template Info

Calling Rift with the `-i` flag and a template name preceded by a dot will print all the comments at the start of the template file, which typically contain the documentation for the template:

```
python3 FileRift.py -i .obj

usage: [name;ident;x_pos;y_pos;z_pos;rot;scale]
add an object instance with the provided details
```
