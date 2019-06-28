#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:20:09 2019
@author: wangxin
"""

import hashlib
import os, shutil, random
import imghdr
import json
from .face_utils import load_face_names, save_face_names
from .thing_utils import load_thing_names, save_thing_names


def get_all_images(input_dir):
    """
    遍历获取输入文件夹内的所有图像文件。
    Traverse specific directory to get all images in it.
    
    :param input_dir: str, input directory
    :return image_list: list, image list
    """
    image_list = []
    results = os.walk(input_dir)
    for result in results:
        dir_path, _, image_files = result
        for image_file in image_files:
            if imghdr.what(os.path.join(dir_path, image_file)): # this is an image file
                image_list.append(os.path.join(dir_path, image_file))
    return image_list


def remove_processed_image(image_list, image_list_processed):
    """
    将已处理的图片从待处理的图片列表中移除。
    Romove processed image file from image list to be processed.
    
    :param image_list: image file list to be processed, list
    :param image_list_processed: image file list that have been processed, list
    :return : unprocessed image file list, list
    """
    image_list = set(image_list)
    for image_file in image_list_processed:
        if image_file in image_list:
            image_list.remove(image_file)
    return list(image_list)


def random_rename(image_name):
    """
    通过在图片名后追加随机数字的方式更改图片文件名称。
    Random rename an image file by adding random number to image name.
    
    :param image_name: origin image name, str
    :return image_name: new image name, str
    """
    index = random.randint(0, 9999)
    prefix, suffix = os.path.splitext(image_name)
    image_name = prefix + "_%4d" % index + suffix
    return image_name


def calculate_md5(image_file):
    """
    计算图片文件的md5值作为唯一标识符。
    Calculate md5 calue of image file as its identifier.
    
    :param image_file: image file, str
    :return md5: md5 value, str
    """
    f = open(image_file, "rb").read()
    md5 = hashlib.md5(f).hexdigest()
    return md5


def build_image_link(src_image, dst_image, method="softlink"):
    """
    根据method对图片进行操作处理（复制，移动，建立软链接，建立硬链接）。
    Copy/Move/Build soft(symbolic) link/Build hard link from source image to 
    target image according to given method.    

    :param src_image: source image file, str
    :param dst_image: target image file, str
    :param method: operate method, str
    :return None:
    """
    
    if method == "softlink":
        os.symlink(src_image, dst_image)
    elif method == "hardlink":
        os.link(src_image, dst_image)
    elif method == "copy":
        shutil.copy(src_image, dst_image)
    elif method == "move":
        shutil.move(src_image, dst_image)
    else:
        raise ValueError


def load_api_key(key_file):
    """
    从文本文件中加载API秘钥。
    Load API key and secret key from txt file.
    
    :param key_file: txt file containing API key, str
    :return api_key_dcit: dict object, dict
    """
    with open(key_file, "r") as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    lines = [line.split(":") for line in lines]
    api_key_dcit = dict()
    for line in lines:
        api_key_dcit[line[0]] = line[1]
    return api_key_dcit


def save_api_key(key_file, key, secret_key):
    """
    将API秘钥保存至文本文件中。
    Save API key and secret key into txt file.
    
    :param key_file: txt file containing API key, str
    :param key: API key, str
    :param secret_key: API secret key, str
    :return None:
    """
    with open(key_file, "w") as f:
        f.write("api_key:"+key+"\r\n")
        f.write("secret_key:"+secret_key+"\r\n")


def change_dir_name(class_name, old_name, new_name):
    """
    改变文件夹的名称。
    Change name of directory.
    
    :param class_name: name of class (People/Thing), str
    :param old_name: old name, str
    :param new_name: new name, str
    :return None:
    """
    old_dir = os.path.join("IMAGE", class_name, old_name)
    new_dir = os.path.join("IMAGE", class_name, new_name)
    os.rename(old_dir, new_dir)


def change_text_name(class_name, old_name, new_name):
    """
    改变记录在文本中名称。
    Change names in text file.
    
    :param class_name: name of class (People/Thing), str
    :param old_name: old name, str
    :param new_name: new name, str
    :return None:
    """
    # load names from text file
    if class_name == "People":
        name_list = load_face_names()
    else:
        name_list = load_thing_names()
    # modify
    index = name_list.index(old_name)
    name_list[index] = new_name
    # save names into text file
    if class_name == "People":
        save_face_names(name_list)
    else:
        save_thing_names(name_list)
