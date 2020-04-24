# 行为识别标注工具

+ [行为识别标注工具](#行为识别标注工具)
  + [0. 概述](#0-概述)
  + [1. 标注一条龙](#1-标注一条龙)
  + [2. 可视化工具](#2-可视化工具)
    + [2.1. 需求](#21-需求)
    + [2.2. 实现](#22-实现)

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

### 2.1. 需求
+ 总需求：通过 OpenCV 方便地实现浏览服务器上的图片、视频。
+ 图片：
  + 选择文件夹（可固定，可手动输入），展示文件夹中的文件列表，点击显示每张图片。
  + 可通过键盘键控制“上一张图片”与“下一张图片”。
+ 视频：
  + 视频的形式有两种，一是视频文件，二是视频对应的帧文件夹，可手动选择这两种形式。
  + 展示视频。
  + 可通过键盘键控制“上一个视频”与“下一个视频”。


### 2.2. 实现
+ 脚本：`src/image_video_viewer.py`。
+ 主要思路：
  + 通过 PySimpleGUI 构建，主要就是通过事件来实现。
  + 其他细节见脚本注释。
+ 其他：要运行这个，需要设置X11，windows上需要使用XMing。