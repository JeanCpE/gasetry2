#GASE Egg Hotspot Mapping Prototype App
#-------Dependencies-----------
import streamlit as st
from streamlit.web.cli import main 
import pandas as pd
import leafmap.foliumap as leafmap
#dependencies for gps
from PIL import Image
from PIL.ExifTags import TAGS
import piexif

#------START----
page_title = "GASEApp"
page_icon = ":seedling:"
layout = "centered"


st.set_page_config(page_title=page_title,page_icon=page_icon,layout=layout)
st.title(page_title + " " + page_icon)

st.markdown("<h1 style='text-align: center;'>Gase App</h1>", unsafe_allow_html=True)

#--------------------
def main():
    # Create a menu with multiple pages
    menu = ["Home", "About"]
    choice = st.sidebar.selectbox("Select a page", menu)

    if choice == "Home":
        st.markdown("<h1 style='text-align: center;'>GAS Egg Detector</h1>", unsafe_allow_html=True)
        st.write("<p style='text-align: center; font-style: italic;'>Use these options to upload or capture Kuhol Eggs!</p>", unsafe_allow_html=True)
        st.write("Please upload an image containing GAS eggs:")

        option = st.radio("", ("Upload", "Camera"))
  
        if option == "Upload":
            st.write("Please drag and drop a photo below:")
            uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                # Read the uploaded file and convert it into an image object
                img = Image.open(uploaded_file)
                #st.image(img, caption="Uploaded photo", use_column_width=True)

                # Check if the image has Exif data
                if 'exif' in img.info:
                    # Get the Exif data
                    exif_dict = piexif.load(img.info['exif'])
                    
                    # Extract the GPS coordinates
                    gps_latitude = exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]
                    gps_latitude_ref = exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef]
                    gps_longitude = exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]
                    gps_longitude_ref = exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef]
                    gps_altitude = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
                    gps_altitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSAltitudeRef]
                    
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
                        
                    alt = (gps_altitude[0]/gps_altitude[1])
                    if gps_altitude_ref == 1:
                        alt = -alt              
                    
#------------If the GPS are written, append to csv---------------------------
                    import pandas as pd
                    # df_master = pd.read_csv( "C:/testGPS algo/gtag.csv")
                    df_temporary = pd.DataFrame({'Latitude:':[lat],
                                                 'Longitude':[lon],
                                                 'Altitude':[alt],
                                                #  'Time':[],
                                                #  'Date':[]
                                                 })
                    #---Fill zero values with 1--
                    df_temporary = df_temporary.fillna(1)
                        
                    # next_index = len(df_temporary)
            # Append new row of data to a specific column
                    # new_data = {'Latitude':lat,'Longitude':lon,'Altitude':alt}
                    # df_temporary.loc[next_index] = new_data
                                    
            #------Export to csv--------        
                    df_temporary.to_csv('gase_temp.csv',mode='a',index=False,header=False)
                    st.write (df_temporary)
                    # for csv_file in csv_list:
                    #     df_master = pd.read_csv(csv_file)
                    # df_master.to_csv('gase_plots.csv', mode='a', header=False, index=True)
                    # df_new = pd.read_csv("gase_plots.csv")
                    # st.write (df_new)
                    
                    
                    st.write(f"Latitude: {lat}, Longitude: {lon}, Altitude: {alt}")                                    
                else:
                    st.write("This image does not have Exif data.")
            
        elif option == "Camera":
            from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
            import json
            st.write("Please drag and drop a photo below:")
            image_file = st.camera_input("")
            #---get location via JS_EVAL
            loc = get_geolocation()              
                
            if image_file is not None:
                img = Image.open(image_file)
                st.image(img, caption="Uploaded photo", use_column_width=True)
                
            #Use JS_Eavl to get GPS data and device data

                st.write(f"Screen width is {streamlit_js_eval(js_expressions='screen.width', key = 'SCR')}")
                st.write(f"Page location is _{ streamlit_js_eval(js_expressions='window.location.origin', want_output = True, key = 'LOC')}_")
                st.write(f"Your coordinates are {loc}")

    elif choice == "About":
        st.markdown("<h1 style='text-align: center;'> About </p>", unsafe_allow_html=True)
        st.write("""
        The Golden Apple Snail Eggs Detection Application is a web application designed to detect the presence of Golden Apple Snail eggs in images.
        The app uses image processing and machine learning techniques to identify and highlight the location of Golden Apple Snail eggs in the uploaded images.

        The Golden Apple Snail Eggs Detection Application is a computer vision-based application that aims to detect the presence of golden apple snail eggs in rice fields. The golden apple snail is a notorious pest in rice fields, and its eggs can cause significant damage to crops. This application provides a quick and efficient way to detect the presence of these eggs, allowing farmers to take appropriate measures to prevent further damage.

        The application is built using deep learning techniques and is trained on a large dataset of images of golden apple snail eggs. It uses convolutional neural networks (CNNs) to automatically extract features from the input images and classify them as either containing or not containing golden apple snail eggs. The application can be run on a desktop computer or a mobile device and can be accessed through a user-friendly interface.

        The Golden Apple Snail Eggs Detection Application has the potential to revolutionize the way farmers detect and prevent golden apple snail infestations. By providing a fast and accurate way to detect the presence of snail eggs, the application can help farmers save time and money and reduce the use of harmful pesticides.
        """)
        st.write(""" Created by Marian De Chavez, Jean Recon, and Roselle Macaraig """)


#-+++++++++++++++++++++++++++++++++++++++
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)

def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

#------------------------------------------
#load main dataset
df = load_data('gase_temp.csv')
df = df.fillna(1)
#drop the Number customized column
# df = df.drop('No', axis=1)

#Open Leafmap with Google Map Layer
# with st.echo():   #indent the importation if this shall be activated
import streamlit as st
import leafmap.foliumap as leafmap
    
m = leafmap.Map(height="1020px", width="720px",center=[12.3, 122], zoom=6.5)
colors = ['blue','red']
vmin = 1
vmax = 100
m.add_colorbar(colors=colors, vmin=vmin, vmax=vmax, font_size=12)

#added layer
m.add_tile_layer(
    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    name="Google Satellite",
    attribution="Google",
    )
m.add_title("Golden Apple Snail Egg Heat Map", font_size="20px", align="center")


#Add the heatmap
# with st.echo():

gase_dataset = load_data('gase_temp.csv')
gase_dataset = gase_dataset.fillna(1)

m.add_heatmap(
    gase_dataset,
    latitude="Latitude",
    longitude='Longitude',
    value="Altitude",
    # name="Heat map",
    radius=12,
)

#This is used to display the map within the bounded settings of Width and Height
m.to_streamlit(width=700, height=500, add_layer_control=True)
#Read Google Sheets

#display DataFrame
df = pd.read_csv('gase_temp.csv')
# Fill NaN values with a specific value, such as 0
df = df.fillna(1)
st.write(df)

#-----------------------------------------
if __name__ == '__main__':
    main()