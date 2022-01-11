# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 20:42:42 2022

@author: AJ
"""

from random import choice
from experta import *
from experta.utils import unfreeze

import nlp
    
class Chatbot(KnowledgeEngine):  
    @DefFacts()
    def needed_data(self):
        yield Fact(request=False, reqs=None)
        
    @Rule(AND(NOT(Fact(intent='book')),
              NOT(Fact(intent='cancel'))),
          Fact(intent=MATCH.intent))
    def chat(self, intent):
        nlp.speak(intent)
        
    @Rule(AS.intent << Fact(intent='book'),
          AS.active << Fact(request=False, reqs=None),
          Fact(message=MATCH.message))
    def booking(self, active, message, intent):
        #define appropriate params [param_name, value, entity_type, question]
        reqs = [["start", None, "GPE", "Where are you travelling from?\n"],
                 ["destination", None, "GPE", "Where would you like to travel to?\n"],
                 ["date", None, "DATE", "What date are you travelling?\n"],
                 ["time", None, "TIME", "What time do you want to travel? (note: currently only supports 24 hour time in ##:## format)\n"]]
        self.modify(active, request=True, reqs='book')
        returned_params = nlp.response("book", reqs, message) #parse input for named entities
        if returned_params == 'CANCEL':
            self.modify(intent, intent='cancel')
        else:
            #does chatbot have enough data to compute the request
            is_valid = not any(None in l for l in returned_params)
            
            self.declare(Fact(params=returned_params))
            self.declare(Fact(valid=is_valid))
        
    @Rule(AND(Fact(reqs='book'),
             Fact(valid=True)),
             Fact(params=MATCH.params))
    def find_ticket(self, params):
        params = unfreeze(params)
        #with all parameters, begin web scraping for ticket
        nlp.find_ticket(params[0][1], params[1][1], params[2][1], params[3][1])
        engine.reset() #reset facts for next interaction
    
    @Rule(AND(Fact(intent='cancel'),
      Fact(request=True)),
          salience=100)
    def cancel(self):
        nlp.speak("cancel")
        #self.declare(Fact(request=False, reqs=None)) #cancel current transaction
        
    @Rule(AND(Fact(intent='cancel'),
      Fact(request=False)))
    def wtf(self):
        nlp.speak("notunderstood")

nlp.speak("greeting")      
engine = Chatbot()
engine.reset()     
while True:
    msg = nlp.parse_input(input())
    engine.declare(Fact(intent=msg[0]))
    engine.declare(Fact(message=msg[1]))
    engine.run()
    engine.reset()