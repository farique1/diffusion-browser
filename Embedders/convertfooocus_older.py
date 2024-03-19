# Read log.html files from the Fooocus repository
# and embedded into the PNG image chunk info

import os
import json
import glob
import time
import datetime
from collections import OrderedDict
from html.parser import HTMLParser
from PIL import Image, PngImagePlugin

SETS = ('styles', 'resolution', 'adm guidance')

parameters_dict = OrderedDict()
folders_dict = {}

IN_FOLDER = 'D:\\Fooocus_win64_2-1-791\\Fooocus\\outputs'
OUT_FOLDER = 'D:\\Fooocus_win64_2-1-791\\Converted'

# Gel all subfolders from output folder
folders = glob.glob(IN_FOLDER + '\\*\\', recursive=True)


# Create a subclass and override the handler methods for the HTML parser
class MyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.newimage = ''
        self.attr_name = ''
        self.lora_numb = 1

    # Get image name from the DIV tag. Each DIV has one image parameters
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.newimage = attrs[0][1][:-4] + '.png'
            self.lora_numb = 1

    # If DIV tag is closed, add parameters dict to the folder dict
    def handle_endtag(self, tag):
        global parameters_dict
        if tag == 'div':
            folders_dict[self.newimage] = parameters_dict
            parameters_dict = {}

    # Get data from HTML
    def handle_data(self, data):
        if data.strip() == '' and self.attr_name != '':
            self.get_data(self.attr_name, data)

        if data.strip() != '':
            if data.strip()[-1] == ':':
                self.attr_name = data
            else:
                self.get_data(self.attr_name, data)

    # Custom method, add parameter to parameters dictionary
    def get_data(self, name, data):
        name = name.strip(', ').strip(':').lower()
        data = data.strip(', ')
        if name in SETS:
            data = data[1:-1]
        if name == 'resolution':
            data = data.replace(', ', ' x ')
        if name[:4] == 'lora':
            lora = name[6:-9]
            parameters_dict[f'lora {self.lora_numb}'] = lora
            name = f'weight {self.lora_numb}'
            self.lora_numb += 1
        if name:
            parameters_dict[name] = data
            self.attr_name = ''


parser = MyHTMLParser()

# Gett all PNG file names in the subfolders
files = []
for folder in folders:
    pngs = glob.glob(folder + '*.png', recursive=True)
    files.append([folder, pngs])

# Process HTML files on each folder
images_dict = {}
for folder in files:
    log_file = folder[0] + '\\log.html'
    try:
        with open(log_file) as file:
            html = file.read()
    except IOError:
        print(f'log.html not found on folder: {folder[0]}')
        continue

    # Parse HTML and create folder dictionary
    parser.feed(html)

    # Add to the main dictionary
    images_dict[folder[0]] = folders_dict

    folders_dict = {}

    # images_dict[folder[0]] = parameters_dict

# for i, folder in enumerate(images_dict):
#     print(i, folder)
#     for n, file in enumerate(images_dict[folder]):
#         print(n, os.path.join(folder, file))
#         print(json.dumps(images_dict[folder][file]))
#         print()
#     print()
#     print()
#     print()

# raise SystemExit(0)

# Copying image with new embedded text
for i, folder in enumerate(images_dict, 1):
    print()
    print(folder)
    for n, file in enumerate(images_dict[folder], 1):
        file_w_path = os.path.join(folder, file)

        # Open file
        try:
            im = Image.open(file_w_path)
        except FileNotFoundError:
            print('*** Image not found:', file_w_path)
            continue

        # Show file name and original embedded information
        print(file)

        # Get modification date from original file
        date = os.path.getmtime(file_w_path)
        date = datetime.datetime.fromtimestamp(date)
        modTime = time.mktime(date.timetuple())

        # Prepare information to embed
        info = PngImagePlugin.PngInfo()
        info.add_text('Fooocus', json.dumps(images_dict[folder][file]))

        print(json.dumps(images_dict[folder][file]))

        # Save file
        file_name = os.path.basename(file)
        save_file = os.path.join(OUT_FOLDER, file)
        im.save(save_file, 'PNG', pnginfo=info)
        im3 = Image.open(save_file)

        # Apply original date to new file
        os.utime(save_file, (modTime, modTime))

        # Show new embedded information
        print(im3.text)
        print()
