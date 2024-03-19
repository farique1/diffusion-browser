# Read log.html files from the Fooocus repository
# and embedded into the PNG image chunk info

import os
import json
import glob
import time
import datetime
from collections import OrderedDict
from PIL import Image, PngImagePlugin

IN_FOLDER = 'D:\\Fooocus_win64_2-1-791\\Fooocus\\teste'
OUT_FOLDER = 'D:\\Fooocus_win64_2-1-791\\Converted'

# Parameters with "( )" to remove
SETS = ('styles', 'resolution', 'adm guidance')

# Gel all subfolders from output folder
folders = glob.glob(IN_FOLDER + '\\*\\', recursive=True)


def process_html(html):
    def get_key_value(line):
        try:
            key_start = line.index("class='key'>")
            key_end = line.index('</td><td ')
            value_start = line.index("class='value'>")
            value_end = line.index('</td></tr>')
        except ValueError:
            return None, None

        key = line[key_start + 12:key_end].lower()
        value = line[value_start + 14:value_end].lower()

        if key in SETS:
            value = value[1:-1]
        if key == 'resolution':
            value = value.replace(', ', ' x ')
        if key[:4] == 'lora':
            key = (f'lora name {lora_numb}', f'lora weight {lora_numb}')
            lora_value = value.split(' : ')
            value = (lora_value[0], lora_value[1])

        return key, value

    images_dict = {}
    html_list = html.split('\n\n')[1:-1]

    print('HTML data')
    print()

    for block in html_list:
        block_list = block.split('\n')
        parameters_dict = OrderedDict()
        lora_numb = 1

        for line in block_list:
            if line.startswith('<td><a href="'):
                start = len('<td><a href="')
                end = line.index('" target=')
                print(f'-> {line[start:end]}')
                image = line[start:end]

            key, value = get_key_value(line)

            if type(key) is tuple:
                print(f'{key[0]}: {value[0]}')
                print(f'{key[1]}: {value[1]}')
                parameters_dict[key[0]] = value[0]
                parameters_dict[key[1]] = value[1]
                lora_numb += 1
            elif key:
                print(f'{key}: {value}')
                parameters_dict[key] = value

        print()
        images_dict[image] = parameters_dict

    return images_dict


# Gett all PNG file names in the subfolders
folder_files = []
for folder in folders:
    pngs = glob.glob(folder + '*.png', recursive=True)
    folder_files.append([folder, pngs])

# Process HTML files on each folder
folders_dict = {}

for folder in folder_files:
    log_file = folder[0] + '\\log.html'
    try:
        with open(log_file) as file:
            html = file.read()
    except IOError:
        print(f'*** log.html not found on folder: {folder[0]}')
        continue

    # Parse HTML and create folder dictionary
    images_dict = process_html(html)

    # Add to the main dictionary
    folders_dict[folder[0]] = images_dict


# Copying image with new embedded text
for i, folder in enumerate(folders_dict, 1):
    print('Compiled data')
    print()
    print('Folder')
    print(folder)
    print()

    for n, file in enumerate(folders_dict[folder], 1):
        file_w_path = os.path.join(folder, file)

        # Open file
        try:
            im = Image.open(file_w_path)
        except FileNotFoundError:
            print(f'*** Image not found: {file_w_path}')
            continue

        # Show file name and original embedded information
        print(f'-> {file}')

        # Get modification date from original file
        date = os.path.getmtime(file_w_path)
        date = datetime.datetime.fromtimestamp(date)
        modTime = time.mktime(date.timetuple())

        # Prepare information to embed
        info = PngImagePlugin.PngInfo()
        info.add_text('Fooocus', json.dumps(folders_dict[folder][file]))

        print('- Prepared data')
        print(json.dumps(folders_dict[folder][file]))

        # Save file
        file_name = os.path.basename(file)
        save_file = os.path.join(OUT_FOLDER, file)
        im.save(save_file, 'PNG', pnginfo=info)
        im3 = Image.open(save_file)

        # Apply original date to new file
        os.utime(save_file, (modTime, modTime))

        # Show new embedded information
        print('- Embedded data')
        print(im3.text)
        print()
