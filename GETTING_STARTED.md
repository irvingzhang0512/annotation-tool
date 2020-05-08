# 记录标注过程

+ [记录标注过程](#记录标注过程)
  + [0. 前言](#0-前言)
  + [1. 具体步骤](#1-具体步骤)
  + [2. 结构化视频文件夹处理](#2-结构化视频文件夹处理)
  + [3. 视频提取帧](#3-视频提取帧)
  + [4. 将标注结果转换为TSM模型可识别的形式](#4-将标注结果转换为tsm模型可识别的形式)

## 0. 前言
+ 目标：包括拍摄摄视频、标注动作、将标注结果转换为TSM可用的形式。
+ 一些代号：
  + `src_videos_dir`：原始视频文件所在文件夹。
  + `from_label.txt`：网页标注结果。
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
  + `from_frames_dir`：网页标注所需的帧文件夹，默认是 `./annotation-tool/input/video`。
  + `to_label.txt`：TSM可用的标签。
  + `to_frames_dir`：TSM可用的帧文件夹路径。
  + `web_videos.txt`：网页标注所需输入，用于保存所有视频路径的编号以及路径。
    + 样例文件 `sample/web_videos.txt`。
    + 有表头，共两列，分别是 `URLID` 与 `URL`。
    + 前者是视频编号，后者是视频路径（包括名称）。
    + **不需要确保有对应的视频文件存在**。
  + `web_frames.txt`：网页标注所需输入，用于保存所有视频对应的帧文件名以及对应的时间。
    + 对应的帧文件保存在 `from_frames_dir` 中。
    + 样例文件：`sample/web_frames.txt`。
    + 有表头，共三列，分别是 `URLID`、`Frame`与`Time`。
    + 分别表示视频编号（与视频配置文件中的 `URLID` 对应）、帧名称（帧图片的文件名，包括图片后缀）、对应时间（单位为秒，表示在视频中的第几秒）
  + `web_labels.txt`：网页标注所需输入，用于保存行为类别。
    + 样例文件 `sample/web_labels.txt`。
    + 有表头，共两列，分别是 `TagID` 与 `Tag`。
    + 前者是标签编号，后者是标签名称。
  + `category.txt`：保存所有类别名称。
    + 样例文件 `sample/category.txt`。
    + 一行一个类别名称。

## 1. 具体步骤
+ 第一步：请各位大佬拍摄视频，将所有视频文件保存到服务器一个文件夹中，即 `src_videos_dir`，并查看拍摄视频的类型。
  + 如果每个视频只有一个动作，那就在 `src_videos_dir` 中建立若干子文件夹，每个文件夹代表一种行为，通过子文件夹将行为分类。
    + 这种形式的文件夹取名为**结构化的视频文件夹**。
    + 通过 `src/categoried_videos.py` 就可以实现所有功能，不需要进行下面的步骤。
    + 具体内容请查看 [2. 结构化视频文件夹处理](#2-结构化视频文件夹处理)。
  + 如果每个视频有多个动作，则需要需要进行下面步骤。
+ 第二步：视频转换为帧。
  + 具体请看 [3. 视频提取帧](#3-视频提取帧)。
  + 脚本：`src/video_to_frames.py`。
  + 输入：`src_videos_dir`。
  + 输出：`from_frames_dir`，`vidoes.txt`，`frames.txt`。
+ 第三步：网页标注行为。
  + 在网页上输入 `web_videos.txt`，`web_frames.txt`，`web_labels.txt`。
  + 标注完成后下载得到 `from_label.txt`。
+ 第四步：将标注结果转换为TSM模型可识别的形式。
  + 具体请查看 [4. 将标注结果转换为TSM模型可识别的形式](#4-将标注结果转换为tsm模型可识别的形式)
  + 脚本：`src/labels_to_labels.py`。
  + 输入：`from_frames_dir`, `from_label.txt`。
  + 输出：`to_frames_dir`，`to_label.txt`。


## 2. 结构化视频文件夹处理
+ 功能简介：结构化的视频文件夹（即某文件夹中有若干子文件夹，每个子文件夹代表一个类型的行为，子文件夹中有若干视频文件）转换为TSM可识别的形式。
+ 脚本：`src/categoried_videos.py`
+ 需求：
  + 输入：视频文件夹路径 `src_videos_dir` 以及类别文件 `category.txt`。
    + 所谓`结构化的视频文件夹`是指：文件夹有若干子目录，每个目录的名称就是动作的名称，与类别文件中名称对应。
    + 类别文件（样例`sample/category.txt`），一行代表一种行为的名称，从0开始编号。
  + 输出：TSM标签 `to_label.txt` 以及对应新建的帧文件夹与帧图片。
+ 参数：
  + `--src-videos-path`
  + `--category-file-path`
  + `--ffmpeg`
  + `--fps`
  + `--tmp-video`
  + `--to-labels-file-path`
  + `--to-labels-file-append`：是追加文件，还是覆盖文件。
  + `--to-frames-dir`
  + `--start-id`：`to_frames_dir` 中子文件夹的起始编号。
  + `--img-prefix`：帧文件名格式。
+ 具体功能：
  + 基本功能：
    + 读取所有类别名称，如果 `src_videos_dir` 中有与类别名称相同的子文件夹，则遍历子文件夹中的所有视频。
    + 将每个视频提取帧，提取到的帧保存到对应的frames文件夹中。
    + 每个视频对应一个frames文件夹，文件夹通过 `to_frames_dir` 和 `--start-id` 以及当前视频在所有视频中的编号来确定。
    + 提取帧的过程中分别生成 `--to-labels-file-path` ，作为TSM的输入。
  + 提供了两种提取帧的方法。
    + 方法一：使用ffmpeg提取帧。
      + 需要设置参数 `--ffmpeg`。
      + 通过 `ffmpeg -i "/path/to/input.mp4" -threads 1 -vf scale=-1:256 -q:v 0 "/path/to/frames/dir/{img_prefix}"` 提取帧。
      + 注意事项：这种方法不能设置提取到的帧的数量（可能ffmpeg命令可以设置，但没具体查过），所以提取到的帧数量较多。
    + 方法二：通过opencv读取视频，然后提取帧。
      + 会用到参数 `--tmp-video`，`--fps`。
      + 基本流程：
        + 第一步：由于Linux上读取mp4视频可能存在问题，所以首先将原始视频转换格式为avi形式（通过ffmpeg实现），avi视频路径就是 `--tmp-video`。
        + 第二步：控制获取帧的数量。原始视频的fps可能较多（如25/30），而我们希望提取帧的数量较少（如10/15）。我们需要的fps通过 `--fps` 设置。
        + 第三步：遍历视频文件中的所有帧，然后选择我们需要的保存下来。

## 3. 视频提取帧
+ 功能简介：将原始视频文件提取帧，作为网页标注输入。
+ 脚本：`src/video_to_frames.py`
+ 需求
  + 输入：视频文件夹路径 `src_videos_dir`。
  + 输出：
    + 原始帧文件夹路径`from_frames_dir`。
    + 标注工具所需的`web_vidoes.txt`（提取的视频列表，包括编号与视频路径）。
    + 标注工具所需的`frames.txt`（每个视频对应所有帧的名称以及对应时间）。
      + 样例：`sample/video.txt`、`sample/frame.txt`两个文件。
      + 两个文件可以是新建，也可以是追加。
      + 每个视频文件对应`video.txt`中的一行，记录视频编号以及视频路径。
      + 每个视频文件对应 `frame.txt` 中的多行，视频的每一帧对应 `frame.txt` 中的一行。
+ 参数：
  + `--src-videos-path`
  + `--fps`
  + `--ffmpeg`
  + `--tmp-video`
  + `--web-videos-file-path`
  + `--web-videos-file-append`
  + `--web-frames-file-path`
  + `--web-frames-file-append`
  + `--from-frames-dir`
  + `--start-id`：`from_frames_dir` 中子文件夹的起始编号。
  + `--img-prefix`：帧文件名格式。
+ 具体功能：
  + 基本功能：
    + 读取 `src_videos_dir` 中的每个视频。
    + 将每个视频提取帧，提取到的帧保存到对应的frames文件夹中。
    + 每个视频对应一个frames文件夹，文件夹通过 `from_frames_dir` 和 `--start-id` 以及当前视频在所有视频中的编号来确定。
    + 提取帧的过程中分别生成 `--web-videos-file-path` 以及 `--web-frames-file-path` 两个文件，用于网页标注。
  + 提供了两种提取帧的方法。
    + 方法一：使用ffmpeg提取帧。
      + 需要设置参数 `--ffmpeg`。
      + 通过 `ffmpeg -i "/path/to/input.mp4" -threads 1 -vf scale=-1:256 -q:v 0 "/path/to/frames/dir/{img_prefix}"` 提取帧。
      + 注意事项：这种方法不能设置提取到的帧的数量（可能ffmpeg命令可以设置，但没具体查过），所以提取到的帧数量较多。
    + 方法二：通过opencv读取视频，然后提取帧。
      + 会用到参数 `--tmp-video`，`--fps`。
      + 基本流程：
        + 第一步：由于Linux上读取mp4视频可能存在问题，所以首先将原始视频转换格式为avi形式（通过ffmpeg实现），avi视频路径就是 `--tmp-video`。
        + 第二步：控制获取帧的数量。原始视频的fps可能较多（如25/30），而我们希望提取帧的数量较少（如10/15）。我们需要的fps通过 `--fps` 设置。
        + 第三步：遍历视频文件中的所有帧，然后选择我们需要的保存下来。

## 4. 将标注结果转换为TSM模型可识别的形式
+ 功能简介：将网页标注结果转换转换为TSM的输入形式。
+ 脚本：`src/labels_to_labels.py`
+ 需求
  + 输入：类别文件 `category.txt`、网页标注结果 `from_label.txt`以及对应的帧路径 `from_frames_dir`。
    + 输入一个文件夹，文件夹中每个文件都是网页标注结果（样例 `sample/from_label.txt`）。
  + 输出：TSM可用的标签 `to_label.txt` 以及对应的帧文件夹/图片。
    + 每个样本对应的图像帧是从原始图像帧中复制、重命名。
+ 注意事项：
  + 除了读取标注结果文件、生成TSM样本输入文件外，还会复制原始帧图片、重新编号帧图片。
+ 参数：
  + `--category-file-path`
  + `--from-labels-file-dir`
  + `--from-frames-dir`
  + `--from-img-prefix`：帧文件名格式。
  + `--from-time-interval`
  + `--to-labels-file-path`
  + `--to-labels-file-append`：是追加文件，还是覆盖文件。
  + `--to-frames-dir`
  + `--to-img-prefix`：帧文件名格式。
  + `--to-time-interval`
  + `--start-id`：`to_frames_dir` 中子文件夹的起始编号。
