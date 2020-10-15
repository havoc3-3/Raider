from termcolor import colored
import requests
import json
import csv 
import sys


hunter_api = ''

def start():
    # Landing Page (the "r" in front of the triple quotes == raw)
    print(colored(r"""
     __    __   __    __  .__   __. .___________. _______ .______         __    ______   
    |  |  |  | |  |  |  | |  \ |  | |           ||   ____||   _  \       |  |  /  __  \  
    |  |__|  | |  |  |  | |   \|  | `---|  |----`|  |__   |  |_)  |      |  | |  |  |  | 
    |   __   | |  |  |  | |  . `  |     |  |     |   __|  |      /       |  | |  |  |  | 
    |  |  |  | |  `--'  | |  |\   |     |  |     |  |____ |  |\  \----.__|  | |  `--'  | 
    |__|  |__|  \______/  |__| \__|     |__|     |_______|| _| `._____(__)__|  \______/  
                                                                                    
    """, "red"))                                                               
    print(colored("Select a method to use \n", "white"))
    global platform
    # Get user input
    platform = input(colored("""\
    OPTIONS:
    [1] Domain search (ex. megacorp.com)
    [2] Email search (ex. fidel.castro@megacorp.com, Requires company domain and an individuals first and last name)
    [3] Email verification ()
    \n""", "magenta") + "> ")         
    operation() # Calling to the function whos IF statements launch the function associated with selected platform, located at bottom of code  

def hunter_io_domain():
    domain = input('Enter domain to to enumerate: \n> ')
    try:  
        response = requests.get('https://api.hunter.io/v2/domain-search?domain=' + domain + '&api_key=' + hunter_api)
        data = response.json()
        print(data)
    except:
        pass

def hunter_io_email():
    print('This will attempt to find the work related email of an individual whos name you have enumerated...\n')
    domain = input('Enter domain to to enumerate: \n> ')
    first_name = input('First name of individual: \n')
    last_name = input('Enter last name of individual: \n')
    try:  
        response = requests.get('https://api.hunter.io/v2/email-finder?domain=' + domain + '&first_name=' + first_name + '&last_name=' + last_name + '&api_key=' + hunter_api)
        data = response.json()
        print(data)
    except:
        pass

def hunter_io_email_verify():
    email = input('Enter email to attempt to verify: \n> ')
    try:  
        response = requests.get('https://api.hunter.io/v2/email-verifier?email=' + email + '&api_key=' + hunter_api)
        data = response.json()
        print(data)
    except:
        pass

def operation():
    if platform == "1":
        try:
            hunter_io_domain()
        except:
            pass 
        start()

    if platform == "2":
        try:
            hunter_io_email()
        except:
            pass
        start()

    if platform == "3":
        try:
            hunter_io_email_verify()
        except:
            pass
        start()
try:
    start()
except KeyboardInterrupt: # Keyboard interrupt supported
    print("\n\nExiting...\n")
    sys.exit()
