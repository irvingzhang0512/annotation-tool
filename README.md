# 行为识别标注工具

+ [行为识别标注工具](#行为识别标注工具)
  + [0. 概述](#0-概述)
  + [1. 标注一条龙](#1-标注一条龙)
  + [2. 可视化工具](#2-可视化工具)
    + [2.1. 可视化工具本身](#21-可视化工具本身)
    + [2.2. 样本过滤工具](#22-样本过滤工具)
  + [3. 拆分数据集](#3-拆分数据集)
  + [4. 通过视频获取若干 nothing 样本](#4-通过视频获取若干-nothing-样本)

## 0. 概述
+ 本标注工具修改自
+ 目标
  + 预处理所有视频文件，包括将视频转换为若干图片帧、生成相应的配置文件。
  + 网页端标注图片，并生成标注结果。
  + 将标注结果转化为TSM可用的形式。
+ TODO
  + [x] 预处理视频文件 - 视频转换为若干图片帧。
  + [x] 预处理视频文件 - 生成相应的配置文件。
  + [x] 网页端标注图片。
  + [x] 将标注结果转换为TSM可用的形式。

## 1. 标注一条龙
+ 标注相关的可以查看 [GETTING_STARTED.md](GETTING_STARTED.md)

## 2. 可视化工具

### 2.1. 可视化工具本身
+ 脚本：`src/image_video_viewer.py`。
+ 实现思路：
  + 通过 PySimpleGUI 构建，主要就是通过事件来实现。
  + 其他细节见脚本注释。
+ 需求
  + 总需求：通过 OpenCV 方便地实现浏览服务器上的图片、视频。
  + 图片：
    + 选择文件夹（可固定，可手动输入），展示文件夹中的文件列表，点击显示每张图片。
    + 可通过键盘键控制“上一张图片”与“下一张图片”。
  + 视频：
    + 视频的形式有两种，一是视频文件，二是视频对应的帧文件夹，可手动选择这两种形式。
    + 展示视频。
    + 可通过键盘键控制“上一个视频”与“下一个视频”。
+ 其他：要运行这个，需要设置X11，windows上需要使用XMing。

### 2.2. 样本过滤工具
+ 脚本：`src/image_video_viewer_filter.py`
+ 需求：根据样本类别、帧文件夹过滤样本。
+ 输入：
  + 目标类别编号列表。
  + 样本文件列表文件，形如 `to_label.txt`。
  + 帧文件夹（因为在可视化工具中基本上都是显示同一文件夹内的数据，所以有这个限定）。
+ 输出：过滤文件（一行一个文件/文件夹名）。


## 3. 拆分数据集
+ 功能简介：拆分数据集。
+ 脚本：`src/split_dataset.py`
+ 需求：
  + 输入：标签类别数量、等待拆分的数据集文件、验证集比例/样本数/最大样本数、拆分结果（包括训练集与验证集）路径。
  + 输出：拆分结果。
+ 具体功能：
  + 第一步：读取待拆分的数据集。
    + 原始数据集的形式就是 `to_label.txt` 的形式。
    + 形成一个字典，key为标签（字符串形式），value为列表（列表元素为一个完成样本）。
  + 第二步：拆分数据集。
    + 分别读取每一类的样本列表，打乱顺序。
    + 根据输入（验证集比例/样本数/最大样本数）确定验证集样本数量（每一类的验证集样本数量可能不一样）。
+ 验证集样本数量的的确定规则：
  + 相关参数：
    + `--max-val-per-category`：必选参数，验证集样本数量最大数量。
    + `--val-percent-per-category`：可选参数，验证集样本比例。
  + 获取方式：
    + 如果指定了 `--val-percent-per-category` 则先根据该参数获取样本，然后与 `--max-val-per-category` 比较，去较少的数值作为样本数。
    + 如果没有指定 `--val-percent-per-category`，那每一类就是获取 `--max-val-per-category` 个样本。

## 4. 通过视频获取若干 nothing 样本
+ 功能简介：输入长视频，生成若干样本为 nothing 的数据。
+ 脚本：`src/nothing_videos_to_labels.py`
+ 需求：
  + 输入：原始视频所在目录，目标帧文件夹以及相关参数（起始id/每个样本的帧数量/帧图片名模版）。
  + 输出：`to_label.txt` 文件，帧文件夹下相关文件夹与帧图片。
+ 具体功能：
  + 第一步：读取视频。
  + 第二步：分别读取帧，达到 `--frames-per-sample` 后保存图片到目标帧文件夹。

