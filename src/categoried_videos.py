import os
import cv2
import shutil
import argparse
import logging
from flip_utils import flip_samples


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--categoried-base-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/categoried/0428")
    parser.add_argument("--videos-dir-name", type=str, default="videos")
    parser.add_argument("--ffmpeg", action="store_true", default=False)
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--tmp-video", type=str,
                        default="./test-categoried.avi")
    parser.add_argument("--category-file-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/category.txt")

    # to labels 相关
    parser.add_argument("--to-frames-dir-name", type=str, default="frames")
    parser.add_argument("--to-labels-file-name",
                        type=str, default="to_label.txt")
    parser.add_argument("--to-labels-file-append", action="store_true")
    parser.add_argument("--global-to-labels-dir", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/summary")
    parser.add_argument("--img-format", type=str, default="{:05d}.jpg")

    # flip
    parser.add_argument("--flip", action="store_true")
    parser.add_argument("--flip-frames-dir-name", type=str,
                        default="flip_frames")
    parser.add_argument("--flip-to-labels-file-name",
                        type=str, default="flip_to_label.txt")

    return parser.parse_args()


def _convert_fps(source_fps, target_fps):
    assert source_fps >= target_fps, "source fps must larger than target fps"

    interval = int(source_fps * 1.0 / target_fps)
    return [i*interval for i in range(int(source_fps/interval))]


def _handle_single_video(video_path,  # 输入视频绝对路径
                         cur_idx,  # 当前视频对应编号
                         to_label_file,  # TSM标签文件 writer，用于构建 to_label.txt
                         category_id,  # 当前视频代表的行为类别编号,
                         ffmpeg,  # 是否使用 ffmpeg 来提取帧
                         cur_frames_dir,  # frames 保存路径
                         img_format,
                         fps,
                         tmp_video,
                         ):
    logging.info("start handling {}".format(video_path))
    if not os.path.exists(video_path):
        logging.warn("{} doesn't exist.".format(video_path))
        return

    # ffmpeg 提取帧
    if ffmpeg:
        # {:06d}.jpg -> %06d.jpg
        fmt = img_format.replace("{", "") \
            .replace("}", "").replace(":", "%")
        raw_cmd = [
            'ffmpeg',
            '-i', '{}',
            '-r', '{}',
            '-threads 1 -vf scale=-1:256 -q:v 0',
            '"{}/{}"'
        ]
        cmd = (" ".join(raw_cmd))\
            .format(video_path, fps, cur_frames_dir, fmt)
        os.system(cmd)
        to_label_file.write(cur_frames_dir +
                            " " + str(len(os.listdir(cur_frames_dir))) +
                            " " + str(category_id) + "\n")
        return

    # opencv 提取帧

    # 转换输入视频格式
    cmd = "ffmpeg -i {} -q:v 6 {}".format(video_path, tmp_video)
    if os.path.exists(tmp_video):
        os.remove(tmp_video)
    os.system(cmd)
    cap = cv2.VideoCapture(tmp_video)
    source_fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 有一个问题需要处理：
    # 输入视频文件的fps和我们需要的fps是不同的
    # 一般来说，视频的fps大于我们需要的fps
    # 所以，需要在视频的fps中选择我们需要的若干帧图像
    # 下面这个函数就是选择的帧的编号
    ids = _convert_fps(source_fps, fps)

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
            img_name = img_format.format(file_name_id)
            cv2.imwrite(os.path.join(cur_frames_dir, img_name), frame)
    to_label_file.write(cur_frames_dir + " " + str(file_name_id) +
                        " " + str(category_id) + "\n")
    cap.release()
    if os.path.exists(tmp_video):
        os.remove(tmp_video)


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
    # 1. 构建相关文件夹路径，并验证
    src_videos_dir = os.path.join(
        args.categoried_base_path,
        args.videos_dir_name,
    )
    assert os.path.exists(src_videos_dir)
    to_frames_dir = os.path.join(
        args.categoried_base_path,
        args.to_frames_dir_name,
    )
    if not os.path.exists(to_frames_dir):
        os.makedirs(to_frames_dir)
    cur_idx = _get_start_id(to_frames_dir)

    # 2. 获取类别信息
    with open(args.category_file_path, "r") as f:
        categories = f.readlines()
    categories = [c.replace("\n", "") for c in categories]
    category_to_id = {c: idx for idx, c in enumerate(categories)}

    # 3. 获取 to labels 文件，并以此遍历每个子文件夹
    to_labels_file_path = os.path.join(
        args.categoried_base_path,
        args.to_labels_file_name,
    )
    if args.to_labels_file_append:
        to_file = open(to_labels_file_path, "a")
    else:
        to_file = open(to_labels_file_path, "w")
    for category in categories:
        # 依次遍历每类视频
        video_dir_path = os.path.join(src_videos_dir, category)
        if not os.path.isdir(video_dir_path):
            continue
        for video_name in os.listdir(video_dir_path):
            cur_frames_dir = os.path.join(to_frames_dir, str(cur_idx))
            if not os.path.exists(cur_frames_dir):
                os.mkdir(cur_frames_dir)
            _handle_single_video(
                os.path.join(video_dir_path, video_name),  # 输入视频绝对路径
                cur_idx,  # 当前视频对应编号
                to_file,  # TSM标签文件 writer，用于构建 to_label.txt
                category_to_id[category],  # 当前视频代表的行为类别编号,
                args.ffmpeg,  # 是否使用 ffmpeg 来提取帧
                cur_frames_dir,  # frames 保存路径
                args.img_format,
                args.fps,
                args.tmp_video,
            )
            cur_idx += 1
    to_file.close()

    # 3. flip
    if args.flip:
        flip_to_frames_dir = os.path.join(
            args.categoried_base_path,
            args.flip_frames_dir_name,
        )
        if not os.path.exists(flip_to_frames_dir):
            os.makedirs(flip_to_frames_dir)
        flip_samples(
            to_labels_file_path,
            os.path.join(args.categoried_base_path,
                         args.flip_to_labels_file_name),
            flip_to_frames_dir
        )

    # 4. 复制 to label 文件到to-labels-file-path
    shutil.copy(to_labels_file_path,
                os.path.join(args.global_to_labels_dir,
                             os.path.basename(args.categoried_base_path)
                             + "_categoried_to_labels.txt"))
    if args.flip:
        shutil.copy(to_labels_file_path,
                    os.path.join(args.global_to_labels_dir,
                                 os.path.basename(args.categoried_base_path)
                                 + "_categoried_flip_to_labels.txt"))


if __name__ == '__main__':
    main(_parse_args())
