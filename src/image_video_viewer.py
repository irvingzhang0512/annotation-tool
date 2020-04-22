import os
import cv2
import PySimpleGUI as sg

# 一些固定不变的参数
IMAGE_SIZE = (512, 512)  # 展示的图像大小
DEFAULT_TIMEOUT = 50  # 展示视频时的timeout
IMG_TYPES = (".png", ".jpg", "jpeg", ".tiff", ".bmp")  # 支持的图像类型
VIDEO_TYPES = (".mp4", ".avi")  # 支持的视频类型
LISTBOX_FILTER_FILE_PATH = "/ssd4/zhangyiyang/temporal-shift-module/data/filter.txt"

# GUI 相关内容
image_elem = sg.Image(data=None, size=IMAGE_SIZE)
filename_display_elem = sg.Text("No Folder Selected Yet", size=(80, 1))
file_num_display_elem = sg.Text('No Folder Selected Yet.')
file_listbox = sg.Listbox(values=[], change_submits=True,
                          size=(50, 50), key='listbox')
layout = [
    [
        sg.InputText('/ssd4/zhangyiyang/data/jester-v1/20bn-jester-v1', size=(80, 1),
                     change_submits=True, key="dir"),
        sg.FolderBrowse(),
        sg.Radio('Image', "Radio",
                 change_submits=True, key="radio_image"),
        sg.Radio('Video/File', "Radio",
                 change_submits=True, key="radio_video_file"),
        sg.Radio('Video/Dir', "Radio", default=True,
                 change_submits=True, key="radio_video_dir"),
    ],
    [
        sg.Column([
            [file_listbox],
            [
                sg.Button('Prev', size=(8, 2)),
                sg.Button('Next', size=(8, 2)),
                file_num_display_elem
            ]
        ]),
        sg.Column([
            [filename_display_elem],
            [image_elem]
        ])
    ]
]
window = sg.Window('Image/Video Viewer', layout,
                   default_element_size=(40, 1),
                   grab_anywhere=False,
                   return_keyboard_events=True,
                   location=(0, 0), )
print("window created.")

# 整体框架的timeout
# 当timeout为None时，表示展示图像或展示视频结束，图像保持不变
# 当timeout为DEFAULT_TIMEOUT时，表示展示视频，一帧一帧往后展示
timeout = None

# 展示视频相关的全局变量
radio_video1_cap = None
radio_video1_idx = -1
radio_video2_idx = -1
radio_video2_fnames = []

# listbox 相关全局变量
fnames = []
cur_listbox_id = -1


def _is_video(file_path):
    return file_path.lower().endswith(VIDEO_TYPES)


def _is_image(file_path):
    return file_path.lower().endswith(IMG_TYPES)


def _is_dir(file_path):
    return os.path.isdir(file_path)


def _update_listbox(values):
    # 改变 values['dir'] 时或改变 radio时调用
    # 作用就是更新 listbox 中的文件列表
    # 如果文件列表不为空，则默认选择第一个文件作为默认选项
    global fnames
    global cur_listbox_id
    cur_path = values['dir']
    if values['radio_image']:
        if_fn = _is_image
    elif values['radio_video_file']:
        if_fn = _is_video
    else:
        if_fn = _is_dir
    flist = os.listdir(cur_path)
    fnames = [f for f in flist if if_fn(os.path.join(cur_path, f))]
    if os.path.exists(LISTBOX_FILTER_FILE_PATH):
        with open(LISTBOX_FILTER_FILE_PATH, 'r') as f:
            file_names = f.readlines()
        file_names = [l.strip() for l in file_names]
        if len(file_names) > 0:
            fnames = [f for f in fnames if f in file_names]
    fnames.sort()
    if len(fnames) == 0:
        cur_listbox_id = None
    else:
        cur_listbox_id = 0
    file_listbox.Update(fnames, set_to_index=cur_listbox_id)


def _update_image(values):
    # 展示GUI中的图像
    # 分为三种情况，即radio中的三个选项：Image, Video/File, Video/Dir

    def _do_update_image_frame(frame, resize_size=IMAGE_SIZE):
        frame = cv2.resize(frame, resize_size)
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()
        image_elem.update(data=imgbytes)

    def _update_image_radio_image(values):
        img_path = os.path.join(values['dir'], file_listbox.get()[0])
        frame = cv2.imread(img_path)
        _do_update_image_frame(frame)

    def _update_image_radio_video1(values):
        global radio_video1_idx
        flag, frame = radio_video1_cap.read()
        radio_video1_idx += 1
        filename_display_elem.Update(
            "{} selected, {}/{}".format(
                file_listbox.get()[0],
                radio_video1_idx,
                radio_video1_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        )
        if not flag:
            global timeout
            timeout = None
            radio_video1_cap.release()
            return
        _do_update_image_frame(frame)

    def _update_image_radio_video2(values):
        global radio_video2_idx
        # 目标文件夹中没有图片
        if len(radio_video2_fnames) == 0:
            image_elem.Update(None)
            filename_display_elem.Update(
                "{} selected, no images in this directory")
            return

        filename_display_elem.Update("{} selected, {}/{}, {}".format(
            file_listbox.get()[0],
            radio_video2_idx + 1,
            len(radio_video2_fnames),
            radio_video2_fnames[radio_video2_idx]
        ))

        # 当展示到最后一张图片
        if radio_video2_idx + 1 == len(radio_video2_fnames):
            global timeout
            timeout = None
            return

        # 展示普通图片
        img_path = os.path.join(
            values['dir'],
            file_listbox.get()[0],
            radio_video2_fnames[radio_video2_idx])
        frame = cv2.imread(img_path)
        _do_update_image_frame(frame)
        radio_video2_idx += 1

    # 上面定义了三种情况如何展示图像
    # 下面是展示图像的基本流程

    if len(fnames) == 0:
        # 如果没有listbox中没有文件
        filename_display_elem.Update("No available files in target directory")
        return

    if values['radio_image']:
        _update_image_radio_image(values)
        filename_display_elem.Update(
            "{} selected.".format(file_listbox.get()[0]))
    elif values['radio_video_file']:
        _update_image_radio_video1(values)
    else:
        _update_image_radio_video2(values)


def _update_showing_params(values):
    # 当改变展示文件（即listbox中的选项）/展示文件类型（即radio）后调用
    # 主要作用就是修改全局变量的数值，为调用 _update_image 做准备
    global radio_video1_cap
    global radio_video1_idx
    global radio_video2_fnames
    global radio_video2_idx
    global timeout

    # 首先将所有全局变量赋值为初始状态
    timeout = None
    if radio_video1_cap is not None:
        try:
            radio_video1_cap.release()
        except:
            pass
        radio_video1_cap = None
    radio_video2_fnames = []
    radio_video2_idx = -1
    radio_video1_idx = -1

    # 如果listbox中没有可展示的内容，就直接退出
    if len(file_listbox.get()) == 0:
        filename_display_elem.Update("No available file exists.")
        return

    # 根据radio改变全局变量参数值
    if values['radio_video_file']:
        timeout = DEFAULT_TIMEOUT
        radio_video1_idx = 0
        radio_video1_cap = cv2.VideoCapture(
            os.path.join(values['dir'], file_listbox.get()[0])
        )
    elif values['radio_video_dir']:
        timeout = DEFAULT_TIMEOUT
        radio_video2_idx = 0
        radio_video2_fnames = os.listdir(
            os.path.join(values['dir'], file_listbox.get()[0]))
        radio_video2_fnames = [
            f for f in radio_video2_fnames
            if _is_image(os.path.join(values['dir'],
                                      file_listbox.get()[0], f))
        ]
        radio_video2_fnames.sort()


def _update_file_num_text(values):
    # 更新 listbox 描述文本
    # 在改变listbox（包括改变dir或radio）、改变listbox中的选中项时调用

    # listbox 如果没有文件
    if len(fnames) == 0:
        file_num_display_elem.Update("No Files in Target Directory.")
        return

    # 更新文本
    file_num_display_elem.Update(
        "{}, {}/{}".format(fnames[cur_listbox_id],
                           cur_listbox_id + 1,
                           len(fnames)))


while True:
    event, values = window.read(timeout=timeout)
    # print(event, values)

    if event == 'Exit' or event is None:
        # 关闭窗口
        break
    elif event == 'dir':
        # 改变路径
        if not os.path.isdir(values['dir']):
            continue
        _update_listbox(values)
        _update_file_num_text(values)
        _update_showing_params(values)
    elif str(event).startswith("radio"):
        # 改变展示数据类型
        if not os.path.isdir(values['dir']):
            continue
        _update_listbox(values)
        _update_file_num_text(values)
        _update_showing_params(values)
    elif event == 'listbox':
        # 选择listbox中的文件

        if len(file_listbox.get()) != 0:
            # 如果已经选择了文件，则更新listbox_id
            cur_listbox_id = fnames.index(file_listbox.get()[0])
        _update_file_num_text(values)
        _update_showing_params(values)
    elif event in ['Next', 'Down:104']:
        # 键盘右/下，改变listbox中的选中文件
        file_listbox.set_focus()
        if cur_listbox_id < len(fnames) - 1:
            cur_listbox_id += 1
            file_listbox.Update(set_to_index=cur_listbox_id)
            _update_file_num_text(values)
        _update_showing_params(values)
    elif event in ['Prev', 'Up:98']:
        # 键盘左/上，改变listbox中的选中文件
        file_listbox.set_focus()
        if cur_listbox_id > 0:
            cur_listbox_id -= 1
            file_listbox.Update(set_to_index=cur_listbox_id)
            _update_file_num_text(values)
        _update_showing_params(values)

    # 展示图像
    _update_image(values)


window.close()
