import os
import glob
import math
import configparser
import tkinter as tk
from tkinter import font
from tkinter import filedialog
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk

# Constants
COL_NBR = 5
ROW_NBR = 5
GRID_IMG_SZ = 100
INFO_IMG_SZ = 250
BUTT_HEIGHT = 26
FONT_NAME = 'Tahoma'
FONT_SIZE = 10
FONT_WEIGHT = 'normal'
BG_COLOR = 'black'
FONT_COLOR = 'teal'
ACC_COLOR1 = 'goldenrod'
ACC_COLOR2 = 'grey70'
ALERT_COLOR = 'dark red'
TOP_PATH = 'D:/Stable Diffusion WebUI/stable-diffusion-webui/outputs/'

FONT = [FONT_NAME, FONT_SIZE, FONT_WEIGHT]

TEXT_TAGS = ['Yaml', 'batch_size:', 'cfg_scale:', 'ddim_eta:', 'ddim_steps:',
             'denoising_strength:', 'height:', 'n_iter:', 'prompt:',
             'resize_mode:', 'sampler_name:', 'seed:', 'target:',
             'toggles:', '-', 'width:', 'real_width:', 'real_height:', 'path']

INFO_SORT = ['Yaml', 'prompt:', 'seed:', 'target:', 'sampler_name:', 'ddim_steps:', 'cfg_scale:',
             'denoising_strength:', 'n_iter:', 'batch_size:', 'ddim_eta:', 'resize_mode:',
             'height:', 'width:', 'real_width:', 'real_height:', 'toggles:', '-', 'path:']

# TOGGLES = {'txt2img': {'0': 'Create prompt matrix', '1': 'Normalize Prompt Weights',
#                        '2': 'Save individual images', '3': 'Save grid',
#                        '4': 'Sort samples by prompt', '5': 'Write samples info files',
#                        '6': 'write sample info to log file', '7': 'jpg samples',
#                        '8': 'Fix faces using GFPGAN', '9': 'Upscale images using RealESRGAN'},
#            'img2img': {'0': 'Create prompt matrix', '1': 'Normalize Prompt Weights',
#                        '2': 'Loopback', '3': 'Random loopback seed', '4': 'Save individual images',
#                        '5': 'Save grid', '6': 'Sort samples by prompt', '7': 'Write sample info files',
#                        '8': 'Write sample info to one file', '9': 'jpg samples',
#                        '10': 'Fix faces using GFPGAN', '11': 'Upscale images using RealESRGAN'}}

# Variable initialization
current_seed = ''
current_image = ''
image_folder = ''

local_path = os.path.split(os.path.abspath(__file__))[0]
ini_path = os.path.join(local_path, 'difbrowser.ini')
config_ini = configparser.ConfigParser()
if os.path.isfile(ini_path):
    try:
        config_ini.read(ini_path)
        config_sec = config_ini['CONFIGS']
        COL_NBR = int(config_sec.get('number_of_columns'))
        ROW_NBR = int(config_sec.get('number_of_lines'))
        GRID_IMG_SZ = int(config_sec.get('grid_image_size'))
        INFO_IMG_SZ = int(config_sec.get('preview_image_size'))
        BUTT_HEIGHT = int(config_sec.get('button_height'))
        FONT_NAME = config_sec.get('font_name')
        FONT_SIZE = int(config_sec.get('font_size'))
        FONT_WEIGHT = config_sec.get('font_weight')
        BG_COLOR = config_sec.get('background_color')
        FONT_COLOR = config_sec.get('main_color')
        ACC_COLOR1 = config_sec.get('accent_color_1')
        ACC_COLOR2 = config_sec.get('accent_color_2')
        ALERT_COLOR = config_sec.get('alert_color')
        TOP_PATH = config_sec.get('default_path')

        FONT = [FONT_NAME, FONT_SIZE, FONT_WEIGHT]

    except (ValueError, configparser.NoOptionError) as e:
        print(f'.INI file problem: {str(e)}')
        raise SystemExit(0)


def Resize_Image(image, maxsize):
    r1 = image.size[0] / maxsize[0]  # width ratio
    r2 = image.size[1] / maxsize[1]  # height ratio
    ratio = max(r1, r2)
    newsize = (int(image.size[0] / ratio), int(image.size[1] / ratio))
    image = image.resize(newsize, Image.Resampling.LANCZOS)
    return image


def _on_mousewheel(event):
    if str(event.widget).split('.')[-1] == 'text_info' \
            or str(event.widget).split('.')[-1] == 'font_list':
        return
    canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')


def _on_click(image_path):
    global image_data
    global current_image
    global current_seed
    global image_folder

    current_image = image_path
    image_folder = os.path.dirname(current_image)

    image_data = Image.open(image_path)
    real_size = image_data.size[0], image_data.size[1]
    image_data = Resize_Image(image_data, (INFO_IMG_SZ, INFO_IMG_SZ))
    image_data = ImageTk.PhotoImage(image_data)
    img_info.config(image=image_data)
    img_info.config(bg=BG_COLOR)

    infotxt = image_path[:-3] + 'yaml'
    try:
        with open(infotxt) as file:
            yaml = file.readlines()
    except IOError:
        yaml = ['Yaml file not found\n']

    yaml.append(f'real_width: {real_size[0]}\n')
    yaml.append(f'real_height: {real_size[1]}\n')
    yaml.append(f'path: {image_path}\n')

    # Give names to toggles.
    # Disabled because they do not respect the
    # toggle number integrity between versions.
    # A new version add a toggle in the middle
    # and all the subsequent names become offset.
    #
    # # Add names to the toggle numbers
    # yaml_tmp = []
    # for line in yaml:
    #     new_line = line
    #     if line.startswith('target:'):
    #         target = line[7:].strip()
    #         CURR_TOGGLE = TOGGLES[target]
    #     if line.startswith('-'):
    #         toggle = line.lstrip('- ').strip()
    #         new_line = f'- {toggle} {CURR_TOGGLE[toggle]}\n'
    #     yaml_tmp.append(new_line)
    # yaml = yaml_tmp

    # Make tag - content tuples for sorting
    yaml_sort = []
    for line in yaml:
        tag = line.split(' ')[0].strip()
        content = line[len(tag):].strip()
        new_line = (tag, content)
        yaml_sort.append(new_line)

    # Sort according to preexisting list
    yaml_sort.sort(key=lambda i: INFO_SORT.index(i[0]))

    # Restore tag - content to string
    yaml = [f"{' '.join(i)}\n" for i in yaml_sort]

    matches = []
    for i, line in enumerate(yaml, 1):
        for tag in TEXT_TAGS:
            if line.startswith(tag):
                start = f'{str(i)}.{len(tag)}'
                end = f'{str(i)}.{len(line)}'
                content = line[len(tag):]
                matches.append((tag, start, end, content))

    text_info['state'] = 'normal'
    text_info.delete('1.0', 'end')
    yaml = ''.join(yaml)
    text_info.insert('insert', yaml)
    for match in matches:
        if match[0].startswith('seed:'):
            current_seed = match[3]
        color = ACC_COLOR2
        if match[3].strip().replace('.', '').isdigit():
            color = ACC_COLOR1
        if match[0].startswith('Yaml'):
            color = ALERT_COLOR
        text_info.tag_add(match[0], match[1], match[2])
        text_info.tag_config(match[0], foreground=color)
    text_info['state'] = 'disable'


def maintain_aspect_ratio(event, aspect_ratio):
    new_aspect_ratio = event.width / event.height
    global image

    if new_aspect_ratio > aspect_ratio:
        desired_width = event.width
        desired_height = int(event.width / aspect_ratio)
    else:
        desired_height = event.height
        desired_width = int(event.height * aspect_ratio)

    if event.width != desired_width or event.height != desired_height:
        try:
            event.widget.geometry(f'{desired_width}x{desired_height}')
            size = (desired_width, desired_height)
            resized = original.resize(size, Image.Resampling.LANCZOS)
            image = ImageTk.PhotoImage(resized)
            c_full_img.delete('IMG')
            c_full_img.create_image(0, 0, image=image, anchor='nw', tags='IMG')
        except AttributeError:
            pass
        return 'break'


def _show_full_image():
    if not current_image:
        return

    global c_full_img
    global original

    image_window = tk.Toplevel()
    image_window.title(f'{current_seed} - {os.path.basename(current_image)}')

    original = Image.open(current_image)

    # Prevent showing images bigger than the screen size
    max_width = min(original.size[0], image_window.winfo_screenwidth())
    max_height = min(original.size[1], image_window.winfo_screenheight())
    original = Resize_Image(original, (max_width, max_height))

    image = ImageTk.PhotoImage(original)

    x = root.winfo_x()
    y = root.winfo_y() + 30 + BUTT_HEIGHT
    dimensions = f'{image.width()}x{image.height()}+{x}+{y}'
    image_window.geometry(dimensions)

    frame = tk.Frame(image_window)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    c_full_img = tk.Canvas(image_window, bd=0, highlightthickness=0)
    c_full_img.create_image(0, 0, image=image, anchor='nw', tags='IMG')
    c_full_img.image = image
    c_full_img.grid(row=0, sticky='news')
    c_full_img.pack(fill='both', expand=1)

    image_window.update()
    width = image_window.winfo_width()
    height = image_window.winfo_height()
    image_window.bind('<Configure>', lambda event: maintain_aspect_ratio(event, width / height))


def update_progress(count, total):
    bar = '#' * int(count / total * 50)
    precent = int(count / total * 100)
    print(f'\rLoading images: [{bar: <49}] {precent}% - {count} of {total}', end='', flush=True)


def new_path():
    global TOP_PATH

    folder_selected = filedialog.askdirectory()
    if not folder_selected:
        return

    TOP_PATH = folder_selected

    reset_interface()


def reset_interface():
    global restart
    global frame_all

    restart = tk.Toplevel()
    x = root.winfo_x() + GRID_IMG_SZ * COL_NBR
    y = root.winfo_y() + 30 + BUTT_HEIGHT
    restart.geometry(f'+{x}+{y}')

    restart.title(f'Restarting')
    restart.resizable(False, False)
    restart_frame = tk.Frame(restart, bg=BG_COLOR)
    restart_frame.pack(expand=True, fill='both')
    loading = tk.Label(restart_frame, bg=BG_COLOR, fg=FONT_COLOR,
                       font=(FONT[0], int(FONT[1] * 1.5), FONT[2]),
                       text='Loading files\nPlease wait')
    loading.pack(pady=20, padx=50)
    loading.update()

    frame_all.destroy()

    main()


def open_config():
    global config
    global conf_entries
    global conf_labels
    global bt_color_list

    config = tk.Toplevel()
    config.title('Configuration')
    config.grab_set()
    config.option_add('*font', FONT)
    config.resizable(False, False)
    x = root.winfo_x() + GRID_IMG_SZ * COL_NBR
    y = root.winfo_y() + 30 + BUTT_HEIGHT
    config.geometry(f'+{x}+{y}')
    config_frame = tk.Frame(config, bg=BG_COLOR)
    config_frame.pack(expand=True, fill='both')

    dummy = tk.Label(config_frame, text=' ', bg=BG_COLOR)
    dummy.grid(row=0)

    config_frame.grid_columnconfigure(0, weight=0)
    config_frame.grid_columnconfigure(1, weight=0)
    config_frame.grid_columnconfigure(1, weight=1)

    conf_cont = [['Number of columns', COL_NBR, None, None],
                 ['Number of rows', ROW_NBR, None, None],
                 ['Gird image size', GRID_IMG_SZ, None, None],
                 ['Preview image size', INFO_IMG_SZ, None, None],
                 ['Button height', BUTT_HEIGHT, None, None],
                 ['Font name', FONT[0], 'get', None, font_requester],
                 ['Font size', FONT[1], 'get', None, font_requester],
                 ['Font weight', FONT[2], 'get', None, font_requester],
                 ['Background color', BG_COLOR, 'pick', BG_COLOR, pick_color],
                 ['Main color', FONT_COLOR, 'pick', FONT_COLOR, pick_color],
                 ['Accent color 1', ACC_COLOR1, 'pick', ACC_COLOR1, pick_color],
                 ['Accent color 2', ACC_COLOR2, 'pick', ACC_COLOR2, pick_color],
                 ['Alert color', ALERT_COLOR, 'pick', ALERT_COLOR, pick_color],
                 ['Default path', TOP_PATH, 'get', None, change_config_path]]

    brd_bt_color_list = []
    bt_color_list = []
    conf_entries = []
    conf_labels = []
    for r, cont in enumerate(conf_cont, 1):
        label = tk.Label(config_frame, text=cont[0], bg=BG_COLOR, fg=FONT_COLOR)
        label.grid(row=r, column=0, sticky='e', padx=(20, 0))
        conf_labels.append(label)

        brd_bt_tbox = tk.Frame(config_frame, bg=BG_COLOR)
        brd_bt_tbox.grid(row=r, column=1, sticky='wens')
        tbox = tk.Entry(brd_bt_tbox, bg=ACC_COLOR1, fg=BG_COLOR, width=30, bd=0, name=str(r),
                        selectbackground=FONT_COLOR, selectforeground=ACC_COLOR2)
        tbox.insert('insert', cont[1])
        tbox.bind('<Return>', lambda event, nbr=r: change_color(nbr))
        tbox.bind('<Tab>', lambda event, nbr=r: change_color(nbr))
        tbox.pack(expand=True, fill='both', pady=1, padx=1)
        conf_entries.append(tbox)

        if cont[2]:
            brd_bt_action = tk.Frame(config_frame, bg=BG_COLOR)
            brd_bt_action.grid(row=r, column=2, sticky='wens')
            action = tk.Button(brd_bt_action, text=cont[2], bd=0,
                               bg=FONT_COLOR, fg=BG_COLOR, activebackground=ACC_COLOR1)
            action.bind('<ButtonRelease-1>', lambda event, func=cont[4], nbr=r: func(nbr))
            action.pack(expand=True, fill='both', pady=1, padx=1)

        if cont[3]:
            brd_bt_color = tk.Frame(config_frame, bg=BG_COLOR)
            brd_bt_color.grid(row=r, column=3, sticky='wens', padx=(0, 20))
            color = tk.Label(brd_bt_color, text='   ', bg=cont[3])
            color.pack(expand=True, fill='both', pady=1, padx=1)
            brd_bt_color_list.append(brd_bt_color)
            bt_color_list.append(color)

    brd_bt_color_list[0]['bg'] = FONT_COLOR
    conf_entries[13].xview_moveto(1)

    btn_frame = tk.Frame(config_frame, bg=BG_COLOR)
    btn_frame.grid(row=r + 1, columnspan=4, sticky='ew', pady=(20, 20))
    btn_frame.grid_columnconfigure(0, weight=1)
    btn_frame.grid_columnconfigure(1, weight=1)

    brd_bt_btn_accept = tk.Frame(btn_frame, bg=BG_COLOR)
    brd_bt_btn_accept.grid(row=0, column=0, sticky='wens', padx=(20, 0))
    btn_accept = tk.Button(brd_bt_btn_accept, text='OK (restart)',
                           bg=FONT_COLOR, fg=BG_COLOR, bd=0, activebackground=ACC_COLOR1)
    btn_accept['command'] = lambda arg=conf_entries: accept_config(arg)
    btn_accept.pack(expand=True, fill='both', pady=1, padx=1)

    brd_btn_cancel = tk.Frame(btn_frame, bg=BG_COLOR)
    brd_btn_cancel.grid(row=0, column=1, sticky='wens', padx=(0, 20))
    btn_cancel = tk.Button(brd_btn_cancel, text='cancel', bd=0, command=cancel_config,
                           bg=FONT_COLOR, fg=BG_COLOR, activebackground=ACC_COLOR1)
    btn_cancel.pack(expand=True, fill='both', pady=1, padx=1)


def change_config_path(r):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        conf_entries[r - 1].delete(0, 'end')
        conf_entries[r - 1].insert('insert', folder_selected)
        conf_entries[r - 1].xview_moveto(1)


def change_color(r):
    if r < 9 or r > 13:
        return
    try:
        bt_color_list[r - 9]['bg'] = conf_entries[r - 1].get()
    except tk.TclError:
        conf_entries[r - 1].delete(0, 'end')
        conf_entries[r - 1].insert('insert', 'Invalid color')


def pick_color(r):
    conf_entries[r - 1].delete(0, 'end')
    color = askcolor(title=conf_labels[r - 1]['text'])[1]
    conf_entries[r - 1].insert('insert', color)
    change_color(r)


def cancel_config():
    config.destroy()


def accept_config(conf_entries):
    global COL_NBR
    global ROW_NBR
    global GRID_IMG_SZ
    global INFO_IMG_SZ
    global BUTT_HEIGHT
    global FONT
    global BG_COLOR
    global FONT_COLOR
    global ACC_COLOR1
    global ACC_COLOR2
    global ALERT_COLOR
    global TOP_PATH

    COL_NBR = int(conf_entries[0].get())
    ROW_NBR = int(conf_entries[1].get())
    GRID_IMG_SZ = int(conf_entries[2].get())
    INFO_IMG_SZ = int(conf_entries[3].get())
    BUTT_HEIGHT = int(conf_entries[4].get())
    FONT = (conf_entries[5].get(),
            int(conf_entries[6].get()),
            conf_entries[7].get())
    BG_COLOR = bt_color_list[0]['bg']
    FONT_COLOR = bt_color_list[1]['bg']
    ACC_COLOR1 = bt_color_list[2]['bg']
    ACC_COLOR2 = bt_color_list[3]['bg']
    ALERT_COLOR = bt_color_list[4]['bg']
    TOP_PATH = conf_entries[13].get()

    FONT_NAME = FONT[0]
    FONT_SIZE = FONT[1]
    FONT_WEIGHT = FONT[2]

    if not config_ini.has_section('CONFIGS'):
        config_ini.add_section('CONFIGS')
    config_ini.set('CONFIGS', 'number_of_columns', str(COL_NBR))
    config_ini.set('CONFIGS', 'number_of_lines', str(ROW_NBR))
    config_ini.set('CONFIGS', 'grid_image_size', str(GRID_IMG_SZ))
    config_ini.set('CONFIGS', 'preview_image_size', str(INFO_IMG_SZ))
    config_ini.set('CONFIGS', 'button_height', str(BUTT_HEIGHT))
    config_ini.set('CONFIGS', 'font_name', FONT_NAME)
    config_ini.set('CONFIGS', 'font_size', str(FONT_SIZE))
    config_ini.set('CONFIGS', 'font_weight', FONT_WEIGHT)
    config_ini.set('CONFIGS', 'background_color', BG_COLOR)
    config_ini.set('CONFIGS', 'main_color', FONT_COLOR)
    config_ini.set('CONFIGS', 'accent_color_1', ACC_COLOR1)
    config_ini.set('CONFIGS', 'accent_color_2', ACC_COLOR2)
    config_ini.set('CONFIGS', 'alert_color', ALERT_COLOR)
    config_ini.set('CONFIGS', 'default_path', TOP_PATH)

    with open(ini_path, 'w') as configfile:
        config_ini.write(configfile)

    config.destroy()

    reset_interface()


def font_requester(r):
    global font_box
    global font_pick
    global available_fonts
    global size_entry
    global font_temp
    global font_req

    font_temp = FONT

    font_req = tk.Toplevel()
    font_req.title('Font')

    available_fonts = font.families()

    font_box = tk.Listbox(font_req, highlightthickness=0, relief='flat', name='font_list',
                          bg=ACC_COLOR1, fg=BG_COLOR, selectbackground=FONT_COLOR)
    font_box.grid(row=0, columnspan=3, sticky='news')
    font_box.option_add('*font', FONT)

    config.grab_release()
    font_req.grab_set()

    for fonts in available_fonts:
        font_box.insert('end', fonts)

    font_box.bind("<ButtonRelease-1>",
                  lambda e: change_font([available_fonts[font_box.curselection()[0]],
                                         int(size_entry.get()),
                                         font_temp[2]]))

    weight_list = []
    brd_norm_butt = tk.Frame(font_req, bg=BG_COLOR)
    brd_norm_butt.grid(row=1, column=0, sticky='nsew')
    norm_butt = tk.Button(brd_norm_butt, text="N", bg=FONT_COLOR, fg=BG_COLOR,
                          font=(FONT[0], FONT[1], 'normal'), activebackground=ACC_COLOR1,
                          bd=0, command=lambda: font_weight(0, weight_list))
    norm_butt.pack(expand=True, fill='both', pady=1, padx=1)
    weight_list.append([norm_butt, 'normal'])

    brd_norm_bold = tk.Frame(font_req, bg=BG_COLOR)
    brd_norm_bold.grid(row=1, column=1, sticky='nsew')
    bold_butt = tk.Button(brd_norm_bold, text="B", bg=FONT_COLOR, fg=BG_COLOR,
                          font=(FONT[0], FONT[1], 'bold'), activebackground=ACC_COLOR1,
                          bd=0, command=lambda: font_weight(1, weight_list))
    bold_butt.pack(expand=True, fill='both', pady=1, padx=1)
    weight_list.append([bold_butt, 'bold'])

    brd_norm_ital = tk.Frame(font_req, bg=BG_COLOR)
    brd_norm_ital.grid(row=1, column=2, sticky='nsew')
    ital_butt = tk.Button(brd_norm_ital, text="I", bg=FONT_COLOR, fg=BG_COLOR,
                          font=(FONT[0], FONT[1], 'italic'), activebackground=ACC_COLOR1,
                          bd=0, command=lambda: font_weight(2, weight_list))
    ital_butt.pack(expand=True, fill='both', pady=1, padx=1)
    weight_list.append([ital_butt, 'italic'])

    size_entry = tk.Entry(font_req, text="cancel", bd=0, bg=ACC_COLOR1, fg=BG_COLOR)
    size_entry.delete(0, 'end')
    size_entry.insert('insert', FONT[1])
    size_entry.bind('<Return>', lambda e: change_font([font_temp[0],
                                                       int(size_entry.get()),
                                                       font_temp[2]]))
    size_entry.bind('<Tab>', lambda e: change_font([font_temp[0],
                                                    int(size_entry.get()),
                                                    font_temp[2]]))
    size_entry.grid(row=2, column=0, columnspan=3, sticky='nsew')
    size_entry.grid(row=2, column=0, columnspan=3, sticky='nsew')

    brd_ok_butt = tk.Frame(font_req, bg=BG_COLOR)
    brd_ok_butt.grid(row=3, column=0, columnspan=2, sticky='nsew')
    ok_butt = tk.Button(brd_ok_butt, text="OK", bd=0, bg=FONT_COLOR, fg=BG_COLOR,
                        activebackground=ACC_COLOR1, command=accept_font)
    ok_butt.pack(expand=True, fill='both', pady=1, padx=1)

    brd_cancel_butt = tk.Frame(font_req, bg=BG_COLOR)
    brd_cancel_butt.grid(row=3, column=2, columnspan=2, sticky='nsew')
    cancel_butt = tk.Button(brd_cancel_butt, text="cancel", bd=0, bg=FONT_COLOR, fg=BG_COLOR,
                            activebackground=ACC_COLOR1, command=cancel_font)
    cancel_butt.pack(expand=True, fill='both', pady=1, padx=1)

    font_pick = tk.Label(font_req, text="Diffusion", bg=BG_COLOR, fg=FONT_COLOR, font=(FONT[0], FONT[1], FONT[2]))
    font_pick.grid(row=4, columnspan=3, sticky='nsew')

    font_req.resizable(False, False)
    font_req.geometry(f'+{config.winfo_x()}+{config.winfo_y()}')


def accept_font():
    conf_entries[5].delete(0, 'end')
    conf_entries[5].insert('insert', font_temp[0])
    conf_entries[6].delete(0, 'end')
    conf_entries[6].insert('insert', font_temp[1])
    conf_entries[7].delete(0, 'end')
    conf_entries[7].insert('insert', font_temp[2])
    config.grab_set()
    font_req.destroy()


def cancel_font():
    config.grab_set()
    font_req.destroy()


def font_weight(weight, weight_list):
    global font_temp
    for item in weight_list:
        item[0]['bg'] = FONT_COLOR
        item[0]['fg'] = BG_COLOR

    weight_list[weight][0]['bg'] = BG_COLOR
    weight_list[weight][0]['fg'] = FONT_COLOR

    font_temp[2] = weight_list[weight][1]
    font_temp[1] = int(size_entry.get()),

    change_font(font_temp)


def change_font(font_arg):
    global font_temp
    font_temp = font_arg
    font_pick.config(font=font_temp)


def copy_to_clipboard():
    root.clipboard_append(TOP_PATH)
    root.update()


def open_image_folder():
    if not image_folder:
        return
    os.startfile(image_folder)


def open_folder():
    os.startfile(TOP_PATH)


def copy_text(event):
    try:
        root.clipboard_clear()
        root.clipboard_append(text_info.selection_get())
    except tk.TclError:
        return


# Main interface
def main():

    global canvas
    global img_info
    global text_info
    global frame_all

    root.option_add('*font', FONT)

    # Get images from the path
    files = glob.glob(TOP_PATH + '/**/*.png', recursive=True)
    image_amount = len(files)
    image_rows = math.ceil(image_amount / COL_NBR)

    # Frame to hold the entire interface
    frame_all = tk.Frame(root, bg=BG_COLOR)
    frame_all.pack(fill=None, expand=False)

    # Top frame for labels and buttons
    frame_top = tk.Frame(frame_all, bg=BG_COLOR, height=BUTT_HEIGHT)
    frame_top.grid(row=0, column=0, sticky='news')
    frame_top.grid_propagate(False)

    frame_top.grid_columnconfigure(0, weight=1)
    frame_top.grid_columnconfigure(1, weight=0)

    # Top left sub frame for labels
    frame_top_l = tk.Frame(frame_top, bg=BG_COLOR, height=BUTT_HEIGHT)
    frame_top_l.grid(row=0, column=0, sticky='ewns')

    frame_top_l.grid_columnconfigure(0, weight=0)
    frame_top_l.grid_columnconfigure(1, weight=1)

    # Top right sub frame for buttons
    frame_top_r = tk.Frame(frame_top, height=BUTT_HEIGHT, width=250, bg=BG_COLOR)
    frame_top_r.grid(row=0, column=1, sticky='ewns')
    frame_top_r.grid_propagate(False)

    frame_top_r.grid_columnconfigure(0, weight=1)
    frame_top_r.grid_columnconfigure(1, weight=1)
    frame_top_r.grid_columnconfigure(2, weight=1)

    # Number of files label, top left frame
    lbl_files = tk.Label(frame_top_l,
                         bg=BG_COLOR, fg=ACC_COLOR1,
                         text=f'{image_amount} images')
    lbl_files.grid(row=0, column=0, sticky='w')

    # Current path label, top left frame
    lbl_path = tk.Button(frame_top_l,
                         bg=BG_COLOR, fg=FONT_COLOR, bd=0, command=copy_to_clipboard,
                         activeforeground=ACC_COLOR1, activebackground=BG_COLOR,
                         text=TOP_PATH, anchor='e', justify='right')
    lbl_path.grid(row=0, column=1, sticky='w')

    # Path button, top right frame
    brd_bt_path = tk.Frame(frame_top_r, bg=BG_COLOR)
    brd_bt_path.grid(row=0, column=0, sticky='snwe')
    butt_path = tk.Button(brd_bt_path, text='path', bd=0, command=new_path,
                          bg=FONT_COLOR, fg=BG_COLOR, activebackground=ACC_COLOR1)
    butt_path.pack(expand=True, fill='both', pady=1, padx=1)

    # Explorer button, top right frame
    brd_bt_open = tk.Frame(frame_top_r, bg=BG_COLOR)
    brd_bt_open.grid(row=0, column=1, sticky='snwe')
    butt_open = tk.Button(brd_bt_open, text='explorer', bd=0, command=open_folder,
                          bg=FONT_COLOR, fg=BG_COLOR, activebackground=ACC_COLOR1)
    butt_open.pack(expand=True, fill='both', pady=1, padx=1)

    # Config button, top right frame
    brd_bt_conf = tk.Frame(frame_top_r, bg=BG_COLOR)
    brd_bt_conf.grid(row=0, column=2, sticky='snwe')
    butt_conf = tk.Button(brd_bt_conf, text='config', bd=0, command=open_config,
                          bg=FONT_COLOR, fg=BG_COLOR, activebackground=ACC_COLOR1)
    butt_conf.pack(expand=True, fill='both', pady=1, padx=1)

    # Frame for the grid and info
    frame_main = tk.Frame(frame_all, bg=BG_COLOR)
    frame_main.grid(sticky='news')
    frame_main.grid(row=1, column=0, sticky='nw')

    # Frame for the info
    info_frame = tk.Frame(frame_main, bg=BG_COLOR,
                          width=INFO_IMG_SZ, height=GRID_IMG_SZ * ROW_NBR)
    info_frame.grid(row=0, column=1, sticky='nw')

    # Button to show the selected image
    img_info = tk.Button(info_frame, bg=FONT_COLOR, fg=BG_COLOR, activebackground=ACC_COLOR1,
                         text='Diffusion\nBrowser', font=(FONT[0], FONT[1] * 3, 'bold'),
                         borderwidth=0, command=_show_full_image)
    img_info.place(x=0, y=0, height=INFO_IMG_SZ, width=INFO_IMG_SZ)

    # Text box to show the selected image info
    text_info_height = GRID_IMG_SZ * ROW_NBR - INFO_IMG_SZ - BUTT_HEIGHT
    text_info = tk.Text(info_frame, name='text_info',
                        bg=BG_COLOR, fg=FONT_COLOR,
                        selectbackground=FONT_COLOR, selectforeground=BG_COLOR,
                        borderwidth=0, padx=10, pady=10)
    text_info.bind('<ButtonRelease-1>', copy_text)
    text_info.insert('insert', 'Diffusion Browser v1.0\n'
                               'github.com/farique1/diffusion-browser\n'
                               '(c) Fred Rique 2022\n\n'
                               'For Stable Diffusion ds-webui\n'
                               'github.com/sd-webui')
    text_info.place(x=0, y=INFO_IMG_SZ, height=text_info_height, width=INFO_IMG_SZ)
    text_info['state'] = 'disable'

    # Button to open folder containing image
    brd_bt_folder = tk.Frame(info_frame, bg=BG_COLOR)
    brd_bt_folder.place(x=0, y=text_info_height + INFO_IMG_SZ, height=BUTT_HEIGHT, width=INFO_IMG_SZ)
    butt_folder = tk.Button(brd_bt_folder, text='explorer', bd=0, command=open_image_folder,
                            bg=FONT_COLOR, fg=BG_COLOR, activebackground=ACC_COLOR1)
    butt_folder.pack(expand=True, fill='both', pady=1, padx=1)

    # Frame for the image grid
    frame_canvas = tk.Frame(frame_main, bg=BG_COLOR)
    frame_canvas.grid(row=0, column=0, sticky='nw')
    frame_canvas.grid_rowconfigure(0, weight=1)
    frame_canvas.grid_columnconfigure(0, weight=1)
    frame_canvas.grid_propagate(False)

    # Add a canvas in that frame
    canvas = tk.Canvas(frame_canvas, bg=BG_COLOR, borderwidth=0, highlightthickness=0)
    canvas.bind_all('<MouseWheel>', _on_mousewheel)
    canvas.grid(row=0, column=0, sticky='news')

    # Create a frame to contain the buttons
    frame_buttons = tk.Frame(canvas, bg=BG_COLOR)
    canvas.create_window((0, 0), window=frame_buttons, anchor='nw')

    # Link a scrollbar to the canvas
    vsb = tk.Scrollbar(frame_canvas, orient='vertical', command=canvas.yview)
    vsb.grid(row=0, column=1, sticky='ns')
    canvas.configure(yscrollcommand=vsb.set)

    # Add buttons to the frame
    rows = image_rows
    columns = COL_NBR
    image_path = [['' for j in range(columns)] for i in range(rows)]
    buttons = [[tk.Button() for j in range(columns)] for i in range(rows)]
    c = 0
    for i in range(0, rows):
        for j in range(0, columns):
            if c >= image_amount:
                break
            image_path[i][j] = files[c]
            originalImg1 = Image.open(image_path[i][j])
            originalImg1 = Resize_Image(originalImg1, (GRID_IMG_SZ, GRID_IMG_SZ))
            img1 = ImageTk.PhotoImage(originalImg1)

            buttons[i][j] = tk.Button(frame_buttons, image=img1, relief='flat',
                                      highlightthickness=0, borderwidth=0, activebackground=ACC_COLOR1)
            buttons[i][j]['command'] = lambda arg=image_path[i][j]: _on_click(arg)
            buttons[i][j].image = img1
            buttons[i][j].grid(row=i, column=j)
            c += 1
            update_progress(c, image_amount)

    # Update buttons frames idle tasks to let tkinter calculate buttons sizes
    frame_buttons.update_idletasks()

    # Resize the canvas and frame
    grid_width = (COL_NBR * GRID_IMG_SZ) + vsb.winfo_width()
    grid_height = ROW_NBR * GRID_IMG_SZ
    frame_canvas.config(width=grid_width, height=grid_height)

    # Set the canvas scrolling region
    canvas.config(scrollregion=canvas.bbox('all'))

    # Avoud error if not resetting the interface
    try:
        restart.destroy()
    except NameError:
        pass

    # Launch the GUI
    root.mainloop()


root = tk.Tk()
root.title('Diffusion Browser')
root.resizable(False, False)

main()
