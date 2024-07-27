import pickle
import cv2
import numpy as np



map_file_path = "map.p"
countries_file_path = "countries.p"
cam_id = 1
width, height = 1920, 1080


cap = cv2.VideoCapture(cam_id)


cap.set(3, width)
cap.set(4, height)


file_obj = open(map_file_path, 'rb')
map_points = pickle.load(file_obj)
file_obj.close()
print(f"Loaded map coordinates.", map_points)
