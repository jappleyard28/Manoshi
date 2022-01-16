# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 20:42:42 2022

@author: AJ
"""

from random import choice
from experta import *
from experta.utils import unfreeze

import nlp

def fire_message(text):
    #will be used to pass chatbot dialogue to ui
    print("Firing a message: " + text)
    
class Chatbot(KnowledgeEngine):  
    @DefFacts()
    def needed_data(self):
        yield Fact(request=False, reqs=None)
        
    @Rule(AND(NOT(Fact(intent='book')),
              NOT(Fact(intent='cancel')),
              NOT(Fact(intent='delay'))),
          Fact(intent=MATCH.intent))
    def chat(self, intent):
        fire_message(nlp.speak(intent))
        
    @Rule(AS.intent << Fact(intent='book'),
          AS.active << Fact(request=False, reqs=None),
          Fact(message=MATCH.message))
    def booking(self, active, message, intent):
        #define appropriate params [param_name, value, entity_type, question]
        reqs = [["start", None, "GPE", "Where are you travelling from?"],
                 ["destination", None, "GPE", "Where would you like to travel to?"],
                 ["date", None, "DATE", "What date are you travelling?"],
                 ["time", None, "TIME", "What time do you want to travel?"]]
        self.modify(active, request=True, reqs='book')
        
        fire_message(nlp.speak('book'))
        message = unfreeze(message)
        returned_params = nlp.response(reqs, message, None, intent) #parse input for named entities

        is_valid = not any(None in l for l in returned_params)
        
        self.declare(Fact(params=returned_params))
        self.declare(Fact(valid=is_valid))
        
    @Rule(AS.intent << Fact(intent='bookreturn'),
          AS.active << Fact(request=False, reqs=None),
          Fact(message=MATCH.message))
    def booking_return(self, active, message, intent):
        #define appropriate params [param_name, value, entity_type, question]
        reqs = [["start", None, "GPE", "Where are you travelling from?"],
                 ["destination", None, "GPE", "Where would you like to travel to?"],
                 ["date", None, "DATE", "What date are you travelling?"],
                 ["time", None, "TIME", "What time do you want to travel?"],
                 ["return_date", None, "DATE", "What date do you want to return?"],
                 ["return_time", None, "TIME", "What time do you want to return?"]]
        self.modify(active, request=True, reqs='bookreturn')
        
        fire_message(nlp.speak('bookreturn'))
        message = unfreeze(message)
        returned_params = nlp.response(reqs, message, None, 'book') #parse input for named entities

        is_valid = not any(None in l for l in returned_params)
        
        self.declare(Fact(params=returned_params))
        self.declare(Fact(valid=is_valid))
    
    @Rule(AS.intent << Fact(intent='delay'),
          AS.active << Fact(request=False, reqs=None),
          Fact(message=MATCH.message))
    def delaying(self, active, message, intent):
        #define appropriate params [param_name, value, entity_type, question]
        reqs = [["destination", None, "GPE", "Where is your train now?"],
                 ["time", None, "TIME", "Where are you travelling to?"],
                 ["time", None, "TIME", "How long are you delayed?"]]
        self.modify(active, request=True, reqs='delay')
        
        fire_message(nlp.speak('delay'))
        message = unfreeze(message)
        returned_params = nlp.response(reqs, message, None, intent) #parse input for named entities

        is_valid = not any(None in l for l in returned_params)
        
        self.declare(Fact(params=returned_params))
        self.declare(Fact(valid=is_valid))
        
    @Rule(Fact(request=True, reqs=MATCH.reqs),
          AS.validity << Fact(valid=False),
          Fact(params=MATCH.params),
          AS.cur_intent << Fact(intent=MATCH.intent),
          AS.old_params << Fact(params=MATCH.params))
    def req_inprocess(self, reqs, validity, params, cur_intent, old_params):
        params = unfreeze(params)
        returned_params = None
        for req in params:
            while req[1] == None:
                fire_message(req[3])
                message = input()
                returned_params = nlp.response(params, message, req[3], cur_intent)
                if returned_params == 'CANCEL':
                    self.modify(cur_intent, intent='cancel')
                    return
                if req[1] == None:
                    fire_message(nlp.speak('datanotfound'))
        self.modify(old_params, params=returned_params)
        is_valid = not any(None in l for l in returned_params)
        self.modify(validity, valid=is_valid)
        
    @Rule(AND(Fact(reqs='book'),
             Fact(valid=True)),
             Fact(params=MATCH.params))
    def find_ticket(self, params):
        params = unfreeze(params)
        #with all parameters, begin web scraping for ticket
        fire_message(nlp.find_ticket(params[0][1], params[1][1], params[2][1], params[3][1]))
        engine.reset() #reset facts for next interaction
        
    @Rule(AND(Fact(reqs='bookreturn'),
             Fact(valid=True)),
             Fact(params=MATCH.params))
    def find_return(self, params):
        params = unfreeze(params)
        #with all parameters, begin web scraping for ticket
        fire_message(nlp.find_return(params[0][1], params[1][1], params[2][1], params[3][1], params[4][1], params[5][1]))
        engine.reset() #reset facts for next interaction
        
    @Rule(AND(Fact(reqs='delay'),
             Fact(valid=True)),
             Fact(params=MATCH.params))
    def find_delay(self, params):
        params = unfreeze(params)
        fire_message("PUT DELAY PREDICTION HERE")
        #fire_message(prediction_guess.predict(params[0][1], params[1][1], params[2][1]))
        engine.reset()
    
    @Rule(AND(Fact(intent='cancel'),
      Fact(request=True)),
          salience=100)
    def cancel(self):
        fire_message(nlp.speak("cancel"))
        engine.reset()
        #self.declare(Fact(request=False, reqs=None)) #cancel current transaction
        
    @Rule(AND(Fact(intent='cancel'),
      Fact(request=False)))
    def wtf(self):
        fire_message(nlp.speak("notunderstood"))


engine = Chatbot()
engine.reset() 
fire_message(nlp.speak("greeting"))       
while True:
    msg = nlp.parse_input(input())
    engine.declare(Fact(intent=msg[0]))
    engine.declare(Fact(message=msg[1]))
    engine.run()
    engine.reset()