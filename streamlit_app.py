import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from PIL import Image, ImageDraw, ImageFont


st.title("AHS Map")
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
  carbon_levels = pd.read_csv(uploaded_file, skipfooter = 3, engine = 'python', index_col=0) 
  carbon_levels_without_empty_columns = carbon_levels[[c for c in carbon_levels.columns if not c.startswith('Unnamed: ')]]  #removes the 175 empty columns at end of dataset
  pd.DataFrame.iteritems = pd.DataFrame.items
  pd.set_option("display.max.columns", None)
  #carbon_levels.dropna(axis = 1, inplace = True)
  carbon_levels_without_empty_columns.dropna(axis = 0)
  
  
  #PROCESS FOR FILTERING
  Holidays_for_script = [
      datetime.date(2024, 1, 1),
      datetime.date(2024, 1, 15),
      datetime.date(2024, 2, 19),
      datetime.date(2024, 2, 20),
      datetime.date(2024, 2, 21),
      datetime.date(2024, 2, 22),
      datetime.date(2024, 2, 23),
      datetime.date(2024, 4, 15),
      datetime.date(2024, 4, 16),
      datetime.date(2024, 4, 17),
      datetime.date(2024, 4, 18),
      datetime.date(2024, 4, 19),
      datetime.date(2024, 5, 27),
      datetime.date(2024, 6, 19)
      #datetime.date(2019, 2, 18), #when the data starts - feb break
      #datetime.date(2019, 2, 19),
      #datetime.date(2019, 2, 20),
      #datetime.date(2019, 2, 21),
      #datetime.date(2019, 2, 22),
      #datetime.date(2019, 4, 15), #april break
      #datetime.date(2019, 4, 16),
      #datetime.date(2019, 4, 17),
      #datetime.date(2019, 4, 18),
      #datetime.date(2019, 4, 19),
      #datetime.date(2019, 5, 27) #memorial day
  ] 
  
  early_release_days = [
      datetime.date(2024, 1, 26),
      datetime.date(2024, 3, 8),
      datetime.date(2024, 5, 3)
      #datetime.date(2019, 2, 1),
      #datetime.date(2019, 3, 15),
      #datetime.date(2019, 5, 3)
  ]
  SCHOOL_START_TIME = datetime.time(8, 15) #7:45 for old data, 8:15 for new
  NORMAL_RELEASE_TIME = datetime.time(2, 51) #2:20 for old data, 2:51 for new
  EARLY_RELEASE_TIME = datetime.time(11, 30) #10:50 for old data, 11:30 for new
  
  carbon_levels_without_empty_columns.index = pd.to_datetime(carbon_levels_without_empty_columns.index)
  #print(carbon_levels.index)
  #print(carbon_levels.index.time)
  
  time_is_not_notschool = ~np.isin(carbon_levels_without_empty_columns.index.time, (pd.date_range("8:00", "15:00", freq = "1min").time))
  carbon_levels_school = carbon_levels_without_empty_columns[~time_is_not_notschool] #filters out of school hours
  
  
  time_is_not_weekend = ~np.isin(carbon_levels_school.index.weekday, [5,6]) #filters weekends
  carbon_levels_not_weekends = carbon_levels_school[time_is_not_weekend]
  
  #print(carbon_levels_not_weekends)
  
  time_is_not_holiday = ~np.isin(carbon_levels_not_weekends.index.date, Holidays_for_script) #filters holidays
  carbon_levels_without_holidays = carbon_levels_not_weekends[time_is_not_holiday]
  
  is_early_release_day = np.isin(carbon_levels_without_holidays.index.date, early_release_days) #filters early release days
  is_within_early_release_hours = (
      is_early_release_day
      & (carbon_levels_without_holidays.index.time >= SCHOOL_START_TIME)
      & (carbon_levels_without_holidays.index.time <= EARLY_RELEASE_TIME)
  )
  is_within_normal_school_hours = (
      ~is_early_release_day
      & (carbon_levels_without_holidays.index.time >= SCHOOL_START_TIME)
      & (carbon_levels_without_holidays.index.time <= NORMAL_RELEASE_TIME)
  )
  carbon_levels_in_normal_school_hours = carbon_levels_without_holidays[
      (is_within_early_release_hours | is_within_normal_school_hours)
  ]
  
  
  #BEGINNING OF HEATMAP (?) CODE
   
  im1 = Image.open("assets/Screenshot 2024-07-26 120058.png")
  #im2
  #im3
  
  
  fig, ax = plt.subplots()
  ax.imshow(im1)
  #st.image(im1, caption='School Map', use_column_width=True)
  
  draw = ImageDraw.Draw(im1)
  
  #coords=[]
  
  #def clickMap(area):
  #    print("Click detected...")
  #    x, y = area.xdata, area.ydata  #takes x and y and changes them into coordinates
  #    coords.append((x,y))
  #    print(f'Coordinates: ({x}, {y})')  #f-string makes it easier to print
  
  #cid = fig.canvas.mpl_connect('button_press_event', clickMap)   #connects the clickMap function to the image, parameter for area is automatically funneled into the function
  
  #print(f'Event connected: {cid}')  #cid -> connection id
  
  #plt.show()
  #what the above does is make a script where whatever I click produces coords in the terminal
  
  
  
  #pain and suffering - gathering each individual ordered pair
  
  floor_columns = [col for col in carbon_levels_without_holidays.columns if col.startswith('RM1')]
  specific_sensors = [col for col in carbon_levels_without_holidays.columns if 'FieldHouse' in col or 'Cafe' in col]
  filtered_columns = floor_columns + specific_sensors
  filtered_df = carbon_levels_without_holidays[filtered_columns]
  temperature_columns = [col for col in filtered_df.columns if 'T' in col and 'CO2' not in col and 'Q' not in col]
  temperature_df = filtered_df[temperature_columns]

  
  
  coordinates = {
      'RM116 ZN06  ZN-T': (485.45, 448.79),
      'RM138 ZN09 ZN-T': (811.1, 445.64),
      'RM137 ZN09 ZN-T': (815.72, 408.3),
      'RM139 ZN09 ZN-T': (785.93, 440.61),
      'Cafe UV08 ZN08 ZN-T': (738.65, 374.67),
      'Cafe UV01 ZN08 ZN-T': (744.03, 448.18),
      'Cafe UV14 ZN08 ZN-T': (530.67, 439.22),
      'Cafe UV02 ZN08ZN-T': (548.6, 380.05),
      'FieldHouse-NE ZN1 ZN-T': (209.72, 250.95),
      'FieldHouse-NW ZN1 ZN-T': (53.73, 250.57),
      'FieldHouse-SE ZN1 ZN-T': (213.3, 512.73),
      'FieldHouse-SW ZN1 ZN-T': (55.52, 510.94)
      }
      
  
  medians = temperature_df.median()
  medians_dict = medians.to_dict()

  st.write(medians_dict)
      
  for sensor, coord in coordinates.items():
      x, y = coord
      ax.plot(x, y, 'ro')  # 'ro' means red dot
  
  was_sensor_clicked = {}
  # Function to display temperature when a dot is clicked
  def on_click(event):
      x_click, y_click = event.xdata, event.ydata
      
      if x_click is None or y_click is None:
          return  # Click was outside the image area
      
      # Find the closest sensor to the click
      closest_sensor = None
      min_distance = float('inf')
      
      for sensor, (x, y) in coordinates.items():
          distance = np.sqrt((x_click - x) ** 2 + (y_click - y) ** 2)
          if distance < min_distance:
              min_distance = distance
              closest_sensor = sensor
      
      # If a close enough sensor is found, display its median temperature
      if closest_sensor and min_distance < 10:# Adjust threshold as needed
          if closest_sensor in was_sensor_clicked:
              was_sensor_clicked[closest_sensor].remove()
              del was_sensor_clicked[closest_sensor]
          else:
              median_temp = medians_dict[closest_sensor]
              clicked = ax.text(x_click, y_click, f'{median_temp:.1f}°F', fontsize=12, color='blue')
              was_sensor_clicked[closest_sensor] = clicked
      plt.draw()  # Update the plot with the text
  
  # Connect the click event to the function    
  cid = fig.canvas.mpl_connect('button_press_event', on_click)
  
  st.pyplot(fig)
      
  
  #print(carbon_levels_without_holidays[firstFloor])
  #necessaryCoords = []
  
  #print(f'Coordinates: ({x}, {y})')
  
  fig.canvas.mpl_disconnect(cid)
else:
  st.write("Make sure to upload a CSV file from Metasys!")




