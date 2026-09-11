import pandas as pd
import numpy as np
import streamlit as st
from utils.helper import (
    plot_bar_by_season,
    plot_trend_line,
    plot_percentage_change,
    plot_percentage_change_per_year,
    plot_annual_heatmap,
    convert_df_year_to_season_year,
)


all_df = pd.read_csv('all_data.csv')
all_df['date'] = pd.to_datetime(all_df['date'], errors='coerce')
main_df = convert_df_year_to_season_year(all_df)
pollutant_params = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
support_params = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']


st.header('Analisis Data Air Quality')

@st.fragment
def trend_pollutant_per_season():
    st.subheader('Distribusi Parameter Polutan per Musim')
    min_date = all_df["date"].min()
    max_date = all_df["date"].max()
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
        key='trend_pollutant_per_season'
    )
    main_df = all_df[(all_df["date"] >= str(start_date)) & 
                    (all_df["date"] <= str(end_date))]
    
    fig = plot_bar_by_season(main_df, pollutant_params)

    st.pyplot(fig)


@st.fragment
def trend_support_parameter():
    st.subheader('Tren Parameter Meteorologi Berdasarkan Polutan')

    support_param_df = pd.DataFrame(
        np.array([
            support_params,
            ['Temperatur', 'Tekanan Udara', 'Titik Embun', 'Curah Hujan', 'Kecepatan Angin'],
            [0.75, 0.75, 0.75, 0.95, 0.5],
            [50, 30, 30, 200, 35],
            [100, 100, 100, 200, 100],
        ]).T,
        columns=['param', 'label', 'quantile', 'n_bins', 'min_points_per_bin']
    )

    support_param_df = support_param_df.astype({
        'param': 'str',
        'label': 'str',
        'quantile': 'float',
        'n_bins': 'int32',
        'min_points_per_bin': 'int32',
    })

    min_date = all_df["date"].min()
    max_date = all_df["date"].max()

    support_param_select_box = st.selectbox(
        'Pilih parameter meteorologi: ', 
        support_param_df['label']
    )
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
        key='trend_support_parameter'
    )
    main_df = all_df[
        (all_df["date"] >= str(start_date)) & 
        (all_df["date"] <= str(end_date))
    ]
    
    support_param_idx = support_param_df.index[
        support_param_df['label'] == support_param_select_box
    ][0]
    
    fig = plot_trend_line(
        main_df,
        x_param=support_param_df.at[support_param_idx, 'param'],
        y_param_list=pollutant_params,
        x_label=support_param_df.at[support_param_idx, 'label'],
        quantile=support_param_df.at[support_param_idx, 'quantile'],
        n_bins=support_param_df.at[support_param_idx, 'n_bins'],
        min_points_per_bin=support_param_df.at[support_param_idx, 'min_points_per_bin'],
    )

    st.pyplot(fig)


@st.fragment
def trend_pollutant_by_compare_year():
    st.subheader('Perbandingan Perubahan Konsentrasi Polutan Antar Tahun')
    st.caption('Disclaimer: Winter bulan Januari dan Februari akan dianggap sebagai data tahun sebelumnya, e.g. Winter Januari 2017, season_year = 2016')

    col1, col2 = st.columns(2)
    year_opts = main_df['season_year'].unique()
    year_opts.sort()
    year1_idx, = np.where(year_opts == year_opts[0])
    year2_idx, = np.where(year_opts == year_opts[-1])

    with col1:
        year1 = st.selectbox(
            'Pilih tahun ke-1: ', 
            year_opts,
            key='trend_pollutant_by_compare_year1',
            index=int(year1_idx[0])
        )
    
    with col2:
        year2 = st.selectbox(
            'Pilih tahun ke-2: ', 
            year_opts,
            key='trend_pollutant_by_compare_year2',
            index=int(year2_idx[0])
        )

    years = [year1, year2]
    fig = plot_percentage_change(main_df, pollutant_params, years)
    st.pyplot(fig)


@st.fragment
def trend_pollutant_percentage_every_year():
    st.subheader('Perubahan Persentase Polutan Tiap Tahun')
    year_opts = main_df['season_year'].unique()
    col1, col2 = st.columns(2)

    with col1:
        selected_pollutant = st.selectbox(
            'Pilih polutan: ',
            pollutant_params,
            key='trend_pollutant_percentage_every_year_pollutant'
        )

    with col2:
        year = st.selectbox(
            'Pilih tahun pembanding: ', 
            year_opts,
            key='trend_pollutant_percentage_every_year1',
        )

    fig = plot_percentage_change_per_year(
        main_df, selected_pollutant, year)
    
    st.pyplot(fig)


@st.fragment
def trend_pollutant_concentration_every_year():
    st.subheader('Perubahan Konsentrasi Polutan Tiap Tahun')

    selected_pollutant = st.selectbox(
        'Pilih polutan: ',
        pollutant_params,
        key='trend_pollutant_concentration_every_year_pollutant'
    )

    fig = plot_annual_heatmap(
        main_df, selected_pollutant,
        is_heatmap_square=selected_pollutant != 'CO')
    
    st.pyplot(fig)


st.divider()
# trend_pollutant_per_season()
st.divider()
# trend_support_parameter()
st.divider()
# trend_pollutant_by_compare_year()
st.divider()
trend_pollutant_percentage_every_year()
st.divider()
trend_pollutant_concentration_every_year()

