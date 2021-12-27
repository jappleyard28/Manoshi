# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 16:15:04 2021

@author: AJ
"""

import spacy
nlp = spacy.load("en_core_web_md")

import re
import numpy as np
from tensorflow.keras.models import load_model
import json
import pickle

import scraper2


intents = json.load(open('intents.json'))

with open('classes.pickle', 'rb') as f:
    classes = pickle.load(f)
with open('known_words.pickle', 'rb') as f:
    known_words = pickle.load(f)
    
model = load_model("nlp.h5")

ignore = [",", ".", "!", "?"] #put any ignored characters here

#TODO add dictionary lookup for shorthands ie st --> street

def parse_input():
    while True:
        query = input() #take user input
        query = clean(query) #clean and tokenize user input for parsing
        
        #create bag of words, metric used by neural network
        bow = [0] * len(known_words)        
        for word in query:
            i = 0
            for known_word in known_words: #iterate through chatbots known words
                if word == known_word:
                    bow[i] = 1 #word matches are used to score input
                i = i + 1
        bow = np.array(bow) #np array for passing into neural net
        prediction = model.predict(np.array([bow]))[0]
        
        results = []
        i = 0
        #put probabilities in tuple with class before sorting array
        for prob in prediction:
            results.append((prob, classes[i]))
            i = i + 1
        
        threshold = 0.6
        #sort array in descending order to get highest probability at index[0]
        results = sorted(results, key=lambda tup: tup[0], reverse=True)
        
        if results[0][0] > threshold:
            response(results[0][1]) #pass the most likely intent to response output
        else:
            response("notunderstood")
        
def speak(intent):
    #get a random response from corresponding intent in intents.json,
    #determines what the chatboy says
    for pattern in intents['intents']:
        if pattern['tag'] == intent:
            print(np.random.choice(pattern['responses']))
        
def response(rq):
    speak(rq)
    
    #these are further dialogues when the bot needs to take input
    if rq == "book":
        params = { #add more params ie return = True/False
            "start": None,
            "destination": None,
            "date": None,
            "time": None
        }
        
        valid = False #false while required params are missing
        
        while valid == False:
            valid = True
            for key, val in params.items():
                if val == None: #not all data retrieved, keep pressing
                    valid = False
                    if key == "start":
                        dialogue = input("Where are you travelling from?\n")
                        params["start"] = preen(dialogue, "GPE")
                    elif key == "destination":
                        dialogue = input("Where would you like to travel to?\n")
                        params["destination"] = preen(dialogue, "GPE")
                    elif key == "date":
                        dialogue = input("What date are you travelling?\n")
                        params["date"] = preen(dialogue, "DATE")
                    elif key == "time":
                        dialogue = input("What time do you want to travel? (note: currently only supports 24 hour time in ##:## format)\n")
                        params["time"] = preen(dialogue, "TIME")
        
        print("PARAMS: " + str(params))
        input("Is this ok?\n") #TODO
        if valid == True:
            find_ticket(params["start"], params["destination"], params["date"], params["time"])
                

def find_ticket(start, destination, date, time):
    #some regex for reformatting date/time (remove punctuation/symbols)
    date = re.sub(r'[^\w\s]', "", date)
    date.strip()
    time = re.sub(r'[^\w\s]', "", time)
    time.strip()
    #call the scraper module to get ticket/train info
    data = scraper2.search(start, destination, date, time)
    print("The cheapest ticket is " + data[0])
    print("Leaves at " + data[2] + " and arrives at " + data[3])
    print("Purchase at: " + data[1])
    
def preen(dialogue, entity_type):
    #TODO add regex for detecting date/time where ner fails
    #^ OR create a database of stations/shortforms
    #used to search input for a named entity
    #entity_type needs to be specified e.g. GPE = Geographical
    dialogue = nlp(dialogue) #tokenize input using spacy
    for ent in dialogue.ents:
        if ent.label_ == entity_type:
            print("Correct data! IDENTIFIED: " + str(ent.text))
            return ent.text
    return None #no named entities found


def clean(token):
    #cleans text, lemmatizing and lowercase
    ret = []
    token = nlp(token) #tokenize input using spacy
    for word in token:
        if word.lemma_ not in ignore: #remove punctuation
            ret.append(word.lemma_.lower()) #get lemmatized form of word
    return ret

speak("greeting")
parse_input()