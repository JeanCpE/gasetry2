import streamlit as st

# File processing Pkgs
from PIL import Image

import torch
from torchvision import transforms
from models.experimental import attempt_load

import cv2
import numpy as np

import os
import subprocess
import detect
import argparse

from IPython.display import display

def load_image(image_file):
    img = Image.open(image_file)
    return img

def main():
    # allDF contains the transactions or all the data (firstly contains the GPS and the File Name)
    # gaseDF contains the data of the recently uploaded file
    # allDF = allDF + gaseDF
    # gpsDF contains the data of all True in detections allDF - gaseDF (False detections)

    print('~~APP STARTED~~')



    st.title("YOLOv7 Object Detection")

    #Get input Image
    image_file = st.file_uploader("Upload Images", type=["png","jpg","jpeg"])

    if image_file is not None:
        #Display uploaded image
        display_image = st.image(load_image(image_file),width=300)

        # Convert uploaded file to image object
        file_path = image_file.name #Get Image file name

        # Save the uploaded file to disk
        with open("uploads/"+file_path, "wb") as f:
            f.write(image_file.getbuffer())
            #Show image save success
            st.write("File saved!")

        # Change detect parameters
        if 'weights' not in [action.dest for action in detect.parser._actions]:
            detect.parser.add_argument('--weights', nargs='+', type=str, default='yolov7.pt', help='model.pt path(s)')
            print('weights args added')
        if 'source' not in [action.dest for action in detect.parser._actions]:
            detect.parser.add_argument('--source', type=str, default='inference/images',
                            help='source')  # file/folder, 0 for webcam
            print('source args added')
        if 'conf_thres' not in [action.dest for action in detect.parser._actions]:
            detect.parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
            print('conf args added')

        detect.parser.set_defaults(weights='runs/weights/exp-18-last.pt', conf_thres=0.1, source=("uploads/"+file_path))
        args = detect.parser.parse_args()
        print('Arguments passed:',args)

        gaseDF = detect.main(args)

        # Specify the directory to scan
        directory = 'runs/detect'

        # Get a list of all directories in the specified directory
        directories = [entry.path for entry in os.scandir(directory) if entry.is_dir()]

        # Sort the directories by modification time in descending order
        directories.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        # Get the latest directory
        latest_directory = directories[0]

        print("Latest directory:", latest_directory)

        new_image_path = latest_directory + "/" +file_path
        display_image.image(new_image_path, caption='New Image')

        print('DF:')
        display(gaseDF)





if __name__ == '__main__':
    main()
