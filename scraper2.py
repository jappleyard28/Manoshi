# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 00:05:27 2021

@author: AJ
"""

import requests
from bs4 import BeautifulSoup

def search(start, destination, date, time):
    session = requests.Session()
    
    session.get("https://www.nationalrail.co.uk/")
    url = "https://ojp.nationalrail.co.uk/service/timesandfares/" + start + "/" + destination + "/" + date + "/" + time + "/dep"
    request = session.get(url)
    
    source = request.text    
    soup = BeautifulSoup(source, features="html5lib")
    
    try: 
        ticket = soup.find("td", {"class": "fare has-cheapest"}) #cheapest ticket returned
        ticket = ticket.find("label", {"class": "opsingle"})
        ticket = ticket.get_text().strip() #clean and retrieve ticket price
        
        train = soup.find("td", {"class": "fare has-cheapest"}).parent  
        leaves = train.find("div", {"class": "dep"})
        leaves = leaves.get_text().strip()
        arr = train.find("div", {"class": "arr"})
        arr = arr.get_text().strip()
        
        return ticket, url, leaves, arr #TODO return train details
    except:
        return None #no tickets found on page
