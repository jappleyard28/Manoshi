# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 15:17:40 2022

@author: AJ
"""

import pandas as pd
import numpy as np
from math import sqrt
import pickle

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score 

def ttm(time):
    #convert ##:## to minutes
    return int(time[:-3]) * 60 + int(time[-2:])

def mtt(minutes):
    minutes = int(minutes)
    return '{:02d}:{:02d}'.format(*divmod(minutes, 60))

if __name__ == "__main__":
    test_pd = pd.read_csv('new_data_EXTRA.csv')
    
    #DEFINE TRAINING DATA FOR X AND Y
    Y = test_pd.iloc[:,10]
    
    #10 = est_delayed_time, our target value
    Y = np.nan_to_num(Y)
    #alter nan inputs
    
    X = test_pd.iloc[:,[2,5,9,11,13,14,15]]
    #2 = tpl of 1st station, #5 = tpl of 2nd station, #9 = minutes_late
    #11 = hour_of_day, #13 = day_of_week, #14 = is_weekend, #15 = is_offpeak
    X = np.nan_to_num(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=.3, random_state=4)
    
    knn = KNeighborsRegressor(n_neighbors=3)  
    knn.fit(X_train, y_train)
    
        
    #ACCURACY TESTING
    y_guess = knn.predict(X_test)
    print("MEAN SQUARED ERROR:      R2 SCORE:")
    print(sqrt(mean_squared_error(y_test, y_guess)), r2_score(y_test, y_guess)) 
    
    
    df = pd.DataFrame({'Actual': y_test.flatten(), 'Predicted': y_guess.flatten()})
    print(df)
    #END OF ACCURACY TESTING
    
    #with open('knnModel.pickle', 'wb') as f:
        #pickle.dump(knn, f)