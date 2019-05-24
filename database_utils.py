#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: wangx
"""

import os, json


TABLE_CREATIION_DICT = {"DateWeek": """CREATE TABLE DateWeek (image_file nvarchar primart key, 
                        md5 char(32), 
                        create_date date, 
                        image_name_date nvarchar, 
                        create_week char(22), 
                        image_name_week nvarchar)""", 
                        
                        "Place": """CREATE TABLE Place (image_file nvarchar primary key,
                        md5 char(32), 
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
                        image_name_address nvarchar)""", 
                        
                        "Thing": """CREATE TABLE Thing (image_file nvarchar primary key, 
                        md5 char(32), 
                        top5 nvarchar, 
                        image_name_thing text)""", 
                        
                        "People": """CREATE TABLE People (image_file nvarchar primary key, 
                        md5 char(32), 
                        bbox text, 
                        feature text, 
                        person text, 
                        image_name_person text)""", 
                        
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
TABLES = set(["DateWeek", "Place", "Thing", "People", "Summary"]) # for table name checking


def table_exist(cursor, table, output=False):
    """
    在数据库database中检查是否存在表table，如果不存在则创建对应的新表。
    Check if table exists in database. 
    if table does not exist, create a new table.
    
    :param cursor: c ursor of database, sqlite3.Cursor
    :param database: database file, str
    :param table: table name, str
    :return None:
    """
    assert table in TABLES, "You should input correct table name!"
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


def get_image_file_from_table(cursor, table):
    """
    获取数据库database中表table的所有image_file条目。
    Get all image_file items of table in database.
    
    :param cursor: c ursor of database, sqlite3.Cursor
    :param database: database file, str
    :param table: table name, str
    :return results: all image files of table in database, list
    """
    assert table in TABLES, "You should input correct table name!"
    results = cursor.execute("SELECT image_file from %s" % table).fetchall()
    results = [result[0] for result in results]
    return results


def get_image_item_from_table(cursor, table, image_file):
    """
    从table表中获取image file对应的条目。
    Get image file corresponding item from table.
    
    :param cursor: c ursor of database, sqlite3.Cursor
    :param table: table name, str
    :param image_file: image file name, str
    :return: image item, tuple
    """
    assert table in TABLES, "You should input correct table name!"
    sql_string = "SELECT * FROM %s WHERE image_file=?" % table
    result = cursor.execute(sql_string, tuple([image_file])).fetchall()
    return result[0]
    

def _get_insert_string(table, keys):
    """
    
    Get sql insert string for sql insert operation.
    
    :param table: table name, str
    :param keys: table column names, tuple
    :return sql_string: sql insert string, str
    """
    str_part1 = ", ".join(keys)
    str_part2 = ["?"] * len(keys)
    str_part2 = ", ".join(str_part2)
    sql_string = "INSERT INTO %s (%s) VALUES (%s)" % (table, str_part1, str_part2)
    return sql_string


def insert_image_into_table(cursor, table, key_value_dict):
    """
    向特定表格中插入数据项。
    Insert new data item into specific table.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param key_value_dict: key value items, dict
    :return None:
    """
    assert table in TABLES, "You should input correct table name!"
    
    keys = tuple(key_value_dict.keys())
    values = tuple(key_value_dict[key] for key in keys)
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
    

def update_image_in_summary(cursor, key_value_dict):
    """
    如果image file已经存在于Summary中，更新对应的项目；否则插入一条新项目。
    Update image file item in table summay, if it already exists; 
    Otherwise insert new item into table.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param key_value_dict: key value items, dict
    :return None:
    """
    image_file = key_value_dict["image_file"]
    item = cursor.execute("SELECT image_file FROM Summary WHERE image_file=?", tuple([image_file])).fetchall()
    
    if len(item) == 0: # item does not exist, insert
        insert_image_into_table(cursor, "Summary", key_value_dict)
    else: # item exists, update
        key_value_dict.pop("image_file") # delete image file
        key_value_dict.pop("md5") # delete md5
        keys = tuple(key_value_dict.keys())
        values = tuple(key_value_dict[key] for key in keys)
        sql_string = _get_update_string("Summary", image_file, keys)
        cursor.execute(sql_string, values)


def delete_image_from_table(cursor, table, image_file):
    """
    从将image file对应的数据项从特定表格中删除。
    Delete specific image file from table.
    
    :param cursor: cursor of database, sqlite3.Cursor
    :param table: table name, str
    :param image_file: image file name, str
    :return None:
    """
    assert table in TABLES, "You should input correct table name!"
    sql_string = "SELECT image_file FROM %s WHERE image_file=?" % table
    result = cursor.execute(sql_string, tuple([image_file])).fetchall()
    if len(result) != 0: # if image file exists in table, delete it
        sql_string = "DELETE FROM %s WHERE image_file=?" % table
        cursor.execute(sql_string, tuple([image_file]))


# 警告：当数据库中表结构发生改变时，你需要针对性的更多image_name的索引！！！
# WARNING: When structure of Summary table changed, you need to change this function!!!
def parse_image_item(image_item):
    """
    解析图像条目信息，得到所有图像链接的路径。
    Parse image item, get image link path.
    
    :param image_item: image item, tuple
    :return image_links: image link dict, dict
    """
    image_links = []
    if image_item[3] is not None: # Date link
        image_links.append(os.path.join("Date", image_item[3]))
    if image_item[5] is not None: # Week link
        image_links.append(os.path.join("Week", image_item[5]))
    if image_item[16] is not None: # Addree link
        # Place/province/city/district/image_name
        province = image_item[11]
        city = image_item[12]
        district = image_item[13]
        image_links.append(os.path.join("Place", province, city, district, image_item[16]))
    top5 = json.loads(image_item[17])
    image_name_thing = json.loads(image_item[18])
    if top5 is not None:
        thing = [os.path.join("Thing", image_dir, image_name) for image_dir, image_name in zip(top5, image_name_thing)]
        image_links.extend(thing)
    person = json.loads(image_item[21])
    image_name_person = json.loads(image_item[22])
    if person is not None:
        person = [os.path.join("People", image_dir, image_name) for image_dir, image_name in zip(person, image_name_person)]
        image_links.extend(person)
    return image_links


def database_test():
    """
    Test database module.
    :param None:
    :return None:
    """
    import os, sqlite3
    conn = sqlite3.connect(os.path.join("model", "info.db"))
    cursor = conn.cursor()
    for table in ["DateWeek", "Place", "Thing", "People", "Summary"]:
        table_exist(cursor, table, True)


if __name__ == "__main__":
    database_test()
