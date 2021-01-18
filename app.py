import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
st.markdown("""
# Gothenburg City Purchasing :moneybag:

** Based on open data from Gothenburg City, this is the total purchase broken down in a monthly view. **

> *Open data is information that is available for anyone to use, reuse and share, so that others can develop it and create benefits for more people. ~ Gothenburg City Website*

:books: [Gothenburg Open Data Archive](https://goteborg.se/wps/portal/start/kommun-o-politik/kommunfakta/stadens-digitala-service/oppna-data?uri=gbglnk%3A2015816171319546 'Link to Gothenburg cities website')

""")

### Selection Slicers

checkbox_raw_data = st.sidebar.checkbox(
    'Show Raw Data'
)

checkbox_ma = st.sidebar.checkbox(
    'Show Moving Average'

)
if checkbox_ma:
    slider_ma = st.sidebar.slider(
        'Moving Average', 1,12
    )
else:
     slider_ma = 1


mselect_year = st.sidebar.multiselect(
    'Year',
    (2016,2017,2018,2019),
    default = (2016,2017,2018,2019)
)

mselect_month = st.sidebar.multiselect(
    'Month',
    (1,2,3,4,5,6,7,8,9,10,11,12),
    default= (1,2,3,4,5,6,7,8,9,10,11,12)
)

# Data processing

df_time = pd.read_csv('df_yy_mm.csv')
df_time = df_time[(df_time['year'].isin(mselect_year)) & (df_time['month'].isin(mselect_month))].reset_index(drop = True)
values = np.array(df_time['sum'])
idx = np.array(df_time['period'])

### Color on bar charts

color_list = []

for period in idx:
    year = period[0:4]
    if year == '2016':
        color_list.append('gainsboro')
    elif year == '2017':
        color_list.append('silver')
    elif year == '2018':
        color_list.append('grey')
    else:
        color_list.append('dimgray')

### Rolling Means
rolling_windows = df_time['sum'].rolling(slider_ma)
rolling_mean = rolling_windows.mean().fillna(df_time['sum'][slider_ma])
#print(rolling_mean)


# Display data

if checkbox_raw_data:
    st.write(df_time)

### Plotting
plt.figure(figsize=(20,10))
if checkbox_ma:
    plt.plot(rolling_mean, alpha = 0.8, label = 'Moving Average')
plt.bar(idx,values, color = color_list, alpha = 0.6)
plt.xlabel('Period', fontsize = '30')
plt.xticks(rotation = 90)
plt.ylabel('Amount in BSEK', fontsize = '30')
plt.title('Total Purchase of Gothenburg City', fontsize = '40', fontweight = 'bold')
plt.legend(bbox_to_anchor=(-0.25,0.5,0.5,0.5), prop = {'size': 20})

st.pyplot(plt.gcf())
