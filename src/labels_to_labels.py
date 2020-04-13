import os
import shutil
import argparse
import logging

to_id = 0


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--category-file-path", type=str,
                        default="/ssd4/zhangyiyang/data/jester-v1/category.txt")

    # from
    parser.add_argument("--from-label-dir-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/from_label")
    parser.add_argument("--from-frame-dir-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/video")
    parser.add_argument("--from-img-prefix", type=str, default="{:06d}.jpg")
    parser.add_argument("--from-time-interval", type=float, default=.1)

    # to
    parser.add_argument("--to-frame-dir-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/to_videos")
    parser.add_argument("--to-img-prefix", type=str, default="{:06d}.jpg")
    parser.add_argument("--to-time-interval", type=float, default=.1)

    # output file
    parser.add_argument("--output-file-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/to_label/output.txt")
    parser.add_argument("--output-file-append", action="store_true")

    return parser.parse_args()


def _handle_one_file(file_name, to_file, category_to_id, args):
    # 判断文件是否存在
    logging.info("start processing {}".format(file_name))
    if not os.path.exists(file_name):
        logging.warn("{} doesn't exists".format(file_name))
        return

    # 设置输出样本编号，全局变量的形式保存
    global to_id

    # 设置原始图像帧与当前帧之间的相对关系
    inner_interval = int(
        round(args.to_time_interval / args.from_time_interval, 0))

    # 设置当前样本帧
    to_time_interval = int(round(args.to_time_interval * 10, 0))

    # 读取标注结果文件，并删除第一行
    with open(file_name, "r") as f:
        lines = f.readlines()
    lines = [l.replace("\n", "") for l in lines]
    lines.pop(0)

    # 分别读取标注结果的每一行，一行代表一个TSM样本
    for line in lines:
        # 读取行信息
        splits = line.split(",")
        from_id = splits[0]
        t1 = int(round(float(splits[4]) * 10, 0))
        t2 = int(round(float(splits[5]) * 10, 0))
        label = splits[3]

        # 获取原始图像帧中的编号
        from_ids = [(t1 + i * to_time_interval) * inner_interval
                    for i in range(100)
                    if (t1 + i * to_time_interval) * inner_interval <= t2]

        # 准备复制文件
        from_frame_path = os.path.join(args.from_frame_dir_path, from_id)
        to_frame_path = os.path.join(args.to_frame_dir_path, str(to_id))
        to_id += 1
        if not os.path.exists(from_frame_path):
            print("from frame path {} doesn't exist".format(from_frame_path))
        if not os.path.exists(to_frame_path):
            os.makedirs(to_frame_path)

        # 复制图片，并重新编号
        for to_idx, from_idx in enumerate(from_ids):
            from_img = os.path.join(from_frame_path,
                                    str(args.from_img_prefix).format(from_idx))
            to_img = os.path.join(
                to_frame_path, str(args.to_img_prefix).format(to_idx))
            if os.path.exists(from_img):
                shutil.copyfile(from_img, to_img)
            else:
                print("error copy {} to {}".format(from_img, to_img))

        # 输出文件中添加行
        label_id = category_to_id[label]
        to_frame_path
        frame_cnt = len(from_ids)
        to_file.write(to_frame_path + " " + str(frame_cnt) +
                      " " + str(label_id) + "\n")


def main(args):
    assert args.from_time_interval <= args.to_time_interval

    global to_id
    to_id = args.start_id

    # 1. 读取输入标记结果路径
    file_names = os.listdir(args.from_label_dir_path)
    file_names = [os.path.join(args.from_label_dir_path, f)
                  for f in file_names]

    # 2. 构建输出结果文件
    if args.output_file_append:
        to_file = open(args.output_file_path, "a")
    else:
        to_file = open(args.output_file_path, "w")

    # 3. 获取样本标签字典
    with open(args.category_file_path, "r") as f:
        categories = f.readlines()
    categories = [c.replace("\n", "") for c in categories]
    category_to_id = {c: idx for idx, c in enumerate(categories)}

    # 4. 分别操作每个标记结果文件
    for file_name in file_names:
        _handle_one_file(file_name, to_file, category_to_id, args)


if __name__ == '__main__':
    main(_parse_args())