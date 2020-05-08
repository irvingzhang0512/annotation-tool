import os

from image_video_viewer import LISTBOX_FILTER_FILE_PATH


def _do_filter(loader_file,
               target_ids=[],  # 选择需要的category id
               target_frames_folder=None,  # 选择需要的frames dir
               ):
    with open(loader_file, "r") as f:
        lines = [l.strip() for l in f.readlines()]

    # 设置目标标签
    ids = []
    for line in lines:
        splits = line.split(" ")
        if int(splits[2]) in target_ids:
            if target_frames_folder is None \
                    or os.path.dirname(splits[0]) == target_frames_folder:
                ids.append(os.path.basename(splits[0]))
    with open(LISTBOX_FILTER_FILE_PATH, 'w') as f:
        f.writelines("\n".join(ids))


if __name__ == '__main__':
    jester_categories = [
        "Doing other things",  # 0
        "Drumming Fingers",  # 1
        "No gesture",  # 2
        "Pulling Hand In",  # 3
        "Pulling Two Fingers In",  # 4
        "Pushing Hand Away",  # 5
        "Pushing Two Fingers Away",  # 6
        "Rolling Hand Backward",  # 7
        "Rolling Hand Forward",  # 8
        "Shaking Hand",  # 9
        "Sliding Two Fingers Down",  # 10
        "Sliding Two Fingers Left",  # 11
        "Sliding Two Fingers Right",  # 12
        "Sliding Two Fingers Up",  # 13
        "Stop Sign",  # 14
        "Swiping Down",  # 15
        "Swiping Left",  # 16
        "Swiping Right",  # 17
        "Swiping Up",  # 18
        "Thumb Down",  # 19
        "Thumb Up",  # 20
        "Turning Hand Clockwise",  # 21
        "Turning Hand Counterclockwise",  # 22
        "Zooming In With Full Hand",  # 23
        "Zooming In With Two Fingers",  # 24
        "Zooming Out With Full Hand",  # 25
        "Zooming Out With Two Fingers"  # 26
    ]
    jester_target_ids = []
    jester_loader_file = "/ssd4/zhangyiyang/data/jester-v1/train_videofolder.txt"
    jester_target_frames_folder = None
    _do_filter(
        jester_categories, jester_loader_file,
        jester_target_ids, jester_target_frames_folder,
    )

    ar_catigories = [
        "nothing",  # 0
        "other",  # 1
        "close",  # 2
        "left",  # 3
        "right",  # 4
        "ok",  # 5
    ]
    ar_target_ids = []
    ar_loader_file = "/ssd4/zhangyiyang/data/AR/label/flip_total.txt"
    ar_target_frames_folder = "/ssd4/zhangyiyang/data/AR/flip_frames"
    _do_filter(
        ar_catigories, ar_loader_file,
        ar_target_ids, ar_target_frames_folder,
    )
