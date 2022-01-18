# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 15:23:29 2022

@author: AJ
"""

from datetime import datetime
from datetime import timedelta
import pickle
import build_prediction as bd

def is_weekend(day):
    if day > 4:
        return 1
    return 0

def is_offpeak(hour):
    if hour > 570 and hour < 960:
        return 1
    if hour > 1140 or hour < 240:
        return 1
    return 0

def get_dict():
    with open('stations_dict.pickle', 'rb') as f:
        stations_dict = pickle.load(f)
    return stations_dict

station_code_dict = {
    "dorchester": "DRCHS",
    "wareham": "WARHAM",
    "hamworthy": "HMWTHY",
    "poole": "POOLE",
    "parkstone": "PSTONE",
    "branksome": "BRANKSM",
    "bournemouth": "BOMO",
    "brockenhurst": "BKNHRST",
    "southampton central": "SOTON",
    "southampton": "SOTON",
    "southampton airport parkway": "SOTPKWY",
    "winchester": "WNCHSTR",
    "basingstoke": "BSNGSTK",
    "woking": "WOKING",
    "hamworthy": "HMWTHY",
    "london waterloo": "WATRLMN",
    "waterloo": "WATRLMN"
    }

stations_dict = get_dict()

def get_prediction(start, dest, mins_late):
    try:
        start = station_code_dict[start]
        dest = station_code_dict[dest]
        
        mins_late = [int(s) for s in mins_late.split() if s.isdigit()]
        mins_late = mins_late[0]
        
        with open('knnModel.pickle', 'rb') as f:
            knn = pickle.load(f)
            
        date = datetime.now()
        time = date.time()
        
        hour = time.hour * 60
        day_of_week = date.weekday()
        is_wknd = is_weekend(day_of_week)
        is_ofpk = is_offpeak(hour)
        
        data = [[stations_dict.get(start), stations_dict.get(dest), int(mins_late), hour, day_of_week, is_wknd, is_ofpk]]
        prediction = knn.predict(data)
        prediction = prediction[0]
        now = datetime.now()
        now = now + timedelta(minutes=prediction)
        est_time = now.strftime("%H:%M")
        return "My estimation for your arrival is {prediction}.".format(prediction = est_time)
    except:
        return "Sorry, I cannot provide a reasonable estimate."

if __name__ == "__main__":
    print(get_prediction("dorchester", "wareham", "20 minute"))