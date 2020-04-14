import os
import cv2
import argparse
import logging


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--img-prefix", type=str, default="{:06d}.jpg")
    parser.add_argument("--tmp-video", type=str, default="./test.avi")

    # input video path
    parser.add_argument("--category-file-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/ar/category.txt")
    parser.add_argument("--video-base-path", type=str,
                        default="/ssd5/zhangyiyang/data/AR")

    # output frame path
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--frame-output-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/ar/video")

    # output file
    parser.add_argument("--output-file-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/ar/to_label.txt")
    parser.add_argument("--output-file-append", action="store_true")

    return parser.parse_args()


def _convert_fps(source_fps, target_fps):
    assert source_fps >= target_fps, "source fps must larger than target fps"

    interval = int(source_fps * 1.0 / target_fps)
    return [i*interval for i in range(int(source_fps/interval))]


def _handle_single_video(video_path, cur_idx, to_file, category_id, args):
    logging.info("start handling {}".format(video_path))
    if not os.path.exists(video_path):
        logging.warn("{} doesn't exist.".format(video_path))
        return

    # 读取视频
    cmd = "ffmpeg -i {} -q:v 6 {}".format(video_path, args.tmp_video)
    os.system(cmd)
    cap = cv2.VideoCapture(args.tmp_video)
    source_fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 有一个问题需要处理：
    # 输入视频文件的fps和我们需要的fps是不同的
    # 一般来说，视频的fps大于我们需要的fps
    # 所以，需要在视频的fps中选择我们需要的若干帧图像
    # 下面这个函数就是选择的帧的编号
    ids = _convert_fps(source_fps, args.fps)

    # 构建输出帧的路径
    output_path = os.path.join(args.frame_output_path, str(cur_idx))
    if not os.path.exists(output_path):
        os.mkdir(output_path)

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
            cv2.imwrite(os.path.join(output_path, img_name), frame)
    to_file.write(output_path + " " + str(file_name_id) +
                  " " + str(category_id) + "\n")
    cap.release()
    if os.path.exists(args.tmp_video):
        os.remove(args.tmp_video)


def main(args):
    # 初始化TSM格式的标签文件
    if args.output_file_append:
        to_file = open(args.output_file_path, "a")
    else:
        to_file = open(args.output_file_path, "w")

    with open(args.category_file_path, "r") as f:
        categories = f.readlines()
    categories = [c.replace("\n", "") for c in categories]
    category_to_id = {c: idx for idx, c in enumerate(categories)}

    tp_idx = 0
    for category in os.listdir(args.video_base_path):
        # 依次遍历每类视频
        video_dir_path = os.path.join(args.video_base_path, category)
        videos = os.listdir(video_dir_path)
        videos = [os.path.join(video_dir_path, v) for v in videos]

        for video_path in videos:
            # 依次遍历每类视频中的每个视频文件
            _handle_single_video(video_path,
                                 args.start_id + tp_idx,
                                 to_file,
                                 category_to_id[category],
                                 args)
            tp_idx += 1

    to_file.close()


if __name__ == '__main__':
    main(_parse_args())
