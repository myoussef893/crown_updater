##################################### DESCRIPTION #########################################
## THE MAIN GOAL OF THIS APPLICATION IS TO GET ALL THE UPDATES FROM THIER CSV, UPDATE, CLEAR AND PREPROCESS IN AN SQL FOR FASTER ANALYSIS. 
## THERE SHOULD BE 3 MAIN PAGES, (UPDATER FORM, DATA VIEWER, DASHBOARD)
## FOR THE TABLES IT SHOULD AVE 3 TABLES, (STAYS, HOTELS INDEX, BOOKING)
## WHAT SHOULD BE VIEWED IS THE FOLLOWING (ADR, OCCUPANCY, PAYMENT TREND, NIGHTS/STAYS, BOOKING WINDOW, ) 

import streamlit as st 
import pandas as pd 
import seaborn as sns 



CON = 'sqlite:///database.db'
query = 'select * from '
status = 'replace'

pd.read_csv('hotel_index.csv').to_sql('hotel_index',con=CON,if_exists='replace')
############################################################# UPLOADER PAGE #############################################################

# UPLOADER PAGE: 
def uploader_reservation(): 
    with st.form(key='uploader_form'): 
        file = st.file_uploader('Uploder')
        submit = st.form_submit_button('Upload')
        if submit:
            hotel_index = pd.read_sql('select * from hotel_index','sqlite:///database.db')
            df = pd.read_csv(file,skiprows=1,encoding='utf-16',index_col=False).to_sql('booking_date',con=CON,if_exists=status)
            df = pd.read_sql(query+'booking_date',con=CON)
            df.drop_duplicates(keep='last')
            df = pd.merge(df,hotel_index[['Property','Company']],how='left').to_sql('booking_date',con=CON,if_exists=status)
            st.success('Sucessfully Uploaded & Updated.')
            st.write(df)

def uploader_stays():
    with st.form(key='uploader_form'): 
        file = st.file_uploader('Uploder')
        submit = st.form_submit_button('Upload')
        if submit:
            hotel_index = pd.read_sql('select * from hotel_index','sqlite:///database.db')
            df = pd.read_csv(file,skiprows=1,encoding='utf-16',index_col=False).to_sql('staying_date',con=CON,if_exists=status)
            df = pd.read_sql(query+'staying_date',con=CON)
            df.drop_duplicates(keep='last')
            df = pd.merge(df,hotel_index[['Property','Company']],how='left').to_sql('staying_date',con=CON,if_exists=status)
            st.success('Sucessfully Uploaded & Updated.')
            st.write(df)
    

def viewer(): 
    df_booking_date = pd.read_sql(query+'booking_date',con=CON)
    filter =st.selectbox('Filter by Hotel',options=df_booking_date['Property'].unique())
    st.write(df_booking_date[df_booking_date['Property'] == filter])

################################################## DATAFRAMES #######################################################
hotel_index =  pd.read_sql('select * from hotel_index',con= 'sqlite:///database.db')
booking_date = pd.read_sql('select * from booking_date',con= 'sqlite:///database.db')
staying_date = pd.read_sql('select * from staying_date',con= 'sqlite:///database.db')   
booking_date['Booking Date and Time'] = pd.to_datetime(booking_date['Booking Date and Time'])
staying_date['Check In'] = pd.to_datetime(staying_date['Check In'])
staying_date['Check Out'] = pd.to_datetime(staying_date['Check Out'])


################################################# DASHBOARD #######################################################
def dashboard():
    b_df = booking_date
    b_df = b_df[['Property','Booking Date and Time']].drop_duplicates(subset=['Property','Booking Date and Time'],keep='first')
    b_df = b_df.sort_values(by=['Property','Booking Date and Time'])
    s_df = staying_date[['Property','Check In', 'Check Out']]
    def count_occurrences(row):
    # Filter s_df where property matches
        mask = (s_df['Property'] == row['Property']) & \
            (s_df['Check In'] <= row['Booking Date and Time']) & \
            (s_df['Check Out'] > row['Booking Date and Time'])
        
        return mask.sum() 
    # Apply function to each row
    b_df['Stays Count'] = b_df.apply(count_occurrences, axis=1)

    # Display result
    final_df = b_df

    final_df = pd.merge(final_df,hotel_index[['Property','Total Rooms']],how='left')
    final_df['Occ_rate'] = final_df['Stays Count']/final_df['Total Rooms']
    final_df['Occ_rate'] = pd.to_numeric(final_df['Occ_rate'])
    final_df['Occ_rate'] = final_df['Occ_rate'].apply(lambda x: f"{x * 100:.2f}%")

    final_df = pd.merge(final_df,hotel_index[['Property','Company']],how='left')

    hotel_filter = st.selectbox('Select Hotel',options=final_df['Property'].unique())
    filtered_fdf = final_df[final_df['Property'] == hotel_filter].sort_values(by='Booking Date and Time')
    st.line_chart(filtered_fdf,x='Booking Date and Time',y='Occ_rate',use_container_width=True)




def new_viewer():
    col1, col2 = st.columns(2)
    row1, row2, row3, row4 = st.columns(4)

    with col1:
        fltr_hotel = st.multiselect('Select Hotel',options=hotel_index['Property'].unique())
    with col2:
        fltr_company = st.multiselect('Select Company',options=hotel_index['Company'].unique())


    if fltr_company or fltr_company:
        st.write(hotel_index.loc[[fltr_company],[fltr_hotel]])
    else:
        st.write(hotel_index)

# VIEWER FUNCTION: 
st.navigation(
    [
        uploader_reservation,
        uploader_stays,
        viewer,
        dashboard,
        new_viewer
    ]
).run()