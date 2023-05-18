# GASE Egg Hotspot Mapping Prototype App
# -------Dependencies-----------
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit.web.cli import main
import pandas as pd
import leafmap.foliumap as leafmap

# dependencies for gps
from PIL import Image
from PIL.ExifTags import TAGS
import piexif

# dependecies for detect
import torch
from torchvision import transforms
from models.experimental import attempt_load

import cv2
import numpy as np

import os
import detect
import argparse

from IPython.display import display

# dependencies for Camera GPS
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
import json

# dependencies for Google API
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import io

import logging

log_file = "loghome.log"

logging.basicConfig(filename=log_file, level=logging.INFO)

# ------START----
logging.info('~~APP STARTED~~')

# Set the Google Drive API credentials
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gdata_drive"],
    scopes=['https://www.googleapis.com/auth/drive']
)

# Create a Google Drive service object
drive_service = build('drive', 'v3', credentials=credentials)
folder_id = "1A102nf_J2ouBoZOds_3OTXYAAtp6cFdX"


def upload_to_drive(uploaded_file, folder_id):
    # Create file metadata with parent folder ID
    file_metadata = {
        'name': uploaded_file.name,
        'parents': [folder_id]
    }

    # Create media object with uploaded file
    media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)

    # Upload the file to Google Drive
    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    st.success("File uploaded successfully!")

    # except Exception as e:
    #     st.error(f"Error uploading file: {str(e)}")


page_title = "GASEApp"
page_icon = ":seedling:"
layout = "centered"

logging.info(f'page_title = {page_title}, page_icon = {page_icon}, layout{layout}')

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)


# st.markdown("<h1 style='text-align: center;'>Gase App</h1>", unsafe_allow_html=True)
# --------------------
def load_image(image_file):
    logging.info(f'loading image: {image_file}')
    img = Image.open(image_file)
    return img


def detection(image_file, text):
    # Convert uploaded file to image object
    file_path = image_file.name  # Get Image file name

    # Save the uploaded file to disk
    with open("uploads/" + file_path, "wb") as f:
        f.write(image_file.getbuffer())
        # Show image save success
        text.markdown(f"<div style='text-align: center;font-size: 24px;'>File Saved!</div>", unsafe_allow_html=True)

    # Change detect1 parameters
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

    detect.parser.set_defaults(weights='exp-18-last.pt', conf_thres=0.1, source=("uploads/" + file_path))
    args = detect.parser.parse_args()

    text.markdown(f"<div style='text-align: center;font-size: 24px;font-weight: bold;'>Running Detection</div>",
                  unsafe_allow_html=True)
    gase_detection = detect.main(args)
    if int(gase_detection) > 0:
        text.markdown(
            f"<div style='text-align: center;font-size: 24px;font-weight: bold;'> GAS Eggs Detected : {gase_detection}</div>",
            unsafe_allow_html=True)
    else:
        text.markdown(
            f"<div style='text-align: center;font-size: 24px;font-weight: bold;'> No GAS Eggs Detected </div>",
            unsafe_allow_html=True)
    print(f'number of detection:{gase_detection}')
    display(gase_detection)
    return gase_detection


def show_detection(image_file):
    # Specify the directory to scan
    directory = 'runs/detect'

    # Get a list of all directories in the specified directory
    directories = [entry.path for entry in os.scandir(directory) if entry.is_dir()]

    # Sort the directories by modification time in descending order
    directories.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    # Get the latest directory
    # latest_directory = directories[0]

    print("Latest directory:", directories[0])
    # Get the latest directory / Image file name
    return directories[0] + "/" + image_file.name


def check_exif(uploaded_file):
    img = Image.open(uploaded_file)
    if 'exif' in img.info:
        # Get the Exif data
        exif_dict = piexif.load(img.info['exif'])

        # Extract the GPS coordinates if available
        if "GPS" in exif_dict and piexif.GPSIFD.GPSLatitude in exif_dict["GPS"] and \
                piexif.GPSIFD.GPSLatitudeRef in exif_dict["GPS"] and \
                piexif.GPSIFD.GPSLongitude in exif_dict["GPS"] and \
                piexif.GPSIFD.GPSLongitudeRef in exif_dict["GPS"]:
            return True
        else:
            # Handle the case when GPS coordinates are not present
            gps_latitude = None
            gps_latitude_ref = None
            gps_longitude = None
            gps_longitude_ref = None
            st.warning('This image does not have a GPS.', icon="⚠️")
            st.write("Please make sure that the uploaded image was taken with an open GPS.")
            return False

    else:
        st.warning('This image does not have an exif data', icon="⚠️")
        return False


def upload_gps(uploaded_file, gase_detected):
    # Read the uploaded file and convert it into an image object
    img = Image.open(uploaded_file)
    # st.image(img, caption="Uploaded photo", use_column_width=True)

    exif_dict = piexif.load(img.info['exif'])

    gps_latitude = exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]
    gps_latitude_ref = exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef]
    gps_longitude = exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]
    gps_longitude_ref = exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef]
    # gps_altitude = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
    # gps_altitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSAltitudeRef]

    # Convert the GPS coordinates to degrees
    lat = (gps_latitude[0][0] / gps_latitude[0][1] +
           gps_latitude[1][0] / (60 * gps_latitude[1][1]) +
           gps_latitude[2][0] / (3600 * gps_latitude[2][1]))

    if gps_latitude_ref == "S":
        lat = -lat

    lon = (gps_longitude[0][0] / gps_longitude[0][1] +
           gps_longitude[1][0] / (60 * gps_longitude[1][1]) +
           gps_longitude[2][0] / (3600 * gps_longitude[2][1]))
    if gps_longitude_ref == "W":
        lon = -lon

    gps_to_csv(lat, lon, gase_detected)


def camera_gps():
    logging.info(f"camera_gps(gase_detected)")
    # ---get location via JS_EVAL
    loc = get_geolocation()
    logging.info(f"our coordinates are {loc}")
    lat = None
    lon = None
    if loc is not None:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        # Use JS_Eval to get GPS data and device data
        logging.info(f"lat{lat}, lon{lon}")
    return lat, lon


def gps_to_csv(lat, lon, gase_detected):
    # ------------If the GPS are written, append to csv---------------------------
    import pandas as pd
    # df_master = pd.read_csv( "C:/testGPS algo/gtag.csv")
    df_temporary = pd.DataFrame({'Latitude': [lat],
                                 'Longitude': [lon],
                                 # 'Altitude': [alt],
                                 'Detected': [gase_detected]
                                 #  'Time':[],
                                 #  'Date':[]
                                 })
    # ---Fill zero values with 0--
    df_temporary = df_temporary.dropna(how='any')

    # ------Export to csv--------
    filename = 'gase_temp.csv'
    if os.path.exists(filename):
        df_temporary.to_csv(filename, mode='a', index=False, header=False)
    else:
        df_temporary.to_csv(filename, index=False)


# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)


def map_gase():
    # load main dataset
    df = load_data('gase_temp.csv')
    df = df.fillna(1)
    # drop the Number customized column
    # df = df.drop('No', axis=1)

    # Open Leafmap with Google Map Layer
    # with st.echo():   #indent the importation if this shall be activated
    # import matplotlib.cm as cm

    m = leafmap.Map(center=[13.79, 121.18], zoom=25)

    # added layer
    m.add_tile_layer(
        url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        name="Google Satellite",
        attribution="Google",
    )
    m.add_title("Golden Apple Snail Egg Heat Map", font_size="20px", align="center")

    # Add the heatmap

    # Function to update the heatmap
    def update_heatmap():
        # Reload the dataset
        gase_dataset = pd.read_csv('gase_temp.csv')
        gase_dataset = gase_dataset.fillna(0)

        # Create a new map object to clear the layers
        new_map = leafmap.Map(height="1020px", width="720px",
                              center=[gase_dataset['Latitude'].iloc[-1], gase_dataset['Longitude'].iloc[-1]], zoom=20)
        new_map.add_tile_layer(
            url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            name="Google Satellite",
            attribution="Google",
        )
        colors = ['blue', 'green', 'yellow', 'red']
        vmin = gase_dataset['Detected'].min()
        vmax = gase_dataset['Detected'].max()
        new_map.add_colorbar(colors=colors, vmin=vmin, vmax=vmax, font_size=12)
        # Add the updated heatmap layer
        new_map.add_heatmap(
            gase_dataset,
            latitude="Latitude",
            longitude="Longitude",
            value="Detected",
            name="Heat map",
            radius=18,
            layer_control=True,
            overlay=True,
            control_scale=True,
            cmap=colors,
            opacity=0.7,
            min_opacity=0.5,
        )

        # new_colors = ['blue', 'green', 'yellow','red']
        # new_vmin = gase_dataset['Detected'].min()
        # new_vmax = gase_dataset['Detected'].sum()
        # new_map.add_colorbar(colors=new_colors, vmin=new_vmin, vmax=new_vmax, font_size=6)

        # This is used to display the map within the bounded settings of Width and Height
        new_map.to_streamlit(add_layer_control=True)

    # Initial heatmap
    update_heatmap()

    # # Read Google Sheets
    # gase_dataset = pd.read_csv('gase_temp.csv')
    # print(gase_dataset.columns)
    # # display DataFrame
    # df = pd.read_csv('gase_temp.csv')
    # # Fill NaN values with a specific value, such as 0
    # df = df.fillna(0)
    # st.write(df)


def main():
    logging.info("Running main()")
    with st.sidebar:
        choice = option_menu(
            menu_title="Main Menu",
            options=["Home", "GAS Eggs Heatmap", "About"],
            icons=['house', 'pin-map-fill', 'info-circle-fill']
        )
        logging.info(f"Choice = {choice}")

    if choice == "Home":
        st.markdown("<h1 style='text-align: center;'>GAS Egg Detector</h1>", unsafe_allow_html=True)
        st.write(
            "<p style='text-align: center; font-style: italic;'>Use these options to upload or capture Kuhol Eggs!</p>",
            unsafe_allow_html=True)

        st.markdown(
            '<style>div.row-widget.stRadio div{flex-direction:row;justify-content: center; padding-top: {1}rem} </style>',
            unsafe_allow_html=True)
        st.markdown(
            """<style>
            div[class*="stFileUploader"] > label > div[data-testid="stMarkdownContainer"] > p {
            font-size: 20px;
            }
            </style>
            """, unsafe_allow_html=True)
        option = st.radio("Choose a method:", ["Upload", "Camera"], horizontal=True, label_visibility="collapsed")
        logging.info(f"Option = {option}")
        # Display initial text
        text = st.empty()  # Create an empty placeholder for the text
        if option == "Upload":
            st.write("Please upload an image containing GAS eggs:")
            uploaded_file = st.file_uploader("Please upload an image containing GAS eggs:", type=["jpg", "jpeg", "png"],
                                             label_visibility="collapsed")
            if uploaded_file is not None:
                upload_to_drive(uploaded_file, folder_id)
                logging.info(f"uploaded_file is not None")

                # Read the uploaded file and convert it into an image object
                logging.info(f"displaying uploaded_file")
                img = st.image(load_image(uploaded_file))
                logging.info(f"uploaded_file displayed")

                if check_exif(uploaded_file):
                    logging.info(f"detection(uploaded_file)")
                    gase_detected = detection(uploaded_file, text)  # shall return numbers of detected GASE
                    logging.info(f"detection done. gase_detected= {gase_detected}")
                    new_image_path = show_detection(uploaded_file)  # shall return file path
                    logging.info(f"new_image_path = {new_image_path}")
                    # Display image with bounding boxes
                    img.image(new_image_path, caption='New Image')
                    logging.info(f"Image Changed")
                    if int(gase_detected) > 0:
                        logging.info(f"getting GPS of upload")
                        upload_gps(uploaded_file, int(gase_detected))

        elif option == "Camera":
            lat, lon = camera_gps()
            st.write("Please drag and drop a photo below:")
            image_file = st.camera_input("", label_visibility="collapsed")
            if image_file is not None:
                logging.info(f"image_file is not None")
                # Read the uploaded file and convert it into an image object
                logging.info(f"displaying image_file")
                img = st.image(load_image(image_file))
                logging.info(f"image_file displayed")
                # Start detection
                logging.info(f"detection(uploaded_file)")
                gase_detected = detection(image_file, text)
                logging.info(f"detection done. gase_detected= {gase_detected}")
                new_image_path = show_detection(image_file)  # shall return file path
                logging.info(f"new_image_path = {new_image_path}")
                img.image(new_image_path, caption='New Image')
                logging.info(f"Image Changed")
                if int(gase_detected) > 0:
                    logging.info(f"getting GPS of device")
                    gps_to_csv(lat, lon, gase_detected)
            image_file = None

    elif choice == "GAS Eggs Heatmap":
        map_gase()
    elif choice == "About":
        st.markdown("<h1 style='text-align: center;'> About </p>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-indent: 25px; text-align: justify'>The Golden Apple Snail Eggs Detection Application is a web application designed to detect the presence of Golden Apple Snail eggs in images.</p>",
            unsafe_allow_html=True)
        st.markdown(
            "<p style='text-indent: 25px; text-align: justify'>The app uses image processing and machine learning techniques to identify and highlight the location of Golden Apple Snail eggs in the uploaded images.</p>",
            unsafe_allow_html=True)
        st.markdown(
            "<p style='text-indent: 25px; text-align: justify'>The Golden Apple Snail Eggs Detection Application is a computer vision-based application that aims to detect the presence of golden apple snail eggs in rice fields. The golden apple snail is a notorious pest in rice fields, and its eggs can cause significant damage to crops. This application provides a quick and efficient way to detect the presence of these eggs, allowing farmers to take appropriate measures to prevent further damage.</p>",
            unsafe_allow_html=True)
        st.markdown(
            "<p style='text-indent: 25px; text-align: justify'>The application is built using deep learning techniques and is trained on a large dataset of images of golden apple snail eggs. It uses convolutional neural networks (CNNs) to automatically extract features from the input images and classify them as either containing or not containing golden apple snail eggs. The application can be run on a desktop computer or a mobile device and can be accessed through a user-friendly interface.</p>",
            unsafe_allow_html=True)
        st.markdown(
            "<p style='text-indent: 25px; text-align: justify'>The Golden Apple Snail Eggs Detection Application has the potential to revolutionize the way farmers detect and prevent golden apple snail infestations. By providing a fast and accurate way to detect the presence of snail eggs, the application can help farmers save time and money and reduce the use of harmful pesticides.</p>",
            unsafe_allow_html=True)
        st.write(""" Created by Marian De Chavez, Jean Recon, and Roselle Macaraig """)


if __name__ == '__main__':
    main()
