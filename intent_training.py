# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 15:29:11 2021

@author: AJ
"""

import json
from sklearn.preprocessing import LabelEncoder
import numpy as np
from tensorflow import keras
from keras.models import Model,Sequential
from keras.layers import Activation, Dense, Dropout

import spacy
nlp = spacy.load('en_core_web_sm')

import pickle
#import tenserflow.keras


data = json.load(open('intents.json'))

ignore = [",", ".", "!", "?", "'"] #put any ignored characters here

known_words = [] #stores all known vocab from intents.json
classes = [] #stores the intents.json tags, aka intent classes
documents = [] #stores sentence:intent for all intents in intents.json

def clean(pattern):
    #cleans text, lemmatizing and lowercase
    ret = []
    pattern = nlp(pattern)
    for word in pattern:
        if word.lemma_ not in ignore: #remove punctuation
            ret.append(word.lemma_.lower())
    return ret
    
def process():
    #run through intents and reformat into a list of categorised tuples
    #so that we can dynamically make a bag of words model
    for intent in data['intents']:
        for pattern in intent['patterns']:
            word_list = clean(pattern) #clean the pattern first
            
            known_words.extend(word_list)
            documents.append((word_list, intent['tag']))

            if intent['tag'] not in classes:
                classes.append(intent['tag'])

def bag_of_words():
    #produces a bag of words model, indicating how many times known words
    #in the grammar appear in an intent pattern, for feeding into a neural
    #network
    training = []
    for doc in documents:
        bow = [] #bag for 0,1 values (0 = word not present, 1 = present)
        sentence = doc[0] #doc[0] is the sentence, doc[1] is the intent
        
        for word in known_words:
            if word in sentence:
                bow.append(1)
            else:
                bow.append(0)
                
        intent = [0] * len(classes) #create a list of 0s based on class count
        intent[classes.index(doc[1])] = 1 #mark the corresponding intent as 1 based on classes order
        training.append([bow, intent])
        
    training = np.array(training, dtype=object)
    
    print("TRAINING:\n" + str(training))
    training_x = list(training[:, 0]) #get all 0 dimension values for x training
    #training_x stores the bag of words and 1s for present words in vocab
    training_y = list(training[:, 1]) #get all 1 dimension values for y training
    #training_y stores a binary representation of which intent the bag of words belongs to
    
    print("TRAINING_X:\n" + str(training_x))
    print("TRAINING_Y:\n" + str(training_y))
    return training_x, training_y

def model(training_x, training_y):
    #this builds our neural network
    num = 50 #initial dense value
    model = Sequential()
    model.add(Dense(num, activation='relu', input_shape=(len(training_x[0]),)))
    model.add(Dropout(0.5))
    model.add(Dense(num/2, activation='relu'))
    model.add(Dropout(0.5))
    
    model.add(Dense(len(classes), activation = 'softmax'))
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    batch_size = 5
    epoch_count = 200 #train for 200 epochs 
    
    #create the neural net model with training data and specifications
    nlp_model = model.fit(np.array(training_x), np.array(training_y), 
            batch_size = batch_size, epochs = epoch_count,
            verbose = 1) 
    #save model for loading into main chatbot application
    model.save("nlp.h5", nlp_model)
    #write intents and vocab to file as main application will need access
    with open("classes.pickle", 'wb') as f:
        pickle.dump(classes, f)
    with open('known_words.pickle', 'wb') as f:
        pickle.dump(known_words, f)
    
process()
known_words = set(known_words) #remove duplicates by converting to set
known_words = list(known_words) #convert back to list

training_x, training_y = bag_of_words()
model(training_x, training_y)