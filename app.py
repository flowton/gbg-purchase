import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.markdown("""
# Gothenburg City Purchasing :moneybag:

** Based on open data from the city of Gothenburg, this is the total purchase broken down in a monthly view. **

> *Open data is information that is available for anyone to use, reuse and share, so that others can develop it and create benefits for more people. ~ Gothenburg City Website*

:books: [Gothenburg Open Data Archive](https://goteborg.se/wps/portal/start/kommun-o-politik/kommunfakta/stadens-digitala-service/oppna-data?uri=gbglnk%3A2015816171319546 'Link to Gothenburg cities website')

---

""")

### Data imports
df_time = pd.read_csv('df_yy_mm.csv')
df_supp_yy = pd.read_csv('df_supp_yy.csv')



### Selection Slicers

st.sidebar.markdown("""
                    **Select a Mode**
                    """)

modes = st.sidebar.selectbox(
    'Modes: ',
    ('','time', 'trend', 'account', 'financial', 'supplier search')
)

st.sidebar.markdown("""
                    **Possibile settings in this mode**
                    """)


def time_mode():
    st.markdown("""
    # :calendar: Time Analysis
    
    > Exploration starts from a time perspective. Having data for 48 months provides the opportunity to analyze this both from a seasonality and a general trend angle.
    """)
    checkbox_raw_data = st.sidebar.checkbox(
        'Show Raw Data'
    )

    checkbox_ma = st.sidebar.checkbox(
        'Show Moving Average (months)'

    )

    slider_ma = st.sidebar.slider(
        'Moving Average', 1, 12
    )

    mselect_year = st.sidebar.multiselect(
        'Year(s)',
        (2016, 2017, 2018, 2019),
        default=(2016, 2017, 2018, 2019))

    mselect_month = st.sidebar.multiselect(
        'Month(s)',
        (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
        default=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
    )
    df_time_filter = df_time[(df_time['year'].isin(mselect_year)) & (df_time['month'].isin(mselect_month))].reset_index(
        drop=True)

    if checkbox_raw_data:
       st.write(df_time_filter)

    ### Rolling Means
    rolling_windows = df_time_filter['sum'].rolling(slider_ma)
    rolling_mean = rolling_windows.mean().fillna(df_time_filter['sum'][slider_ma])
    # print(rolling_mean)


    values = np.array(df_time_filter['sum'])
    idx = np.array(df_time_filter['period'])

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

    ### Plotting
    plt.figure(figsize=(20, 10))
    if checkbox_ma:
        plt.plot(rolling_mean, alpha=0.8, label='Moving Average')
    plt.bar(idx, values, color=color_list, alpha=0.6)
    plt.xlabel('Period', fontsize='30', fontweight = 'bold')
    plt.yticks(fontsize = 30)
    plt.xticks(rotation=90, fontsize = 20)
    plt.ylabel('Amount in BSEK', fontsize='30', fontweight = 'bold')
    plt.title('Total Purchase of Gothenburg City', fontsize='40', fontweight='bold')
    plt.legend(bbox_to_anchor=(-0.25, 0.5, 0.5, 0.5), prop={'size': 20})

    st.pyplot(plt.gcf())



def trend_mode():

    st.markdown("""
    # :chart_with_upwards_trend: Trend analysis""")

    st.markdown('''
    ### Finding suppliers on upwards or downwards trends.
    
    > Looking at the trend, interesting suppliers could be filtered out as having an steady upwards (receiving more purchases) or downwards trend.
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

    df_supp_agg = df_supp_yy.groupby(['leverantör'])['belopp'].agg(
        [increasing, decreasing, 'mean', total_diff, changes_wrt_mean]).reset_index()

    mean_threshold_rise = st.slider('Total purchases in KSEK', 10, 10000)
    mean_threshold = mean_threshold_rise * 1000

    df_output = df_supp_agg[
        (df_supp_agg['mean'] > mean_threshold) & (df_supp_agg['changes_wrt_mean'] > 200)].sort_values(
        'changes_wrt_mean', ascending=True).tail(20)
    plt.barh(df_output['leverantör'], df_output['changes_wrt_mean'], color='green')
    plt.ylabel('Leverantörer')
    plt.xlabel('Changes in % \n (compared with the mean purchase)')
    plt.title('Suppliers on trend with more purchases')

    st.pyplot(plt.gcf())

    plt.clf()

    mean_threshold_fall = st.slider('Total purchases in KSEK ', 10, 10000)
    mean_threshold = mean_threshold_fall * 1000


    df_output = df_supp_agg[
        (df_supp_agg['mean'] > mean_threshold) & (df_supp_agg['changes_wrt_mean'] < -200)].sort_values(
        'changes_wrt_mean', ascending=False).tail(20)
    plt.barh(df_output['leverantör'], df_output['changes_wrt_mean'], color='red')
    plt.ylabel('Leverantörer')
    plt.xlabel('Changes in % \n (compared with the mean purchase)')
    plt.title('Suppliers on trend with less purchases')

    st.pyplot(plt.gcf())





def account_mode():
    st.markdown("""
    # :clipboard: Account Analysis 
                
    > Analyze the account amounts to better understand on what cost categories the city of Gothenburg spends its money on. 
                """)
    df_account = pd.read_csv('df_account.csv')

    st.dataframe(df_account)

def financial_mode():
    st.markdown("""
                # :heavy_dollar_sign: Financials
                
                > Exploration with financial data. Suppliers are having different levels of dependency on the purchases of the City of Gothenburg to survive. To find out, the open data can be augmented with the suppliers financial data to compare invoicing with their total turnover .
                
                ### Accounting Year 2019
                """)
    df_financial = pd.read_csv('df_financial_filtered.csv')
    supplier_list = pd.read_csv('df_supplier_list.csv')

    st.dataframe(df_financial)
    slider_finance_threshold = st.sidebar.slider('Minimum size of company (turnover) in MSEK',0, 100 )
    turnover_threshold = slider_finance_threshold * 1000000


    # Filter out data for only 2019 and having financial turnover > 0 and proporton of turnover <1.
    # Get top 10 companies
    df_plot = df_financial[df_financial['financial_turnover'] > turnover_threshold].sort_values('proportion_of_turnover',ascending=False).head(10)
    # Based on the organization number, fetch the correct supplier name
    # Note that because of mergers and other reasons, there can be a 1-to-many connection between org_number and supplier name

    label_names = []
    a = 0
    for org_number in df_plot['organisationsnummer']:
        list_of_names = supplier_list['leverantör'][supplier_list['organisationsnummer'] == str(org_number)]
        name_variants = ""
        for item in list_of_names:
            name_variants = name_variants + ' \n' + item
        label_names.append(name_variants)


    # Replace organization number with actual name for the suppliers
    plt.figure(figsize=(10,10))
    plt.barh(label_names, df_plot['proportion_of_turnover'], color='red')
    plt.ylabel('Suppliers', fontsize=16)
    plt.xlabel('Percentage of total revenue', fontsize=16)
    plt.title('Suppliers dependency on Gothenburg City \n (year 2019)', fontsize=20)

    st.pyplot(plt.gcf())

def supplier_search_mode():
    st.markdown('''
    # :mag: Supplier Search
    
    > Free text search to find specific suppliers
    ''')

    user_input = st.text_input('Search for specific supplier here ', 'chalmers')
    st.write('Data is filtered on: \'' + user_input + '\'')

    if user_input == '':
        user_input = ' '


    df_supplier_filter = df_supp_yy[df_supp_yy['leverantör'].str.lower().str.match('.*' + user_input.lower() + '*')]
    st.dataframe(
        df_supplier_filter
    )

    st.bar_chart(df_supplier_filter.groupby(['leverantör'])['belopp'].sum().sort_values(axis = 0))

def mode_selector(current_mode):
    if current_mode == 'time':
        time_mode()
    elif current_mode == 'trend':
        trend_mode()
    elif current_mode == 'account':
        account_mode()
    elif current_mode == 'financial':
        financial_mode()
    elif current_mode == 'supplier search':
        supplier_search_mode()
    else:
        st.markdown("""
                    # :arrow_upper_left: Select a Mode in the Sidebar
                    """)

mode_selector(modes)







