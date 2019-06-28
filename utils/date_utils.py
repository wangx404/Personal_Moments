#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 14:21:00 2019
@author: wangxin
"""

import os, time, datetime
import imghdr
from PIL import Image


def _get_time_stamp_by_exif(image_file):
    """
    通过文件的exif信息获取文件的创建日期。
    Get the creating date of an image through its EXIF.
    注意：此函数要求EXIF信息中的时间戳格式为"YYYY:MM:DD HH:mm:SS"
    Attention: this function requires time stamp in EXIF has the format of "YYYY:MM:DD HH:mm:SS"
    
    :param image_file: str, image file path
    :return time_str: str, time string in format of "YYYY-MM-DD"
    """
    tags = Image.open(image_file)._getexif()
    time_str = tags[36868]
    time_str = time_str.split(" ")[0]
    if time_str.count(":") != 2:
        raise Exception("Error with image exif")
    time_str = time_str.replace(":", "-")
    return time_str


def _get_time_stamp_by_file(image_file):
    """
    通过文件的属性信息获取文件的创建日期。
    Get the creating date of an image through its file information.
    
    :param image_file: str, image file path
    :return time_str: str, time string in format of "YYYY-MM-DD"
    """
    # 获取文件创建时间
    time_str = min(os.path.getctime(image_file), os.path.getmtime(image_file))
    time_str = time.localtime(time_str)
    time_str = time.strftime("%Y-%m-%d", time_str)
    return time_str


def get_time_stamp(image_file):
    """
    获取输入图像文件的创建日期。
    Get the creating date of an image file.
    对于包含exif信息的图像，通过exif信息查询创建日期，否则通过属性信息查询创建日期。
    If the image contains EXIF infromation, get the date by EXIF. Otherwise, 
    get the date by file information.
    
    :param image_file: str, image file path
    :return time_str: str, time string in format of "YYYY-MM-DD"
    """
    image_format = imghdr.what(image_file)
    if image_format not in ("jpeg", "tiff"): # jpeg/tiff image has EXIF
        time_str = _get_time_stamp_by_file(image_file)
    else:
        # if error occurs during reading process, use another function
        try:
            time_str = _get_time_stamp_by_exif(image_file)
        except Exception:
            time_str = _get_time_stamp_by_file(image_file)
    return time_str


def date2week_date(date):
    """
    将输入的date转化为date所在week的date字符串。
    例如2010.01.01属于2009年第53周第5天，那么由此可知本周的起止日期为：
    2009.12.28-2010.01.03。
    即输入2010-01-01,输出2009-12-28to2010-01-03。
    Transform a date string to week string which the specific date belongs to.
    For example, 2010.01.01 is the 5th day of the 53th week of 2009, so this week's 
    beginning date is 2009.12.28, and ending date is 2010.01.03.
    So when inputing 2010.01.01, this function outputs 2009.12.28-2010.01.03
    
    :param date: str, date string in format of "YYYY-MM-DD"
    :return : str, starting date to ending date of this week
    """
    # 处理成datetime格式
    dates = date.split("-")
    dates = [int(element) for element in dates]
    year, month, day = dates
    date = datetime.date(year, month, day)
    # 计算年，周，第几日
    _, week_index, day_index = date.isocalendar()
    # 获取本周的起止日期
    start_date = date - datetime.timedelta(days=day_index-1)
    start_date = start_date.isoformat()
    end_date = date + datetime.timedelta(days=7-day_index)
    end_date = end_date.isoformat()
    return start_date + "to" + end_date

