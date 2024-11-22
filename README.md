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

File Rift has two modes: decode and recode. In decode mode, File Rift will convert Swordigo binary files into a custom plain text format, which looks similar to a markup language. In recode mode, File Rift will convert those plain text files back into binary files which can be added to the game. Normally, File Rift will decode the original game files and recode any custom files you give it, however it can decode or recode any Swordigo files you give it.

## Usage
Clone the repo or download a release. Run `FileRiftx.x.py` using Python 3.
```bash
python3 FileRiftx.x.py
```
To change the rift mode, open FileRiftx.x.py in an editor and change the value of the string `rift_mode`. Valid options are `"decode"`, `"recode"` and `"both"`.
All files in `/de_in` are used as input files for the decoder. The folders `all`, `scene` and `scl` are intended for the original game files. Any folders you make will be scanned when rifting, and all output files will be placed in `/de_out`.
All files in `/re_in` are used as input files for the recoder. Any folders you make will be scanned when rifting, and all output files will be placed in `/re_out`.
