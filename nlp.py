# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 16:15:04 2021

@author: AJ
"""

import spacy
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_md")
from spacy.pipeline import EntityRuler

import re
import numpy as np
from tensorflow.keras.models import load_model
import json
import pickle

import scraper2


#LOAD EXTERNAL FILES
intents = json.load(open('intents.json'))
#intent classes and vocab derived from intents.json
with open('classes.pickle', 'rb') as f:
    classes = pickle.load(f)
with open('known_words.pickle', 'rb') as f:
    known_words = pickle.load(f)
    
model = load_model("nlp.h5") #nn for nlp

#Language processing
ignore = [",", ".", "!", "?"] #put any ignored characters here

slang_dict = {'st':'street', 'rd':'road', 'ave':'avenue',} #TODO add more

#state for storing data about bot's knowledge in a subtopic
class State:
    def __init__(self, last_response, params):
        self.last_response = last_response
        self.params = params

def parse_input(query):
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
        return results[0][1], query
        #pass the most likely intent to response output
    else:
        return "notunderstood", query
        #no reasonable response was found
        
def speak(intent):
    #get a random response from corresponding intent in intents.json,
    #determines what the chatboy says
    for pattern in intents['intents']:
        if pattern['tag'] == intent:
            print(np.random.choice(pattern['responses']))

def response(intent, params, query):
    speak(intent)
    
    #these are further dialogues when the bot needs to take input
    if intent == "book":
        valid = False #valid is false until enough data is gathered for search
        
        state = State(None, params)
        state.params = preen(query, state) #initial search for parameters

        while valid == False:
            valid = True
            for req in state.params:
                while req[1] == None: #not all data retrieved, keep pressing
                    valid = False
                    dialogue = input(req[3]) #ask q associated with data
                    state.last_response = req[3]
                    intent, dialogue = parse_input(dialogue)
                    if intent == 'cancel':
                        return 'CANCEL'
                    state.params = preen(dialogue, state)
                    if req[1] == None:
                        speak('datanotfound')
        #pass acquired data to scraper for ticket retrieval
        params = state.params
        return params
        #find_ticket(params[0][1], params[1][1], params[2][1], params[3][1])
        
def find_ticket(start, destination, date, time):
    #some regex for reformatting date/time (remove punctuation/symbols)
    date = re.sub(r'[^\w\s]', "", date)
    date.strip()
    time = re.sub(r'[^\w\s]', "", time)
    time.strip()
    #call the scraper module to get ticket/train info
    data = scraper2.search(start, destination, date, time)
    
    if data == None:
        print("Sorry, no tickets were found for your requirements.")
    else:
        print("The cheapest ticket is " + data[0])
        print("Leaves at " + data[2] + " and arrives at " + data[3])
        print("Purchase at: " + data[1])

def preen(dialogue, state):
    #create an array of null values to represent parameters
    params = state.params
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
                    if preen_context(dialogue, ent, state) != None and preen_context(dialogue, ent, state) != params[i][0]:
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

def preen_context(dialogue, ent, state):
    #helper method that detects the word before an entity to infer the context
    start = ["from", "at"]
    dest = ["to", "toward", "towards", "into"]
    
    if ent.label_ == "GPE":
        context = str(dialogue[ent.start - 1])
        if context in start or state.last_response == state.params[0][3]:
            return "start"
        if context in dest or state.last_response == state.params[1][3]:
            return "destination"
    #TODO add time
    return None

def regex_check(dialogue, ent_type):
    #regex for catching format ##:## as nlp sometimes misses them
    #TODO add more formats
    matcher = Matcher(nlp.vocab)
    if ent_type == "TIME":
        pattern = [{"TEXT": {"REGEX": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"}}]
        matcher.add("TIME", [pattern])
    if ent_type == "DATE":
        #ref: https://stackoverflow.com/questions/15491894/regex-to-validate-date-formats-dd-mm-yyyy-dd-mm-yyyy-dd-mm-yyyy-dd-mmm-yyyy
        pattern = [{"TEXT": {"REGEX": r'^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$'}}]
        matcher.add("DATE", [pattern])
    else:
        return None
    matches = matcher(dialogue)
    
    #ref https://spacy.io/usage/rule-based-matching
    for match_id, start, end in matches:
        span = dialogue[start:end]
        print("RETURNING REGEX: " + str(span.text))
        return span.text
        

def clean(token):
    #cleans text, lemmatizing and lowercase
    ret = []
    
    #detect any shortforms and change them into their full words
    new_token = []
    for word in token.split():
        if word.lower() in slang_dict:
            new_token.append(slang_dict[word.lower()])
        else:
            new_token.append(word)
    token = ' '.join(new_token)
    
    token = nlp(token) #tokenize input using spacy
    for word in token:
        if word.lemma_ not in ignore: #remove punctuation
            ret.append(word.lemma_.lower()) #get lemmatized form of word
    return ret

def stations():
    #updates nlp ner with station names + codes from file
    my_file = open("station_codes (07-12-2020).csv", "r")
    content = my_file.read()
    content = list(filter(None, re.split(",|\n", content)))
    
    pattern = []
    for i in range(len(content)):
        content[i] = content[i].lower()
        pattern.append({"label": "GPE", "pattern": content[i]})
        
    with open("stations.pickle", 'wb') as f:
        pickle.dump(pattern, f)

try:
    print("Loading stations.pickle...")
    with open('stations.pickle', 'rb') as f:
        pattern = pickle.load(f)
except FileNotFoundError:
    print("stations.pickle not found, creating file...")
    stations()
    with open('stations.pickle', 'rb') as f:
        pattern = pickle.load(f)
 
config = {"overwrite_ents": True}
station_list = nlp.add_pipe("entity_ruler", config=config)
station_list.add_patterns(pattern)

if __name__ == "__main__":
    speak("greeting")