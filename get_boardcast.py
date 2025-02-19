import re
import pandas as pd

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

# input
dau_vao = "Phường Phúc Xá - 50"

administrative_unit_name = dau_vao.rsplit(" - ", 1)[0]
number_of_boardcast_point = dau_vao.rsplit(" - ", 1)[1]

tram_ca = pd.read_excel("D:\workspaces\get_broadcast\E124-2009 (31-12)2-MSDVHCVN.xls", sheet_name="Xa", usecols="D,G")

# Validate input
tram_ca = tram_ca[tram_ca["Tên đơn vị hành chính"].str.contains(administrative_unit_name,regex=True)]

lat_dd, lon_dd = lat_lon_convert(tram_ca["Toạ độ điểm trung tâm (Vĩ độ, Kinh độ)"].iloc[0])


