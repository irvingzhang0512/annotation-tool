import os
import cv2
import argparse
import logging


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--ffmpeg", action="store_true", default=False)
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--tmp-video", type=str,
                        default="./test-categoried.avi")

    # input video path
    parser.add_argument("--category-file-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/category.txt")
    parser.add_argument("--src-videos-dir", type=str,
                        default="/ssd4/zhangyiyang/data/AR/videos/4-28")

    # to_frames_dir
    parser.add_argument("--to-frames-dir", type=str,
                        default="/ssd4/zhangyiyang/data/AR/raw_to_frames")
    parser.add_argument("--img-prefix", type=str, default="{:05d}.jpg")

    # to_labels.txt
    parser.add_argument("--to-labels-file-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/append-5-9.txt")
    parser.add_argument("--to-labels-file-append", action="store_true")

    return parser.parse_args()


def _convert_fps(source_fps, target_fps):
    assert source_fps >= target_fps, "source fps must larger than target fps"

    interval = int(source_fps * 1.0 / target_fps)
    return [i*interval for i in range(int(source_fps/interval))]


def _handle_single_video(
        video_path,  # 输入视频绝对路径
        cur_idx,  # 当前视频对应编号
        to_label_file,  # TSM标签文件 writer，用于构建 to_label.txt
        category_id,  # 当前视频代表的行为类别编号
        args):
    logging.info("start handling {}".format(video_path))
    if not os.path.exists(video_path):
        logging.warn("{} doesn't exist.".format(video_path))
        return

    # 构建输出帧的路径
    cur_frames_dir = os.path.join(args.to_frames_dir, str(cur_idx))
    if not os.path.exists(cur_frames_dir):
        os.mkdir(cur_frames_dir)

    # ffmpeg 提取帧
    if args.ffmpeg:
        # {:06d}.jpg -> %06d.jpg
        fmt = args.img_prefix.replace("{", "") \
            .replace("}", "").replace(":", "%")
        cmd = 'ffmpeg -i "{}" -threads 1 -vf scale=-1:256 -q:v 0 "{}/{}"'\
            .format(video_path, cur_frames_dir, fmt)
        os.system(cmd)
        to_label_file.write(cur_frames_dir +
                            " " + str(len(os.listdir(cur_frames_dir))) +
                            " " + str(category_id) + "\n")
        return

    # opencv 提取帧

    # 转换输入视频格式
    cmd = "ffmpeg -i {} -q:v 6 {}".format(video_path, args.tmp_video)
    if os.path.exists(args.tmp_video):
        os.remove(args.tmp_video)
    os.system(cmd)
    cap = cv2.VideoCapture(args.tmp_video)
    source_fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 有一个问题需要处理：
    # 输入视频文件的fps和我们需要的fps是不同的
    # 一般来说，视频的fps大于我们需要的fps
    # 所以，需要在视频的fps中选择我们需要的若干帧图像
    # 下面这个函数就是选择的帧的编号
    ids = _convert_fps(source_fps, args.fps)

    # 分别读取每一帧，然后分别处理
    id = -1
    file_name_id = 0
    frame_cnt = 0
    while True:
        flag, frame = cap.read()
        if not flag:
            break
        frame_cnt += 1
        id += 1
        if id >= source_fps:
            id = 0

        if id in ids:
            # 如果当前帧需要保存，则要保存到目标文件夹中
            file_name_id += 1
            img_name = args.img_prefix.format(file_name_id)
            cv2.imwrite(os.path.join(cur_frames_dir, img_name), frame)
    to_label_file.write(cur_frames_dir + " " + str(file_name_id) +
                        " " + str(category_id) + "\n")
    cap.release()
    if os.path.exists(args.tmp_video):
        os.remove(args.tmp_video)


def _get_start_id(cur_dir):
    max_id = 0
    for file_name in os.listdir(cur_dir):
        try:
            idx = int(file_name)
            max_id = max(idx, max_id)
        except:
            pass
    return max_id + 1


def main(args):
    # 初始化TSM格式的标签文件
    if args.to_labels_file_append:
        to_file = open(args.to_labels_file_path, "a")
    else:
        to_file = open(args.to_labels_file_path, "w")

    with open(args.category_file_path, "r") as f:
        categories = f.readlines()
    categories = [c.replace("\n", "") for c in categories]
    category_to_id = {c: idx for idx, c in enumerate(categories)}

    # tp_idx = 0
    cur_idx = _get_start_id(args.to_frames_dir)
    for category in categories:
        video_dir_path = os.path.join(args.src_videos_dir, category)
        if not os.path.isdir(video_dir_path):
            continue
        # 依次遍历每类视频
        videos = os.listdir(video_dir_path)
        videos = [os.path.join(video_dir_path, v) for v in videos]

        for video_path in videos:
            # 依次遍历每类视频中的每个视频文件
            _handle_single_video(video_path,
                                 cur_idx,
                                 to_file,
                                 category_to_id[category],
                                 args)
            cur_idx += 1

    to_file.close()


if __name__ == '__main__':
    main(_parse_args())
