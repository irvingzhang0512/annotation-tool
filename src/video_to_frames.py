import os
import cv2
import argparse
import logging


def _parse_args():
    parser = argparse.ArgumentParser()

    # video
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--fps", type=int, default=10)

    # input
    parser.add_argument("--video-dir-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/videos")

    # output
    parser.add_argument("--video-file-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/video2.txt")
    parser.add_argument("--video-file-append", action="store_true")
    parser.add_argument("--frame-file-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/frame2.txt")
    parser.add_argument("--frame-file-append", action="store_true")
    parser.add_argument("--img-prefix", type=str, default="{:06d}.jpg")
    parser.add_argument("--frame-output-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/video")

    return parser.parse_args()


def _convert_fps(source_fps, target_fps):
    assert source_fps >= target_fps, "source fps must larger than target fps"

    interval = int(source_fps * 1.0 / target_fps)
    return [i*interval for i in range(int(source_fps/interval))]


def _handle_one_video(video_path,
                      fps, output_path,
                      frame_file_writer,
                      img_prefix, url_id,
                      resize_size=None):
    # 判断视频文件是否存在，不存在就跳过
    logging.info("Start handling {}".format(video_path))
    if not os.path.exists(video_path):
        logging.warn("{} doesn't exist.".format(video_path))
        return

    # 读取视频，并初始化一些参数
    cap = cv2.VideoCapture(video_path)
    source_fps = cap.get(cv2.CAP_PROP_FPS)
    id = -1
    file_name_id = 1
    interval_time = 1.0 / fps

    # 有一个问题需要处理：
    # 输入视频文件的fps和我们需要的fps是不同的
    # 一般来说，视频的fps大于我们需要的fps
    # 所以，需要在视频的fps中选择我们需要的若干帧图像
    # 下面这个函数就是选择的帧的编号
    ids = _convert_fps(source_fps, fps)

    # 分别读取每一帧，然后分别处理
    while True:
        flag, frame = cap.read()
        if not flag:
            break
        if resize_size:
            frame = cv2.resize(frame, resize_size)
        id += 1
        if id >= source_fps:
            id = 0

        if id in ids:
            # 如果当前帧需要保存，则要保存到目标文件夹中，且要在对应配置文件中添加行
            img_name = img_prefix.format(file_name_id)
            cv2.imwrite(os.path.join(output_path, img_name), frame)
            context = str(url_id) + "," + img_name + "," + \
                "%.1f" % ((file_name_id-1) * interval_time) + "\n"
            frame_file_writer.write(context)
            file_name_id += 1


def main(args):
    # 1. 获取目录下所有视频文件的绝对路径
    if not os.path.isdir(args.video_dir_path):
        raise("Wrong video dir path {}".format(args.video_dir_path))
    file_names = os.listdir(args.video_dir_path)
    file_names = [os.path.join(args.video_dir_path, file_name)
                  for file_name in file_names]

    # 2. 新建配置文件，可以是新建，也可以是追加
    if args.video_file_append:
        video_file = open(args.video_file_path, "a")
    else:
        video_file = open(args.video_file_path, "w")
        video_file.write("URLID,URL\n")
    if args.frame_file_append:
        frame_file = open(args.frame_file_path, "a")
    else:
        frame_file = open(args.frame_file_path, "w")
        frame_file.write("URLID,Frame,Time\n")

    # 3. 遍历每个视频文件
    for idx, file_name in enumerate(file_names):
        # 每个视频文件对应一个输出文件夹，文件夹名称就是一个编号
        cur_idx = idx + args.start_id
        output_path = os.path.join(args.frame_output_path, str(cur_idx))
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # 在配置文件中写入数据
        video_file.write(str(cur_idx) + "," + file_name + "\n")

        # 单独处理每个视频文件
        _handle_one_video(file_name, args.fps, output_path,
                          frame_file, args.img_prefix, cur_idx)
    video_file.close()
    frame_file.close()


if __name__ == "__main__":
    main(_parse_args())
