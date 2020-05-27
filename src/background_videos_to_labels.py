import os
import cv2
import shutil
import argparse
from flip_utils import flip_samples

cur_frames_cnt = 0


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--nothing-label-id", type=int, default=0)

    parser.add_argument("--background-base-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/background/0527")
    parser.add_argument("--videos-dir-name", type=str, default="videos")
    parser.add_argument("--frames-per-sample", type=int, default=40)
    parser.add_argument("--img-format", type=str, default="{:05d}.jpg")
    parser.add_argument("--tmp-video", type=str,
                        default="./test-bg.avi")

    # to labels 相关
    parser.add_argument("--to-frames-dir-name", type=str, default="frames")
    parser.add_argument("--to-labels-file-name",
                        type=str, default="to_label.txt")
    parser.add_argument("--to-labels-file-append", action="store_true")
    parser.add_argument("--global-to-labels-dir", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/summary")

    # flip
    parser.add_argument("--flip", action="store_true")
    parser.add_argument("--flip-frames-dir-name", type=str,
                        default="flip_frames")
    parser.add_argument("--flip-to-labels-file-name",
                        type=str, default="flip_to_label.txt")

    return parser.parse_args()


def _handle_one_video(video_path, to_labels_file,
                      tmp_video, frames_per_sample,
                      to_frames_dir,
                      nothing_label_id,
                      img_format,):
    global cur_frames_cnt

    cmd = "ffmpeg -i {} -q:v 6 {}".format(video_path, tmp_video)
    if os.path.exists(tmp_video):
        os.remove(tmp_video)
    os.system(cmd)

    cap = cv2.VideoCapture(tmp_video)
    frames = []

    while True:
        flag, frame = cap.read()
        if not flag:
            break
        frames.append(frame)
        if len(frames) >= frames_per_sample:
            cur_frame_dir = os.path.join(to_frames_dir,
                                         str(cur_frames_cnt))
            if not os.path.exists(cur_frame_dir):
                os.makedirs(cur_frame_dir)
            for img_id, frame in enumerate(frames):
                cv2.imwrite(os.path.join(cur_frame_dir,
                                         img_format.format(img_id+1)),
                            frames[img_id])
            cur_frames_cnt += 1
            to_labels_file.write(cur_frame_dir + " " +
                                 str(len(frames)) + " " +
                                 str(nothing_label_id) + "\n")
            frames.clear()

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
    src_videos_dir = os.path.join(
        args.background_base_path,
        args.videos_dir_name,
    )
    assert os.path.exists(src_videos_dir)

    # 1. 构建 to frames 文件夹以及相关参数
    to_frames_dir = os.path.join(
        args.background_base_path,
        args.to_frames_dir_name,
    )
    if not os.path.exists(to_frames_dir):
        os.makedirs(to_frames_dir)
    global cur_frames_cnt
    cur_frames_cnt = _get_start_id(to_frames_dir)

    # 2. 构建 to labels 文件，并依次处理每个视频
    to_labels_file_path = os.path.join(
        args.background_base_path,
        args.to_labels_file_name,
    )
    if args.to_labels_file_append:
        to_labels_file = open(to_labels_file_path, "a")
    else:
        to_labels_file = open(to_labels_file_path, "w")
    for video_file_name in os.listdir(src_videos_dir):
        _handle_one_video(os.path.join(src_videos_dir, video_file_name),
                          to_labels_file,
                          args.tmp_video,
                          args.frames_per_sample,
                          to_frames_dir,
                          args.nothing_label_id,
                          args.img_format,)
    to_labels_file.close()

    # 3. flip
    flip_to_frames_dir = os.path.join(
        args.background_base_path,
        args.flip_frames_dir_name,
    )
    if not os.path.exists(flip_to_frames_dir):
        os.makedirs(flip_to_frames_dir)
    if args.flip:
        flip_samples(
            to_labels_file_path,
            os.path.join(args.background_base_path,
                         args.flip_to_labels_file_name),
            flip_to_frames_dir
        )

    # 4. 复制 to label 文件到to-labels-file-path
    shutil.copy(to_labels_file_path,
                os.path.join(args.global_to_labels_dir,
                             os.path.basename(args.background_base_path)
                             + "_background_to_labels.txt"))
    if args.flip:
        shutil.copy(to_labels_file_path,
                    os.path.join(args.global_to_labels_dir,
                                 os.path.basename(args.background_base_path)
                                 + "_background_flip_to_labels.txt"))


if __name__ == '__main__':
    main(_parse_args())
