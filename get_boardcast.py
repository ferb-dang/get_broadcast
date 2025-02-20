import re
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

#  thông tin tên Trạm CA, số Điểm phát sóng gần nhất muốn tìm 
"""
input : mã số tỉnh - mã số huyện - mã số xã - tên đơn vị hành chính - số điểm phát sóng gần nhất ( int : 55)
output : tọa độ các điểm 
"""
def lat_lon_convert(lat_lon):
    def dms_to_dd(degrees, minutes, second_direction):
        match = re.match(r"([0-9]+)([a-z]+)", second_direction, re.I).groups()
        seconds = int(match[0])
        direction = str(match[1])

        dd = int(degrees) + (int(minutes) / 60) + (seconds / 3600)
        if direction in ['S', 'W']:
            dd *= -1  # South and West are negative
        return dd
    
    lat = lat_lon.split(",")[0].strip().split()
    lon = lat_lon.split(",")[1].strip().split()
    
    
    lat_dd = dms_to_dd(lat[0], lat[1], lat[2])
    lon_dd = dms_to_dd(lon[0], lon[1], lon[2])

    return lat_dd, lon_dd

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_closest(lat, lon, locations):
    # Compute distances
    distances = {location: haversine(lat, lon, location[0], location[1]) for location in locations}

    # Find 5 closest points
    closest_points = sorted(distances.items(), key=lambda item: item[1])[:5]
    return closest_points


# input
dau_vao = "Phúc Xá - 50"

administrative_unit_name = dau_vao.rsplit(" - ", 1)[0]
number_of_boardcast_point = dau_vao.rsplit(" - ", 1)[1]

tram_ca = pd.read_excel("C:\Workspace\get_broadcast\E124-2009 (31-12)2-MSDVHCVN.xls", sheet_name="Xa", usecols="D,G")
broadcast_location = pd.read_excel("C:\Workspace\get_broadcast\hanoi.xlsx", usecols="B, C")

list_broadcast_locations = []
for index, rows in broadcast_location.iterrows():
    # Create list for the current row
    my_list =(rows.Lat.item(), rows.Lon.item())
    
    # append the list to the final list
    list_broadcast_locations.append(my_list)

# Validate input
tram_ca = tram_ca[tram_ca["Tên đơn vị hành chính"].str.contains(administrative_unit_name,regex=True)]

lat_dd, lon_dd = lat_lon_convert(tram_ca["Toạ độ điểm trung tâm (Vĩ độ, Kinh độ)"].iloc[0])

close = get_closest(lat_dd, lon_dd, list_broadcast_locations)

close
