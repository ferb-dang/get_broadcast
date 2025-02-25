import re
import os
import pandas as pd
from unidecode import unidecode
from tkinter import Tk, Label, Entry, Button, Frame, Scrollbar, Listbox, RIGHT, Y, END
from math import radians, sin, cos, sqrt, atan2

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

def get_closest(lat, lon, locations, number_of_location):
    # Compute distances
    distances = {location: haversine(lat, lon, location[0], location[1]) for location in locations}

    # Find closest points
    closest_points = sorted(distances.items(), key=lambda item: item[1])[:int(number_of_location)]
    return closest_points

def get_file_data(file_dir, file_names, sheet_name=None, usecols=None):
    def read_file(file_dir, file, sheet_name=None, usecols=None):
        filename, file_extension = os.path.splitext(file)
        if file_extension in [".xls", ".xlsx", ".xlsm", ".xlsb", ".odf"]:
            return pd.read_excel(os.path.join(file_dir, file), sheet_name=sheet_name, usecols=usecols)
        if file_extension in [".csv"]:
            return pd.read_csv(os.path.join(file_dir, file), usecols=['Lat', 'Lon'])
    
    if len(file_names) > 1 and isinstance(file_names, list):
        dfs = []
        for file in file_names:
            df = read_file(file_dir, file, sheet_name, usecols)
            dfs.append(df)
        return pd.concat(dfs, axis=0, ignore_index=True)

    else:
        data = read_file(file_dir, file_names[0], sheet_name, usecols)
        return data
    
def find_city(province_name):
    for i in ["Thành phố", "Tỉnh", "TP."]:
        if i in province_name:
            pattern = r"^(Thành phố |Tỉnh |TP\.)"
            # Use re.sub to replace the pattern with an empty string
            province_name = re.sub(pattern, "", province_name).strip()

    province_name = unidecode(province_name)
    dir_names = os.listdir("toa_do")

    closest_matches = [file for file in dir_names if re.match(rf'^{re.escape(province_name)}\s*\d*\.xlsx|csv$', file)]
    return closest_matches

def main(city, administrative_unit, number_of_boardcast):
    validate_data(city, str, "Vui lòng nhập Thành phố/Tỉnh cần tìm kiếm")
    validate_data(administrative_unit, str, "Vui lòng nhập Xã/Phường cần tìm kiếm")
    validate_data(number_of_boardcast, int, "Vui lòng nhập số điểm phát sóng là số nguyên dương.")

    tram_ca_file_name = os.listdir("tram_ca")
    if not tram_ca_file_name or len(tram_ca_file_name) > 1:
        result_textbox.delete(0, END)
        result_textbox.insert(END, "Vui lòng kiểm tra dữ liệu trạm CA, hiện đang bị thiếu file hoặc thừa file.")
        return

    tram_ca = get_file_data("tram_ca", tram_ca_file_name, sheet_name="Xa", usecols="A,D,G")

    tram_ca_mapped = tram_ca[tram_ca["Tên đơn vị hành chính"].str.contains(administrative_unit,regex=True)]
    
    city_name = find_city(city)
    
    if len(tram_ca_mapped) > 0:
        lat_dd, lon_dd = lat_lon_convert(tram_ca_mapped["Toạ độ điểm trung tâm (Vĩ độ, Kinh độ)"].iloc[0])

        broadcast_location = get_file_data("toa_do", city_name, sheet_name=0, usecols="B, C")
        list_broadcast_locations = []
        for index, rows in broadcast_location.iterrows():
            # Create list for the current row
            my_list =(rows.Lat.item(), rows.Lon.item())
            
            # append the list to the final list
            list_broadcast_locations.append(my_list)

        closest_points = get_closest(lat_dd, lon_dd, list_broadcast_locations, number_of_boardcast)

        # Clear previous output and insert new text
        result_textbox.config(state="normal")  # Enable editing
        result_textbox.delete(0, END)  # Clear previous text
        
        # Format output text
        result_textbox.insert(END, f"Tọa độ {number_of_boardcast} điểm phát sóng gần trạm CA nhất:")

        for point, distance in closest_points:
            result_textbox.insert(END, f"{point} - khoảng cách {distance:.2f} km")

    else:
        result_textbox.config(state="normal")  # Enable editing
        result_textbox.delete(0, END)
        result_textbox.insert(END, "Không tìm thấy thông tin.")
        result_textbox.insert(END, "Vui lòng kiểm tra lại thông tin đã nhập.")

def validate_data(input_data, type, message):
    try:
        input_data = type(input_data)
    except:
        result_textbox.config(state="normal")
        result_textbox.delete(0, END)
        result_textbox.insert(END, message)

def frame_gui():
    root.title("Tìm kiếm tọa độ thông qua trạm CA")
    root.geometry("600x450")
    root.configure(bg="#f0f0f0")

    # Create main frame
    main_frame = Frame(root, padx=20, pady=20, bg="#f0f0f0")
    main_frame.pack(expand=True)

    # Title
    instructions = Label(main_frame, text="Điền thông tin cần tìm kiếm phía dưới", font=("Arial", 12, "bold"), bg="#f0f0f0")
    instructions.grid(row=0, column=0, columnspan=2, pady=10)

    # Text box and title of administrative unit
    input_city = Label(main_frame, text="Tên thành phố/tỉnh:", font=("Arial", 10), bg="#f0f0f0")
    input_city.grid(row=1, column=0, sticky="w", padx=5, pady=5)
    city = Entry(main_frame, width=40)
    city.grid(row=1, column=1, padx=5, pady=5)

    # Text box and title of administrative unit
    input_name = Label(main_frame, text="Tên trạm CA:", font=("Arial", 10), bg="#f0f0f0")
    input_name.grid(row=2, column=0, sticky="w", padx=5, pady=5)
    administrative_unit = Entry(main_frame, width=40)
    administrative_unit.grid(row=2, column=1, padx=5, pady=5)

    # Text box and title of "number of boardcast"
    input_number = Label(main_frame, text="Số điểm phát sóng:", font=("Arial", 10), bg="#f0f0f0")
    input_number.grid(row=3, column=0, sticky="w", padx=5, pady=5)
    number_of_boardcast = Entry(main_frame, width=40)
    number_of_boardcast.grid(row=3, column=1, padx=5, pady=5)

    # Search button
    button_search = Button(main_frame, text="Tìm kiếm", command=lambda: main(city.get(), administrative_unit.get(), number_of_boardcast.get()))
    button_search.grid(row=4, column=0, columnspan=2, pady=15)

if __name__ == "__main__":
    # Create GUI
    root = Tk()
    frame_gui()

    # Scrollbar 
    scrollbar = Scrollbar(root)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Text widget for displaying results
    result_textbox = Listbox(root, font=("Arial", 10), fg="blue", bg="#f8f8f8", height=15, width=75, yscrollcommand=scrollbar.set)
    result_textbox.pack(pady=10)

    # Run
    root.mainloop()