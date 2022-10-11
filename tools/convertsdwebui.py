# Read yaml files from sd-webui Stable Diffusion repository
# and embedded into PNG image chunk info

import os
import json
import glob
import time
import datetime
from PIL import Image, PngImagePlugin
import collections

IN_FOLDER = 'D:/Stable Diffusion WebUI/stable-diffusion-webui/outputs'
OUT_FOLDER = 'D:/Stable Diffusion Auto1111/stable-diffusion-webui/outputs/fromsdwebui'

# Gel all files from folder and subfoldres
files = glob.glob(IN_FOLDER + '/**/*.png', recursive=True)

# Get yaml files associated with images
img_dict = {}
for n, image_path in enumerate(files):
    img_param = {}
    infotxt = image_path[:-3] + 'yaml'
    try:
        with open(infotxt) as file:
            yaml = file.readlines()
    except IOError:
        print(f'Yaml file not found: {infotxt}')
        yaml = {}

    # Process yamls files
    img_param = {}
    toggles = ''
    for n, line in enumerate(yaml):
        tag = line.split(' ')[0].strip()
        content = line[len(tag):].strip()
        tag = tag.rstrip(':')
        if tag == 'toggles' or tag == '-':
            if yaml[n + 1].startswith('-'):
                toggles += f'{yaml[n + 1][2:].strip()} '
                continue
        if toggles:
            img_param['toggles'] = toggles.strip()
            toggles = ''
            continue
        img_param[tag] = content

    img_dict[image_path] = img_param

print(img_dict)

# Check for duplicated files
file_check = []
for key in img_dict:
    filename = os.path.basename(key)
    file_check.append(filename)
    print(filename)

if len(file_check) == len(set(file_check)):
    print('No duplicated file names')
else:
    print('Duplicates', len(file_check), len(set(file_check)), len(file_check) - len(set(file_check)))
    print([item for item, count in collections.Counter(file_check).items() if count > 1])

# raise SystemExit(0)

# Copying image with new embedded text
for n, file in enumerate(files, 1):
    # Open file
    im = Image.open(file)

    # Show file name and original embedded information
    print(n)
    print(file)
    print(im.text)

    # Get modification date from original file
    date = os.path.getmtime(file)
    date = datetime.datetime.fromtimestamp(date)
    modTime = time.mktime(date.timetuple())

    # Prepare information to embed
    info = PngImagePlugin.PngInfo()
    info.add_text('sd-webui', json.dumps(img_dict[file]))

    # Save file
    file_name = os.path.basename(file)
    save_file = os.path.join(OUT_FOLDER, file_name)
    im.save(save_file, 'PNG', pnginfo=info)
    im3 = Image.open(save_file)

    # Apply original date to new file
    os.utime(save_file, (modTime, modTime))

    # Show new embedded information
    print(im3.text)
    print()
