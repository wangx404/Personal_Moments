#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue May 14 14:58:44 2019
@author: wangxin
"""

import os, time, json
import sqlite3
import argparse
from collections import defaultdict
from PyQt5.QtCore import QThread, pyqtSignal

from .common_utils import get_all_images, random_rename, remove_processed_image,\
                        load_api_key, build_image_link, calculate_md5
from .database_utils import table_exist, get_all_image_from_table,image_in_table,\
                            insert_image_into_table, update_image_in_table,\
                            delete_image_from_table, query_image_links
from .date_utils import get_time_stamp, date2week_date
from .gps_utils import get_gps_info, get_address_from_gps
from .face_utils import load_feature_centers, load_face_numbers, load_face_names,\
                        get_face_features, init_feature_center, KNN_search,\
                        update_feature_center, add_feature_center,\
                        save_feature_centers, save_face_numbers, save_face_names


class DateThread(QThread):
    signal = pyqtSignal(int, str) # emit progress percent and thread name at the same time
    def __init__(self):
        super(DateThread, self).__init__()
        self.database = os.path.join("record", "info.db") # database
        self.input_dir = None # input directory
        self.output_dir = None # output directory
        self.ui_invoke = False # whether invoke by ui
    
    
    def run(self):
        """
        遍历输入文件夹中的所有文件，读取文件的创建日期，根据日期进行分类。
        Traverse input directory to get all image files, read creating dates of them, 
        sort these image files by creating date.
        pipeline: 
            check if related tables exist or not,
            traverse all image files, 
            remove image files that have been processed, 
            get image create date in for loop,
            process image file in for loop:
                build image link in corresponding date directory, 
                build image link in corresponding week directory, 
                write data into database
        """
        # check if Summary and Date exist
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        table_exist(cursor, "Summary")
        table_exist(cursor, "Date")
        
        image_list = get_all_images(self.input_dir) # traverse all image files
        image_list_processed = get_all_image_from_table(cursor, "Date") # get image files that have been processed
        image_list = remove_processed_image(image_list, image_list_processed) # remove image files that have been processed
        image_list.sort() # sort
        image_number = len(image_list) # total number of image files
        image_cnt = 0 # image counter
        
        date_image_dict = defaultdict(list) # date: [image_file, ]
        for image_file in image_list:
            date = get_time_stamp(image_file) # get time stamp 
            date_image_dict[date].append(image_file) # add into container
        
        dates = list(date_image_dict.keys())
        dates.sort()
        for date in dates: # process image file in for loop
            # create directory under output_dir/Date/
            if not os.path.exists(os.path.join(self.output_dir, "Date", date)):
                os.makedirs(os.path.join(self.output_dir, "Date", date))
            # create directory under output_dir/Week/
            week = date2week_date(date)
            if not os.path.exists(os.path.join(self.output_dir, "Week", week)):
                os.makedirs(os.path.join(self.output_dir, "Week", week))
            
            # create image link in corresponding directory
            image_list = date_image_dict[date]
            for image_file in image_list:
                key_value_dict = dict()
                _, image_name = os.path.split(image_file)
                
                # check name, build image link, jump exception 
                if os.path.exists(os.path.join(self.output_dir, "Date", date, image_name)):
                    image_name_date = random_rename(image_name)
                else:
                    image_name_date = image_name
                if os.path.exists(os.path.join(self.output_dir, "Week", week, image_name)):
                    image_name_week = random_rename(image_name)
                else:
                    image_name_week = image_name
                try:
                    build_image_link(image_file, os.path.join(self.output_dir, "Date", date, image_name_date))
                    build_image_link(image_file, os.path.join(self.output_dir, "Week", week, image_name_week))
                except Exception:
                    print("Error happened when building image link of %s" % image_file)
                    image_cnt += 1
                    continue
                
                # write data into database
                key_value_dict["create_date"] = date
                key_value_dict["image_name_date"] = image_name_date
                key_value_dict["create_week"] = week
                key_value_dict["image_name_week"] = image_name_week
                insert_image_into_table(cursor, "Date", key_value_dict)
                # if image_file item has already in Table Summary, update
                if image_in_table(cursor, "Summary", image_file):
                    update_image_in_table(cursor, "Summary", image_file, key_value_dict)
                # insert new record, add extra items (image_file, md5)
                else:
                    key_value_dict["image_file"] = image_file
                    md5 = calculate_md5(image_file)
                    key_value_dict["md5"] = md5
                    insert_image_into_table(cursor, "Summary", key_value_dict)
                conn.commit()
                
                print("Date/Week processing: %s" % image_file)
                # update process percent, and emit signal
                image_cnt += 1
                if self.ui_invoke:
                    progress_pct = int(image_cnt / image_number * 100)
                    self.signal.emit(progress_pct, "date")
        
        conn.close()
        print("All images are sorted by date.")


class PlaceThread(QThread):
    signal = pyqtSignal(int, str) # signal object
    def __init__(self):
        super(PlaceThread, self).__init__()
        self.database = os.path.join("record", "info.db") # datebase
        self.key_file = os.path.join("record", "key_file.txt") # key text file
        self.input_dir = None # input directory
        self.output_dir = None # output directory
        self.ui_invoke = False # whether invoke by ui
    
    
    def run(self):
        """
        遍历输入文件夹中的所有文件，读取GPS信息，通过腾讯lbs API获取详细地址，根据地址进行图片整理。
        Traverse input directory to get all image files, get GPS location from image's 
        EXIF, get detailed address by invoking Tencent lbs API, sort by district.
        pipeline:
            load api key, 
            check if related tables exist or not,
            traverse all image files, 
            remove image files that have been processed, 
            process image in for loop:
                get gps location information, 
                query address by tencent lbs api, 
                build image link, 
                write data into database, 
                sleep if it is necessary.
        """
        # load api keys, if keys don't exist, return
        api_key_dict = load_api_key(self.key_file) 
        for key in ("api_key", "secret_key"):
            if key not in api_key_dict.keys():
                return 
        api_key = api_key_dict["api_key"]
        secret_key = api_key_dict["secret_key"]
        
        # check if table Summary and Place exist
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        table_exist(cursor, "Summary")
        table_exist(cursor, "Place")
        
        image_list = get_all_images(self.input_dir) # traverse all image files
        image_list_processed = get_all_image_from_table(cursor, "Place") # get image files that have been processed
        image_list = remove_processed_image(image_list, image_list_processed) # remove image files that have been processed
        image_list.sort()
        
        image_number = len(image_list)
        image_cnt = 0
        for image_file in image_list: # process in for loop
            key_value_dict = dict()
            gps_info = get_gps_info(image_file) # get GPS location info
            if gps_info is None: # No GPS location info
                image_cnt += 1
                continue
            
            s_time = time.time()
            address = get_address_from_gps(gps_info, api_key, secret_key) # parse detailed address
            if address is None: # error happen
                image_cnt += 1
                continue
            # extract address information
            nation = address["nation"]
            province = address["province"]
            city = address["city"]
            district = address["district"]
            street = address["street"]
            street_number = address["street_number"]
            # make dirs
            if not os.path.exists(os.path.join(self.output_dir, "Place", province, city, district)):
                os.makedirs(os.path.join(self.output_dir, "Place", province, city, district))
            # check image name
            _, image_name = os.path.split(image_file)
            if os.path.exists(os.path.join(self.output_dir, "Place", province, city, district, image_name)):
                image_name_address = random_rename(image_name)
            else:
                image_name_address = image_name
            # build image link
            try:
                build_image_link(image_file, os.path.join(self.output_dir, "Place", province, city, district, image_name_address))
            except Exception:
                print("Error happened when building image link of %s" % image_file)
                image_cnt += 1
                continue
            
            # prepare data for database
            key_value_dict["gps_latitude_d"] = gps_info["GPSLatitudeRef"]
            key_value_dict["gps_latitude"] = gps_info["GPSLatitude"]
            key_value_dict["gps_longitude_d"] = gps_info["GPSLongitudeRef"]
            key_value_dict["gps_longitude"] = gps_info["GPSLongitude"]
            key_value_dict["nation"] = nation
            key_value_dict["province"] = province
            key_value_dict["city"] = city
            key_value_dict["district"] = district
            key_value_dict["street"] = street
            key_value_dict["street_number"] = street_number 
            key_value_dict["image_name_address"] = image_name_address
            # write data into database
            insert_image_into_table(cursor, "Place", key_value_dict)
            
            # update or insert
            if image_in_table(cursor, "Summary", image_file): 
                update_image_in_table(cursor, "Summary", image_file, key_value_dict)
            else:
                key_value_dict["image_file"] = image_file 
                md5 = calculate_md5(image_file)
                key_value_dict["md5"] = md5
                insert_image_into_table(cursor, "Summary", key_value_dict)
            conn.commit()
            print("Place processing: %s" % image_file)
            # update process percent, and emit signal
            image_cnt += 1
            if self.ui_invoke:
                progress_pct = int(image_cnt / image_number * 100)
                self.signal.emit(progress_pct, "place")
            
            # tencent lbs api QPS=5 for personal developer. 
            time_interval = time.time() - s_time
            if time_interval < 0.2:
                time.sleep(0.2 - time_interval)
        
        conn.close()
        print("All images are sorted by address.")


class PeopleThread(QThread):
    signal = pyqtSignal(int, str) # signal object
    def __init__(self):
        super(PeopleThread, self).__init__()
        self.database = os.path.join("record", "info.db") # datebase
        self.method = "dlib" # face detection method
        self.dist_threshold = 0.2 # face distance 
        self.input_dir = None # input directory
        self.output_dir = None # output directory
        self.ui_invoke = False # whether invoke by ui
    
    
    def run(self):
        """
        遍历输入文件夹中的所有文件，检测人脸，计算人脸特征，为图片中的人脸找到归属。
        Traverse input directory to get all image files; detect face, calculate face feature, 
        find face attribution for every image.
        pipeline: 
            check if related table exists or not,
            traverse all image files, 
            remove image files that have been processed, 
            load face feature, face number, face_name
            process image in for loop:
                get image face bbox and feature, 
                search for classification, 
                build image link, 
                write data into database.
        """
        # 检查表Summary和People是否存在
        # check if table Summary and People exist
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        table_exist(cursor, "Summary")
        table_exist(cursor, "People")
        # 获取所有即将进行处理的图片
        # get all images to be processed
        image_list = get_all_images(self.input_dir) # traverse all image files
        image_list_processed = get_all_image_from_table(cursor, "People") # get processed image files
        image_list = remove_processed_image(image_list, image_list_processed) # remove processed files
        image_list.sort()
        # 加载人脸特征矩阵，人脸数量统计值以及人脸姓名
        # load face feature, counts, names for classification
        feature_centers = load_feature_centers()
        if feature_centers is None: # initialize related data when first invoking
            feature_centers, face_numbers, face_names = init_feature_center()
        else:
            face_numbers = load_face_numbers()
            face_names = load_face_names()
        # 在for循环依次获取图片中的人脸边框、特征和归属
        # get face bbox/feature/classification of image in for-loop
        image_number = len(image_list)
        image_cnt = 0
        for image_file in image_list:
            key_value_dict = dict()
            result = get_face_features(image_file, self.method) # get face bbox and feature in image
            # 处理过程中发生错误或者没有人脸/特征
            # error happen or no face/feature
            if result is None:
                image_cnt += 1
                continue
            # 为每张人脸找到对应的归属分类
            # find classification for each face
            bboxs, features = result
            persons = [] # to store face classification
            for feature in features:
                find_flag, p_index = KNN_search(feature_centers, feature, self.dist_threshold)
                # 找到了合适的归属
                # find proper distribution class
                if find_flag:
                    # 对应人脸的中心特征（即平均特征）
                    # corresponding face center(average face feature)
                    feature_center = feature_centers[p_index]
                    # 对应人脸的当前照片数目
                    # corresponding face number
                    f_number = face_numbers[p_index]
                    # 计算新的人脸中心特征（因为有新的人脸图片加入）
                    # calculate new_feture_center
                    feature_center = update_feature_center(feature_center, f_number, feature)
                    
                    # 更新对应人脸的特征
                    # update corresponding face feature
                    feature_centers[p_index] = feature_center
                    # 更新对应人脸的数目
                    # update corresponding face number
                    face_numbers[p_index] = f_number + 1
                    persons.append(face_names[p_index])# add result
                # 没有找到合适的归属
                # not find proper distribution class
                else:
                    # 添加新的特征，添加新人脸数量（1），添加新人名（Person_%04d形式）
                    # add new feature, new face number  and new face name (Person_%04d)
                    feature_centers, face_numbers, face_names = add_feature_center(feature_centers, face_numbers, face_names, feature)
                    persons.append(face_names[-1]) # add result
            
            # make directory, build image link
            image_name_persons = []
            for person in persons:
                # 新建文件夹，如果image link存在同名文件，对image link重命名
                # make directory and rename image link when image link with the same name exists
                if not os.path.exists(os.path.join(self.output_dir, "People", person)):
                    os.makedirs(os.path.join(self.output_dir, "People", person))
                _, image_name = os.path.split(image_file)
                if os.path.exists(os.path.join(self.output_dir, "People", person, image_name)):
                    image_name_person = random_rename(image_name)
                else:
                    image_name_person = image_name
                # 创建图片链接
                # build image link
                try:
                    build_image_link(image_file, os.path.join(self.output_dir, "People", person, image_name_person))
                    image_name_persons.append(image_name_person)
                except Exception: # when error happen, append None
                    print("Error happened when building image link of %s" % image_file)
                    image_name_persons.append(None)
            
            # 将数据写入数据库
            # write data into database
            key_value_dict["bbox"] = json.dumps(bboxs) # face bounding box
            features = [feature.tolist() for feature in features]
            key_value_dict["feature"] = json.dumps(features) # face feature
            key_value_dict["person"] = json.dumps(persons) # face classification
            key_value_dict["image_name_person"] = json.dumps(image_name_persons) # image link name
            insert_image_into_table(cursor, "People", key_value_dict)
            # if image_file item has already in Table Summary, update; otherwise insert new
            if image_in_table(cursor, "Summary", image_file): 
                update_image_in_table(cursor, "Summary", image_file, key_value_dict)
            else:
                key_value_dict["image_file"] = image_file # image file
                md5 = calculate_md5(image_file)
                key_value_dict["md5"] = md5 # md5
                insert_image_into_table(cursor, "Summary", key_value_dict)
            conn.commit()
            
            # send signal of percent number of processed images
            print("People processing: %s" % image_file)
            image_cnt += 1
            if self.ui_invoke:
                progress_pct = int(image_cnt / image_number * 100)
                self.signal.emit(progress_pct, "people")
        
        # 将更新后的人脸特征、人脸数目和人脸姓名写入本地文件
        # save updated face features, face numbers and face names into local files
        save_feature_centers(feature_centers)
        save_face_numbers(face_numbers)
        save_face_names(face_names)
        conn.close()
        print("All images are sorted by face.")


class ThingThread(QThread):
    signal = pyqtSignal(int, str) # signal object
    def __init__(self):
        super(ThingThread, self).__init__()
        self.database = os.path.join("record", "info.db") # datebase
        self.input_dir = None # input directory
        self.output_dir = None # output directory
        self.ui_invoke = False # whether invoke by ui
    
    
    def run(self):
        """
        使用事物分类标签对照片进行整理。请注意，因为每张照片可以有若干个不同的分类标签，因此在
        整理的过程中会建立若干个不同链接，同时将记录写入数据库中。
        Sort image by thing classification. Note that an image can have several different 
        thing classification tags, so an image may have several different image link.
        pipeline:
            check if related table exists or not,
            traverse all image files, 
            remove image files that have been processed, 
            process image in for loop:
                get thing classification result, 
                build image link, 
                write data into database.
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        table_exist(cursor, "Summary")
        table_exist(cursor, "Thing")
        
        image_list = get_all_images(self.input_dir) # traverse all image files
        image_list_processed = get_all_image_from_table(cursor, "Thing") # get processed image files
        image_list = remove_processed_image(image_list, image_list_processed) # remove processed files
        image_list.sort()
        
        print("I'm sorry, but this function hasn't been built because of lacking of proper model.")


class CheckThread(QThread):
    signal = pyqtSignal(int) # signal object
    def __init__(self):
        super(CheckThread, self).__init__()
        self.database = os.path.join("record", "info.db") # datebase
        self.output_dir = None # output directory
        self.ui_invoke = False # whether invoke by ui
    
    
    def run(self):
        """
        检查表中的image file的源图片是否还存在。如果不存在，则将对应的图片链接全部删除，
        并删除表中的对应项目。
        Check if image files in database still exists. If not, delete data item, remove 
        related image link.
        pipeline:
            check if related table exists or not,
            get all image files in table Summary,
            process image file in for loop:
                check if image file exists,
                if not, delete data item, remove image link
        """
        # check table
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        table_exist(cursor, "Summary")
        table_exist(cursor, "Date")
        table_exist(cursor, "Place")
        table_exist(cursor, "People")
        table_exist(cursor, "Thing")
        # get all image files
        image_list = get_all_image_from_table(cursor, "Summary")
        image_list.sort()
        
        # process in for loop
        image_number = len(image_list)
        image_cnt = 0
        for image_file in image_list:
            if not os.path.exists(image_file):
                # query image links, and delete image_file records
                image_links = query_image_links(cursor, image_file)
                for image_link in image_links:
                    os.remove(os.path.join(self.output_dir, image_link))
                # delete image_file records from tables
                delete_image_from_table(cursor, "Summary", image_file)
                delete_image_from_table(cursor, "Date", image_file)
                delete_image_from_table(cursor, "Place", image_file)
                delete_image_from_table(cursor, "People", image_file)
                delete_image_from_table(cursor, "Thing", image_file)
                print("Invalid image links of %s have been deleted." % image_file)
            
            image_cnt += 1
            if self.ui_invoke:
                progress_pct = int(image_cnt / image_number * 100)
                self.signal.emit(progress_pct)
        print("All image files' existence checked.")


def parse_args():
    """
    命令行解析器。
    Command line parsing function.
    
    :param None:
    :return args: arguments, argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='Image sorting script by date/week/location/face/thing',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input_dir", required=True, type=str, 
                        help="input directory, complete route recommended")
    parser.add_argument("--output_dir", required=True, type=str, 
                        help="output directory")
    parser.add_argument("--key_file", required=False, type=str, default=os.path.join("model", "key_file.txt"), 
                        help="tencent lbs service key")
    parser.add_argument("--date", required=False, action="store_true", 
                        help="whether sort image by date or not")
    parser.add_argument("--place", required=False, action="store_true", 
                        help="whether sort image by address or not")
    parser.add_argument("--people", required=False, action="store_true", 
                        help="whether sort image by human face or not")
    parser.add_argument("--thing", required=False, action="store_true", 
                        help="whether sort image by thing classification")
    parser.add_argument("--check", required=False, action="store_true", 
                        help="check source images exist or not")
    args = parser.parse_args()
    return args