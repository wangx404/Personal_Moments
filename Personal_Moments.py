#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 14:34:43 2019
@author: wangxin
"""

import sys, os, math
import sqlite3

from pyui.mainWindow import Ui_MainWindow
from pyui.welcomeArea import Ui_Form as _WelcomeForm
from pyui.dateArea import Ui_Form as _DateHome
from pyui.placeArea import Ui_Form as _PlaceHome
from pyui.peopleArea import Ui_Form as _PeopleHome
from pyui.thingArea import Ui_Form as _ThingHome
from pyui.searchArea import Ui_Form as _SearchHome
from pyui.importArea import Ui_Form as _ImportForm
from pyui.settingArea import Ui_Form as _SettingForm
from pyui.aboutArea import Ui_Form as _AboutForm
from pyui.searchImageArea import Ui_Form as _SearchImage
from pyui.classImageArea import Ui_Form as _ClassImage

from PyQt5.QtCore import Qt, QPoint, QDate
from PyQt5.QtGui import QPixmap, QBitmap, QIcon, QPalette
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QMessageBox,\
                            QFileDialog, QStackedWidget, QTableWidgetItem, QLabel,\
                            QHeaderView, QMenu, QVBoxLayout, QScrollArea,\
                            QSizePolicy, QAction, QAbstractItemView,\
                            QInputDialog, QLineEdit
from utils.database_utils import get_province_from_table, get_city_from_table,\
                                get_district_from_table, sort_query_result,\
                                all_search, date_search, place_search, people_search,\
                                thing_search, delete_image_from_subclass,\
                                image_group_by_date, image_group_by_place,\
                                image_group_by_person, image_group_by_thing,\
                                query_subclass, rename_subclass, database_test
from utils.common_utils import change_dir_name, change_text_name
from utils.image_sorting import DateThread, PlaceThread, PeopleThread, ThingThread


# In order to query data from database, a global database cursor has to be created here.
DATABASE = os.path.join("record", "info.db")
CONN = sqlite3.connect(DATABASE)
CURSOR = CONN.cursor()


class MainWindow(QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        """
        初始化主窗口。
        Initialize main window.
        """
        super(MainWindow, self).__init__() # father construction
        self.setupUi(self) # Ui_MainWindow construction
        #self.tray = QSystemTrayIcon()
        #self.tray.setIcon(QIcon(os.path.join("record", "camera.png")))
        #self.tray.show()
        self.set_icons() # setting push button icon
        
        self.currentButton = None # variable to store current pressed button
        self.set_push_button_action() # set push button action
        
        # construct a series of working area
        self.welcome = WelcomeForm()
        self.date = DateForm()
        self.place = PlaceForm()
        self.people = PeopleForm()
        self.thing = ThingForm()
        self.search = SearchForm()
        
        self._import = ImportForm()
        self.setting = SettingForm()
        self.about = AboutForm()
        # add to stacked widget
        self.workArea.addWidget(self.welcome)
        self.workArea.addWidget(self.date)
        self.workArea.addWidget(self.place)
        self.workArea.addWidget(self.people)
        self.workArea.addWidget(self.thing)
        self.workArea.addWidget(self.search)
        self.workArea.addWidget(self._import)
        self.workArea.addWidget(self.setting)
        self.workArea.addWidget(self.about)
        self.areaIndexDict = {"Date": 1, 
                              "Place": 2,
                              "People": 3,
                              "Thing": 4,
                              "Search": 5,
                              "Import": 6,
                              "Setting": 7,
                              "About": 8} # button text to index
    
    
    def set_icons(self):
        """
        为主窗口中的按钮设置图标。
        Setting icon for buttons and labels in main window.
        """
        icon = QPixmap(os.path.join("icon", "camera.png")) # icon pixmap
        icon_size = self.app_icon.size() # get icon size
        icon = icon.scaled(icon_size.width(), icon_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation) # scale image
        self.app_icon.setPixmap(icon) # set icon
        
        icon_size = self.label_date.size()
        # date push button
        icon = QPixmap(os.path.join("icon", "date.png"))
        icon = icon.scaled(icon_size.width(), icon_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_date.setPixmap(icon)
        # place push button
        icon = QPixmap(os.path.join("icon", "place.png"))
        icon = icon.scaled(icon_size.width(), icon_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_place.setPixmap(icon)
        # people push button
        icon = QPixmap(os.path.join("icon", "people.png"))
        icon = icon.scaled(icon_size.width(), icon_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_people.setPixmap(icon)
        # thing push button
        icon = QPixmap(os.path.join("icon", "thing.png"))
        icon = icon.scaled(icon_size.width(), icon_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_thing.setPixmap(icon)
        # search push button
        icon = QPixmap(os.path.join("icon", "search.png"))
        icon = icon.scaled(icon_size.width(), icon_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_search.setPixmap(icon)
        # import push button
        icon = QPixmap(os.path.join("icon", "import.png"))
        icon = icon.scaled(icon_size.width(), icon_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_import.setPixmap(icon)
        # setting push button
        icon = QPixmap(os.path.join("icon", "setting.png"))
        icon = icon.scaled(icon_size.width(), icon_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_setting.setPixmap(icon)
        # about push button
        icon = QPixmap(os.path.join("icon", "about.png"))
        icon = icon.scaled(icon_size.width(), icon_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_about.setPixmap(icon)
    
    
    def set_push_button_action(self):
        """
        设置按钮动作。按钮被按下后，弹起现有按钮，并更新工作区的内容。
        Set push button action. When pressed, pop up current button and reload working area.
        """
        # invoke up_current_button
        self.pushButton_date.pressed.connect(lambda:self.up_current_button(self.pushButton_date))
        self.pushButton_place.pressed.connect(lambda:self.up_current_button(self.pushButton_place))
        self.pushButton_people.pressed.connect(lambda:self.up_current_button(self.pushButton_people))
        self.pushButton_thing.pressed.connect(lambda:self.up_current_button(self.pushButton_thing))
        self.pushButton_search.pressed.connect(lambda:self.up_current_button(self.pushButton_search))
        self.pushButton_import.pressed.connect(lambda:self.up_current_button(self.pushButton_import))
        self.pushButton_setting.pressed.connect(lambda:self.up_current_button(self.pushButton_setting))
        self.pushButton_about.pressed.connect(lambda:self.up_current_button(self.pushButton_about))
        # invoke change_work_area
        self.pushButton_date.pressed.connect(lambda:self.change_work_area(self.pushButton_date))
        self.pushButton_place.pressed.connect(lambda:self.change_work_area(self.pushButton_place))
        self.pushButton_people.pressed.connect(lambda:self.change_work_area(self.pushButton_people))
        self.pushButton_thing.pressed.connect(lambda:self.change_work_area(self.pushButton_thing))
        self.pushButton_search.pressed.connect(lambda:self.change_work_area(self.pushButton_search))
        self.pushButton_import.pressed.connect(lambda:self.change_work_area(self.pushButton_import))
        self.pushButton_setting.pressed.connect(lambda:self.change_work_area(self.pushButton_setting))
        self.pushButton_about.pressed.connect(lambda:self.change_work_area(self.pushButton_about))
    
    
    def up_current_button(self, btn):
        """
        更改现有按钮的状态（弹起），并将现有按钮更改为当前按下的按钮。
        Change state of current button, change current button to pressed button.
        
        :param btn: button, QtWidgets.QPushButton
        :return None:
        """
        if self.currentButton is not None: # pressed button up
            self.currentButton.toggle() 
        self.currentButton = btn # change current button to this button
    
    
    def change_work_area(self, btn):
        """
        更改当前工作区的显示内容。
        Change content of current working area.
        
        :param btn: button, QtWidgets.QPushButton
        :return None:
        """
        text = btn.text()
        index = self.areaIndexDict[text]
        self.workArea.setCurrentIndex(index)
    
    
    def closeEvent(self, event):
        """
        关闭应用时关闭数据库连接。
        Close database when application was closed.
        """
        CONN.close()
    
    
    def resizeEvent(self, event):
        """
        当主窗口的尺寸发生改变时，调整工作区的大小。但目前存在的问题是界面的刷新是滞后的。
        When main window is resized, resize working area.
        The problem existed here is the refresh is delayed, and it can be annoying sometimes.
        """
        super().resizeEvent(event)
        #self.workArea.adjustSize()
        #self.update()



class WelcomeForm(QWidget, _WelcomeForm):
    def __init__(self):
        """
        打开应用后显示的欢迎页面。
        Show welcome page after application is opened.
        """
        super(WelcomeForm, self).__init__()
        self.setupUi(self)



# 继承层次
# Inheritance hierarchy
# DateForm
    # DateHome
        # own widgets
        # ClassImage
    # SearchImage
    # SearchImage
class DateForm(QStackedWidget):
    def __init__(self):
        """
        DateForm和下述定义的PlaceForm、PeopleForm以及ThingForm都继承自QStackedWidget，并对其进行了修改。
        该类作为一个容器类，用以存储对应的实际页面，并提供在页面间进行切换的函数。
        """
        super(DateForm, self).__init__()
        self.date_home = DateHome(table_name="Date", like=True, rename=True)
        self.date_image = SearchImage(table_name="Date", like=True, delete=False)
        self.search_image = SearchImage(table_name="Date", like=True, delete=False)
        self.addWidget(self.date_home)
        self.addWidget(self.date_image)
        self.addWidget(self.search_image)
        
        # click search button in home page, switch to searching result
        self.date_home.pushButton_search.clicked.connect(self.show_image)
        # click return button in subclass/search page, switch to home page
        self.date_image.pushButton_return.clicked.connect(self.show_home)
        self.search_image.pushButton_return.clicked.connect(self.show_home)
        # double click in home page, switch to subclass page
        self.date_home.image_area.tableWidget_image.cellDoubleClicked.connect(self.show_subclass)
        
    
    def show_home(self):
        """
        将当前页面切换到首页。
        Switch current page to home page.
        """
        self.setCurrentIndex(0)
    
    
    def show_subclass(self):
        """
        显示子类图片页面。
        流程：
            调用DateHome.image_area.query_subclass查询子类图片，
            切换当前显示页面的索引，
            刷新date_image的页面显示。
        Show subclass page.
        Pipeline:
            invoke DateHome.image_area.query_subclass to get images of subclass,
            switch index of current shown page,
            refresh date_image.
        """
        
        self.date_image.image_list, self.date_image.subclass_name = self.date_home.image_area.query_subclass()
        if self.date_image.image_list is None:
            return
        self.setCurrentIndex(1)
        self.date_image.refresh()
    
    
    def show_image(self):
        """
        显示搜索图片页面。
        流程：
            调用DateHome.search搜索图片，
            切换当前显示页面的索引，
            刷新search_image的页面显示。
        Show searching page.
        Pipeline:
            invoke DateHome.search to get searching results,
            switch index of current shown page,
            refresh search_image.
        """
        self.search_image.image_list = self.date_home.search()
        self.setCurrentIndex(2)
        self.search_image.refresh()
        


class DateHome(QWidget, _DateHome):
    def __init__(self, table_name, like, rename):
        """
        日期搜索页面。
        Date searching page.
        """
        super(DateHome, self).__init__()
        self.setupUi(self)
        # set end date to current date
        self.dateEdit_end.setDate(QDate.currentDate())
        # set new image area to show images and labels
        self.image_area = ClassImage(table_name=table_name, like=like, rename=rename)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_area.sizePolicy().hasHeightForWidth())
        self.image_area.setSizePolicy(sizePolicy)
        self.image_area.setObjectName("image_area")
        self.verticalLayout.addWidget(self.image_area)
        self.verticalLayout.setStretch(0,0)
        self.verticalLayout.setStretch(1,0)
        self.verticalLayout.setStretch(2,1)
        
    
    def search(self):
        """
        通过给定的日期限定区间搜索图片。
        Search image files by specific date interval.
        """
        self.start_date = self.dateEdit_start.date().toString("yyyy-MM-dd")
        self.end_date = self.dateEdit_end.date().toString("yyyy-MM-dd")
        return date_search(CURSOR, self.start_date, self.end_date)



class PlaceForm(QStackedWidget):
    def __init__(self):
        super(PlaceForm, self).__init__()
        self.place_home = PlaceHome(table_name="Place", like=True, rename=False)
        self.place_image = SearchImage(table_name="Place", like=True, delete=False)
        self.search_image = SearchImage(table_name="Place", like=True, delete=False)
        self.addWidget(self.place_home)
        self.addWidget(self.place_image)
        self.addWidget(self.search_image)
        
        
        self.place_home.pushButton_search.clicked.connect(self.show_image)
        self.place_image.pushButton_return.clicked.connect(self.show_home)
        self.search_image.pushButton_return.clicked.connect(self.show_home)
        self.place_home.image_area.tableWidget_image.cellDoubleClicked.connect(self.show_subclass)
    
    
    def show_home(self):
        """
        将当前页面切换到首页。
        Switch current page to home page.
        """
        self.setCurrentIndex(0)
    
    
    def show_subclass(self):
        """
        显示子类图片页面。
        Show subclass page.
        """
        self.place_image.image_list, self.place_image.subclass_name = self.place_home.image_area.query_subclass()
        if self.place_image.image_list is None:
            return
        self.setCurrentIndex(1)
        self.place_image.refresh()
    
    
    def show_image(self):
        """
        显示搜索结果中的图片。
        Show images in searching result.
        """
        self.search_image.image_list = self.place_home.search() # this is pretty quick
        self.setCurrentIndex(2)
        self.search_image.refresh() # but this can take a very long time, especially when there are many large images



class PlaceHome(QWidget, _PlaceHome):
    def __init__(self, table_name, like, rename):
        """
        地点搜索页面。
        Place searching page.
        """
        super(PlaceHome, self).__init__()
        self.setupUi(self)
        provinces = get_province_from_table(CURSOR)
        provinces = sort_query_result(provinces)
        self.comboBox_province.addItems(provinces)
        # add comboBox action
        self.comboBox_province.activated.connect(self.query_city)
        self.comboBox_city.activated.connect(self.query_district)
        # set new image area to show images and labels
        self.image_area = ClassImage(table_name=table_name, like=like, rename=rename)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_area.sizePolicy().hasHeightForWidth())
        self.image_area.setSizePolicy(sizePolicy)
        self.image_area.setObjectName("image_area")
        self.verticalLayout.addWidget(self.image_area)
        self.verticalLayout.setStretch(0,0)
        self.verticalLayout.setStretch(1,0)
        self.verticalLayout.setStretch(2,1)
    
    
    def query_city(self):
        """
        使用当前的省份名称查询对应的城市列表。
        Using current province name to query city list and set comboBox of city.
        """
        # get current province, query city list, porcess, clear current items, add new items
        province = self.comboBox_province.currentText()
        if province == "None":
            cities = ["None"]
        else:
            cities = get_city_from_table(CURSOR, province)
            cities = sort_query_result(cities)
        self.comboBox_city.clear()
        self.comboBox_city.addItems(cities)
    
    
    def query_district(self):
        """
        使用当前的城市名称查询对应的城区名称。
        Using current city name to query district list and set comboBox of district.
        """
        city = self.comboBox_city.currentText()
        if city == "None":
            districts = ["None"]
        else:
            districts = get_district_from_table(CURSOR, city)
            districts = sort_query_result(districts)
        self.comboBox_district.clear()
        self.comboBox_district.addItems(districts)
    
    
    def search(self):
        """
        通过给定的省份、城市和城区搜索图片。
        Search image files by specific province, city and district.
        """
        self.province = self.comboBox_province.currentText()
        self.city = self.comboBox_city.currentText()
        self.district = self.comboBox_district.currentText()
        return place_search(CURSOR, self.province, self.city, self.district)



class PeopleForm(QStackedWidget):
    def __init__(self):
        super(PeopleForm, self).__init__()
        self.people_home = PeopleHome(table_name="People", like=True, rename=True)
        self.people_image = SearchImage(table_name="People", like=True, delete=True)
        self.search_image = SearchImage(table_name="People", like=True, delete=False)
        self.addWidget(self.people_home)
        self.addWidget(self.people_image)
        self.addWidget(self.search_image)
        
        self.people_home.pushButton_search.clicked.connect(self.show_image)
        self.people_image.pushButton_return.clicked.connect(self.show_home)
        self.search_image.pushButton_return.clicked.connect(self.show_home)
        self.people_home.image_area.tableWidget_image.cellDoubleClicked.connect(self.show_subclass)
    
    
    def show_home(self):
        """
        将当前页面切换到首页。
        Switch current page to home page.
        """
        self.setCurrentIndex(0)
    
    
    def show_subclass(self):
        """
        显示子类图片页面。
        Show subclass page.
        """
        self.people_image.image_list, self.people_image.subclass_name = self.people_home.image_area.query_subclass()
        if self.people_image.image_list is None:
            return
        self.setCurrentIndex(1)
        self.people_image.refresh()
    
    
    def show_image(self):
        """
        显示搜索结果中的图片。
        Show images in searching result.
        """
        success_flag, self.search_image.image_list = self.people_home.search()
        if not success_flag:
            _ = QMessageBox.warning(self, "Warning", "You should enter a name in the first line", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.setCurrentIndex(2)
        self.search_image.refresh()



class PeopleHome(QWidget, _PeopleHome):
    def __init__(self, table_name="People", like=True, rename=True):
        """
        人物搜索页面。
        People searching page.
        """
        super(PeopleHome, self).__init__()
        self.setupUi(self)
        # set new image area to show images and labels
        self.image_area = ClassImage(table_name=table_name, like=like, rename=rename)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_area.sizePolicy().hasHeightForWidth())
        self.image_area.setSizePolicy(sizePolicy)
        self.image_area.setObjectName("image_area")
        self.verticalLayout.addWidget(self.image_area)
        self.verticalLayout.setStretch(0,0)
        self.verticalLayout.setStretch(1,0)
        self.verticalLayout.setStretch(2,1)
    
    
    def search(self):
        """
        通过给定的人物姓名和逻辑关系搜索图片。对字段的处理留给具体的业务代码。
        Search image files by specific person name and logical relationship.
        Detailed processing of text of lineEdit/comboBox is done by related back-end function.
        """
        self.p1 = self.lineEdit_p1.text()
        if self.p1 == "": # unvalid searching conditon
            return False, None
        self.logic = self.comboBox_logic.currentText()
        self.p2 = self.lineEdit_p2.text()
        return True, people_search(CURSOR, self.p1, self.logic, self.p2)



class ThingForm(QStackedWidget):
    def __init__(self):
        super(ThingForm, self).__init__()
        # initialize sub pages, add to widget
        self.thing_home = ThingHome(table_name="Thing", like=True, rename=False)
        self.thing_image = SearchImage(table_name="Thing", like=True, delete=True)
        self.search_image = SearchImage(table_name="Thing", like=True, delete=False)
        self.addWidget(self.thing_home)
        self.addWidget(self.thing_image)
        self.addWidget(self.search_image)
        # double click, get item, get sub class images, switch page, refresh
        self.thing_home.pushButton_search.clicked.connect(self.show_image) # show search image
        self.thing_image.pushButton_return.clicked.connect(self.show_home) # return button-> return to home
        self.search_image.pushButton_return.clicked.connect(self.show_home)
    
    
    def show_home(self):
        """
        将当前页面切换到首页。
        Switch current page to home page.
        """
        self.setCurrentIndex(0)
    
    
    def show_subclass(self):
        """
        显示子类图片页面。
        Show subclass page.
        """
        self.thing_image.image_list, self.thing_image.subclass_name = self.thing_home.image_area.query_subclass()
        if self.thing_image.image_list is None:
            return
        self.setCurrentIndex(1)
        self.thing_image.refresh()
    
    
    def show_image(self):
        """
        显示搜索结果中的图片。
        Show images in searching result.
        """
        self.search_image.image_list = self.thing_home.search()
        self.setCurrentIndex(2)
        self.search_image.refresh()



class ThingHome(QWidget, _ThingHome):
    def __init__(self, table_name="Thing", like=True, rename=False):
        """
        物品搜索页面。
        Thing searching page.
        """
        super(ThingHome, self).__init__()
        self.setupUi(self)
        # set new image area to show images and labels
        self.image_area = ClassImage(table_name=table_name, like=like, rename=rename)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_area.sizePolicy().hasHeightForWidth())
        self.image_area.setSizePolicy(sizePolicy)
        self.image_area.setObjectName("image_area")
        self.verticalLayout.addWidget(self.image_area)
        self.verticalLayout.setStretch(0,0)
        self.verticalLayout.setStretch(1,0)
        self.verticalLayout.setStretch(2,1)
    
    
    def search(self):
        """
        通过给定的物品名称搜索图片。
        Search image files by specific keyword.
        """
        self.thing = self.lineEdit_people.text()
        return thing_search(CURSOR, self.thing)



class SearchForm(QStackedWidget):
    def __init__(self):
        super(SearchForm, self).__init__()
        self.search_home = SearchHome() # search home page
        self.search_image = SearchImage(table_name="Search", like=True, delete=False) # search image page
        self.addWidget(self.search_home)
        self.addWidget(self.search_image)
        # action of push button on sub page is defined here
        self.search_home.pushButton_search.clicked.connect(self.show_image)
        self.search_image.pushButton_return.clicked.connect(self.show_home)
    
    
    def show_home(self):
        """
        显示搜索工作区的首页。
        Show home page of search working area.
        """
        self.setCurrentIndex(0) # show home page
    
    
    def show_image(self):
        """
        显示搜索结果中的图片。
        Show image files in searching result.
        Pipeline: 
            show search image page,
            search for image files in home page (image_list is updated),
            refresh images in search image page
        """
        self.search_image.image_list = self.search_home.search() # search for image
        self.setCurrentIndex(1) # show image page
        self.search_image.refresh() # refresh image page


class SearchHome(QWidget, _SearchHome):
    def __init__(self):
        """
        搜索页面。
        Searching page.
        """
        super(SearchHome, self).__init__()
        self.setupUi(self)
        # set end date to current date
        self.dateEdit_end.setDate(QDate.currentDate())
        # set province list
        provinces = get_province_from_table(CURSOR)
        provinces = sort_query_result(provinces)
        self.comboBox_province.addItems(provinces)
        # add comboBox action
        self.comboBox_province.activated.connect(self.query_city)
        self.comboBox_city.activated.connect(self.query_district)
    
    
    def query_city(self):
        """
        使用当前的省份名称查询对应的城市列表。
        Using current province name to query city list and set comboBox of city.
        """
        # get current province, query city list, porcess, clear current items, add new items
        province = self.comboBox_province.currentText()
        if province == "None":
            cities = ["None"]
        else:
            cities = get_city_from_table(CURSOR, province)
            cities = sort_query_result(cities)
        self.comboBox_city.clear()
        self.comboBox_city.addItems(cities)
    
    
    def query_district(self):
        """
        使用当前的城市名称查询对应的城区名称。
        Using current city name to query district list and set comboBox of district.
        """
        city = self.comboBox_city.currentText()
        if city == "None":
            districts = ["None"]
        else:
            districts = get_district_from_table(CURSOR, city)
            districts = sort_query_result(districts)
        self.comboBox_district.clear()
        self.comboBox_district.addItems(districts)
    
    
    def search(self):
        """
        根据搜索条件搜索对应的图片，并更新image_list。
        Search image files by specific searching conditions, and update image_list.
        """
        self.start_date = self.dateEdit_start.date().toString("yyyy-MM-dd")
        self.end_date = self.dateEdit_end.date().toString("yyyy-MM-dd")
        self.province = self.comboBox_province.currentText()
        self.city = self.comboBox_city.currentText()
        self.district = self.comboBox_district.currentText()
        self.people = self.lineEdit_people.text()
        self.thing = self.lineEdit_thing.text()
        return all_search(CURSOR, self.start_date, self.end_date, 
                                  self.province, self.city, self.district, 
                                  self.people, self.thing)


class ImportForm(QWidget, _ImportForm):
    def __init__(self):
        """
        图片导入页面。
        Image importing page.
        """
        super(ImportForm, self).__init__()
        self.setupUi(self)
        self.date_process_thread = DateThread() # date week process thread
        self.date_process_thread.signal.connect(self.set_progress_pct) # set thread signal handling method
        self.date_process_thread.finished.connect(lambda:self.set_progress_pct(100, "date")) # set process percent to 100% when thread ends
        self.place_process_thread = PlaceThread() # similar as above
        self.place_process_thread.signal.connect(self.set_progress_pct)
        self.place_process_thread.finished.connect(lambda:self.set_progress_pct(100, "place"))
        self.people_process_thread = PeopleThread() # similar as above
        self.people_process_thread.signal.connect(self.set_progress_pct)
        self.people_process_thread.finished.connect(lambda:self.set_progress_pct(100, "people"))
        self.thing_process_thread = ThingThread() # similar as above
        self.thing_process_thread.signal.connect(self.set_progress_pct)
        self.thing_process_thread.finished.connect(lambda:self.set_progress_pct(100, "thing"))
        
        self.pushButton_import.clicked.connect(self.choose_image_folder) # choose an image folder for processing
        self.pushButton_process.clicked.connect(self.process_images) # begin to process images
    
    
    def choose_image_folder(self):
        """
        选择要导入的图片文件夹，设置线程参数。
        Choose an image folder for processing, and set thread parameters.
        """
        image_dir = QFileDialog.getExistingDirectory(self, "Open Image Folder", ".")
        self.set_thread_param(image_dir)
    
    
    def set_thread_param(self, image_dir):
        """
        设置图片处理线程中的参数：输入文件夹，输出文件夹，是否发送处理进程信号。
        Set input directory/output directory/ui_invoke flag of image process thread.
        
        :param image_dir: image folder for processing, str
        :return None:
        """
        self.date_process_thread.input_dir = image_dir # set input directory
        self.date_process_thread.output_dir = "IMAGE" # set output directory
        self.date_process_thread.ui_invoke = True # send progress percent signal when processing (default False)
        self.place_process_thread.input_dir = image_dir # similar as above
        self.place_process_thread.output_dir = "IMAGE"
        self.place_process_thread.ui_invoke = True
        self.people_process_thread.input_dir = image_dir # similar as above
        self.people_process_thread.output_dir = "IMAGE"
        self.people_process_thread.ui_invoke = True
        self.thing_process_thread.input_dir = image_dir # similar as above
        self.thing_process_thread.output_dir = "IMAGE"
        self.thing_process_thread.ui_invoke = True
    
    
    # image processing thread may lead to fake death of main thread
    def process_images(self):
        """
        启动图片处理线程。
        Start image processing threads.
        """
        self.date_process_thread.start() # no error
        self.place_process_thread.start() # no error
        self.people_process_thread.start()
        self.thing_process_thread.start() # not implemented
    
    # set value of progress bar
    def set_progress_pct(self, process_pct, thread_name):
        """
        当图片处理线程发送信号之后，改变进度条的数值。
        When image processing thread emits a signal, change value of progress bar.
        """
        if thread_name == "date":
            self.progressBar_date.setValue(process_pct)
        elif thread_name == "place":
            self.progressBar_place.setValue(process_pct)
        elif thread_name == "people":
            self.progressBar_people.setValue(process_pct)
        elif thread_name == "thing":
            self.progressBar_thing.setValue(process_pct)


class SettingForm(QWidget, _SettingForm):
    def __init__(self):
        """
        API秘钥设置页面。
        API Key and Secret key setting page.
        """
        super(SettingForm, self).__init__()
        self.setupUi(self)
        # setting push button action
        self.pushButton_setting.clicked.connect(self.set_api_key)
        self.pushButton_test.clicked.connect(self.varify_api_key)
    
    
    def set_api_key(self):
        """
        将设定的API Key和Secret Key保存至本地文本文件中。
        Save API key and secret key into local text file.
        """
        import os
        from utils.common_utils import save_api_key
        key = self.lineEdit_key.text()
        secret_key = self.lineEdit_sk.text()
        key_file = os.path.join("record", "key_file.txt")
        save_api_key(key_file, key, secret_key)
    
    
    def show_test_info(self, title, information):
        """
        使用对话框显示API确认的结果。
        Show API varification result.
        
        :param title: title of message box, str
        :param information: information shown in message box, str
        """
        _ = QMessageBox.information(self, title, information, QMessageBox.Ok, QMessageBox.Ok)
    
    
    def varify_api_key(self):
        """
        确认设定的API Key和Secret Key是有效的。
        Varify if API key and secret key is valid.
        """
        from utils.gps_utils import gps_test
        key_file = os.path.join("record", "key_file.txt")
        test_result = gps_test(key_file)
        # success
        if test_result == 0:
            self.show_test_info("Success", "API key and secret key is valid.")
        # wrong API key or connection error
        elif test_result == 1:
            self.show_test_info("Warning", "API invoking error, please check network connection or verify your API key.")
        # wrong API key format
        elif test_result == -1:
            self.show_test_info("Warning", "You have not set your API key and secret key.")
        else:
            self.show_test_info("Warning", "You should save your API key with given format in record/key_file.txt")


class AboutForm(QWidget, _AboutForm):
    def __init__(self):
        """
        关于我页面。
        About me information page.
        """
        super(AboutForm, self).__init__()
        self.setupUi(self)


class SearchImage(QWidget, _SearchImage):
    def __init__(self, table_name=None, subclass_name=None, like=False, delete=False):
        """
        此页面用于显示搜索结果或者子类中的图片。
        This page is used to show images in searching result and sub class.
        
        :param table_name: table name (used for sql query, None in searching page), str
        :param like: whether to enable like action in right menu, bool
        :param delete: whether to enable delete action in right menu, bool
        """
        super(SearchImage, self).__init__()
        self.setupUi(self)
        # related parameters
        # current table name, in order to delete image from specific table
        # its value will not be changed during life cell
        self.table_name = table_name 
        # current subclass name, in order to update specific item value of image
        # its value will be changed each time enthering from index page
        self.subclass_name = subclass_name
        self.like = like # whether to enable like action
        self.delete = delete # whether to enable delete action
        self.column_num = 4 # column number
        self.row_num = 5 # row number
        self.item_size = 200 # item size
        self.image_list = None # image files
        self.image_num = None # number of image files
        self.deleted_image = set() # container for deleted image files
        self.current_page = None # current page index
        self.last_page = None # last page index
        # table decoration
        self.mask = QBitmap(os.path.join("icon", "delete.png"))
        self.pushButton_return.setIcon(QIcon(os.path.join("icon", "return.png"))) # set return button icon
        self.set_table_attributes()
        # image viewer
        self.image_viewer = ImageViewer()
        # table button action
        self.tableWidget_image.customContextMenuRequested.connect(self.choose_action) # right menu action
        self.tableWidget_image.setEditTriggers(QAbstractItemView.NoEditTriggers) # forbid edit behavour
        self.tableWidget_image.cellDoubleClicked.connect(self.show_origin_image) # double-click action
        # pushButton action
        self.set_actions()
    
    
    def set_actions(self):
        """
        为pushButton设置触发动作
        Set triggered actions for pushButtons.
        """
        self.pushButton_fisrt.clicked.connect(self.first_button_clicked)
        self.pushButton_previous.clicked.connect(self.previous_button_clicked)
        self.pushButton_next.clicked.connect(self.next_button_clicked)
        self.pushButton_last.clicked.connect(self.last_button_clicked)
    
    
    def set_table_attributes(self):
        """
        设置QTableWidget的一些属性信息。
        Set some attributes of QTableWidget.
        """
        # table section stretch mode
        #self.tableWidget_image.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_image.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # set row/column number
        self.tableWidget_image.setRowCount(self.row_num)
        self.tableWidget_image.setColumnCount(self.column_num)
        # set row/column width
        for i in range(self.row_num):
            self.tableWidget_image.setRowHeight(i, self.item_size)
        for j in range(self.column_num):
            self.tableWidget_image.setColumnWidth(j, self.item_size)
        #min_width = self.column_num * self.item_size
        #min_height = self.row_num * self.item_size
        #self.tableWidget_image.setMinimumSize(QtCore.QSize(min_width, min_height))
    
    
    def first_button_clicked(self):
        """
        当按钮pushButton_first被点击后，修改当前页面索引值，并刷新页面。
        After pushButton_first was clicked, modify value of current page index, 
        and then refresh current page.
        """
        if self.current_page == 0: # already the first page
            _ = QMessageBox.information(self, "Notice", "Current page is already the first page", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.current_page = 0
        self.update_display()
    
    
    def previous_button_clicked(self):
        """
        当按钮pushButton_previous被点击后，修改当前页面索引值，并刷新页面。
        After pushButton_previous was clicked, modify value of current page index, 
        and then refresh current page.
        """
        if self.current_page == 0: # already the first page
            _ = QMessageBox.information(self, "Notice", "Current page is already the first page", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.current_page -= 1
        self.update_display()
    
    
    def next_button_clicked(self):
        """
        当按钮pushButton_next被点击后，修改当前页面索引值，并刷新页面。
        After pushButton_next was clicked, modify value of current page index, 
        and then refresh current page.
        """
        if self.current_page == self.last_page:
            _ = QMessageBox.information(self, "Notice", "Current page is already the last page", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.current_page += 1
        self.update_display()
    
    
    def last_button_clicked(self):
        """
        当按钮pushButton_last被点击后，修改当前页面索引值，并刷新页面。
        After pushButton_last was clicked, modify value of current page index, 
        and then refresh current page.
        """
        if self.current_page == self.last_page:
            _ = QMessageBox.information(self, "Notice", "Current page is already the last page", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.current_page = self.last_page
        self.update_display()
    
    
    # If indexes returned here are modified, some function will not work as expected
    def get_image_indexes(self):
        """
        获取选中图片的索引坐标。
        Get coordinates of selected image items.
        
        :param None:
        :return indexes: selected image item indexes, list
        """
        indexes = []
        item_indexes = self.tableWidget_image.selectedIndexes()
        for item_index in item_indexes:
            indexes.append((item_index.row(), item_index.column()))
        return indexes
    
    
    def choose_action(self, position):
        """
        显示鼠标右键菜单，根据选择的动作执行对应的操作。
        Show mouse right menu, and execute corrsponding function according to action.
        
        :param position: right menu activated position, QCursor.pos
        """
        # construct righr button menu
        right_menu = QMenu(self)
        like_action = right_menu.addAction("Like") # like action
        if not self.like:
            like_action.setEnabled(False) # can not be clicked
        delete_action = right_menu.addAction("Delete") # delete action
        if not self.delete: # whether
            delete_action.setEnabled(False) # can not be clicked
        
        action = right_menu.exec_(self.tableWidget_image.mapToGlobal(position)) # show menu
        indexes = self.get_image_indexes() # get selected image indexes
        if action == like_action: # choose action, execute corresponding function
            self.like_image(indexes)
        elif action == delete_action:
            self.delete_image(indexes)
    
    
    def like_image(self, indexes):
        """
        在数据库中为图片文件添加喜欢记录。
        Add like record for image file in database.
        """
        pre_index = self.current_page*self.row_num*self.column_num
        for index in indexes:
            index = index[0]*self.column_num + index[1]
            index = pre_index + index
            if index >= self.image_num:
                continue
        print("This function has not been implemented yet.")
    
    
    def set_mask(self, row, column):
        """
        为删除的子部件设置掩码（或者新图片）。
        Set mask (or new image) for deleted cell widget.
        
        :param row: row index of selected cell widget, int
        :param column: column index of selected cell widget, int
        """
        # set mask or set new image
        self.tableWidget_image.cellWidget(row, column).setMask(self.mask)
    
    
    # this function can work properly now
    def delete_image(self, indexes):
        """
        从数据库中删除数据条目，但不删除图片文件。
        Delete image item from database, and do not delete image file.
        
        Pipeline:
            filter deleted image,
            show delete icon at image position(),
            delete image item in related table (specific table and Summary),
            delete image link in corresponding directory, # not exist yet
            add to deleted image.
        """
        # there may be multiple previous pages
        pre_index = self.current_page*self.row_num*self.column_num
        # raise warning note if multiple image files are chosen
        if len(indexes) > 1:
            choice = QMessageBox.warning(self, "Warning", "Do you really want to delete these images?", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if choice == QMessageBox.Cancel: # choose cancel, quit function
                return
        
        for index in indexes:
            # set image mask
            self.set_mask(index[0], index[1])
            # get real index in whole image_list
            index = index[0]*self.column_num + index[1]
            index = pre_index + index
            if index >= self.image_num:
                continue
            image_file = self.image_list[index]
            self.deleted_image.add(image_file)
            # delete image from table 
            deleted_image_link = delete_image_from_subclass(CURSOR, self.table_name, self.subclass_name, image_file)
            CONN.commit()
            # delete local image link
            try:
                os.remove(os.path.join("IMAGE", self.table_name, self.subclass_name, deleted_image_link))
            except Exception as e:
                print(e)
        # reduce number of image file
        self.image_num -= len(indexes)
        # romove image file from image_list
        for image_file in self.deleted_image:
            index = self.image_list.index(image_file)
            _ = self.image_list.pop(index)
        self.deleted_image.clear()
    
    
    def show_origin_image(self, row, column):
        """
        在新窗口中显示原始尺寸的图片。如果图片过大，对其进行缩放。
        Show image with original size in new window. If image is too large, scale it down.
        
        :param row: row index, int
        :param column: column index, int
        """
        # calculate which image is double clicked
        pre_row_num = self.current_page*self.row_num
        image_index = (pre_row_num+row)*self.column_num + column
        if image_index >= self.image_num: # cell can be double-clicked anywhere
            return
        image_file = self.image_list[image_index]
        # display image
        self.image_viewer.image_file = image_file
        self.image_viewer.display()
        self.image_viewer.show()
    
    
    def update_page_index(self):
        """
        更新显示在label_curent_page中的当前页面索引值。
        Update current page index shown in label_curent_page.
        """
        self.label_page_index.setText(" %d " % (self.current_page+1))
    
    
    def update_page_name(self):
        """
        从分类页面调用时，需要将label_notice的显示内容设置为对应的子类的名称，例如“2010-01-01/北京市/我自己/狗狗”等。
        When invoked from class page, content of label_notice should be class name, such as 
        "2010-01-01/Beijing/Myself/Dog" and so on.
        
        :param label: class label, str
        """
        if self.subclass_name is None:
            return
        self.label_page_name.setText(self.subclass_name)
    
    
    def update_display(self):
        """
        将图片列表中的图片显示在表格中。
        Given an image list, show them in table widget.
        
        :param image_list: image list, list
        :param column_num: column number of table widget, int
        :param item_size: image item size, int
        :return None:
        """
        # update page note (current page index)
        self.update_page_name()
        self.update_page_index()
        # update images displayed
        pre_index = self.column_num*self.row_num*self.current_page
        for i in range(self.row_num):
            for j in range(self.column_num):
                index = pre_index + i*self.column_num + j
                if index >= self.image_num: # avoid IndexError
                    item = QLabel()
                    self.tableWidget_image.setCellWidget(i, j, item)
                    continue
                # 耗时分析： 加载、缩放、设置像素值、设置子部件
                # time consuming analysis: load/ scale/ setPix/ setCell
                # (E-02:E-01)/ (E-03:E-02)/ (E-05)/ (E-04)
                # 可以看出从硬盘中加载图片是最耗时的环节（且图片尺寸越大，体积越大，耗时约长），暂无优化
                # so we can conclude loading image from hard disk is quite time consuming
                icon = QPixmap(self.image_list[index]) # load image file into pixel map
                icon = icon.scaled(self.item_size, self.item_size, Qt.KeepAspectRatio, Qt.SmoothTransformation) # scale pixel map
                item = QLabel()
                item.setAlignment(Qt.AlignCenter)
                item.setPixmap(icon) # set pixel map
                self.tableWidget_image.setCellWidget(i, j, item) # add cell widget
        # scroll to the top of table 
        self.tableWidget_image.verticalScrollBar().setSliderPosition(0)
    
    
    def refresh(self):
        """
        当一个新的image list或者None传递给image_list时，更改相关参数，并刷新当前页（首页）。
        After new image list/None was passed to image_list, modify related parameters, 
        and update current page (the first page).
        """
        # 如果图片列表为None，显示警告信息，确认后返回首页。
        # if image list is None, show warning information
        if self.image_list is None:
            _ = QMessageBox.warning(self, "Warning", "No images satisfy searching condition", QMessageBox.Ok, QMessageBox.Ok)
            self.pushButton_return.click()
            return
        self.current_page = 0 # current page index
        self.image_num = len(self.image_list) # image number 
        self.last_page = math.ceil(self.image_num/(self.row_num*self.column_num)) - 1 # last page index
        self.update_display() # update current image
        self.update() # force table to update


class ClassImage(QWidget, _ClassImage):
    def __init__(self, table_name=None, like=False, rename=False):
        """
        This class is used to show class images.
        Its layout and function is similar to that of SearchImage.
        
        :param table_name: current table name, str
        :param rename: whether to enable rename function, bool
        """
        super(ClassImage, self).__init__()
        self.setupUi(self)
        self.table_name = table_name
        self.like = like
        self.rename = rename
        self.column_num = 4
        self.row_num = 4
        self.item_size = 200
        self.subclass_list = None
        self.subclass_num = None
        self.current_page = 0
        self.last_page = 0
        self.name2function = {"Date": image_group_by_date,
                              "Place": image_group_by_place,
                              "People": image_group_by_person,
                              "Thing": image_group_by_thing}
        self.set_icons()
        self.set_actions()
        self.set_table_attributes()
        # context menu action
        self.tableWidget_image.customContextMenuRequested.connect(self.choose_action)
        self.tableWidget_image.setSelectionBehavior(QAbstractItemView.SelectItems) # item selection mode
        self.tableWidget_image.setSelectionMode(QAbstractItemView.SingleSelection) # allow single selection
        self.tableWidget_image.setEditTriggers(QAbstractItemView.NoEditTriggers) # forbid edit behavour
        # initialize images and labels displayed
        self.init_display()
    
    
    def set_icons(self):
        """
        为四个按钮设置图标。
        Set icons for four push buttons.
        """
        self.pushButton_first.setIcon(QIcon(os.path.join("icon", "first.png")))
        self.pushButton_previous.setIcon(QIcon(os.path.join("icon", "previous.png")))
        self.pushButton_next.setIcon(QIcon(os.path.join("icon", "next.png")))
        self.pushButton_last.setIcon(QIcon(os.path.join("icon", "last.png")))
    
    
    def set_actions(self):
        """
        为四个按钮设置触发动作。
        Set triggered actions fro four push buttons.
        """
        self.pushButton_first.clicked.connect(self.first_button_clicked)
        self.pushButton_previous.clicked.connect(self.previous_button_clicked)
        self.pushButton_next.clicked.connect(self.next_button_clicked)
        self.pushButton_last.clicked.connect(self.last_button_clicked)
    
    
    def set_table_attributes(self):
        """
        设置QTableWidget的一些属性信息。
        Set some attributes of QTableWidget.
        """
        # table section stretch mode
        self.tableWidget_image.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # set row/column number
        self.tableWidget_image.setRowCount(self.row_num)
        self.tableWidget_image.setColumnCount(self.column_num)
        # set row/column width
        for i in range(self.row_num):
            self.tableWidget_image.setRowHeight(i, self.item_size+20)
        for j in range(self.column_num):
            self.tableWidget_image.setColumnWidth(j, self.item_size)
    
    
    def first_button_clicked(self):
        """
        当按钮pushButton_first被点击后，修改当前页面索引值，并刷新页面。
        After pushButton_first was clicked, modify value of current page index, 
        and then refresh current page.
        """
        if self.current_page == 0: # already the first page
            _ = QMessageBox.information(self, "Notice", "Current page is already the first page", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.current_page = 0
        self.update_display()
    
    
    def previous_button_clicked(self):
        """
        当按钮pushButton_previous被点击后，修改当前页面索引值，并刷新页面。
        After pushButton_previous was clicked, modify value of current page index, 
        and then refresh current page.
        """
        if self.current_page == 0: # already the first page
            _ = QMessageBox.information(self, "Notice", "Current page is already the first page", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.current_page -= 1
        self.update_display()
    
    
    def next_button_clicked(self):
        """
        当按钮pushButton_next被点击后，修改当前页面索引值，并刷新页面。
        After pushButton_next was clicked, modify value of current page index, 
        and then refresh current page.
        """
        if self.current_page == self.last_page:
            _ = QMessageBox.information(self, "Notice", "Current page is already the last page", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.current_page += 1
        self.update_display()
    
    
    def last_button_clicked(self):
        """
        当按钮pushButton_last被点击后，修改当前页面索引值，并刷新页面。
        After pushButton_last was clicked, modify value of current page index, 
        and then refresh current page.
        """
        if self.current_page == self.last_page:
            _ = QMessageBox.information(self, "Notice", "Current page is already the last page", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.current_page = self.last_page
        self.update_display() 
    
    
    def update_page_index(self):
        """
        当页面切换时，更新显示在label_page_index中的页当前页数。
        Update current page index shown in label_page_index when page is switched.
        """
        self.label_page_index.setText(" %d " % (self.current_page+1))
    
    
    def update_display(self):
        """
        更新显示当前的图片
        Update images and labels displayed.
        """
        # update shown page index
        self.update_page_index()
        pre_index = self.column_num*self.row_num*self.current_page
        for i in range(self.row_num):
            for j in range(self.column_num):
                index = pre_index + self.column_num*i + j
                if index >= self.subclass_num: # avoid IndexError
                    item = QTableWidgetItem("")
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable) # item placeholder, can not be chosen
                    self.tableWidget_image.setItem(i, j, item)
                    continue
                
                item = LabeledImage(self.subclass_list[index])
                self.tableWidget_image.setCellWidget(i, j, item) # add cell widget
        # scroll to top
        self.tableWidget_image.verticalScrollBar().setSliderPosition(0)
    
    
    def init_display(self):
        """
        初始化显示的图片和标签。在部件的整个生命周期中，该函数仅被调用一次。
        流程：
            使用相应的函数查询subclass_list，
            检查返回结果是否为空，
            计算相关参数，
            更新显示内容。
        Initialize images and labels displayed. This function will be invoked 
        only once during whole life cell.
        Pipeline:
            query images using specific function,
            check if it's None,
            calculate related parameters,
            show images and labels.
        """
        image_group_function = self.name2function[self.table_name] # get corresponding function
        self.subclass_list = image_group_function(CURSOR) # query for subclass images
        # make sure it's not None
        if self.subclass_list is None:
            # showing warning information?
            #_ = QMessageBox.warning(self, "Warning", "No Records in this Class", QMessageBox.Ok, QMessageBox.Ok)
            return
        self.current_page = 0 # current page index
        self.subclass_num = len(self.subclass_list) # image number 
        self.last_page = math.ceil(self.subclass_num/(self.row_num*self.column_num)) - 1 # last page index
        self.update_display() # update current image
    
    
    def get_subclass_index(self):
        """
        获取被双击的子类的索引。
        Get index of double-clicked subclass item.
        
        :param None:
        :return index: double-clicked subclass item, int
        """
        indexes = self.tableWidget_image.selectedIndexes()
        if len(indexes) == 0: # wrong widgets were chosen
            return None, None, None
        pre_index = self.current_page*self.row_num*self.column_num
        for index in indexes:
            row = index.row()
            column = index.column()
        index = pre_index + row*self.column_num + column
        return index, row, column
    
    
    def query_subclass(self):
        """
        查询子类图片。
        Query images of subclass.
        
        :return subclass_images: images of subclass, list
        :return subclass_value: name of subclass, str
        """
        subclass_index, _row, _column = self.get_subclass_index()
        if subclass_index is None:
            return None, None
        subclass_info = self.subclass_list[subclass_index]
        subclass_key = subclass_info[0]
        subclass_value = subclass_info[1]
        subclass_images = query_subclass(CURSOR, subclass_key, subclass_value)
        return subclass_images, subclass_value
    
    
    def choose_action(self, position):
        """
        显示鼠标右键菜单，根据选择的动作执行对应的操作。
        Show mouse right menu, and execute corrsponding function according to action.
        
        :param position: right menu activated position, QCursor.pos
        """
        # construct righr button menu
        right_menu = QMenu(self)
        like_action = right_menu.addAction("Like") # like action
        if not self.like:
            like_action.setEnabled(False) # can not be clicked
        rename_action = right_menu.addAction("Rename") # rename action
        if not self.rename:
            rename_action.setEnabled(False)
        
        action = right_menu.exec_(self.tableWidget_image.mapToGlobal(position)) # show menu
        index, _row, _column = self.get_subclass_index() # get selected subclass index, only one can be chosen each time
        if action == like_action: # choose action, execute corresponding function
            self.like_subclass(index, _row, _column)
        elif action == rename_action:
            self.rename_subclass(index, _row, _column)
    
    
    def like_subclass(self, index, row, column):
        """
        为子类中的图片添加喜欢记录。
        Add like records for images in current chosen subclass.
        """
        if index is None:
            return
        print(index)
        print("Sorry, this function has not been implemented yet.")
    
    
    def show_input_dialog(self, default_text):
        """
        显示输入对话框，以便从用户的输入中获得一个新名称。
        Show input dialog to get a new name from user.
        
        :param default_text: default text shown in input dialog, str
        :return text: new subclass name, str/None
        """
        text, ok = QInputDialog.getText(self, "Input Dialog", "Please enter new name:", 
                                        QLineEdit.Normal, default_text)
        if ok:
            return text
        return None
    
    
    def new_name_exist(self, new_name):
        """
        判断新名称是否已经存在。
        Verify if this new name already exists.        
        
        :param new_name: new subclass name, str
        :return : whether new name is legal or not, bool
        """
        subclass_set = set(subclass[1] for subclass in self.subclass_list)
        return new_name in subclass_set
    
    
    def rename_subclass(self, index, row, column):
        """
        将当前选定的子类重命名。
        流程：
            显示修改对话框，
            检查新名称是否合法（无重复），
            修改显示的名称，
            
            修改数据库中对应的记录。
        Rename current chosen subclass.
        pipeline:
            show dialog to modify current name,
            verify new name,
            change displayed name,
            
            change related records in database.
        
        :param index: index of subclass in whole subclass_list, int
        :param row: row index in table, int
        :param column: column index in table, int
        """
        # index is out of range
        if index is None:
            return
        # show dialog to get new name
        subclass_name = self.subclass_list[index][1]
        new_name = self.show_input_dialog(subclass_name)
        if new_name is None: # choose cancel
            return
        if new_name == "": # empty string
            _ = QMessageBox.warning(self, "Warning", "You should enter a valid name", 
                                        QMessageBox.Ok, QMessageBox.Ok)
            return
        if new_name == subclass_name: # unchanged name
            _ = QMessageBox.warning(self, "Warning", "You should enter a different name", 
                                        QMessageBox.Ok, QMessageBox.Ok)
            return
        # verify new name, subclass with the same name may exist
        if self.new_name_exist(new_name):
            _ = QMessageBox.warning(self, "Warning", "Same name already exists", 
                                        QMessageBox.Ok, QMessageBox.Ok)
            return
        # change displayed name of chosen cell
        self.tableWidget_image.cellWidget(row, column).label_text.setText(new_name)
        # change subclass name in subclass_list
        self.subclass_list[index] = (self.subclass_list[0], new_name, self.subclass_list[2])
        # change records in database
        rename_subclass(CURSOR, self.table_name, subclass_name, new_name)
        CONN.commit()
        # change name of directory
        change_dir_name(self.table_name, subclass_name, new_name)
        # change name recoreded in text file
        change_text_name(self.table_name, subclass_name, new_name)


class ImageViewer(QWidget):
    def __init__(self, image_file=None):
        """
        该类用于图片的显示。
        This class is used to display an image.
        
        :param image_file: image file path, str
        """
        super(ImageViewer, self).__init__()
        self.scale_factor = 1.0 # default scale factor
        self.minimum_factor = 0.1 # minimum image scale factor
        self.maximum_factor = 10.0 # maximum image scale factor
        self.zoom_in_step = 1.25 # zoom in step 
        self.zoom_out_step = 0.8 # zoom out step
        self.ctrl_pressed = False
        self.image_file = image_file
        self.default_ratio = 0.75 # using 75% area of screen to display image
        self._calculate_default_size()
        
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base) # fill background with base color
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setAlignment(Qt.AlignCenter) # center align
        self.imageLabel.setScaledContents(True) # when label scales, its content is scaled ath the same time

        self.scrollArea = QScrollArea() # scroll area
        self.scrollArea.setBackgroundRole(QPalette.Dark) # dark background
        self.scrollArea.setWidget(self.imageLabel) # imageLabel is child widget of scroll area
        self.centerLayout = QVBoxLayout(self)
        self.centerLayout.addChildWidget(self.scrollArea)
        self.setLayout(self.centerLayout)
        # add two action triggered by shortcut to invoke zoom in/out function 
        self.Action_zoom_out = QAction("", self, shortcut="Ctrl+Down", triggered=self.zoom_out)
        self.addAction(self.Action_zoom_out)
        self.Action_zoom_in = QAction("", self, shortcut="Ctrl+Up", triggered=self.zoom_in)
        self.addAction(self.Action_zoom_in)
        
        self.display()
    
    
    def set_window_title(self):
        """
        从图像文件路径中解析得到图片名，并将其设置为窗口标题。
        Using name of image file to set window title.
        """
        image_path, image_file = os.path.split(self.image_file)
        self.setWindowTitle(image_file)
    
    
    def _calculate_default_size(self):
        """
        计算用于显示图片的默认尺寸大小。
        Calculate default size to display an image.
        """
        desktop = QApplication.desktop().availableGeometry()
        self.default_width = int(desktop.width() * self.default_ratio)
        self.default_height = int(desktop.height() * self.default_ratio)
    
    
    def _calculate_size(self, width, height):
        """
        为了限制图片的尺寸小于初始化尺寸，计算新的图片尺寸。
        To constraint image size smaller than init_size, calculate new image size.
        
        :param width: image width, int
        :param height: image height, int
        :return w_target: proper image width, int
        :return h_target: proper image height, int
        """
        w_ratio = self.default_width / width
        h_ratio = self.default_height / height
        ratio = min(w_ratio, h_ratio)
        self.scale_factor = ratio # set scale factor to this value
        w_target = int(ratio * width)
        h_target = int(ratio * height)
        return w_target, h_target
    
    
    def _calculate_location(self):
        """
        为了将ImageViewer移动至屏幕的中心位置，计算位置信息。
        Calculate position in order to move ImageViewer to the center of screen.
        
        :return x_target: left position value, int
        :return y_target: top position value, int
        """
        #desktop = QApplication.desktop().availableGeometry()
        #x = desktop.x()
        #y = desktop.y()
        x_target = (self.default_width * 2 - self.size().width()) // 2
        y_target = (self.default_height * 2 - self.size().height()) // 2
        return x_target, y_target
        
    
    def display(self):
        """
        调整部件尺寸，显示图片，设置部件标题。
        Adjust widget size, display image, set window title.
        """
        # prevent error
        if self.image_file is None:
            return
        # resize and move widget
        img = QPixmap(self.image_file)
        width, height = self._calculate_size(img.width(), img.height())
        self.resize(width, height)
        x, y = self._calculate_location()
        self.move(x, y)
        # set pixel map, adjust, move to center, set title
        self.imageLabel.setPixmap(img)
        self.imageLabel.adjustSize()
        self.label_to_center()
        self.set_window_title()
    
    
    def label_to_center(self):
        """
        将imageLabel移动至部件的中心。
        Move imageLabel to the center of the widget.
        """
        # calculate where to move
        widget_geo = self.geometry()
        label_geo = self.imageLabel.geometry()
        x = (widget_geo.width() - label_geo.width()) // 2
        y = (widget_geo.height() - label_geo.height()) // 2
        x = x if x > 0 else 0
        y = y if y > 0 else 0
        # move to let imageLabel located in the middle of the widget
        # This still exists a problem here. After moveing imageLabel, the widget 
        # should be updated immediately, but it is not updated immediately.
        self.imageLabel.move(QPoint(x,y))
    
    
    def resizeEvent(self, event):
        """
        当部件的尺寸发生变化时，调整scroll area的尺寸，以便其尺寸和部件尺寸保持
        一致，同时调用label_to_center使label移动到部件中心。
        When widget is resized, change the size of scroll area 
        in order to keep its size as same as widget's and keep label in the middle.
        """
        super().resizeEvent(event)
        self.scrollArea.resize(self.size())
        self.label_to_center()
        
    
    def keyPressEvent(self, event):
        """
        当Ctrl键被按下时，将ctrl_pressed的值设置为True。
        When Ctrl is pressed, set value of ctrl_pressed to True.
        """
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = True
    
    def keyReleaseEvent(self, event):
        """
        当Ctrl键被释放时，将ctrl_pressed的值设置为False。
        When Ctrl is released, set value of ctrl_pressed to False.
        """
        super().keyReleaseEvent(event)
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = False
    
    
    def wheelEvent(self, event):
        """
        当鼠标滚轮滚动时，放大或者缩小图片。
        When wheel is rolled, zoom in/out image.
        """
        super().wheelEvent(event)
        if self.ctrl_pressed:
            delta = event.angleDelta()
            oriention = delta.y()
            if oriention > 0: # up, zoom in, scale to larger size
                self.zoom_in()
            elif oriention < 0: # down, zoom out, scale to smaller size
                self.zoom_out()
    
    
    def zoom_in(self):
        """
        放大图片。
        Zoom in image.
        """
        scale_factor = self.scale_factor * self.zoom_out_step
        if scale_factor > self.maximum_factor: # not larger than maximum value
            return
        self.scale_image(self.zoom_in_step)
    
    
    def zoom_out(self):
        """
        缩小图片。
        Zoom out image.
        """
        scale_factor = self.scale_factor * self.zoom_out_step
        if scale_factor < self.minimum_factor: # not smaller than minimum value
            return
        self.scale_image(self.zoom_out_step)
    
    
    def scale_image(self, ratio):
        """
        根据现有的缩放比例和缩放系数对图片进行缩放。
        Scale the image according to current scale factor and factor.
        
        :param ratio: scale ratio which indicates scale direction and ratio, float
        """
        self.scale_factor = self.scale_factor * ratio
        self.imageLabel.resize(self.scale_factor * self.imageLabel.pixmap().size()) # resize image label
        self.label_to_center()
        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), ratio) # adjust scroll bar
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), ratio)
    
    
    def adjustScrollBar(self, scroll_bar, ratio):
        """
        设置滚动条的新数值。
        Adjust scroll bar value.
        
        :param scroll_bar: scroll bar to be adjusted, QScrollBar
        :param ratio: ratio value, float
        """
        scroll_bar.setValue(int(ratio * scroll_bar.value()
                                + ((ratio - 1) * scroll_bar.pageStep()/2)))


class LabeledImage(QWidget):
    def __init__(self, info_list, item_size=200):
        """
        该类用于显示底部带有文字标签的图片。方式为将部件设置为带有两个QLabel的竖直布局，
        一个用于显示图片，一个用于显示文字。
        This class is used to show image with text label below.
        Place two labels in vertical layout, one for image, one for text.
        """
        super(LabeledImage, self).__init__()
        self.text = info_list[1]
        self.image_file = info_list[2]
        self.item_size = item_size
        # vertical layout with two label
        self.layout = QVBoxLayout()
        self.label_image = QLabel(self) # for image showing
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_text = QLabel(self) # for text showing
        self.label_text.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.layout.addWidget(self.label_image)
        self.layout.addWidget(self.label_text)
        self.setLayout(self.layout)
        self.set_content()
    
    
    def set_content(self):
        """
        为部件设置图片和标签。
        Set image and label in widget.
        """
        icon = QPixmap(self.image_file)
        icon = icon.scaled(self.item_size, self.item_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_image.setPixmap(icon)
        self.label_text.setText(self.text)



if __name__ == "__main__":
    database_test(output=False) # beforing opening application, make tables exist
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
