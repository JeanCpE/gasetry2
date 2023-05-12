#GASE Egg Hotspot Mapping Prototype App
#-------Dependencies-----------
import streamlit as st 
import pandas as pd

#------WEBPAGE SETTINGS----
page_title = "GASEApp"
page_icon = ":seedling:"
layout = "centered"

#---------------------------
#--------------------------

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
#display DataFrame
df

#-----------------------------------------