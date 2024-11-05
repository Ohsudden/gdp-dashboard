from dotenv import load_dotenv
from datetime import timedelta, datetime
import streamlit as st
import pandas as pd
import math
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, db
import os
import json
import requests



load_dotenv()


# Initialize Firebase
if not firebase_admin._apps:
    #cred = credentials.Certificate("vyshnevetskyi-data-engineering-firebase-adminsdk-836jz-b41fb4f91d.json")
    cred_dict = json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT_CREDENTIAL'])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://vyshnevetskyi-data-engineering-default-rtdb.europe-west1.firebasedatabase.app/'
    })


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Metal Prices Dashboard',
    page_icon=':earth_americas:',
)

# Function to fetch metal data from Firebase
@st.cache_data
def get_metal_data_from_firebase():
    ref = db.reference('/')
    metal_data = ref.get()
    
    print("Raw data from Firebase:", metal_data)  # Debug print
    
    if metal_data:
        df_metal = pd.DataFrame(metal_data)
        print("DataFrame shape:", df_metal.shape)  # Debug print
        print("DataFrame columns:", df_metal.columns)  # Debug print
        df_metal['Date'] = pd.to_datetime(df_metal['Date']).dt.date
        return df_metal
    else:
        print("No metal data found in Firebase.")
        return pd.DataFrame()

# Load metal data
metal_df = get_metal_data_from_firebase()
print("Metal DataFrame:")
print(metal_df.head())

# Set the title that appears at the top of the page
st.title(':earth_americas: Metal Prices Dashboard')
st.write("Explore historical data on precious metals prices.")

# Add a date range slider
min_date = metal_df['Date'].min()
max_date = metal_df['Date'].max()

from_date, to_date = st.slider(
    'Select date range:',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Select metals to view
metal_columns = [
    'Gold AM Fix', 'Gold PM Fix', 'Silver Fix', 'Platinum AM Fix', 
    'Platinum PM Fix', 'Palladium AM Fix', 'Palladium PM Fix', 
    'Iridium', 'Ruthenium', 'Rhodium'
]

selected_metals = st.multiselect(
    'Select metals to view:',
    metal_columns,
    default=['Gold AM Fix', 'Gold PM Fix', 'Silver Fix']
)

# Filter data based on selections
filtered_df = metal_df[
    (metal_df['Date'] >= from_date) & (metal_df['Date'] <= to_date)
]

# Ensure selected metals are numeric
filtered_df[selected_metals] = filtered_df[selected_metals].apply(pd.to_numeric, errors='coerce')

# Drop any columns that are entirely NaN
filtered_df = filtered_df.dropna(axis=1, how='all')

# Plotting line chart if there are any valid columns
if not filtered_df[selected_metals].empty:
    st.header('Metal Prices Over Time')
    st.line_chart(filtered_df.set_index('Date')[selected_metals])
else:
    st.warning("No valid data available for the selected metals.")


print("Filtered DataFrame shape:", filtered_df.shape)
print("Filtered DataFrame head:", filtered_df.head())


from_dateA, to_dateB = st.slider(
    'Select date range:',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date],
    key="date_slider"
)
filtered_df = filtered_df[
    (filtered_df['Date'] >= from_dateA) & (filtered_df['Date']<= to_dateB)
]
st.subheader('Filtered Data')
st.dataframe(filtered_df[['Date'] + selected_metals])


