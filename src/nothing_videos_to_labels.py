import os
import cv2
import argparse

cur_frames_cnt = 0


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--nothing-label-id", type=int, default=0)

    # input video path
    parser.add_argument("--src-videos-dir", type=str,
                        default="/ssd4/zhangyiyang/data/AR/videos/mine/nothing")
    parser.add_argument("--tmp-video", type=str,
                        default="./test.avi")

    # to_frames_dir
    parser.add_argument("--to-frames-dir", type=str,
                        default="/ssd4/zhangyiyang/data/AR/raw_to_frames")
    parser.add_argument("--frames-per-sample", type=int, default=32)
    parser.add_argument("--img-prefix", type=str, default="{:05d}.jpg")

    # to_labels.txt
    parser.add_argument("--to-labels-file-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/type3_total.txt")
    parser.add_argument("--to-labels-file-append", action="store_true")

    return parser.parse_args()


def _handle_one_video(video_path, to_labels_file, args):
    global cur_frames_cnt

    cmd = "ffmpeg -i {} -q:v 6 {}".format(video_path, args.tmp_video)
    if os.path.exists(args.tmp_video):
        os.remove(args.tmp_video)
    os.system(cmd)

    cap = cv2.VideoCapture(args.tmp_video)
    frames = []

    while True:
        flag, frame = cap.read()
        if not flag:
            break
        frames.append(frame)
        if len(frames) >= args.frames_per_sample:
            cur_frame_dir = os.path.join(args.to_frames_dir,
                                         str(cur_frames_cnt))
            if not os.path.exists(cur_frame_dir):
                os.makedirs(cur_frame_dir)
            for img_id, frame in enumerate(frames):
                cv2.imwrite(os.path.join(cur_frame_dir,
                                         args.img_prefix.format(img_id)),
                            frames[img_id])
            cur_frames_cnt += 1
            to_labels_file.write(cur_frame_dir + " " +
                                 str(len(frames)) + " " +
                                 str(args.nothing_label_id) + "\n")
            frames.clear()

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
    global cur_frames_cnt
    cur_frames_cnt = _get_start_id(args.to_frames_dir)
    if not os.path.isdir(args.src_videos_dir):
        raise ValueError("unknown video dir {}".format(args.src_videos_dir))

    # 初始化TSM格式的标签文件
    if args.to_labels_file_append:
        to_labels_file = open(args.to_labels_file_path, "a")
    else:
        to_labels_file = open(args.to_labels_file_path, "w")

    for video_file_name in os.listdir(args.src_videos_dir):
        _handle_one_video(os.path.join(args.src_videos_dir, video_file_name),
                          to_labels_file,
                          args)
    to_labels_file.close()


if __name__ == '__main__':
    main(_parse_args())
