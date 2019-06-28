#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 16:51:41 2019
@author: wangxin
"""

import os, json
from .face_utils import load_face_names

# 用于表格创建的语句
# SQL strings for table creation
TABLE_CREATIION_DICT = {"Date": """CREATE TABLE Date (image_file nvarchar primart key)""", 
                        
                        "Place": """CREATE TABLE Place (image_file nvarchar primary key)""", 
                        
                        "Thing": """CREATE TABLE Thing (image_file nvarchar primary key)""", 
                        
                        "People": """CREATE TABLE People (image_file nvarchar primary key)""", 
                        
                        "Summary": """CREATE TABLE Summary (image_file nvarchar primary key, 
                        md5 char(32), 
                        create_date date, 
                        image_name_date nvarchar, 
                        create_week char(22), 
                        image_name_week nvarchar, 
                        gps_latitude_d char(1), 
                        gps_latitude decimal(3,6), 
                        gps_longitude_d char(1), 
                        gps_longitude decimal(3,6), 
                        nation nvarchar, 
                        province nvarchar, 
                        city nvarchar,
                        district nvarchar, 
                        street nvarchar, 
                        street_number nvarchar, 
                        image_name_address nvarchar, 
                        top5 nvarchar, 
                        image_name_thing text, 
                        bbox text, 
                        feature text, 
                        person text, 
                        image_name_person text)"""}
# 表格集合
# set of table
TABLES = set(["Date", "Place", "Thing", "People", "Summary"]) # for table name checking


# 从表格中查询所有的省份/省份对应的城市/城市对应的区县
# query all provinces/all cities of selected province/all districts of selected city from table
def get_province_from_table(cursor):
    """
    获取所有省份的名称。
    Get all province names from table.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :return results: province name list, list
    """
    sql_string = "SELECT DISTINCT province FROM Summary"
    results = cursor.execute(sql_string)
    results = [result[0] for result in results] # None exits in list
    return results


def get_city_from_table(cursor, province):
    """
    给定省份名称，获取下辖城市名称。
    Get all city names of given province.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param province: province name, str
    :return results: city name list of province, list
    """
    sql_string = "SELECT DISTINCT city FROM Summary WHERE province=?"
    results = cursor.execute(sql_string, tuple([province])).fetchall()
    results = [result[0] for result in results]
    return results


def get_district_from_table(cursor, city):
    """
    给定城市名称，查询下辖的区域名称。
    Get all district names of given city.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param city: city name, str
    :return results: district name list of city, list
    """
    sql_string = "SELECT DISTINCT district FROM Summary WHERE city=?"
    results = cursor.execute(sql_string, tuple([city])).fetchall()
    results = [result[0] for result in results]
    return results


# 将None值转化为"None"字符串，通过PinYin对列表排序。
# None to "None", sort list by PinYin (not yet).
def sort_query_result(result):
    """
    将None转为"None"，并根据拼音字母进行排序。
    Transform None into "None", and sort the result by Chinese Pinyin (not yet).
    
    :param result: origin query result, list
    :return result: transformed and sorted result, list
    """
    result = ["None" if ele is None else ele for ele in result]
    return result


def _field_is_none(string):
    """
    判断一个字符串是否为None/"None"/""。
    Judge whether string is None/"None"/"" or not.
    
    :param string: origin string, str
    :return : judgement, bool
    """
    empty = [None, "None", ""]
    if string in empty:
        return True
    else:
        return False


def _add_percent_sign(string):
    """
    在字符串前后添加百分号，以便字符串字段的模糊查询。
    Add percent sign in the both sides of a string.
    """
    return "%" + string + "%"


def _add_quotation(string):
    """
    在字符串前后添加单引号。
    Add single quotation mark in the both sides of a string.
    """
    return "'"+string+"'"


def _process_empty_result(results, source):
    """
    如果sql查询结果为空，返回None；否则返回image_file 列表。
    If sql query result is empty, return None, else return image_file list.
    
    :param results: sql query results, nested list
    :param source: source table, str
    :return results: image_file list, list
    """
    if len(results) == 0:
        print("No image file can satisfy given searching conditions in {}".format(source))
        return None
    else:
        results = [result[0] for result in results]
        return results


# 以下为各类搜索函数：多条件搜索、日期搜索、地点搜索、人名搜索和物品搜索。
# Functions below are all kinds of searching functions.
# multiple conditions search, date search, place search, people search, thing search
def all_search(cursor, start_date, end_date, province, city, district, people, thing):
    """
    通过多个搜索条件搜索图片文件，返回结果按照创建时间排序。
    Search image files by multiple searching conditions.
    Returned results are ordered by create date.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param start_date: start date, str
    :param end_date: end date, str
    :param province: province name, str/None
    :param city: city name, str/None
    :param district: district name, str/None
    :param people:
    :param thing:
    :return results: image file list, list
    """
    # construct sql string from given conditions
    conditions = []
    conditions.append("create_date > DATE({})".format(_add_quotation(start_date)))
    conditions.append("create_date < DATE({})".format(_add_quotation(end_date)))
    if not _field_is_none(province):
        conditions.append("province = %s" % _add_quotation(province))
    if not _field_is_none(city):
        conditions.append("city = %s" % _add_quotation(city))
    if not _field_is_none(district):
        conditions.append("district = %s" % _add_quotation(district))
    if not _field_is_none(people):
        conditions.append("person LIKE %s" % _add_quotation(_add_percent_sign(people)))
    if not _field_is_none(thing):
        conditions.append("thing LIKE %s" % _add_quotation(_add_percent_sign(thing)))
    sql_string = "SELECT image_file FROM Summary WHERE " + " AND ".join(conditions) + " ORDER BY create_date"
    # search and process
    results = cursor.execute(sql_string).fetchall()
    return _process_empty_result(results, "All Search") # return None is searching result is empty


def date_search(cursor, start_date, end_date):
    """
    根据给定的日期范围搜索图片文件，返回结果按照创建时间排序。
    Search for image file by given data range.
    Returned results are ordered by create date.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param start_date: start date, str
    :param end_date: end date, str
    :return results: image file list, list
    """
    sql_string = "SELECT image_file FROM Summary WHERE create_date > DATE(?) AND create_date < DATE(?) ORDER BY create_date"
    results = cursor.execute(sql_string, tuple([start_date, end_date])).fetchall()
    return _process_empty_result(results, "Date Search")


def place_search(cursor, province, city, district):
    """
    根据给定的地点名搜索图片文件，返回结果按照创建时间排序。
    Search for image file by given place(province/city/district) name.
    Returned results are ordered by create date.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param province: province name, str/None
    :param city: city name, str/None
    :param district: district name, str/None
    :return results: image file list, list
    """
    if _field_is_none(province):
        sql_string = "SELECT image_file FROM Summary WHERE province IS NOT NULL ORDER BY create_date"
        results = cursor.execute(sql_string).fetchall()
    elif _field_is_none(city):
        sql_string = "SELECT image_file FROM Summary WHERE province = ? ORDER BY create_date"
        results = cursor.execute(sql_string, tuple([province])).fetchall()
    elif _field_is_none(district):
        sql_string = "SELECT image_file FROM Summary WHERE province = ? AND city = ? ORDER BY create_date"
        results = cursor.execute(sql_string, tuple([province, city])).fetchall()
    else:
        sql_string = "SELECT image_file FROM Summary WHERE province = ? AND city = ? AND district = ? ORDER BY create_date"
        results = cursor.execute(sql_string, tuple([province, city, district])).fetchall()
    # check if searching result is empty
    return _process_empty_result(results, "Place Search")


def people_search(cursor, p1, logic, p2):
    """
    根据给定的人名搜索图片文件，返回结果按照创建时间排序。
    Search for image file by given person name.
    Returned results are ordered by create date.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param p1: person one's name, str
    :param loginc: searching logic, str
    :param p2: person two's name, str
    :return results: image file list, list
    """
    sql_string = "SELECT image_file FROM Summary WHERE person LIKE ?"
    if _field_is_none(p2): # only one condition
        sql_string += " ORDER BY create_date"
        results = cursor.execute(sql_string, tuple([_add_percent_sign(p1)])).fetchall()
    else: # two conditions need to be used
        if logic == "AND": # p1 and p2
            sql_string += " AND person LIKE ? ORDER BY create_date"
        elif logic == "OR": # p1 or p2
            sql_string += " OR person LIKE ? ORDER BY create_date"
        elif logic == "NOT": # p1 not p2
            sql_string += " AND person NOT LIKE ? ORDER BY create_date"
        else:
            raise ValueError
        results = cursor.execute(sql_string, tuple([_add_percent_sign(p1), _add_percent_sign(p2)])).fetchall()
    return _process_empty_result(results, "People Search")


def thing_search(cursor, key):
    """
    根据表Summary中的top5字段是否包含key搜索图片文件，返回结果按照时间排序。
    Search from image file by judging whether keyword is in top5 field in table Summary.
    Returned results are ordered by create date.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param key: thing searching key word, str
    :return results: image file list, list
    """
    if key == "":
        return None
    sql_string = "SELECT image_file from Summary WHERE top5 LIKE ? ORDER BY create_date"
    results = cursor.execute(sql_string, tuple([_add_percent_sign(key)])).fetchall()
    return _process_empty_result(results, "Thing Search")


def table_exist(cursor, table, output=False):
    """
    在数据库database中检查是否存在表table，如果不存在则创建对应的新表。
    Check if table exists in database. 
    if table does not exist, create a new table.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param database: database file, str
    :param table: table name, str
    :return None:
    """
    assert table in TABLES, "You should input a correct table name!"
    # check if target table exist
    result = cursor.execute("SELECT name from sqlite_master WHERE type='table' AND name=?", tuple([table])).fetchall()
    if len(result) == 0:
        # create target table
        table_creation = TABLE_CREATIION_DICT[table]
        table_creation = table_creation.replace("\n", "") # replace'\n'
        cursor.execute(table_creation)
        if output:
            print("Table %s is created." % table)
    else:
        if output:
            print("Table %s exists." % table)


# 由于子表的主要意义在于确认image_file是否存在于子表中（若存在，则代表已经处理过），
# 那么子表的结构可以大幅简化。
# As the main purpose of sub tables is to confirm if image_file exists in it.
# If image_file exists, it means that image_file had been processed.
# So the structure of sub tables can be simplified.
def get_all_image_from_table(cursor, table):
    """
    从表table中获取所有的image_file条目。
    Get all image_file items of table in database.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param database: database file, str
    :param table: table name, str
    :return results: all image files of table in database, list
    """
    assert table in TABLES, "You should input correct table name!"
    results = cursor.execute("SELECT image_file from %s" % table).fetchall()
    results = [result[0] for result in results]
    return results


def image_in_table(cursor, table, image_file):
    """
    检查image_file是否存在于表table中。
    Check if image_file in Table table.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param image_file: image file, str
    :return: whether image_file in table, bool
    """
    assert table in TABLES, "You should input correct table name!"
    sql_string = "SELECT image_file FROM %s WHERE image_file=?" % table
    result = cursor.execute(sql_string, tuple([image_file])).fetchall()
    if len(result) != 0:
        return True
    return False


def insert_image_into_subtable(cursor, table, image_file):
    """
    向子表(Date/Place/People/Thing)中插入一条新纪录。
    Insert a new record into subtable (Date/Place/People/Thing).
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param image_file: image file, str
    """
    sql_string = "INSERT INTO %s (image_file) VALUES (?)" % table
    cursor.execute(sql_string, tuple([image_file]))


def _get_insert_string(table, keys):
    """
    获取SQL插入操作的语句。
    Get sql insert string for sql insert operation.
    
    :param table: table name, str
    :param keys: table column names, tuple
    :return sql_string: sql insert string, str
    """
    str_columns = ", ".join(keys)
    str_placeholders = ["?"] * len(keys)
    str_placeholders = ", ".join(str_placeholders)
    sql_string = "INSERT INTO %s (%s) VALUES (%s)" % (table, str_columns, str_placeholders)
    return sql_string


# 在图片处理的过程中，若对应的记录不存在，则向其中插入新纪录。
# When processing images, if image_file does own a record in table, 
# insert a new record into table.
def insert_image_into_table(cursor, table, key_value_dict):
    """
    向特定表格中插入数据项。
    Insert new data item into specific table.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param key_value_dict: key value items, dict
    :return None:
    """
    assert table in TABLES, "You should input a correct table name!"
    
    keys = tuple(key_value_dict.keys())
    values = tuple([key_value_dict[key] for key in keys]) # generator->list->tuple
    sql_string = _get_insert_string(table, keys)
    cursor.execute(sql_string, values)


def _get_update_string(table, image_file, keys):
    """
    给定信息，获取sql更新语句。
    Get sql update string with given information.
    
    :param table: table name, str
    :param image_file: image file, str
    :param keys: items to be set value, tuple
    :return sql_string: sql update string
    """
    keys = [key+"=?" for key in keys]
    keys = ", ".join(keys)
    sql_string = "UPDATE %s SET %s WHERE image_file='%s'" % (table, keys, image_file)
    return sql_string


# 在图片处理的过程中，若对应的记录已存在，则更新其中的内容。
# When processing images, if image_file owns a record in table, 
# update current record
def update_image_in_table(cursor, table, image_file, key_value_dict):
    """
    更新表table中image_file对应的项目。
    Update corresponding image item of image_file in table.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param image_file: image file, str
    :param key_value_dict: key value items, dict
    :return None:
    """
    keys = tuple(key_value_dict.keys())
    values = tuple([key_value_dict[key] for key in keys])
    sql_string = _get_update_string(table, image_file, keys)
    cursor.execute(sql_string, values)


# 以下的函数用于获取按类别分组的图片
# Functions below are used to query images grouped by category
def image_group_by_date(cursor):
    """
    通过创建日期对图片进行分组，为每一个条目返回("Date", "create_date", 创建日期， 图片文件)。
    Group image file by create date, return table_name, item_name, create_date and image_file for each item.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :return new_results: image file grouped by create date, [(str, str, str, str), ]
    """
    sql_string = "SELECT create_date, image_file FROM Summary WHERE create_date IS NOT NULL GROUP BY create_date ORDER BY create_date"
    results = cursor.execute(sql_string).fetchall()
    # transform format of results
    new_results = []
    for result in results:
        create_date, image_file = result
        new_results.append(("create_date", create_date, image_file)) # table name, item name, item value, image file
    return new_results


def image_group_by_place(cursor):
    """
    通过城市名和城区名对图片进行分组，为每一条目返回("city/district", 城市名/城区名，图片文件)。
    Group image file by city and district, return "city/district", city name/district name and image_file for each item.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :return results:  image file grouped by place, [(str, str, str), ]
    """
    results = []
    sql_string = "SELECT city, image_file FROM Summary WHERE city IS NOT NULL GROUP BY city ORDER BY city"
    city_results = cursor.execute(sql_string).fetchall()
    sql_string = "SELECT district, image_file FROM Summary WHERE city = ? AND district IS NOT NULL GROUP BY district ORDER BY district"
    for city_image in city_results:
        city, image_file = city_image
        results.append(("city", city, image_file))
        district_results = cursor.execute(sql_string, tuple([city])).fetchall()
        for district_image in district_results:
            district, image_file = district_image
            results.append(("district", district, image_file))
    return results


# more information is needed to extract face area from original image file.
def image_group_by_person(cursor):
    """
    通过人名（人脸）对图片进行分组，为每一个条目返回("person", 人名，图片文件)。
    Group image file by person name, return "person", person name and image file for each item.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :return results:person image_file list, [(str, str, str), ]
    """
    results = []
    person_list = load_face_names()
    person_list = person_list[1:] # remove the first one (flag string)
    person_list.sort()
    sql_string = "SELECT image_file FROM Summary WHERE person LIKE ?"
    for person in person_list:
        result = cursor.execute(sql_string, tuple([_add_percent_sign(person)])).fetchall()[0]
        results.append(("person", person, result[0]))
    return results


def image_group_by_thing(cursor):
    """
    通过thing标签对图片进行分组，为每一个条目返回("top5", thing标签，图片文件)。
    Group image file by thing name, return "top5", thing name and image file for each item.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :return results: thing image_file list, [(str, str, str), ]
    """
    results = []
    thing_list = [] # load_thing_names
    thing_list = thing_list[1:]
    thing_list.sort()
    sql_string = "SELECT image_file FROM Summary WHERE top5 like ?"
    for thing in thing_list:
        result = cursor.execute(sql_string, tuple([_add_percent_sign(thing)])).fetchall()[0]
        results.append(("top5", thing, result[0]))
    return results


# 当用户在UI界面中点击某一类别的缩略图时，后台需要查询此类别对应的所有图片。
# When user click one category in user interface, backend needs to query
# all images in this category.
def query_subclass(cursor, key, value):
    """
    使用给定的键和键值查询子类的图片。
    Query for subclass images with given key and value.
    Example: 
        SELECT image_file FROM Summary WHERE top5 LIKE ? ORDER BY create_date
        SELECT image_file FROM Summary WHERE province = ? ORDER BY create_date
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param key: key word (create_date/city/district/person/top5), str
    :param value: subclass value, str
    """
    if key in ["person", "top5"]:
        cnnc_word = "like"
        value = _add_percent_sign(value)
    else:
        cnnc_word = "="
    sql_string = "SELECT image_file FROM Summary WHERE %s %s ? ORDER BY create_date" % (key, cnnc_word)
    results = cursor.execute(sql_string, tuple([value])).fetchall()
    return _process_empty_result(results, "Subclass query")


# 下述的函数（_query_item_value,_find_index_in_item,_modify_item_value,delete_image_from_subclass）
# 用于从特别的类别中删除某一项数值。
# Functions below, including _query_item_value, _find_index_in_item, _modify_item_value 
# and delete_image_from_subclassm are used to delete values in specific items.

# index0为主要修改的内容，index1为要删除的图片链接的位置，剩余为其他要修改的内容。
# index0: main item to be modified, index1: image link, others: other items
TABLE2ITEM_KEYS = {"People":["person", "image_name_person", "bbox", "feature"], 
                    "Thing":["top5", "image_name_thing"]}
def _query_item_value(cursor, table, image_file, item_key):
    """
    利用下述查询语句查询item_key对应的值。
    SELECT item_key FROM table WHERE image_file=image_file
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param image_file: image file name, str
    :param item_key: item key, str
    :return : item value, str
    """
    sql_string = "SELECT %s FROM %s WHERE image_file=?" % (item_key, table)
    results = cursor.execute(sql_string, tuple([image_file])).fetchall()
    return results[0][0]


def _find_index(item_value, subclass):
    """
    在item列表中找到subclass对应的索引。
    Find subclass's index in item list.
    
    :param item_value: item values (json string of list), str
    :param subclass: subclass name, str
    :return: int
    """
    item_value = json.loads(item_value)
    return item_value.index(subclass)


def _modify_value(item_value, index):
    """
    删除index处的数值，得到修改后的item。
    Modify value of item by removing corresponding index value.
    
    :param item_value: item value (json string of list), str
    :paran index: index with value to be deleted, int
    :return item_value: modified item value, str
    :return deleted_value: deleted value from origin item value, str
    """
    item_value = json.loads(item_value) # json string to list
    deleted_value = item_value.pop(index) # pop value at index
    if len(item_value) != 0: # if empty, item is assigned null
        item_value = json.dumps(item_value)
    else:
        item_value = None # change to NULL not "NULL"
    return item_value, deleted_value
    

def delete_image_from_subclass(cursor, table, subclass, image_file):
    """
    如果用户认为image_file不属于subclass并且选择了删除操作，那么我们需要从对应的表中
    将对应的值删去（不是删除image_file对应的整个条目）。
    例如：test.jpg中包含了两只猫，但是模型错误的认为其中同时含有狗和猫，那么用户在浏览狗
    的照片发现了此错误选择将其删除，我们需要将test.jpg在数据库中对应的记录从"狗,猫"修改为"猫"。
    If user thinks image_file does not belong to subclass and choose to delete it, 
    then we delete it (delete subclass value, not whole record) from table.
    Example: If test.jpg contains two cats, but our model mistook one cat for dog. 
    User finds this mistake when browsing, and he decides to delete it from dog. 
    So we need to midify origin database record from "Dog,Cat" to "Cat".
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param subclass: subclass name, str
    :param image_file: image file name, str
    :return deleted_link: image link that needs to be deleted, str
    """
    item_keys = TABLE2ITEM_KEYS[table] # items needed to be modified
    key_value_dict = dict()
    
    main_key = item_keys[0] # main item key ("person"/"top5")
    main_value = _query_item_value(cursor, "Summary", image_file, main_key) # main item value
    index = _find_index(main_value, subclass) # find subclass'sindex in main value
    main_value, _ = _modify_value(main_value, index) # new main value after modification
    key_value_dict[main_key] = main_value
    
    link_key = item_keys[1] # image link key ("image_name_person"/"image_name_thing")
    link_value = _query_item_value(cursor, "Summary", image_file, link_key) # image links
    link_value, deleted_link = _modify_value(link_value, index) # modified image links
    key_value_dict[link_key] = link_value
    
    for key in item_keys[2:]:
        value = _query_item_value(cursor, "Summary", image_file, link_key)
        value, _ = _modify_value(value, index)
        key_value_dict[key] = value
    # update related item in table Summary
    update_image_in_table(cursor, "Summary", image_file, key_value_dict)
    return deleted_link


def rename_subclass(cursor, table, subclass_name, new_name):
    """
    对子类进行重命名。
    Rename subclass.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param subclass_name: origin name of subclass, str
    :param new_name: new name of subclass, str
    :return None:
    """
    # choose corresponding key
    if table == "People":
        key = "person"
    elif table == "Thing":
        key = "top5"
    else:
        raise ValueError
    # query for all image files in this subclass
    image_files = query_subclass(cursor, key, subclass_name)
    # modify record in for-loop
    key_value_dict = dict()
    for image_file in image_files:
        # query origin value
        item = _query_item_value(cursor, "Summary", image_file, key) # value of person/top5
        # modify value
        item = json.loads(item)
        index = item.index(subclass_name)
        item[index] = new_name
        item = json.dumps(item)
        # update
        key_value_dict[key] = item
        update_image_in_table(cursor, "Summary", image_file, key_value_dict)


# 此函数用于删除某些原始文件不存在的图像链接。
# This function is used to delete image links whose origin image file does not exist. 
def query_image_links(cursor, image_file):
    """
    查询表Summary中的图像链接信息。
    Query image links in table Summary.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param image_file: image file name, str
    :return image_links: image link dict, dict
    """
    image_links = []
    sql_string = "SELECT image_name_date, image_name_week, province, city, district, image_name_address, person, image_name_person, top5, image_name_thing FROM Summary WHERE image_file=?"
    results = cursor.execute(sql_string, tuple([image_file])).fetchall()[0]
    # image link in Date
    if results[0] is not None:
        image_links.append(os.path.join("Date", results[0]))
    # image link in Week
    if results[1] is not None:
        image_links.append(os.path.join("Week", results[1]))
    # image link in Place
    province = results[2]
    city = results[3]
    district = results[4]
    image_name_adress = results[5]
    if image_name_adress is not None:
        temp = []
        for item in [province, city, district]:
            if item is not None:
                temp.append(item)
        image_links.append(os.path.join("Place", *temp, image_name_adress))
    # image link in People
    person = results[6]
    image_name_person = results[7]
    if person is not None: # not null
        person = json.loads(person)
        image_name_person = json.loads(image_name_person)
        for p, link in zip(person, image_name_person):
            if link is not None:
                image_links.append(os.path.join("People", p, link))
    # image link in Thing
    top5 = results[8]
    image_name_thing = results[9]
    if top5 is not None:
        top5 = json.loads(top5)
        image_name_thing = json.loads(image_name_thing)
        for t, link in zip(top5, image_name_thing):
            image_links.append(os.path.join("Thing", t, link))
    return image_links


# 从表格中删除image_file对应的记录
# delete record of image_file from table
def delete_image_from_table(cursor, table, image_file):
    """
    从表中删除image_file的记录。
    Delete record of image_file from table.

    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param image_file: image file name, str
    :return None:
    """
    if image_in_table(cursor, table, image_file):
        sql_string = "DELETE FROM %s WHERE image_file=?" % table
        cursor.execute(sql_string, tuple([image_file]))


def database_test(output=True):
    """
    确认数据库中包含必要的表格。
    Make sure database contains necessary tables.
    
    :param None:
    :return None:
    """
    import os, sqlite3
    conn = sqlite3.connect(os.path.join("record", "info.db")) # connect to database
    cursor = conn.cursor()
    for table in ["Date", "Place", "Thing", "People", "Summary"]:
        table_exist(cursor, table, output)
    conn.commit() # commit operations
    conn.close() # disconnect to database


if __name__ == "__main__":
    database_test()
