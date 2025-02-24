import re
import os
import difflib
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

def read_file_using_extension(file_dir, file, sheet_name=None, usecols=None):
    filename, file_extension = os.path.splitext(file)
    if file_extension in [".xls", ".xlsx", ".xlsm", ".xlsb", ".odf"]:
        return pd.read_excel(os.path.join(file_dir, file), sheet_name=sheet_name, usecols=usecols)
    if file_extension in [".csv"]:
        return pd.read_csv(os.path.join(file_dir, file))
    
def find_city(code_province, province_df):
    # Cast from string
    province_df['Mã số'] = pd.to_numeric(province_df['Mã số'], downcast='integer', errors='coerce')
    province_name = province_df.loc[province_df['Mã số'] == int(code_province)]["Tên đơn vị hành chính"].values[0].strip()
    
    for i in ["Thành phố", "Tỉnh", "TP."]:
        if i in province_name:
            pattern = r"^(Thành phố |Tỉnh |TP\.)"
            # Use re.sub to replace the pattern with an empty string
            province_name = unidecode(re.sub(pattern, "", province_name).strip())

    dir_names = os.listdir("toa_do")

    closest_matches = difflib.get_close_matches(province_name, dir_names, n=2, cutoff=0.4)
    return closest_matches


def main(administrative_unit, number_of_boardcast):
    try:
        number_of_boardcast = int(number_of_boardcast)
        tram_ca_file_name = os.listdir("tram_ca")
        if not tram_ca_file_name or len(tram_ca_file_name) > 1:
            result_textbox.delete(0, END)
            result_textbox.insert(END, "Vui lòng kiểm tra dữ liệu trạm CA, hiện đang bị thiếu file hoặc thừa file.")
            return

        tram_ca = read_file_using_extension("tram_ca", tram_ca_file_name[0], sheet_name="Xa", usecols="A,D,G")
        province = read_file_using_extension("tram_ca", tram_ca_file_name[0], sheet_name="Tinh", usecols="B,C")
        # Validate input
        tram_ca_mapped = tram_ca[tram_ca["Tên đơn vị hành chính"].str.contains(administrative_unit,regex=True)]
        
        city_name = find_city(tram_ca_mapped["Mã số Tỉnh"].values[0], province)
        
        if len(tram_ca_mapped) > 0:
            lat_dd, lon_dd = lat_lon_convert(tram_ca_mapped["Toạ độ điểm trung tâm (Vĩ độ, Kinh độ)"].iloc[0])

            # nếu có 2 city trở lên, cần merge dataframe <-----------------------------------------------------------------
            broadcast_location = read_file_using_extension("toa_do", city_name, usecols="B, C")
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
            result_textbox.insert(END, f"Tọa độ {number_of_boardcast} điểm gần trạm CA nhất là:")

            for point, distance in closest_points:
                result_textbox.insert(END, f"{point} - khoảng cách {distance:.2f} km")

        else:
            result_textbox.config(state="normal")  # Enable editing
            result_textbox.delete(0, END)
            result_textbox.insert(END, f"Không tìm thấy kết quả theo tên trạm CA: {administrative_unit}")
            result_textbox.insert(END, "Vui lòng kiểm tra lại tên trạm đã nhập.")
    except Exception:
        result_textbox.delete(0, END)
        result_textbox.insert(END, "Vui lòng nhập số điểm phát sóng là số nguyên dương.")

def main_frame_gui():
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
    input_name = Label(main_frame, text="Tên trạm CA:", font=("Arial", 10), bg="#f0f0f0")
    input_name.grid(row=1, column=0, sticky="w", padx=5, pady=5)
    administrative_unit = Entry(main_frame, width=40)
    administrative_unit.grid(row=1, column=1, padx=5, pady=5)

    # Text box and title of "number of boardcast"
    input_number = Label(main_frame, text="Số điểm phát sóng:", font=("Arial", 10), bg="#f0f0f0")
    input_number.grid(row=2, column=0, sticky="w", padx=5, pady=5)
    number_of_boardcast = Entry(main_frame, width=40)
    number_of_boardcast.grid(row=2, column=1, padx=5, pady=5)

    # Search button
    button_search = Button(main_frame, text="Tìm kiếm", command=lambda: main(administrative_unit.get(), number_of_boardcast.get()))
    button_search.grid(row=3, column=0, columnspan=2, pady=15)

if __name__ == "__main__":
    # Create GUI
    root = Tk()
    main_frame_gui()

    # Scrollbar 
    scrollbar = Scrollbar(root)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Text widget for displaying results
    result_textbox = Listbox(root, font=("Arial", 10), fg="blue", bg="#f8f8f8", height=15, width=75, yscrollcommand=scrollbar.set)
    result_textbox.pack(pady=10)

    # Run
    root.mainloop()