import pandas as pd
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
pollutant_params = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']

st.header('Analisis Data Air Quality')

min_date = all_df["date"].min()
max_date = all_df["date"].max()
 
# Mengambil start_date & end_date dari date_input
start_date, end_date = st.date_input(
    label='Rentang Waktu',min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date],
    key='date1'
)
 
main_df = all_df[(all_df["date"] >= str(start_date)) & 
                (all_df["date"] <= str(end_date))]

st.subheader('Distribusi Parameter Polutan per Musim')
fig = plot_bar_by_season(main_df, pollutant_params)
st.pyplot(fig)

st.subheader('Tren Parameter Meteorologi Berdasarkan Polutan')
fig = plot_trend_line(
    main_df,
    x_param="TEMP",
    y_param_list=pollutant_params,
    x_label="Temperatur",
    quantile=0.75,
    n_bins=50,
    min_points_per_bin=100,
)
st.pyplot(fig)

fig = plot_trend_line(
    main_df,
    x_param="WSPM",
    y_param_list=pollutant_params,
    x_label="Kecepatan angin",
    quantile=0.50,
    n_bins=35,
    min_points_per_bin=100,
)
st.pyplot(fig)

fig = plot_trend_line(
    main_df,
    x_param="RAIN",
    y_param_list=pollutant_params,
    x_label="Curah hujan",
    quantile=0.95,
    n_bins=200,
    min_points_per_bin=200,
)
st.pyplot(fig)

fig = plot_trend_line(
    main_df,
    x_param="PRES",
    y_param_list=pollutant_params,
    x_label="Tekanan udara",
    quantile=0.75,
    n_bins=30,
    min_points_per_bin=100,
)
st.pyplot(fig)

st.subheader('Persentase Perubahan Konsentrasi Polutan 2013 vs 2016')
fig = plot_percentage_change(all_df, pollutant_params)
st.pyplot(fig)

st.subheader('Perubahan Persentase dan Konsentrasi Tahunan Polutan')

# all_df2 = convert_df_year_to_season_year(all_df)
# min_date2 = all_df["date"].min()
# max_date2 = "2016-12-31 23:00:00"

# Mengambil start_date & end_date dari date_input
start_date2, end_date2 = st.date_input(
    label='Rentang Waktu',min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date],
    key='date2'
)

st.subheader('Perubahan Persentase dan Konsentrasi Tahunan PM2.5')
pollutant = 'PM2.5'
annual_df, fig = plot_percentage_change_per_year(all_df, pollutant, start_date2.year)
st.pyplot(fig)
fig = plot_annual_heatmap(
    annual_df, pollutant, 
    min_year=start_date2.year, 
    max_year=end_date2.year
)
st.pyplot(fig)

st.subheader('Perubahan Perubahan Persentase dan Konsentrasi Tahunan PM10')
pollutant = 'PM10'
annual_df, fig = plot_percentage_change_per_year(all_df, pollutant, start_date2.year)
st.pyplot(fig)
fig = plot_annual_heatmap(
    annual_df, pollutant, 
    min_year=start_date2.year, 
    max_year=end_date2.year
)
st.pyplot(fig)

st.subheader('Perubahan Perubahan Persentase dan Konsentrasi Tahunan SO2')
pollutant = 'SO2'
annual_df, fig = plot_percentage_change_per_year(all_df, pollutant, start_date2.year)
st.pyplot(fig)
fig = plot_annual_heatmap(
    annual_df, pollutant, 
    min_year=start_date2.year, 
    max_year=end_date2.year
)
st.pyplot(fig)

st.subheader('Perubahan Perubahan Persentase dan Konsentrasi Tahunan NO2')
pollutant = 'NO2'
annual_df, fig = plot_percentage_change_per_year(all_df, pollutant, start_date2.year)
st.pyplot(fig)
fig = plot_annual_heatmap(
    annual_df, pollutant, 
    min_year=start_date2.year, 
    max_year=end_date2.year
)
st.pyplot(fig)

st.subheader('Perubahan Perubahan Persentase dan Konsentrasi Tahunan CO')
pollutant = 'CO'
annual_df, fig = plot_percentage_change_per_year(all_df, pollutant, start_date2.year)
st.pyplot(fig)
fig = plot_annual_heatmap(
    annual_df, pollutant, 
    is_heatmap_square=False, 
    min_year=start_date2.year, 
    max_year=end_date2.year
)
st.pyplot(fig)

st.subheader('Perubahan Perubahan Persentase dan Konsentrasi Tahunan O3')
pollutant = 'O3'
annual_df, fig = plot_percentage_change_per_year(all_df, pollutant, start_date2.year)
st.pyplot(fig)
fig = plot_annual_heatmap(
    annual_df, pollutant, 
    min_year=start_date2.year, 
    max_year=end_date2.year
)
st.pyplot(fig)
