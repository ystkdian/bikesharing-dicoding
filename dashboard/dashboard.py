import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import requests

sns.set(style='dark')

# Membuat helper function yang menangani monthly_count_df
def create_monthly_count_df(df):
    monthly_count_df = df.resample(rule='ME', on='date').agg({
        "total": "sum"
    })
    
    monthly_count_df.index = monthly_count_df.index.strftime('%b \'%y')
    monthly_count_df = monthly_count_df.reset_index()
    
    return monthly_count_df

# Membuat helper function yang menangani daily_count_df
def create_daily_count_df(df):
    daily_count_df = df.groupby("day", observed=False).total.sum().reset_index()

    daily_count_df['day'] = pd.Categorical(daily_count_df['day'], ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])

    return daily_count_df

# Membuat helper function yang menangani hourly_count_df
def create_hourly_count_df(df):
    hourly_count_df = df.groupby('hour').total.sum().sort_values(ascending=False).reset_index()

    hourly_count_df.hour.replace((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23),
                        ('12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM',
                        '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM',
                        '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM',
                        '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM'), inplace=True)

    return hourly_count_df

# Membuat helper function yang menangani season_count_df
def create_season_count_df(df):
    season_count_df = df.groupby("season", observed=False).total.mean().reset_index()

    return season_count_df

# Membuat helper function yang menangani user_type_df
def create_user_type_df(df):
    user_type_df = day_df.groupby("workingday", observed=True).agg({
    'registered': 'mean', 
    'casual': 'mean'
    }).reset_index()

    return user_type_df

# Membuat helper function yang menangani time_cluster_df
def create_time_cluster_count_df(df):
    df['time_cluster'] = pd.cut(df['hour'], [-1, 3, 6, 12, 17, 20, 23], 
                                 labels = ['Late Night', 'Early Morning', 'Morning', 'Afternoon', 'Evening', 'Night'])

    time_cluster_count_df = df.groupby("time_cluster", observed=True).agg({
        'registered': 'mean', 
        'casual': 'mean'
    }).reset_index()

    return time_cluster_count_df

# Memuat file .csv ke dalam dataframe
day_df = pd.read_csv(r"day.csv")
hour_df = pd.read_csv(r"hour.csv")

datetime_columns = ["date"]
day_df.sort_values(by="date", inplace=True)
day_df.reset_index(inplace=True)
 
for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])
    hour_df[column] = pd.to_datetime(hour_df[column])

# Membuat komponen filter
day_min_date = day_df["date"].min()
day_max_date = day_df["date"].max()

hour_min_date = hour_df["date"].min()
hour_max_date = hour_df["date"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    # image ID
    file_id = "1_DQMKtkxUIVzhi0iu3-8uQJvp9A3UlgZ"

    # URL
    url = f"https://drive.google.com/uc?export=view&id={file_id}"

    response = requests.get(url)
    st.image(response.content)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=day_min_date,
        max_value=day_max_date,
        value=[day_min_date, day_max_date]
    )

main_day_df = day_df[(day_df["date"] >= str(start_date)) & 
                (day_df["date"] <= str(end_date))]

main_hour_df = hour_df[(hour_df["date"] >= str(start_date)) & 
                (hour_df["date"] <= str(end_date))]

# Membuat dataframe
monthly_count_df = create_monthly_count_df(main_day_df)
daily_count_df = create_daily_count_df(main_day_df)
hourly_count_df = create_hourly_count_df(main_hour_df)
season_count_df = create_season_count_df(main_day_df)
user_type_df = create_user_type_df(main_day_df)
time_cluster_count_df = create_time_cluster_count_df(main_hour_df)

# Melengkapi dashboard dengan visualisasi data
st.header('BikeSharing Dashboard :bike:')

# Membuat visualisasi penyewaan harian
col1, col2, col3 = st.columns(3)
 
with col1:
    total_bike_rented = main_day_df.total.sum()
    st.metric("Total Bike Rented", value=total_bike_rented)
 
with col2:
    total_casual = main_day_df.casual.sum()
    st.metric("Total Casual User", value=total_casual)

with col3:
    total_registered = main_day_df.registered.sum()
    st.metric("Total Registered User", value=total_registered)

# Membuat visualisasi tren penyewaan
st.subheader('Performance by Month')

fig, ax = plt.subplots(figsize=(40, 15))


ax.plot(
    monthly_count_df['date'], 
    monthly_count_df['total'], 
    linewidth=2, 
    marker='o')

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)

st.pyplot(fig)

# Membuat visualisasi jumlah pengguna berdasarkan hari
st.subheader('Total Rental by Day')

fig, ax = plt.subplots(figsize=(10, 5))

colors = ["#CFCFCF", "#CFCFCF", "#CFCFCF", "#CFCFCF", "#CFCFCF", "#006BA4", "#CFCFCF"]

sns.barplot(
    y="total", 
    x="day",
    data=daily_count_df.sort_values(by="day"),
    palette=colors
)

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

st.pyplot(fig)

# Membuat visualisasi penggunaan berdasarkan jam
st.subheader('Performance by Hour')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 7))

colors = ["#006BA4", "#CFCFCF", "#CFCFCF", "#CFCFCF", "#CFCFCF"]

sns.barplot(
    x="hour", 
    y="total", 
    data=hourly_count_df.head(5), 
    palette=["#006BA4", "#CFCFCF", "#CFCFCF", "#CFCFCF", "#CFCFCF"],
    ax=ax[0])

ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Hour with The Most Rentals", loc="center", fontsize=20)
ax[0].tick_params(axis ='x', labelsize=18)
ax[0].tick_params(axis ='y', labelsize=18)
 
sns.barplot(
    x="hour", 
    y="total", 
    data=hourly_count_df.sort_values(by="total", ascending=True).head(5), 
    palette=["#FF800E", "#CFCFCF", "#CFCFCF", "#CFCFCF", "#CFCFCF"], 
    ax=ax[1])

ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Hour with The Least Rentals", loc="center", fontsize=20)
ax[1].tick_params(axis='x', labelsize=18)
ax[1].tick_params(axis='y', labelsize=18)

st.pyplot(fig)

# Membuat visualisasi penggunaan berdasarkan musim
st.subheader('Seasonly Performance')

fig, ax = plt.subplots(figsize=(10, 5))

colors = ["#006BA4", "#CFCFCF", "#CFCFCF", "#CFCFCF"]

sns.barplot(
    y="total", 
    x="season",
    data=season_count_df,
    palette=colors
)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# Membuat visualisasi perbedaan penggunaan casual dan registered user
st.subheader('Casual vs Registered User')

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(7, 8))

    sns.barplot(
        y="registered", 
        x="workingday",
        data=user_type_df,
        color='#006BA4',
        label="Registered"
    )

    sns.barplot(
        y="casual", 
        x="workingday",
        data=user_type_df,
        color='#FF800E',
        label='Casual'
    )

    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("User Preferences by Day Type", fontsize=15)
    ax.legend()
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(7, 8))

    sns.barplot(
        y="registered",
        x="time_cluster",
        data=time_cluster_count_df,
        color='#006BA4',
        label='Registered'
    )

    sns.barplot(
        y="casual", 
        x="time_cluster",
        data=time_cluster_count_df,
        color='#FF800E',
        label='Casual'
    )

    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("User Preferences by Time Cluster", fontsize=15)
    ax.legend()
    st.pyplot(fig)

st.caption('Yestika Dian Wulandari, 2025')




