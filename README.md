# 行为识别标注工具

+ [行为识别标注工具](#行为识别标注工具)
  + [0. 概述](#0-概述)
  + [1. 网页端标注图片简介](#1-网页端标注图片简介)
    + [1.1. 配置文件概述](#11-配置文件概述)
    + [1.2. 标注结果简介](#12-标注结果简介)
    + [1.3. 其他](#13-其他)
  + [2. 脚本](#2-脚本)
    + [2.1. 原始视频提取帧](#21-原始视频提取帧)
    + [2.2. 将标注结果转换为TSM可识别的形式](#22-将标注结果转换为tsm可识别的形式)

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

## 1. 网页端标注图片简介

### 1.1. 配置文件概述
+ 视频配置文件（`video.txt`）
  + 有两列，分别是 `URLID` 与 `URL`。
  + 前者是视频编号，后者是视频路径（包括名称）。
+ 标签配置文件（`label.txt`）
  + 有两列，分别是 `TagID` 与 `Tag`。
  + 前者是标签编号，后者是标签名称。
+ 帧配置文件（`frame.txt`）
  + 有三列，分别是 `URLID`、`Frame`与`Time`。
  + 分别表示视频编号（与视频配置文件中的 `URLID` 对应）、帧名称（帧图片的文件名，包括图片后缀）、对应时间（单位为秒，表示在视频中的第几秒）

### 1.2. 标注结果简介
+ 样例：`sample/from_label.txt`。
+ 头文件：`URLID,URL,TagID,Tag,Start,End,Time,State`
  + `URLID`：视频编号，对应 `video.txt` 中的`URLID`。
  + `URL`：视频路径，对应 `video.txt` 中的`URL`。
  + `TagID`：标签表号，对应 `label.txt` 中的`TagID`。
  + `Tag`：标签名称，对应 `label.txt` 中的`Tag`。
  + `Start`：动作起始时间，对应 `frame.txt` 中的 `Time`。
  + `End`：动作结束时间，对应 `frame.txt` 中的 `Time`。
  + `Time`：不清楚。
  + `State`：不清楚。

### 1.3. 其他
+ 路径的注意事项
  + 对于视频文件路径，即`video.txt`中的`URL`，**不需要确保有对应的视频文件存在**。
  + 对于帧图片，即`frame.txt`中的`Frame`，对应的图片路径应该在 `./input/video/{URLID}/frame_name` 中。

## 2. 脚本
+ 目标：
  + [x] 将原始视频文件提取帧，作为标注输入。
  + [x] 将标注结果转换转换为TSM的输入形式。

### 2.1. 原始视频提取帧
+ 脚本：`src/video_to_frames.py`
+ 需求
  + 输入：若干视频的路径。
  + 输出样例：`sample/video.txt`、`sample/frame.txt`两个文件。
    + 两个文件可以是新建，也可以是追加。
    + 每个视频文件对应`video.txt`中的一行，记录视频编号以及视频路径。
    + 每个视频文件对应 `frame.txt` 中的多行，视频的每一帧对应 `frame.txt` 中的一行。

### 2.2. 将标注结果转换为TSM可识别的形式
+ 脚本：`src/labels_to_labels.py`
+ 需求
  + 输入：
    + 输入一个文件夹，文件夹中每个文件都是网页标注结果（样例 `sample/from_label.txt`）。
    + 原始图像帧，即`video_to_frames.py`的结果。
  + 输出：
    + TSM可识别的结果，输入数据统计（样例`sample/to_label.txt`）。
    + 每个样本对应的图像帧，从原始图像帧中复制、重命名。
+ 注意事项：
  + 除了读取标注结果文件、生成TSM样本输入文件外，还会复制原始帧图片、重新编号帧图片。