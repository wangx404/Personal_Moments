#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue May 14 15:06:46 2019
@author: wangxin
"""

import imghdr, os
from PIL import Image
import requests
import hashlib
import json
from .common_utils import load_api_key


def _calculate_degree(degree_list):
    """
    输入嵌套列表，解析得到GPS纬度/经度数值。
    Calculate GPS latitude/longitude degree given nested list.
    
    :param degree_list: GPS latitude/longtitude degree list, nested list
    :return DD: GPS latitude/longtitude decimal degree, float
    """
    degree = degree_list[0]
    degree = float(degree[0] / degree[1])
    minute = degree_list[1]
    minute = float(minute[0]/ minute[1])
    second = degree_list[2]
    second = float(second[0]/ second[1])
    DD = degree + minute / 60.0 + second / 3600.0
    return DD


def _transform_gps_format(gps_info):
    """
    将GPS信息从原始格式转化为标准格式。
    Transfrom GPS info from origin format to standard format.
    
    :param gps_info: origin GPS information, dict
    :param new_gps_info: transformed GPS information, dict
    """
    new_gps_info = dict()
    for key in (1,2,3,4): # make sure latitude and longitude information exists
        if key not in gps_info.keys():
            print("No latitude/longitude info in GPS.")
            return None
    new_gps_info["GPSLatitudeRef"] = gps_info[1]
    new_gps_info["GPSLatitude"] = _calculate_degree(gps_info[2])
    new_gps_info["GPSLongitudeRef"] = gps_info[3]
    new_gps_info["GPSLongitude"] = _calculate_degree(gps_info[4])
    # calculate altitude
    if 6 not in gps_info.keys():
        new_gps_info["GPSAltitude"] = None
    else:
        new_gps_info["GPSAltitude"] = float(gps_info[6][0] / gps_info[6][1])
    return new_gps_info


def get_gps_info(image_file):
    """
    如果图片的EXIF信息中存在GPS信息，将其提取返回。
    Get the GPS information if it exists in image.
    
    :param image_file: image file path, str
    :return gps_info: gps information, dict/None
    """
    image_format = imghdr.what(image_file)
    if image_format not in ("jpeg", "tiff"): # Other formats don't have EXIF
        print("%s does not have EXIF information." % image_file)
        return None
    
    tags = Image.open(image_file)._getexif()
    if tags == None:
        print("%s deos not have EXIF information." % image_file)
        return None
    
    if 34853 not in tags.keys(): # No GPS info
        print("%s does not have GPS information in EXIF." % image_file)
        return None
    
    gps_info = tags[34853] # GPS information key is 34853
    gps_info = _transform_gps_format(gps_info)
    return gps_info


def _calculate_sig(path, param, secret_key):
    """
    计算api调用签名。
    Calculate api invoke signature.
    
    :param path: invoke path, str
    :param param: invoke parameters, str
    :param secret_key: invoke secret key, str
    :return sig: signature, str
    """
    string = path + "?" + param + secret_key
    string = string.encode()
    hash_md5 = hashlib.md5(string)
    return hash_md5.hexdigest()


def _extract_address(response):
    """
    从url get请求的回应中提取地址信息。
    Extract address information from url get response.
    
    :param response: url get response, requests.response
    :return address_info: address information, dict
    """
    data = response.content
    data = json.loads(data)
    address_info = data["result"]["address_component"]
    return address_info


def transform_address_format(address):
    """
    将中国以外的坐标转化为通用的标准格式。
    Transform address which is outside of China into standard format.
    
    :param address: address outside of China, dict
    :return new_adress: address of standard format, dict
    """
    new_address = dict()
    new_address["nation"] = "海外"
    new_address["province"] = address["nation"]
    if ("ad_level_1" in address.keys()) and (address["ad_level_1"] != ""):
        new_address["city"] = address["ad_level_1"]
    else:
        new_address["city"] = "Unknown"
    if ("ad_level_2" in address.keys()) and (address["ad_level_2"] != ""):
        new_address["district"] = address["ad_level_2"]
    else:
        new_address["district"] = "Unknown"
    new_address["street"] = None
    new_address["street_number"] = None
    return new_address


def get_address_from_gps(gps_info, api_key, secret_key):
    """
    将GPS信息转化为地址信息。
    Get address information from GPS information by invoking Tencent API service.
    
    :param gps_info: GPS information, dict
    :param api_key: API invoke key, str
    :param secret_key: API secret key for verification, str 
    :return address: address information, dict
    """
    # get latitude/longitude
    latitude = "%.6f" % gps_info["GPSLatitude"]
    longitude = "%.6f" % gps_info["GPSLongitude"]
    # calculate invoking signature
    invoke_server = "https://apis.map.qq.com"
    invoke_path = "/ws/geocoder/v1"
    invoke_param = "key=%s&location=%s,%s" % (api_key, latitude, longitude)
    invoke_sig = _calculate_sig(invoke_path, invoke_param, secret_key)
    # concat invoking url
    url = "%s%s?%s&sig=%s" % (invoke_server, invoke_path, invoke_param, invoke_sig)
    # invoke API service
    try:
        response = requests.get(url)
        address = _extract_address(response)
    except Exception: # unexpected error
        print("Error happened when querying address.")
        return None
    # address check
    if address["nation"] == "": # No country area
        return None
    if address["nation"] != "中国":
        address = transform_address_format(address)
    return address


def gps_test(key_file):
    """
    Test GPS module.
    
    :param key_file: key txt file, str
    :return None:
    """
    if not os.path.exists(key_file):
        print("You have not set your API key and secret key.") # no key file
        return -1
    
    api_key_dict = load_api_key(key_file)
    # check api key
    for key in ("api_key", "secret_key"):
        if (key not in api_key_dict.keys()) or ("{" in api_key_dict[key]):
            print("You should save your API key with given format in %s" % key_file) # unvalid file format
            return -2 
    
    api_key = api_key_dict["api_key"]
    secret_key = api_key_dict["secret_key"]
    gps_info = dict()
    gps_info["GPSLatitude"] = 38.901859
    gps_info["GPSLongitude"] = -77.026584
    address = get_address_from_gps(gps_info, api_key, secret_key)
    print("API invoking result ", address)
    gps_info["GPSLatitude"] = 39.989469
    gps_info["GPSLongitude"] = 116.305961
    address = get_address_from_gps(gps_info, api_key, secret_key)
    print("API invoking result ", address)
    
    if address is None:
        print("API invoking error, please check network connection or verify your API key.") # api invoke error
        return 1
    else:
        return 0 # success


if __name__ == "__main__":
    key_file = os.path.join("..", "record", "key_file.txt")
    gps_test(key_file)