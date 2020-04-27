import os
import cv2
import shutil
import argparse
from tqdm import tqdm

LABEL_ID_TRANSFORMATION = {
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "4",
    "4": "3",
    "5": "5",
}


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--to-flip-frames-dir", type=str,
                        default="/ssd4/zhangyiyang/data/AR/flip_frames")
    parser.add_argument("--start-id", type=int, default=114860)
    parser.add_argument("--pre-to-labels-file-path", type=str,
                        default="/ssd4/zhangyiyang/tomcat9/webapps/annotation-tool/input/ar/to_label/output.txt")
    parser.add_argument("--after-to-labels-file-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/flip_total.txt")
    parser.add_argument("--after-to-labels-file-append", action="store_true",
                        default=False)

    return parser.parse_args()


def main(args):
    if not args.after_to_labels_file_append and \
            os.path.exists(args.to_flip_frames_dir):
        shutil.rmtree(args.to_flip_frames_dir)
        os.makedirs(args.to_flip_frames_dir)
    with open(args.pre_to_labels_file_path, "r") as f:
        pre_samples = [l.strip() for l in f.readlines()]
    if args.after_to_labels_file_append:
        after_to_labels_file = open(args.after_to_labels_file_path, "a")
    else:
        after_to_labels_file = open(args.after_to_labels_file_path, "w")
    flip_frames_idx = args.start_id
    for pre_sample in tqdm(pre_samples):
        splits = pre_sample.split(" ")
        if len(splits) != 3:
            print("Error pre sample {}".format(pre_sample))
            continue
        original_frames_dir = splits[0]
        # original sample
        after_to_labels_file.write(pre_sample + "\n")

        # flip sample
        cur_flip_frames_dir = os.path.join(
            args.to_flip_frames_dir, str(flip_frames_idx))
        flip_frames_idx += 1
        os.makedirs(cur_flip_frames_dir)
        for frame_name in os.listdir(original_frames_dir):
            frame = cv2.flip(
                cv2.imread(os.path.join(original_frames_dir, frame_name)),
                flipCode=1,
            )
            cv2.imwrite(
                os.path.join(cur_flip_frames_dir, frame_name),
                frame
            )
        after_to_labels_file.write(cur_flip_frames_dir + " " +
                                   splits[1] + " " +
                                   LABEL_ID_TRANSFORMATION[splits[-1]] + "\n")


if __name__ == '__main__':
    main(_parse_args())
