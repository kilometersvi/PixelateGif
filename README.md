# PixelateGif
Applies pixelate effect to a gif, and allows exporting as either gif or spritesheet. Intended for use in Unity game development. 
Requires Pixelator. Find it here: http://pixelatorapp.com/
Only tested on Linux UBuntu 18.04

to install:

place script into pixelator folder (at same directory level as _pixelator_cmd)

to run:

    cd your_pixelator_folder
    
    for single gif: python gifprocess.py infile outfile <gif|spritesheet> <optional: customizationflags>
    
    for batch gifs: pthon gifprocess.py indir outdir <gif|spritesheet> <optional: customizationflags>
    
to generate customizationflags:

    1) run pixelator normally with gif as sourcefile
    
    2) provide desired adjustments to single preview image
    
    3) copy the shell command found under View > Shell Command
    
    4) use everything after "...preview.png" as flags
