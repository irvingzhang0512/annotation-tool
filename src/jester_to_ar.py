ar_categories = [
    "nothing",
    "other",
    "close",
    "left",
    "right",
    "ok",
]

jester_catigories = [
    "Doing other things",  # 0
    "Drumming Fingers",  # 1
    "No gesture",  # 2
    "Pulling Hand In",  # 3
    "Pulling Two Fingers In",  # 4
    "Pushing Hand Away",  # 5
    "Pushing Two Fingers Away",  # 6
    "Rolling Hand Backward",  # 7
    "Rolling Hand Forward",  # 8
    "Shaking Hand",  # 9
    "Sliding Two Fingers Down",  # 10
    "Sliding Two Fingers Left",  # 11
    "Sliding Two Fingers Right",  # 12
    "Sliding Two Fingers Up",  # 13
    "Stop Sign",  # 14
    "Swiping Down",  # 15
    "Swiping Left",  # 16
    "Swiping Right",  # 17
    "Swiping Up",  # 18
    "Thumb Down",  # 19
    "Thumb Up",  # 20
    "Turning Hand Clockwise",  # 21
    "Turning Hand Counterclockwise",  # 22
    "Zooming In With Full Hand",  # 23
    "Zooming In With Two Fingers",  # 24
    "Zooming Out With Full Hand",  # 25
    "Zooming Out With Two Fingers"  # 26
]

jester_train = "/ssd4/zhangyiyang/data/jester-v1/train_videofolder.txt"
jester_val = "/ssd4/zhangyiyang/data/jester-v1/val_videofolder.txt"
ar_total = "/ssd4/zhangyiyang/data/AR/label/jester_to_ar.txt"


pairs = [
    ([2], 0),  # nothing
    ([25, 26], 2),  # close
    ([0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
      14, 15, 16, 17, 18, 21, 22], 1),  # other
]

# 合并Jester数据集的train/val，合并为一个文件。
with open(jester_train, "r") as f:
    train_samples = [line.strip() for line in f.readlines()]
with open(jester_val, "r") as f:
    val_samples = [line.strip() for line in f.readlines()]
total_samples = train_samples + val_samples


# 将Jester的数据转换为AR可用的形式。
ar_samples = []
for cur_pair in pairs:
    cur_ids, cur_label = cur_pair
    for sample in total_samples:
        splits = sample.split(" ")
        if int(splits[2]) in cur_ids:
            ar_samples.append(
                " ".join([splits[0], splits[1], str(cur_label)]))
with open(ar_total, "w") as f:
    f.writelines("\n".join(ar_samples))
