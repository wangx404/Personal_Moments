#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: wangx
"""

import os, time
import sqlite3
import json
from collections import defaultdict
from common_utils import get_all_images, random_rename, remove_processed_image,\
                        load_api_key, build_image_link, calculate_md5
from database_utils import table_exist, get_image_file_from_table, get_image_item_from_table,\
                            insert_image_into_table, update_image_in_summary, delete_image_from_table,\
                            parse_image_item
import argparse


DATABASE = os.path.join("model", "info.db")


def sort_images_by_date(input_dir, output_dir):
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
            write data into database,
    
    :param input_dir: directory containing all your images, str
    :param output_dir: target directory to contain sorted images, str
    :return None:
    """
    from date_utils import get_time_stamp, date2week_date
    # check if Summary and DateWeek exist
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    table_exist(cursor, "Summary")
    table_exist(cursor, "DateWeek")
    
    image_list = get_all_images(input_dir) # traverse all image files
    image_list_processed = get_image_file_from_table(cursor, "DateWeek") # get image files that have been processed
    image_list = remove_processed_image(image_list, image_list_processed) # remove image files that have been processed
    image_list.sort()
    
    date_image_dict = defaultdict(list) # container
    for image_file in image_list: # get image create date
        date = get_time_stamp(image_file)
        date_image_dict[date].append(image_file)
    
    key_value_dict = dict()
    dates = list(date_image_dict.keys())
    dates.sort()
    for date in dates: # process image file in for loop
        # create directory under output_dir/Date/
        if not os.path.exists(os.path.join(output_dir, "Date", date)):
            os.makedirs(os.path.join(output_dir, "Date", date))
        # create directory under output_dir/Week/
        week = date2week_date(date)
        if not os.path.exists(os.path.join(output_dir, "Week", week)):
            os.makedirs(os.path.join(output_dir, "Week", week))
        
        # create image link in corresponding directory
        image_list = date_image_dict[date]
        for image_file in image_list:
            _, image_name = os.path.split(image_file)
            
            # check name, build image link, jump exception 
            if os.path.exists(os.path.join(output_dir, "Date", date, image_name)):
                image_name_date = random_rename(image_name)
            else:
                image_name_date = image_name
            if os.path.exists(os.path.join(output_dir, "Week", week, image_name)):
                image_name_week = random_rename(image_name)
            else:
                image_name_week = image_name
            try:
                build_image_link(image_file, os.path.join(output_dir, "Date", date, image_name_date))
                build_image_link(image_file, os.path.join(output_dir, "Week", week, image_name_week))
            except Exception:
                print("Error happened when building image link of %s" % image_file)
                continue
            # write data into database
            key_value_dict["image_file"] = image_file
            md5 = calculate_md5(image_file)
            key_value_dict["md5"] = md5
            key_value_dict["create_date"] = date
            key_value_dict["image_name_date"] = image_name_date
            key_value_dict["create_week"] = week
            key_value_dict["image_name_week"] = image_name_week
            insert_image_into_table(cursor, "DateWeek", key_value_dict)
            update_image_in_summary(cursor, key_value_dict)
            conn.commit()
            print("Date/Week processing: %s" % image_file)
    
    conn.close()        
    print("All images are sorted by date.")


def sort_images_by_place(input_dir, output_dir, key_file):
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
            
    :param input_dir: directory containing all your images, str
    :param output_dir: target directory to contain sorted images, str
    :param key_file: txt file containing API key, str
    :return None:
    """
    from gps_utils import get_gps_info, get_address_from_gps
    # load api keys, if keys don't exist, return
    api_key_dict = load_api_key(key_file) 
    for key in ("api_key", "secret_key"):
        if key not in api_key_dict.keys():
            return 
    api_key = api_key_dict["api_key"]
    secret_key = api_key_dict["secret_key"]
        
    # check if Summary and Place exist
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    table_exist(cursor, "Summary")
    table_exist(cursor, "Place")
    
    image_list = get_all_images(input_dir) # traverse all image files
    image_list_processed = get_image_file_from_table(cursor, "Place") # get image files that have been processed
    image_list = remove_processed_image(image_list, image_list_processed) # remove image files that have been processed
    image_list.sort()
    
    key_value_dict = dict()
    for image_file in image_list: # process in for loop
        gps_info = get_gps_info(image_file) # get GPS location info
        if gps_info is None: # No GPS location info
            continue
        
        s_time = time.time()
        address = get_address_from_gps(gps_info, api_key, secret_key) # detailed address
        if address is None: # error happen
            continue
        nation = address["nation"]
        province = address["province"]
        city = address["city"]
        district = address["district"]
        street = address["street"]
        street_number = address["street_number"]
        
        # make dirs
        if not os.path.exists(os.path.join(output_dir, "Place", province, city, district)):
            os.makedirs(os.path.join(output_dir, "Place", province, city, district))
        # check image name
        _, image_name = os.path.split(image_file)
        if os.path.exists(os.path.join(output_dir, "Place", province, city, district, image_name)):
            image_name_address = random_rename(image_name)
        else:
            image_name_address = image_name
        # build image link
        try:
            build_image_link(image_file, os.path.join(output_dir, "Place", province, city, district, image_name_address))
        except Exception:
            print("Error happened when building image link of %s" % image_file)
            continue
        
        # prepare data for database
        key_value_dict["image_file"] = image_file 
        md5 = calculate_md5(image_file)
        key_value_dict["md5"] = md5
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
        update_image_in_summary(cursor, key_value_dict)
        conn.commit()
        print("Place processing: %s" % image_file)
        
        # tencent lbs api QPS=5 for personal developer. 
        time_interval = time.time() - s_time
        if time_interval < 0.2:
            time.sleep(0.2 - time_interval)
    
    conn.close()
    print("All images are sorted by address.")


def sort_images_by_people(input_dir, output_dir, method="dlib", dist_threshold=0.2):
    """
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
    
    :param input_dir: directory containing all your images, str
    :param output_dir: target directory to contain sorted images, str
    :param method: face detection method, str
    :return None:
    """
    from face_utils import load_feature_centers, load_face_numbers, load_face_names,\
                        get_face_features, init_feature_center, KNN_search,\
                        update_feature_center, add_feature_center,\
                        save_feature_centers, save_face_numbers, save_face_names
    
    # check if Summary and Place exist
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    table_exist(cursor, "Summary")
    table_exist(cursor, "People")
    
    image_list = get_all_images(input_dir) # traverse all image files
    image_list_processed = get_image_file_from_table(cursor, "People") # get processed image files
    image_list = remove_processed_image(image_list, image_list_processed) # remove processed files
    image_list.sort()
    
    # load face feature, counts, names for classification
    feature_centers = load_feature_centers()
    if feature_centers is None:
        feature_centers, face_numbers, face_names = init_feature_center()
    else:
        face_numbers = load_face_numbers()
        face_names = load_face_names()
    
    # get image face/feature/classification in for loop
    key_value_dict = dict()
    for image_file in image_list:
        result = get_face_features(image_file, method) # get face bbox and feature in image
        if result is None: # error happen or no face/feature
            continue
        
        bboxs, features = result
        persons = [] # to store face classification
        for feature in features:
            flag, p_index = KNN_search(feature_centers, feature, dist_threshold)
            # find proper distribution class
            if flag:
                feature_center = feature_centers[p_index] # current face center(average face feature)
                f_number = face_numbers[p_index] # current face number
                feature_center = update_feature_center(feature_center, f_number, feature) # calculate new_feture_center
                
                #feature_centers[p_index] = feature_center  # update corresponding face feature
                face_numbers[p_index] = f_number + 1 # update corresponding face number
                persons.append(face_names[p_index]) # add result
            # not find proper distribution class
            else:
                # add new feature, new face number and new face name
                feature_centers, face_numbers, face_names = add_feature_center(feature_centers, face_numbers, face_names, feature)
                persons.append(face_names[-1]) # add result
        
        # make directory, build image link
        image_name_persons = []
        for person in persons:
            # make directory and rename
            if not os.path.exists(os.path.join(output_dir, "People", person)):
                os.makedirs(os.path.join(output_dir, "People", person))
            _, image_name = os.path.split(image_file)
            if os.path.exists(os.path.join(output_dir, "People", person, image_name)):
                image_name_person = random_rename(image_name)
            else:
                image_name_person = image_name
            # build image link
            try:
                build_image_link(image_file, os.path.join(output_dir, "People", person, image_name_person))
                image_name_persons.append(image_name_person)
            except Exception: # when error happen, append None
                print("Error happened when building image link of %s" % image_file)
                image_name_persons.append(None)
        
        # write data into database
        key_value_dict["image_file"] = image_file # image file
        md5 = calculate_md5(image_file)
        key_value_dict["md5"] = md5 # md5
        key_value_dict["bbox"] = json.dumps(bboxs) # face bounding box
        features = [feature.tolist() for feature in features]
        key_value_dict["feature"] = json.dumps(features) # face feature
        key_value_dict["person"] = json.dumps(persons) # face classification
        key_value_dict["image_name_person"] = json.dumps(image_name_persons) # image link name
        insert_image_into_table(cursor, "People", key_value_dict)
        update_image_in_summary(cursor, key_value_dict)
        conn.commit()
        print("People processing: %s" % image_file)
    
    # save data into file
    save_feature_centers(feature_centers)
    save_face_numbers(face_numbers)
    save_face_names(face_names)
    conn.close()
    print("All images are sorted by face.")


def sort_images_by_thing(input_dir, output_dir): # To be constructed, not have proper model yet
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
    
    :param input_dir: directory containing all your images, str
    :param output_dir: target directory to contain sorted images, str
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    table_exist(cursor, "Summary")
    table_exist(cursor, "Thing")
    
    image_list = get_all_images(input_dir) # traverse all image files
    image_list_processed = get_image_file_from_table(cursor, "THing") # get processed image files
    image_list = remove_processed_image(image_list, image_list_processed) # remove processed files
    image_list.sort()
    
    print("I'm sorry, but this function hasn't been built because of lacking proper model.")


def check_source_image_existence(output_dir):
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
    
    :param output_dir: output directory (where image link stores), str
    :return None:
    """
    # check table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    table_exist(cursor, "Summary")
    table_exist(cursor, "DateWeek")
    table_exist(cursor, "Place")
    table_exist(cursor, "People")
    table_exist(cursor, "Thing")
    # get all image files
    image_list = get_image_file_from_table(cursor, "Summary")
    image_list.sort()
    # process in for loop
    for image_file in image_list:
        if not os.path.exists(image_file):
            image_item = get_image_item_from_table(cursor, "Summary", image_file)
            # delete image item from tables
            delete_image_from_table(cursor, "Summary", image_file)
            delete_image_from_table(cursor, "DateWeek", image_file)
            delete_image_from_table(cursor, "Place", image_file)
            delete_image_from_table(cursor, "People", image_file)
            delete_image_from_table(cursor, "Thing", image_file)
            # parse image item and delete image links
            image_links = parse_image_item(image_item)
            for image_link in image_links:
                os.remove(os.path.join(output_dir, image_link))
            print("Invalid image links of %s have been deleted." % image_file)
    
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


if __name__ == "__main__":
    args = parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir
    if args.date:
        sort_images_by_date(input_dir, output_dir)
    if args.place:
        key_file = args.key_file
        sort_images_by_place(input_dir, output_dir, key_file)
    if args.people:
        sort_images_by_people(input_dir, output_dir, "dlib", 0.2)
    if args.thing:
        sort_images_by_thing(input_dir, output_dir)
    if args.check:
        check_source_image_existence(output_dir)
