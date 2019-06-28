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

## UI功能

![Date](/description/date.png)

1. 日期分类

1.1 同一天创建的图片位于同一目录中；双击某一日期的目录，即可查看该日期中的所有图片。

1.2 你也可以通过限定起始日期，搜索某一时间范围内的所有图片。

![Place](/description/place.png)

2. 地点分类

2.1 根据照片的定位信息，你可以浏览某一城市/区县的相关照片。

2.2 如果你的照片遍布天南海北，你可以通过设定省份/城市/区县快速找到你想要的照片。

![People0](/description/people_0.png)

![People1](/description/people_1.png)

![People2](/description/people_2.png)

3. 人物分类

3.1 应用会根据图片中是否包含人脸以及人脸的可能归属对图片进行分类。

3.2 你可以修改默认名称以便以后更方便的查找。

3.3 你还可以通过更复杂的组合条件搜索照片。例如，你可以搜索同时包含了你以及你女（男）朋友的照片。

3.4 双击图片可以查看大图。

![Thing](/description/thing.png)

4. 标签分类

在此页面中，你可以通过猫/狗等标签找到你照片中猫猫或者狗狗。

P.S. 此功能尚未实现。

![Search](/description/search.png)

5. 多条件组合搜索

通过组合时间、地点、人脸和标签等搜索条件，你可以进行更为复杂的搜索。

![Import](/description/import.png)

6. 图片导入

在本页面中，你可以选择要导入处理的文件夹。具体说明请参照页面中的使用说明。

![Setting](/description/setting.png)

7. API设置

为了能够解析GPS位置信息，我们需要调用腾讯lbs API。因此，在使用前你需要申请相关密钥并在被页面中进行设置。申请步骤请参照页面中的使用说明。

![About](/description/about.png)

8. 关于页面

在本页你可看到作者及作者公司的简略信息。

## UI functions
1. Date classification

1.1 Images created/taken in the same day are sorted in the same folder. Double click one folder, you can see all the images of this day.

1.2 If you want to browser images taken during a certain peroid of date, choose start date and end date above, and push search button. 

2. Place classification

2.1 Using the location (GPS) information stored in photoes, you can browser photoes of specific city or district.

2.2 If you have travelled to so many cities that you cann't find your favourite one, don't worry. Search it by choosing province/city/district name listed in combo boxes.

3. People classification

3.1 Application can sort your photoes according to whether it contains human face or not and who this face belongs to.

3.2 You can rename default names to make it easier to search.

3.3 You can search for images by combining double searching conditions. For example, you can search for images that contains you and/or/not your girl/boy friend at the same time.

3.4 You can browser origin big image by double-click.

4. Thing classification

4.1 In this page, you can find your doggy or catty by searching corresponding tag.

P.S. This function has not been implemented yet.

5. Search

You can use more complicated searching function by combining searching conditions of date/place/people/thing. 

6. Import

In this page, you can import and process images after choosing a folder that contains them. There is more detailed information in this page, please read it before using.

7. Setting

In order to transform origin GPS information, we need to invoke Tencent lbs API service. So you need to apply for API key and secret key and set them in this page beforing using. Please read application manual in this page.

8. About

Some information about author and author's company can be found here.

## 实现细节
1.  对照片进行处理后，所有的相关数据会被写入到本地的数据库文件中（默认为model文件夹下的info.db文件）。
2.  对照片进行处理后，默认会在对应的文件夹中创建输入图片的软链接（以减少磁盘空间占用），你也可以选用其他的方式（建立硬链接或者复制等）。

## Implementation Details
1.  After processing image, all related information will be written into local database file (default: info.db file in model directory).
2.  After processing image, an image soft link will be created in corresponding directory in default to reduce harddisk usage. Of course, you can choose other ways （copy or build hard link）.


## 文件夹介绍
    
## 数据库结构

数据库中包含了Summary，Date，People，Place和Thing五张表，其结构分别如下所示：

Summary:

| 字段名 | image_file | md5 | create_date | image_name_date | create_week | image_name_week |
| :--: | :--: | :-: | :-: | :-: | :-: | :-: |
| 字段属性 | nvarchar | char(32) | date | nvarchar | char(22) | nvarchar |
| 字段解释 | 图片名 | md5值 | 创建日期 | 具体名称 | 创建周 | 具体名称 |
