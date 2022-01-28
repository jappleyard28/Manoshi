# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 18:45:42 2022

@author: AJ
"""

'''import pandas as pd
import numpy as np
    
def ttm(time):
    #convert ##:## to minutes
    return int(time[:-3]) * 60 + int(time[-2:])

def mtt(minutes):
    minutes = int(minutes)
    return '{:02d}:{:02d}'.format(*divmod(minutes, 60))

def get_dict():
    train_data = pd.read_csv('WEYMTH_WATRLMN_OD_a51_2018_1_1.csv')
    stations_dict = {}
    i = 0
    for station in train_data['tpl'].unique():
        stations_dict[station] = i
        i = i + 1
    return stations_dict

if __name__ == "__main__":
    train_data = pd.read_csv('WEYMTH_WATRLMN_OD_a51_2018_1_1.csv')
    
    
    #CONVERT PTA AND ARR_AT TIMES TO MINUTES
    values = train_data['pta'].fillna('00:00').str.split(':', expand=True).astype(int)
    factors = np.array([60, 1])
    train_data['pta'] = (values * factors).sum(1)
    
    values = train_data['arr_at'].fillna('00:00').str.split(':', expand=True).astype(int)
    factors = np.array([60, 1])
    train_data['arr_at'] = (values * factors).sum(1)
    
    train_data['arr_at'] = np.where(train_data['arr_at'] == 0, train_data['pta'], train_data['arr_at'])
    
    #CREATE NEW COLUMN "MINUTES_LATE"

    train_data['minutes_late'] = (train_data['arr_at'] - train_data['pta'])
    #train_data['minutes_late'] = np.where(train_data['arr_at'] >, train_data['pta'], train_data['arr_at'])
    
    
    #CREATE A DICTIONARY OF STATIONS FOR MAPPING TO NUMBERS
    stations_dict = {}
    i = 0
    for station in train_data['tpl'].unique():
        stations_dict[station] = i
        i = i + 1
    
    train_data['tpl'] = train_data['tpl'].map(stations_dict) #remap station data in table
    
    print((len(train_data['tpl']))-1)
    rid_list = []
    first_station_list = []
    first_arr_list = []
    first_pta_list = []
    second_station_list = []
    arr_at_list = []
    second_pta_list = []
    #mins_late_list = []
    for i in range(len(train_data['tpl'])):
        if i >= (len(train_data['tpl']))-1:
            break
        start_station = train_data['tpl'][i]
        start_arr = train_data['arr_at'][i]
        first_pta = train_data['pta'][i]
        #mins_late = train_data['minutes_late'][i]
        for j in range(i+1, i+100):
            if j >= len(train_data['tpl']):
                break
            if train_data['tpl'][j] == 0:
                break
            first_station_list.append(start_station)
            first_arr_list.append(start_arr)
            first_pta_list.append(first_pta)
            rid_list.append(train_data['rid'][j])
            second_station_list.append(train_data['tpl'][j])
            second_pta_list.append(train_data['pta'][j])
            #mins_late_list.append(mins_late)
            arr_at_list.append(train_data['arr_at'][j])
    
    test_pd = pd.DataFrame(list(zip(rid_list, first_station_list, first_arr_list, first_pta_list, second_station_list, arr_at_list, second_pta_list)),
           columns =['rid', 'station1', 'station1_arr', 'station1_pta', 'station2', 'station2_arr_at', 'station2_pta'])

    test_pd.to_csv('new_dataNEW.csv')

    test_pd = pd.read_csv('new_dataNEW.csv')
    
    test_pd = test_pd.drop('Unnamed: 0', 1)
    
    test_pd['journey_len'] = test_pd['station2_arr_at'] - test_pd['station1_arr']
    print(test_pd['journey_len'])
    
    test_pd['journey_len'] = np.where(test_pd['station1_arr'] > test_pd['station2_arr_at'], (1440 - test_pd['station1_arr']) + test_pd['station2_arr_at'], test_pd['journey_len'])
    
    
    test_pd['minutes_late'] = (test_pd['station1_arr'] - test_pd['station1_pta'])
    test_pd['minutes_late'] = np.where((test_pd['station1_arr'] < 180) & (test_pd['station1_pta'] > 180), (1440 + test_pd['station1_arr']) - test_pd['station1_pta'], test_pd['minutes_late'])
    
    test_pd['est_delayed_time'] = (test_pd['journey_len'] + test_pd['minutes_late'])
    test_pd.to_csv('new_dataNEW3.csv')
    print(test_pd)


    test_pd = pd.read_csv('new_dataNEW3.csv')
    test_pd = test_pd.drop(test_pd[test_pd.station1_arr == 0].index)
    test_pd = test_pd.drop(test_pd[test_pd.station2_arr_at == 0].index)
    
    test_pd.to_csv('new_dataNEW4.csv')
    
    test_pd = pd.read_csv('new_dataNEW4.csv')
    
    test_pd['hour_of_day'] = (test_pd['station1_arr'] - (test_pd['station1_arr'] % 60))
    
    test_pd['date'] = test_pd['rid'].astype(str)
    test_pd['date'] = pd.to_datetime(test_pd['date'].str[:8])
    
    test_pd['day_of_week'] = test_pd['date'].dt.weekday
    
    test_pd['is_weekend'] = 0
    test_pd['is_weekend'] = np.where((test_pd['day_of_week'] > 4), 1, test_pd['is_weekend'])
    
    test_pd['is_offpeak'] = 0
    test_pd['is_offpeak'] = np.where(((test_pd['hour_of_day'] > 570) & (test_pd['hour_of_day'] < 960)) | (test_pd['hour_of_day'] > 1140) | (test_pd['hour_of_day'] < 240), 1, test_pd['is_offpeak'])
    
    test_pd = test_pd.drop('Unnamed: 0', 1)
    test_pd = test_pd.drop('Unnamed: 0.1', 1)
    print(test_pd)
    
    test_pd.to_csv('new_data_EXTRA.csv')
    test_pd = test_pd.drop('Unnamed: 0', 1)
    test_pd = test_pd.drop('Unnamed: 0.1', 1)
    
    test_pd = pd.read_csv('new_data_EXTRA.csv')'''