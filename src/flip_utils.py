import os
import cv2

LABEL_ID_TRANSFORMATION = {
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "4",
    "4": "3",
    "5": "5",
}


def _get_start_id(cur_dir):
    max_id = 0
    for file_name in os.listdir(cur_dir):
        try:
            idx = int(file_name)
            max_id = max(idx, max_id)
        except:
            pass
    return max_id + 1


def flip_samples(src_to_labels_file_path,
                 flip_to_label_file_path,
                 flip_frames_dir,):
    flip_file_writer = open(flip_to_label_file_path, "w")

    if not os.path.exists(flip_frames_dir):
        os.makedirs(flip_frames_dir)
    flip_frames_idx = _get_start_id(flip_frames_dir)
    with open(src_to_labels_file_path, "r") as f:
        pre_samples = [sample.strip() for sample in f.readlines()]
    for pre_sample in pre_samples:
        splits = pre_sample.split(" ")
        if len(splits) != 3:
            print("Error pre sample {}".format(pre_sample))
            continue
        original_frames_dir = splits[0]
        if not os.path.exists(original_frames_dir):
            print("Error source frames dir {}".format(original_frames_dir))
            continue
        cur_flip_frames_dir = os.path.join(
            flip_frames_dir, str(flip_frames_idx))
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
        flip_file_writer.write(cur_flip_frames_dir + " " +
                               splits[1] + " " +
                               LABEL_ID_TRANSFORMATION[splits[-1]] + "\n")
        flip_frames_idx += 1

    flip_file_writer.close()
