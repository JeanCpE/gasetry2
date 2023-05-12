#GASE Egg Hotspot Mapping Prototype App
#-------Dependencies-----------
import streamlit as st
from streamlit.web.cli import main 
import pandas as pd
import leafmap.foliumap as leafmap

#------WEBPAGE SETTINGS----
page_title = "GASEApp"
page_icon = ":seedling:"
layout = "centered"

#---------------------------

st.set_page_config(page_title=page_title,page_icon=page_icon,layout=layout)
st.title(page_title + " " + page_icon)


#----INPUT & SAVE FORM------
if st.button('UPLOAD'):
    st.write('UPLOADED')
else:
    st.write('UPLOAD IMAGE')

#-+++++++++++++++++++++++++++++++++++++++
#----------------------------------------
# Read in data from the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

#------------------------------------------
#load main dataset
df = load_data(st.secrets["public_gsheets_url"])
#drop the Number customized column
df = df.drop('No', axis=1)

#Open Leafmap with Google Map Layer
# with st.echo():   
import streamlit as st
import leafmap.foliumap as leafmap
    
m = leafmap.Map(height="1020px", width="720px",center=[12.3, 122], zoom=6.5)
colors = ['blue','red']
vmin = 1
vmax = 100
m.add_colorbar(colors=colors, vmin=vmin, vmax=vmax)

#added layer
m.add_tile_layer(
    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    name="Google Satellite",
    attribution="Google",
    )
m.to_streamlit() 
#Add the heatmap
with st.echo():
    import leafmap.foliumap as leafmap
    df = load_data(st.secrets["public_gsheets_url"])
    gase_dataset = df
    
    m.add_heatmap(
        gase_dataset,
        latitude="Latitude",
        longitude='Longitude',
        value="Altitude",
        name="Heat map",
        radius=12,
    )


# "## Change basemaps"
# with st.echo():
# m = leafmap.Map()
# m.add_basemap("Esri.NatGeoWorldMap")
# m.to_streamlit()


    # m.add_title("Golden Apple Snail Egg Heat Map", font_size="20px", align="center")
    # m.to_streamlit(width=700, height=500, add_layer_control=True)



#display DataFrame
df

#-----------------------------------------
