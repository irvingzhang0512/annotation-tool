import argparse

import numpy as np


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--num-classes", type=int, default=6)
    parser.add_argument("--to-labels-file-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/flip_total.txt")
    parser.add_argument("--val-percent-per-category", type=float, default=0.1)
    parser.add_argument("--val-samples-per-category", type=int, default=0)
    parser.add_argument("--max-val-per-category", type=int, default=50)

    parser.add_argument("--train-file-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/train_samples.txt")
    parser.add_argument("--val-file-path", type=str,
                        default="/ssd4/zhangyiyang/data/AR/label/val_samples.txt")

    return parser.parse_args()


def main(args):
    with open(args.to_labels_file_path, "r") as f:
        samples = [l.strip() for l in f.readlines()]
    category_id_to_samples_dict = {str(i): [] for i in range(args.num_classes)}
    for sample in samples:
        splits = sample.split(" ")
        category_id_to_samples_dict[splits[-1]].append(sample)

    train_writer = open(args.train_file_path, "w")
    val_writer = open(args.val_file_path, "w")

    for category in range(args.num_classes):
        cur_samples = category_id_to_samples_dict[str(category)]
        cur_samples = np.array(cur_samples)
        np.random.shuffle(cur_samples)

        if args.val_samples_per_category:
            val_number = args.val_samples_per_category
        else:
            val_number = int(len(cur_samples) * args.val_percent_per_category)

        val_number = min(val_number, args.max_val_per_category)
        train_writer.write("\n".join(cur_samples[:-val_number]))
        train_writer.write("\n")
        val_writer.write("\n".join(cur_samples[-val_number:]))
        val_writer.write("\n")

    train_writer.close()
    val_writer.close()


if __name__ == '__main__':
    main(_parse_args())
