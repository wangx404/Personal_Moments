#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 15:25:07 2019
@author: wangxin
"""

import os
import cv2
import dlib
import numpy as np

FEATURE_DIM = 128
TEXT_DIR = "record"
FEATURE_CSV_FILE = os.path.join(TEXT_DIR, "feature_centers.csv")
FACE_NUMBER_TXT_FILE = os.path.join(TEXT_DIR, "face_numbers.txt")
FACE_NAME_TXT_FILE = os.path.join(TEXT_DIR, "face_names.txt")

dlib_face_detector = dlib.get_frontal_face_detector()
MODEL_DIR = "model"
dlib_cnn_face_detector = dlib.cnn_face_detection_model_v1(os.path.join(MODEL_DIR, "mmod_human_face_detector.dat"))
dlib_landmark_predictor = dlib.shape_predictor(os.path.join(MODEL_DIR, "shape_predictor_5_face_landmarks.dat"))
dlib_face_recognizor = dlib.face_recognition_model_v1(os.path.join(MODEL_DIR, "dlib_face_recognition_resnet_model_v1.dat"))


def dlib_face_detect(img, method):
    """
    使用dlib 人脸检测器，检测图片文件中的人脸。（slow but accurate）
    Using dlib CNN face detector, detect faces in image file.
    When using dlib CNN, you can get more accurate result, but it's very slow withou GPU;
    so this function chooose to use dlib frontal face detector in default.
    
    :param img: image object, numpy.ndarray
    :param method: face detection method, str
    :return faces: face bounding boxs, nested list
    """
    if method == "dlib":
        results = dlib_face_detector(img, 1)
    elif method == "dlib_cnn":
        results = dlib_cnn_face_detector(img, 1)
    else:
        raise ValueError
    if len(results) == 0:
        return None
    faces = []
    for result in results: # change format
        if method == "dlib_cnn":
            result = result.rect
        faces.append([result.left(), result.top(), 
                      result.right(), result.bottom()])
    return faces


def _point2list(point):
    """
    将人脸关键点从专有格式转化为列表形式。
    Transform landmark point into format of list.
    
    :param point: landmark point, dlib.point
    :return : landmark point in format of list
    """
    return [point.x, point.y]


def dlib_facial_landmark_detect(img, face):
    """
    给定一张人脸图片和人脸边框，检测人脸关键点坐标。
    Given image and face bounding box, detect facial landmark coordinates.
    
    :param img: image object, numpy.ndarray
    :param face: face bounding box, list
    :return : coordinates of left eye, right eye, nose and mouth, dlib.point
    """
    face = dlib.rectangle(*face) # transform format into dlib.rectangle
    landmarks = dlib_landmark_predictor(img, face)
    landmarks = landmarks.parts()
    
    left_eye = landmarks[0]
    left_eye = _point2list(left_eye)
    right_eye = landmarks[1]
    right_eye = _point2list(right_eye)
    nose = landmarks[2]
    nose = _point2list(nose)
    mouth = (landmarks[3] + landmarks[4]) / 2
    mouth = _point2list(mouth)
    return left_eye, right_eye, nose, mouth


def _calculate_face_angle(left_eye, right_eye):
    '''
    计算人脸倾斜角度的大小。
    左倾时，angle为负值；右倾时，angle为正值。
    Calculate face tilt angle.
    
    :param left_eye: left eye coordinate, list
    :param right_eye: right eye coordinate, list
    :return angle: face tilt angle, float
    '''
    
    deltaX = right_eye[0] - left_eye[0] # delta value in x axis
    deltaY = right_eye[1] - left_eye[1] # delta value in y axis
    
    if deltaX == 0: # face is in horizontal direction
        return None
    angle = np.arctan(deltaY / deltaX) * 180.0 / np.pi
    return angle


def _crop_face_image(img, face, margin_scale=1.5):
    """
    从原始图像中将带有margin的人脸区域剪裁出来。
    Crop face area image with extra margin from origin image.
    
    :param img: origin image, numpy.ndarray
    :param face: face bounding box, list
    :param margin_scale: margin scale factor, float
    :return face_img: face area image, numpy.ndarray
    :return face_shift: face shift relative to crop bbox, list
    """
    height, width, _ = img.shape
    # calculate xywh with margin
    xmin, ymin, xmax, ymax = face
    x = (xmin + xmax) / 2.0
    y = (ymin + ymax) / 2.0
    w = (xmax - xmin) * margin_scale
    h = (ymax - ymin) * margin_scale
    # calculate new coordinate
    n_xmin = x - w/2.0
    n_ymin = y - h/2.0
    n_xmax = x + w/2.0
    n_ymax = y + h/2.0
    # make value is legal
    n_xmin = max(0, int(n_xmin))
    n_ymin = max(0, int(n_ymin))
    n_xmax = min(width, int(n_xmax))
    n_ymax = min(height, int(n_ymax))
    # return value
    face_img = img[n_ymin:n_ymax, n_xmin:n_xmax, :]
    face_shift = [n_xmin - xmin, n_ymin - ymin]
    return face_img, face_shift


def _calculate_face_center(face, face_shift):
    """
    计算剪裁后人脸图片的中心位置，计算方式为计算相对于bbox的左上角的坐标，计算相对于剪裁bbox左上角的坐标。
    Calculate face center relative to left top corner in croped face image.
    
    :param face: face bounding box, list
    :param face_shift: coordinate shift of crop bbox relative to face bbox, list
    :return center: face image center in crop area, list
    """
    rel_x = (face[2] - face[0]) / 2.0
    rel_y = (face[3] - face[1]) / 2.0
    
    rel_x -= face_shift[0]
    rel_y -= face_shift[1]
    center = [rel_x, rel_y]
    return center


def _rotate_face(face_img, face_center, face_angle, scale=1.0):
    """
    调用cv2中的函数,返回一个旋转至竖直状态的人脸
    Invoke rotate function in cv2, rotate a titled face to vertical direction
    
    :param face_img: face area image, numpy.ndarray
    :param face_center: rotate center, list
    :param face_angle: face tilt angle, float
    :param scale: face scale factor, float
    :return rotated_face_img: face image after rotation, numpy.ndarray
    """
    h, w = face_img.shape[:2] # face_img.shape==h,w,c
    # fet rotate matrix
    M = cv2.getRotationMatrix2D(tuple(face_center), face_angle, scale)
    rotated_face_img = cv2.warpAffine(face_img, M, (w, h))
    return rotated_face_img


def extract_face_feature(face_img, method="dlib"):
    """
    计算人脸图片的特征。
    Compute face feature with vertical face image.
    
    :param face_img: face image after rotating to vertical direction, numpy.ndarray
    :return face_feature: face_feature
    """
    if method == "dlib":
        face = dlib_face_detector(face_img, 1)[0]
    elif method == "dlib_cnn":
        face = dlib_cnn_face_detector(face_img, 1)[0].rect
    else:
        raise ValueError
    landmark = dlib_landmark_predictor(face_img, face) # detect facial landmark
    face_feature = dlib_face_recognizor.compute_face_descriptor(face_img, landmark) # compute face feature
    face_feature = np.array(face_feature)
    return face_feature


def get_face_feature(img, face, method):
    """
    一般而言，在计算脸部特征之前无需对人脸进行专门的旋转校正，但是在旋转校正之后再进行特征计算可以得到
    更准确的结果。因此在此函数中使用了这一较为复杂的路线。
    运算过程：人脸关键点检测，倾斜角度计算，人脸旋转，人脸特征计算。
    Generally speaking, you can calculate face feature without rotating it, but 
    we can get more accurate result using this method which is a little more complex.
    pieline: detect facial landmark, calculate face tilt angle, rotate face, 
    calculate face feature.
    
    :param img: image object, numpy.ndarray
    :param face: face bounding box, list
    :method: face detection method, str
    """
    left_eye, right_eye, _nose, _mouth = dlib_facial_landmark_detect(img, face) # detect facial landmark
    face_angle = _calculate_face_angle(left_eye, right_eye) # calculate tilt angle
    #face_angle = - face_angle # 
    face_img, face_shift = _crop_face_image(img, face) # crop face area image
    face_center = _calculate_face_center(face, face_shift) # calculate face center
    rotated_face_img = _rotate_face(face_img, face_center, face_angle)
    face_feature = extract_face_feature(rotated_face_img, method)
    return face_feature


def get_face_feature_without_rotation(img, face, method):
    """
    此函数中的人脸特征计算方法更为简单直接。
    运算过程：人脸关键点检测，人脸特征计算。
    A simple and straight way to get face feature.
    pipeline: detect facial landmark, calculate face feature.
    
    :param img: image object, numpy.ndarray
    :param face: face bounding box, list
    :method: face detection method, str
    """
    face = dlib.rectangle(*face)
    landmark = dlib_landmark_predictor(img, face)
    face_feature = dlib_face_recognizor.compute_face_descriptor(img, landmark)
    return face_feature


def get_face_features(image_file, method="dlib"):
    """
    如果一张图片包含人脸，检测人脸位置及相应特征。
    Given a face image, detect face bounding box and calculate face feature.
    
    :param image_file: image file, str
    :param method: face detection method, str
    :return : face bboxs and face features
    """
    # detect face
    try:
        img = dlib.load_rgb_image(image_file)
        faces = dlib_face_detect(img, method)
    except Exception:
        print("Error happended when detecting face of %s" % image_file)
        return None
    if faces is None: # No face
        print("No face in %s" % image_file)
        return None
    
    bboxs = []
    features = []
    for face in faces: # for loop
        try:
            feature = get_face_feature(img, face, method)
        except Exception: # error happen
            print("Error happened when calculating face feature of %s" % image_file)
            continue
        bboxs.append(face)
        features.append(feature)
    
    if len(bboxs) == 0: # no face and no feature
        print("No face/feature in %s" % image_file)
        return None
    return [bboxs, features]


def load_feature_centers(csv_file=FEATURE_CSV_FILE):
    """
    从csv文件中加载人脸特征矩阵。
    Load face feature matrix from csv file.
    
    :param csv_file: csv file that contains feature matrix, str
    :return feature_centers: face feature centers matrix, numpy.ndarray
    """
    if not os.path.exists(csv_file):
        return None
    feature_centers = np.loadtxt(csv_file, delimiter=",")
    return feature_centers
    

def load_face_numbers(txt_file=FACE_NUMBER_TXT_FILE):
    """
    从文本文件中加载人脸数目信息。
    Load face number of every face from txt file.
    
    :param txt_file: txt file, str
    :return face_numbers: face numbers, list
    """
    with open(txt_file, "r") as f:
        face_numbers = f.readlines()
    face_numbers = [number.rstrip() for number in face_numbers]
    face_numbers = [int(number) for number in face_numbers]
    return face_numbers


def load_face_names(txt_file=FACE_NAME_TXT_FILE):
    """
    从文本文件中加载人链名称。
    Load face names from txt file.
    
    :param txt_file: txt file, str
    :return face_names: face names, list
    """
    with open(txt_file, "r") as f:
        face_names = f.readlines()
    face_names = [name.rstrip() for name in face_names]
    return face_names


def save_feature_centers(feature_centers, csv_file=FEATURE_CSV_FILE):
    """
    将人脸特征矩阵保存至csv文件中。
    Save face feature centers into csv file.
    
    :param feature_centers: face feature centers. numpy.ndarray
    :param csv_file: csv file, str
    :return None:
    """
    np.savetxt(csv_file, feature_centers, delimiter=",", newline="\r\n")


def save_face_numbers(face_numbers, txt_file=FACE_NUMBER_TXT_FILE):
    """
    将每张人脸对应的图片数目保存至文本文件中。
    Save face numbers (image file number of every face) into txt file.
    
    :param face_numbers: face numbers of every face, list
    :param txt_file: txt file, str
    :return None:
    """
    face_numbers = [str(number)+"\r\n" for number in face_numbers]
    with open(txt_file, "w") as f:
        f.writelines(face_numbers)


def save_face_names(face_names, txt_file=FACE_NAME_TXT_FILE):
    """
    将每张人脸对应的姓名保存至文本文件中。
    Save face names (order by feature matrix) into txt file.
    
    :param face_names: face names order by feature matrix, list
    :param txt_file: txt file, str
    :return None:
    """
    face_names = [name+"\r\n" for name in face_names]
    with open(txt_file, "w") as f:
        f.writelines(face_names)


def init_feature_center():
    """
    使用特定值对特征矩阵，人脸数量和人脸名称等相关数据进行更新。
    Initialize feature center, face number, face name with specific values.
    
    :param feature: first feature to be added, numpy.ndarray
    :return feature_centers: initialized feature center matrix, numpy.ndarray
    :return face_numbers: face number, list
    :return face_names: face names, list
    """
    feature_centers = np.zeros(shape=(1, FEATURE_DIM)) # default feature shape is (1,128)
    face_numbers = [-1]
    face_names = ["MrNobody"]
    return feature_centers, face_numbers, face_names


def calculate_distance(f_center, feature):
    """
    计算两个特征向量的欧氏距离。
    Calculate euclidean distance between two feature array.
    
    :param f_center: feature center of one class
    :param feature: one feature array of one image
    :return: euclidean distance
    """
    return np.sum((f_center - feature)**2)


def update_feature_center(f_center, f_number, feature):
    """
    使用新的特征对原有的平均特征进行更新。
    Update feature center of an existing class using its new feature.
    
    :param f_center: feature center of one class, numpy.ndarray
    :param f_number: face number of current feature, int
    :param feature: one feature array of one image, numpy.ndarray
    :return new_f_center: updated feature center
    """
    new_f_center = (f_center * f_number + feature) / (f_number + 1)
    return new_f_center


def add_feature_center(f_centers, f_numbers, f_names, feature):
    """
    增加一个新的特征后，扩展特征矩阵，更新人脸数目和名称信息。
    Expand face feature centers when new feature of new class is added in.
    
    :param f_centers: face feature centers, numpy.ndarray
    :param f_numbers: face numbers, list
    :param f_names: face names, list
    :param feature: new feature, numpy.ndarray
    :return new_f_centers: new face feature centers, numpy.ndarray
    :return f_numbers: new face numbers, list
    :return f_names: new face names, list
    """
    # update feature matrix
    feature = feature.reshape((1, -1))
    new_f_centers = np.concatenate((f_centers, feature), axis=0)
    # update face numbers and names
    f_numbers.append(1)
    f_names.append("Person_%04d" % len(f_names))
    return new_f_centers, f_numbers, f_names


def delete_feature_center(f_centers, f_numbers, f_names, f_index):
    """
    给定一个索引，删除索引对应的特征，人脸数目和姓名。
    Delete feature in the position of f_index.
    
    :param f_centers: face feature centers, numpy.ndarray
    :param f_numbers: face counts, list
    :param f_names: face names, list
    :return new_f_centers: new face feature centers, numpy.ndarray
    :return f_counts: new face counts, list
    :return f_names: new face names, list
    
    """
    new_f_centers = np.delete(f_centers, f_index, axis=0)
    f_numbers.pop(f_index)
    f_names.pop(f_index)
    return new_f_centers, f_numbers, f_names
    

def KNN_search(feature_centers, feature, dist_threshold):
    """
    使用KNN搜索的方式在特征矩阵中为新特征查找最相似的归属类别，最终其和附属类别的中心
    特征之间的欧氏距离应该小于距离阈值。
    Find a proper distribution class for feature using KNN search method, which 
    should have a euclidean distance less than distance threshold.
    
    :param feature_centers: face feature centers, numpy.ndarray
    :param feature: unknown class's feature, numpy.ndarray
    :param dist_threshold: distance threshold, default is 0.6, float
    :return flag: whether or not find a attribution class, bool
    :return index: distribution class index, int
    """
    feature = feature.reshape((1, -1))
    distances = (feature_centers - feature)**2 # calculate diff**2
    distances = distances.sum(axis=1) # sum along feature axis
    indexs = distances.argsort().tolist() # 
    distances.sort()
    distances = distances.tolist()
    
    #print(distances[0], indexs[0])
    if distances[0] < dist_threshold: # find a proper distribution class
        flag = True
        index = indexs[0]
    else:
        flag = False
        index = None
    return flag, index
    

