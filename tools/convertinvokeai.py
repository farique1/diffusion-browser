# Read log files from invoke-ai Stable Diffusion repository
# and embedded into PNG image chunk info

import os
import json
import glob
import time
import datetime
from PIL import Image, PngImagePlugin

CMD_LOG = 'D:/SD-Backups/img-samples/dream_log.txt'
WEB_LOG = 'D:/SD-Backups/img-samples/dream_web_log.txt'

CDM_KEYS = {'-s': 'steps',
            '-W': 'width',
            '-H': 'height',
            '-C': 'cfgscale',
            '-A': 'sampler',
            '-S': 'seed',
            '-ID:': 'initimg',
            '-f': 'strength',
            '--grid': 'grid',
            '-N': 'batch'}

IN_FOLDER = 'D:/SD-Backups/img-samples'
OUT_FOLDER = 'D:/Stable Diffusion Auto1111/stable-diffusion-webui/outputs/frominvokeai2'

# Get image information from command line log file
try:
    with open(CMD_LOG) as file:
        log = file.readlines()
except IOError:
    log = ['Log file not found\n']
    raise SystemExit(0)

# Process image information
img_dict = {}
for line in log:
    img_param = {}
    image_file = line.split(':')[0]
    image_file = os.path.basename(image_file)
    prompt = line.split('"')[1]
    arguments = line.split('"')[2]
    arguments = arguments.strip().split(' ')
    img_param['prompt'] = prompt
    for a in arguments:
        for k in CDM_KEYS:
            if a.startswith(k):
                key = CDM_KEYS[k]
                content = a[len(k):]
                if k == '-ID:':
                    content = os.path.basename(content)
                img_param[key] = content
    img_dict[image_file] = (img_param, 'invoke-ai command line')

# Get image information from web interface log file
try:
    with open(WEB_LOG) as file:
        log = file.readlines()
except IOError:
    log = ['Log file not found\n']
    raise SystemExit(0)

# Process image information
for line in log:
    img_param = {}
    image_file = line.split(':')[0]
    image_file = os.path.basename(image_file)
    line_split = line.find(':') + 1
    line_dict = line[line_split:]
    line_dict = json.loads(line_dict)
    for k in line_dict:
        content = line_dict[k]
        if k == 'seed' and line_dict[k] == '-1':
            content = image_file.split('.')[1]
        img_param[k] = content.lower()
    img_dict[image_file] = (img_param, 'invoke-ai web interface')

# Show processed information
for img in img_dict:
    print(img)
    print(img_dict[img])
    print()

# Get and show file list
folder_list = glob.glob(f'{IN_FOLDER}/*.png')
print(folder_list)

# Copy images with new embedded text
for n, file in enumerate(folder_list, 1):

    # Open file
    im = Image.open(file)

    # Get modification date from original file
    date = os.path.getmtime(file)
    date = datetime.datetime.fromtimestamp(date)
    modTime = time.mktime(date.timetuple())

    # Show file name and original embedded information
    file_name = os.path.basename(file)
    print(n)
    print(file_name)
    print(im.text)

    # Prepare information to embed
    info = PngImagePlugin.PngInfo()
    info.add_text(img_dict[file_name][1], json.dumps(img_dict[file_name][0]))

    # Save file
    save_file = os.path.join(OUT_FOLDER, file_name)
    im.save(save_file, 'PNG', pnginfo=info)
    im3 = Image.open(save_file)

    # Apply original date to new file
    os.utime(save_file, (modTime, modTime))

    # Show new embedded information
    print(im3.text)
    print()
