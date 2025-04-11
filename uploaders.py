import streamlit as st
import pandas as pd
from time import sleep as wait
import seaborn as sns 
import matplotlib.pyplot as plt
if_exists = 'append'

st.set_page_config(layout='wide')

# THIS IS THE UPLOADING PART, HERE THE USER WILL UPLOAD THE CSV FILE AND SAVE IT IN THE DATABASE IN THE SELECTED TABLE
# THE TABLES ARE: 'booking' AND 'staying', THEY ARE THE SAME AS IN THE DATABASE, FOR BOOKING IT'S THE CSV REPORT ACCORDING TO THE BOOKING_DATE, AND STAYING IS ACCORDING TO THE STAYING DATE. 
# THE USER CAN SELECT THE TABLE THEY WANT TO UPLOAD THE CSV FILE TO, AND THE FILE WILL BE UPLOADED TO THAT TABLE.
# THE CSV FILES ARE IN UTF-16 ENCODING, AND THE FIRST ROW IS SKIPPED BECAUSE IT CONTAINS THE HEADERS.
def uploader(): 

    with st.form(key='key'):
        base_selector = st.selectbox('Select base:', ['booking', 'staying'])
        file = st.file_uploader("Upload a file")
        submit = st.form_submit_button("Submit")

        if submit: 
            df_file = pd.read_csv(file, encoding='utf-16', skiprows=1 ,index_col=False)
            df_file.to_sql(base_selector, con = 'sqlite:///database.db', if_exists=if_exists, index=False)
            pd.read_sql(base_selector, con = 'sqlite:///database.db').drop_duplicates(keep='last', inplace=True)
            success_msg = st.success("File uploaded successfully!🎉")
            wait(2)
            success_msg.empty()


# LOAD THE DATABASE AND PREPARTE THE TABLES: 


date_range = pd.date_range(start='2025-01-01', end='2025-12-31', freq='D').to_frame(name='date')
hotel_index = pd.read_csv('hotel_index.csv')

grand_table = hotel_index.merge(date_range,how='cross').to_sql('grand_table', con = 'sqlite:///database.db', if_exists='replace', index=False)


def dashboard(): 

    staying_date = st.date_input("From", value=pd.to_datetime('2025-01-01'))
    staying_date_df = pd.read_sql(f'select * from staying where "Check Out" < "{staying_date}" and "Booking Status" = "Confirmed"', con = 'sqlite:///database.db') 
    property = st.selectbox('Select company:', options=staying_date_df['Property'].unique())
    gt = pd.read_sql(f'select * from grand_table where "date" < "{staying_date}" and "Property" = "{property}"', con = 'sqlite:///database.db')
    gt['date'] = pd.to_datetime(gt['date']).dt.date

    staying_date_df.drop_duplicates(keep='last', inplace=True)
    staying_date_df['Check In'] = pd.to_datetime(staying_date_df['Check In']).dt.date
    staying_date_df['Check Out'] = pd.to_datetime(staying_date_df['Check Out']).dt.date

    gt['Resv Count'] = 0

    for i, row in gt.iterrows(): 

        stay_count = ((staying_date_df['Check In'] <= row['date']) & 
                    (row['date'] < staying_date_df['Check Out']) & 
                    (staying_date_df['Property'] == row['Property'])).sum()

        gt.at[i, 'Resv Count'] = stay_count
    gt['occupancy'] = gt['Resv Count'] / gt['Total Rooms']*100

    col1, col2, = st.columns(2)

    
    with col1:
        st.write(gt,)
    
    with col2: 
        st.text('Occupancy Rate')
        st.line_chart(gt.set_index('date')['occupancy'], use_container_width=True,color='#FFF8cf40')

st.navigation([
    uploader,
    dashboard
]).run()