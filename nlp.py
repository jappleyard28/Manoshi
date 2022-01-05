# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 16:15:04 2021

@author: AJ
"""

import spacy
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_md")

import re
import numpy as np
from tensorflow.keras.models import load_model
import json
import pickle

import scraper2


#LOAD EXTERNAL FILES
intents = json.load(open('intents.json'))

with open('classes.pickle', 'rb') as f:
    classes = pickle.load(f)
with open('known_words.pickle', 'rb') as f:
    known_words = pickle.load(f)
    
model = load_model("nlp.h5")

#Language processing
ignore = [",", ".", "!", "?"] #put any ignored characters here
slang_dict = {'st':'street', 'rd':'road'} #TODO add more

def parse_input():
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
        response(results[0][1], query) 
        #pass the most likely intent to response output
    else:
        response("notunderstood", query)
        #no reasonable response was found
        
def speak(intent):
    #get a random response from corresponding intent in intents.json,
    #determines what the chatboy says
    for pattern in intents['intents']:
        if pattern['tag'] == intent:
            print(np.random.choice(pattern['responses']))
        
def response(rq, query):
    speak(rq)
    
    #these are further dialogues when the bot needs to take input
    if rq == "book":
        params = [["start", None, "GPE", "Where are you travelling from?\n"],
                 ["destination", None, "GPE", "Where would you like to travel to?\n"],
                 ["date", None, "DATE", "What date are you travelling?\n"],
                 ["time", None, "TIME", "What time do you want to travel? (note: currently only supports 24 hour time in ##:## format)\n"]]

        valid = False #valid is false until enough data is gathered for search
        params = preen(query, params) #initial search for parameters

        while valid == False:
            valid = True
            for req in params:
                if req[1] == None: #not all data retrieved, keep pressing
                    valid = False
                    dialogue = input(req[3]) #ask q associated with data
                    dialogue = clean(dialogue)
                    params = preen(dialogue, params)
        #pass acquired data to scraper for ticket retrieval
        find_ticket(params[0][1], params[1][1], params[2][1], params[3][1])
                

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

def preen(dialogue, params):
    #create an array of null values to represent parameters
    data = [None] * len(params) 
    
    #fill data with any parameters already known
    for i in range(len(params)):
        if params[i][1] != None:
            data[i] = params[i][1]
            
    dialogue = ' '.join(dialogue)
    dialogue = nlp(dialogue) #tokenize input using spacy
    
    for ent in dialogue.ents: 
        for i in range(len(data)):
            if data[i] == None: #prevent from overwriting known data
                if params[i][2] == ent.label_: #entity type matches required data
                    if preen_context(dialogue, ent) != None and preen_context(dialogue, ent) != params[i][0]:
                        pass
                    else:
                        data[i] = ent.text
                        print("Correct data! IDENTIFIED: " + str(ent.text))
                        break
    
    for i in range(len(params)):
        params[i][1] = data[i] #put data into updated param list, and return
        #try regex as an additional layer after NER
        if params[i][1] == None:
            params[i][1] = regex_check(dialogue, params[i][2])
    return params

def preen_context(dialogue, ent):
    #helper method that detects the word before an entity to infer the context
    start = ["from", "at"]
    dest = ["to", "toward", "towards"]
    if ent.label_ == "GPE":
        context = str(dialogue[ent.start - 1])
        if context in start:
            return "start"
        if context in dest:
            return "destination"
    #TODO add time
    return None

def regex_check(dialogue, ent_type):
    #regex for catching format ##:## as nlp sometimes misses them
    #TODO add more formats
    if ent_type == "TIME":
        matcher = Matcher(nlp.vocab)
        pattern = [{"TEXT": {"REGEX": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"}}]
        matcher.add("TIME", [pattern])
    
        matches = matcher(dialogue)
        
        #ref https://spacy.io/usage/rule-based-matching
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]
            span = dialogue[start:end]
            return span.text


def clean(token):
    #cleans text, lemmatizing and lowercase
    ret = []
    
    #detect any shortforms and change them into their full words
    new_token = []
    for word in token.split():
        if word.lower() in slang_dict:
            print("Found slang: " + word)
            new_token.append(slang_dict[word.lower()])
            print("Converted to dictionary word: " + word)
        else:
            new_token.append(word)
    token = ' '.join(new_token)
    
    token = nlp(token) #tokenize input using spacy
    for word in token:
        if word.lemma_ not in ignore: #remove punctuation
            ret.append(word.lemma_.lower()) #get lemmatized form of word
    return ret

speak("greeting")
while True:
    parse_input()