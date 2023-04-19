import requests
import pandas as pd
import matplotlib.pyplot as plt
import os


# Data set is of format:
# date_time	station_id	component_id	value
# 1/9/2023 0:00	1	1	19.87760843
try:
    df = pd.read_csv('air_data.csv')
except FileNotFoundError:
    print("Downloading data set...")
    r = requests.get(
        "http://data.sepa.gov.rs/datastore/dump/a8f71ec0-0a68-4d4f-8f37-ceabdcb98569?bom=True", stream=True)
    total_length = int(r.headers.get('content-length'))
    with open('air_data.csv', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    df = pd.read_csv('air_data.csv')
    df.to_csv('air_data.csv', index=False)

id_k_name_dict = {}
id_k_name_stations = {}

try:
    df_components = pd.read_csv('component.csv', sep=';', index_col='id')
    id_k_name_dict = df_components['k_name'].to_dict()
except FileNotFoundError:
    print("Downloading components...")
    r = requests.get(
        "http://data.sepa.gov.rs/datastore/dump/7fa4ab3f-423a-4016-8508-37164b49c087?bom=True", stream=True)
    total_length = int(r.headers.get('content-length'))
    with open('component.csv', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    df_components = pd.read_csv('component.csv', sep=';', index_col='id')

    id_k_name_dict = df_components['k_name'].to_dict()

try:
    df_stations = pd.read_csv('stations.csv', sep=',', index_col='id')
    id_k_name_stations = df_stations['k_name'].to_dict()
except FileNotFoundError:
    print("Downloading stations...")
    r = requests.get(
        "http://data.sepa.gov.rs/datastore/dump/dd7f4e4b-2375-4657-bb91-d541a2759891?bom=True", stream=True)
    total_length = int(r.headers.get('content-length'))
    with open('stations.csv', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    df_stations = pd.read_csv('stations.csv', sep=',', index_col='id')
    id_k_name_stations = df_stations['k_name'].to_dict()


# Convert values to floats
df['value'] = df['value'].astype(float)

# Remove values that are "nan"
df = df[df['value'] != -999]

# Add component name to the data set
df['component_name'] = df['component_id'].map(id_k_name_dict)

# Add station name to the data set
df['station_name'] = df['station_id'].map(id_k_name_stations)

# Convert the date_time column to datetime
df['date_time'] = pd.to_datetime(df['date_time'])

if not os.path.exists("graphs"):
    os.makedirs("graphs")

for station_name in df['station_name'].unique():
    if not os.path.exists(f"graphs/{station_name}"):
        os.makedirs(f"graphs/{station_name}")

# iterate over unique station and component name combinations
for station_name, component_name in df.groupby(['station_name', 'component_name']):
    # compute mean value and skip non-float means
    val = component_name['value'].mean()
    if not isinstance(val, float):
        continue

    # plot and save figure
    plt.plot(component_name['date_time'], component_name['value'])
    plt.title(f"{station_name[0]} - {station_name[1]}")
    plt.xlabel("Datum")
    plt.ylabel("Vrednost")
    component_name_str = str(station_name[1]).replace(
        "<", "vise od").replace(">", "manje on")
    plt.savefig(f"graphs/{station_name[0]}/{component_name_str}.png")
    plt.close()
