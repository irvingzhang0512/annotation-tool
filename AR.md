# 构建AR手势识别数据集

## 0. 前言
+ 目标：构建AR手势识别数据集。
+ 数据集数据来源：
  + 自己录制视频。
  + 从Jester中获取一些需要的数据。
  + 生成一些数据。
+ 需要实现的功能：
  + 从头文件数据集。
  + 为现有数据集添加内容。

## 1. 文件夹结构
+ `raw_to_frames`
+ `videos`
+ `label`：标签文件夹。
  + 主要包括了类别标签 `category.txt` 以及构建数据集过程中生成的 `to_label.txt`。
  + `to_label.txt` 分类：
    + 初次构建数据集
      + `type1_total.txt`：自己录制/标注的样本。
      + `type2_total.txt`：Jester数据集转换为我们需要的样本形式。
      + `type3_total.txt`：将nothing视频转换为标签为nothing的样本。
      + `final_total.txt`：将上面三个文件拼接所得。
      + `flip_total.txt`：`final_total.txt` 水平镜像生成新的标签文件。
    + 为现有数据集添加样本：
      + 先通过各种方法生成一个 `to_label.txt`。
      + 在通过 `horizontal_flip_augmentation.py` 在 `flip_total.txt` 中追加数据。
    + 拆分数据集：
      + 通过 `src/split_dataset.py`，将 `flip_total.txt` 拆分为 `train_samples.txt` 和 `val_samples.txt`，用于训练。
+ `generate_videos`
+ `flip_frames`