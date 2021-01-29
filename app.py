import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### Selection Slicers

checkbox_raw_data = st.sidebar.checkbox(
    'Show Raw Data'
)

checkbox_ma = st.sidebar.checkbox(
    'Show Moving Average'

)

slider_ma = st.sidebar.slider(
    'Moving Average', 1,12
)

mselect_year = st.sidebar.multiselect(
    'Year',
    (2016,2017,2018,2019),
    default= (2016,2017,2018,2019))

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


st.markdown("""
# Gothenburg City Purchasing :moneybag:

** Based on open data from Gothenburg City, this is the total purchase broken down in a monthly view. **

> *Open data is information that is available for anyone to use, reuse and share, so that others can develop it and create benefits for more people. ~ Gothenburg City Website*

:books: [Gothenburg Open Data Archive](https://goteborg.se/wps/portal/start/kommun-o-politik/kommunfakta/stadens-digitala-service/oppna-data?uri=gbglnk%3A2015816171319546 'Link to Gothenburg cities website')

""")

st.markdown('''
## Supplier Analysis
''')

# Display data

if checkbox_raw_data:
    st.write(df_time)

# ----FIND YOUR SUPPLIER-------
st.markdown('''
### Find your supplier
''')

user_input = st.text_input('Search for specific supplier here', 'test')
st.write('Data is filtered on: \'' + user_input + '\'')

df_supp_yy = pd.read_csv('df_supp_yy.csv')
if user_input == '':
    user_input = ' '

sort = st.selectbox('Sort list based on: ', ('leverantör', 'year', 'belopp'))

st.dataframe(df_supp_yy[df_supp_yy['leverantör'].str.lower().str.match('.*' + user_input.lower() + '*')].sort_values(sort))

# ------RISING AND FALLING SUPPLIER-------
st.markdown('''
### Finding rising and falling suppliers
'''
)

# Defining functions
def increasing(series):
    return all(i < j for i, j in zip(series, series[1:])) & (series.size == 4)

def decreasing(series):
    return all(i > j for i, j in zip(series, series[1:])) & (series.size == 4)

def total_diff(series):
    sub = series.iloc[-1] - series.iloc[0]
    return sub

def changes_wrt_mean(series):
    if (series.size != 4):
        return 0
    changes = series.iloc[-1] - series.iloc[0]
    mean = series.mean()
    return 100 * changes / mean

df_supp_agg = df_supp_yy.groupby(['leverantör'])['belopp'].agg([increasing,decreasing,'mean',total_diff,changes_wrt_mean]).reset_index()

mean_threshold_rise = st.slider('Size of company', 100000, 1000000)

df_output = df_supp_agg[(df_supp_agg['mean'] > mean_threshold_rise) & (df_supp_agg['changes_wrt_mean'] > 200)].sort_values('changes_wrt_mean', ascending=True).tail(20)
plt.barh(df_output['leverantör'], df_output['changes_wrt_mean'], color = 'green')
plt.ylabel('Leverantörer')
plt.xlabel('Changes in % \n (measured in company billings mean value)')
plt.title('Rising stars')

st.pyplot(plt.gcf())

plt.clf()
mean_threshold_fall = st.slider('Size of company ', 100000, 10000000)

df_output = df_supp_agg[(df_supp_agg['mean'] > mean_threshold_fall) & (df_supp_agg['changes_wrt_mean'] < -200)].sort_values('changes_wrt_mean', ascending=False).tail(20)
plt.barh(df_output['leverantör'], df_output['changes_wrt_mean'], color = 'red')
plt.ylabel('Leverantörer')
plt.xlabel('Decreases as % of mean')
plt.title('Loosing (top 10 shown)')

st.pyplot(plt.gcf())







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




st.markdown('''
## Supplier Analysis
''')

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
