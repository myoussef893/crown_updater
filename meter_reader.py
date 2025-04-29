import streamlit as st 
import pandas as pd 
from datetime import datetime as date
from time import sleep as wait 

@st.cache_data
def get_hotels(): 
    return pd.read_csv('hotel_index.csv',index_col=False)
hotels = list(get_hotels()['Property'])






with st.sidebar: 
    from_date = st.date_input('From',value='2025-01-01')
    to_date = st.date_input(label='To ',value='2025-12-31')
    hotel = st.selectbox(label='Select Hotel',options=hotels)


with st.form(key='uploader'): 
    photo = st.camera_input('Take a picture')
    meter_type = st.selectbox('Meter Type',['Gas','Electricity'])
    position = st.selectbox('Select Meter Position',['Meter A','Meter B','Meter C'])
    reading = st.number_input('Put the meter reading',min_value=1)
    submit = st.form_submit_button('Submit')

    if submit: 
        # with open(photo,'rb') as image: 
        #     encoded_photo = base64.encode(image.read())
        try: 
            df= pd.DataFrame(
                {
                    'Photo': [photo.getvalue()],
                    'hotel': [hotel],
                    'Reading_date':[date.now().today().strftime("%d/%m/%Y, %H:%M")],
                    'Type': [meter_type],
                    'Reading': [reading],
                    'Position': [position]
                }
            ).to_sql('meter_readings',con='sqlite:///db.db',if_exists='append',index=False)
            st.success('✅ Entry Successfully Added!')
            wait(1.5)

        except Exception as e: 
            st.warning(f'Error: {e}')
    
try: 
    df = pd.read_sql('select * from meter_readings',con='sqlite:///db.db')
    st.write(df)
    
except Exception as e: 
    st.write('Readings are empty')


