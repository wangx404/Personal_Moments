# 个人时光
一个功能类似于谷歌相册的个人照片整理脚本。

# Personal_Moments
An offline script for sorting personal photos with similar functions of Google Photo.

## 功能
- 根据创建时间进行整理：同一天创建的图片位于同一文件夹中
- 根据创建时间所在周进行整理：同一周创建的图片位于同一文件夹内
- 根据位置进行整理：将照片按照省份/城市/城区三级层级进行整理
- 根据人进行整理：通过照片中包含的人（脸）进行分类，每个人拥有各自独立的文件夹
- 根据类别标签进行整理：通过对照片属性的判断，相同属性的照片位于同一文件夹中

## Functions
- sort by creation date: all images created in the same day are in the same directory
- sort by creation week: all images created in the same week are in the same directory
- sort by place: sort image by province, city and district
- sort by people: sort by human (face/faces) in image, every person has a directory of all images belonged to himself/herself
- sort by thing: sort image by thing attribution tags

## 实现方法
- 根据创建时间进行整理：读取图片EXIF；如果不存在EXIF，则读取文件属性信息中的时间
- 根据创建时间所在周进行整理：根据创建时间计算得到所在周
- 根据位置进行整理：读取照片EXIF中的GPS信息，然后调取腾讯lbs API；如果不存在，则跳过
- 根据人进行整理：调用dlib的人脸检测和人脸识别模型进行分类
- 根据类别标签进行整理：通过DNN模型判断照片的属性

## Implementation
- sort by creation date: read EXIF of image; if EXIF doesn't exist, read time stamp in file attributes
- sort by creation week: calculate week by creation date
- sort by place: read GPS information in EXIF of image, and then invoke Tencent lbs API; if EXIF doesn't exist, jump
- sort by people: invoke dlib's face detection and recognition model
- sort by thing: calculate classification tags by DNN model

## 实现细节
1.  对照片进行处理后，所有的相关数据会被写入到本地的数据库文件中（默认为model文件夹下的info.db文件）。
2.  对照片进行处理后，默认会在对应的文件夹中创建输入图片的硬链接（以减少磁盘空间占用），你也可以选用其他的方式（建立符号链接或者复制等）。

## Implementation Details
1.  After processing image, all related information will be written into local database file (default: info.db file in model directory).
2.  After processing image, an image hard link will be created in corresponding directory in default to reduce harddisk usage. Of course, you can choose other ways （copy or build symbolic link）.

## 实现结果
经过脚本处理后，在输出文件夹中会按照以下结果出现若干文件夹，文件夹内存放的图片即对应属性的图片。

输出文件夹的组织结构如下所示：
--output

  --Date
  
    --1970-01-01
    
    ...
    
  --People
  
    --Person_0001
    
    ...
    
  --Place
  
    --北京
    
      --北京
      
        --海淀
    ...
    
  --Thing
  
    --Dog
    
    --Cat
    
    ...
    
  --Week
  
    ...

## Results
After processing by this script, there are some new directories in output directory. Each directory contains related images.

The structure of output directory is as below:

--output

  --Date
  
    --1970-01-01
    
    ...
    
  --People
  
    --Person_0001
    
    ...
    
  --Place
  
    --北京
    
      --北京
      
        --海淀
    ...
    
  --Thing
  
    --Dog
    
    --Cat
    
    ...
    
  --Week
  
    ...
    
## 数据库结构
数据库中包含了Summary，DateWeek，People，Place和Thing五张表，其结构分别如下所示：

DateWeek:

| 字段名 | image_file | md5 | create_date | image_name_date | create_week | image_name_week |
| :--: | :--: | :-: | :-: | :-: | :-: | :-: |
| 字段属性 | nvarchar | char(32) | date | nvarchar | char(22) | nvarchar |
| 字段解释 | 图片名 | md5值 | 创建日期 | 具体名称 | 创建周 | 具体名称 |

## Database Structure
There are five tables in database, which are Summary, DateWeek, People, Place and Thing. Their structures are listed below:

DateWeek:

| item | image_file | md5 | create_date | image_name_date | create_week | image_name_week |
| :--: | :--: | :-: | :-: | :-: | :-: | :-: |
| item attribute | nvarchar | char(32) | date | nvarchar | char(22) | nvarchar |
