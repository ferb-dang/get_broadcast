import re
import pandas as pd
from tkinter import Tk, Label, Entry, Button, Frame, Scrollbar, Text, Listbox, RIGHT, Y, END
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

def main(administrative_unit, number_of_boardcast):
    tram_ca = pd.read_excel("D:\workspaces\get_broadcast\E124-2009 (31-12)2-MSDVHCVN.xls", sheet_name="Xa", usecols="D,G")
    # Validate input
    tram_ca_mapped = tram_ca[tram_ca["Tên đơn vị hành chính"].str.contains(administrative_unit,regex=True)]
    
    if len(tram_ca_mapped) > 0:
        lat_dd, lon_dd = lat_lon_convert(tram_ca_mapped["Toạ độ điểm trung tâm (Vĩ độ, Kinh độ)"].iloc[0])

        broadcast_location = pd.read_excel("D:\workspaces\get_broadcast\hanoi.xls", usecols="B, C")
        list_broadcast_locations = []
        for index, rows in broadcast_location.iterrows():
            # Create list for the current row
            my_list =(rows.Lat.item(), rows.Lon.item())
            
            # append the list to the final list
            list_broadcast_locations.append(my_list)

        closest_points = get_closest(lat_dd, lon_dd, list_broadcast_locations, number_of_boardcast)

        # Format output text
        result = f"Tọa độ {number_of_boardcast} điểm gần trạm CA nhất là:\n"
        result += "\n".join(f"{point} - khoảng cách {distance:.2f} km\n" for point, distance in closest_points)

        # Clear previous output and insert new text
        result_textbox.config(state="normal")  # Enable editing
        result_textbox.delete(1.0, "end")  # Clear previous text
        result_textbox.insert("end", result)  # Insert new result
        # return result_label.config(text=result)

    else:
        result = f"Không tìm thấy kết quả theo tên trạm CA: {administrative_unit}\n Vui lòng kiểm tra lại tên trạm đã nhập."
        # return result_textbox.config(text=result)
        return result_textbox.insert(END, result)

def main_frame_gui():
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

def display_frame_gui():
    pass


if __name__ == "__main__":
    # Create GUI
    root = Tk()
    root.title("Tìm kiếm tọa độ thông qua trạm CA")
    root.geometry("600x450")
    root.configure(bg="#f0f0f0")

    main_frame_gui()

    # Scrollbar 
    scrollbar = Scrollbar(root)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Text widget for displaying results
    result_textbox = Listbox(root, font=("Arial", 10), fg="blue", bg="#f8f8f8", height=15, width=75, yscrollcommand=scrollbar.set)
    result_textbox.pack(pady=10)
    # result_textbox.config(state="disabled")  # Prevent user input

    # Run
    root.mainloop()
    # main("Phúc xá", 5)