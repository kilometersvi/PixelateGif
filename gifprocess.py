from PIL import Image
from PIL import GifImagePlugin
import subprocess, os, shutil, imageio, sys, math, time

""""
pixelator gif processor/batch gif processor.
place script into pixelator folder (at same directory as _pixelator_cmd)
to run:
    cd your_pixelator_folder
    for single gif: python gifprocess.py infile outfile <gif|spritesheet> <optional: customizationflags>
    for batch gifs: pthon gifprocess.py indir outdir <gif|spritesheet> <optional: customizationflags>
to generate customizationflags:
    1) run pixelator normally with gif as sourcefile
    2) provide desired adjustments to single preview image
    3) copy the shell command found under View > Shell Command
    4) use everything after "...preview.png" as flags
"""

temp_home = "/dev/shm/gifpix_temp" #ram filesystem
temp_raw = temp_home + "/raw"
temp_processed = temp_home + "/processed"
mode = "gif"

def maketemp():
    os.mkdir(temp_home)
    os.mkdir(temp_raw)
    os.mkdir(temp_processed)

def emptytemp():
    if(not os.path.exists(temp_home)):
        maketemp()
    #empty temp folders
    for the_file in os.listdir(temp_raw):
        file_path = os.path.join(temp_raw, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    for the_file in os.listdir(temp_processed):
        file_path = os.path.join(temp_processed, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def processgif(ingif,outgif,args):
    emptytemp()
    framenumber = 0
    frameduration = 0.1
    frameduration_total = 0
    processed_images = []
    if(mode=="spritesheet"):
        max_sprites_row = 5.0
        tile_width = 0
        tile_height = 0
        spritesheet_width = 0
        spritesheet_height = 0

    #open gif
    im = Image.open(ingif)

    # To iterate through the entire gif
    try:
        while 1:
            print(ingif+": frame "+str(framenumber)+"/"+str(im.n_frames))
            im.seek(framenumber) #update current frame
            frameduration_total += im.info['duration'] #create average duration between frames

            #export frame to temp
            rawname = "raw_"+str(framenumber)+".gif"
            rawdir = os.path.join(temp_raw,rawname)
            im.save(rawdir,"GIF")

            #run pixelator cmd
            processedname = "processed_"+str(framenumber)+".png"
            processeddir = os.path.join(temp_processed,processedname)
            pixelatorcmd = []
            pixelatorcmd.append(str(os.getcwd())+"/_pixelator_cmd.exe")
            pixelatorcmd.append(rawdir)
            pixelatorcmd.append(processeddir)
            for i in range(0,len(args)):
                pixelatorcmd.append(args[i])
            popen = subprocess.Popen(pixelatorcmd, stdout=subprocess.PIPE)
            popen.wait()

            #output = popen.stdout.read()
            #print(output)

            #transparency = im.info['transparency']
            #im.save(processeddir,transparency=transparency)

            #add processed image to collection
            if(mode=="gif"):
                processed_images.append(imageio.imread(processeddir))
            elif(mode=="spritesheet"):
                newim = Image.open(processeddir)
                processed_images.append(newim.getdata())
                newim.close()
            #print("end "+str(framenumber))

            framenumber += 1

    except EOFError:
        pass # end of sequence

    #get avg frame duration
    frameduration = (frameduration_total/framenumber)/10000

    if(mode=="gif"):
        #combine processed frames into gif
        imageio.mimsave(outgif, processed_images, format="GIF",duration=frameduration)
        print("gif converted as "+outgif)
    elif(mode=="spritesheet"):
        #combine processed frames into spritesheet
        #https://minzkraut.com/2016/11/23/making-a-simple-spritesheet-generator-in-python/
        tile_width = processed_images[0].size[0]
        tile_height = processed_images[0].size[1]
        if len(processed_images) > max_sprites_row :
            spritesheet_width = tile_width * max_sprites_row
            required_rows = math.ceil(len(processed_images)/max_sprites_row)
            spritesheet_height = tile_height * required_rows
        else:
            spritesheet_width = tile_width * len(processed_images)
            spritesheet_height = tile_height

        spritesheet = Image.new("RGBA",(int(spritesheet_width), int(spritesheet_height)))
        #spritesheet.save(outgif, "PNG")
        for current_frame in processed_images :
            top = tile_height * math.floor((processed_images.index(current_frame))/max_sprites_row)
            left = tile_width * (processed_images.index(current_frame) % max_sprites_row)
            bottom = top + tile_height
            right = left + tile_width

            box = (left,top,right,bottom)
            box = [int(i) for i in box]
            cut_frame = current_frame.crop((0,0,tile_width,tile_height))

            spritesheet.paste(cut_frame,box)

        spritesheet.save(outgif, "PNG")
        print("gif converted as "+outgif)

    #cleanup
    emptytemp()
    im.close()

if(len(sys.argv)==1):
    print("usage: gifprocess.py infile outfile <gif|spritesheet> --flags")
elif(not os.path.exists(sys.argv[1])):
    print("source not found")
else:
    mode = sys.argv[3]
    print("will output as "+mode)
    if(os.path.isdir(sys.argv[1])):
        print("dir input detected, now batch processing")
        os.mkdir(sys.argv[2])
        for the_file in os.listdir(sys.argv[1]):
            file_path = os.path.join(sys.argv[1], the_file)
            print("file "+file_path)
            try:
                if os.path.isfile(file_path):
                    processgif(file_path,os.path.join(sys.argv[2],"pr_"+the_file),sys.argv[4:])
            except Exception as e:
                print(e)
        print("all gifs processed")
    else:
        processgif(sys.argv[1],sys.argv[2],sys.argv[4:])
