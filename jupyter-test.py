#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd 

date_list = pd.date_range('2025-01-01', periods=365.25, freq='D')
date_df = pd.DataFrame(date_list, columns=['date'])
hotel_df = pd.read_csv('hotel_index.csv')

merge_df = hotel_df.merge(date_df, how='cross')
merge_df['date'] = pd.to_datetime(merge_df['date'])
merge_df.to_sql('merge_df', con='sqlite:///hotel_data.db', if_exists='replace', index=False)



# In[13]:


s_df = pd.read_sql('select * from staying', con='sqlite:///database.db')
merged = pd.read_sql("select * from merge_df where date < '2025-06-01'", con='sqlite:///hotel_data.db')
s_df['Check In'] = pd.to_datetime(s_df['Check In'])
s_df['Check Out'] = pd.to_datetime(s_df['Check Out'])
merged.date = pd.to_datetime(merged.date)
for i, row in merged.iterrows():
    if row['date'] >= s_df['Check In'].min() and row['date'] < s_df['Check Out'].max():
        merged.at[i, 'stay'] = 1
    else:
        merged.at[i, 'stay'] = 0
merged[merged.stay > 0]

