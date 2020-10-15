from termcolor import colored
from secret import *
import subprocess
import requests
import pymysql
import shodan
import json
import csv
import sys
import re

def start():
    # Landing Page (the "r" in front of the triple quotes == raw)
    print(colored(r"""
      _____       _______ ______ _  ________ ______ _____       __ 
     / ____|   /\|__   __|  ____| |/ /  ____|  ____|  __ \     /_ |
    | |  __   /  \  | |  | |__  | ' /| |__  | |__  | |__) |_   _| |
    | | |_ | / /\ \ | |  |  __| |  < |  __| |  __| |  ___/\ \ / / |
    | |__| |/ ____ \| |  | |____| . \| |____| |____| |     \ V /| |
     \_____/_/    \_\_|  |______|_|\_\______|______|_|      \_/ |_|
    """, "red"))                                                               
    print(colored("Welcome to GK_v2, a field version of our OSINT Framework\n\n"
                "Ensure that your API keys are located where they need to be...\n\n"
                "Which platform would you like to use?\n", "white"))
    global platform
    # Get user input
    platform = input(colored("""\
    OPTIONS:
    [1] Dehashed
    [2] Shodan (Temp Removed)
    [3] Hunter.io
    [4] Darksearch (Temp Removed)
    [5] BinaryEdge

    \n""", "magenta") + "> ")
    operation() # Calling to the function whos IF statements launch the function associated with selected platform, located at bottom of code  

# Function to query Dehashed API, parse data, store in DB, output to .csv file unique to target
def dehashed_func():
    inp = input("Parameter to test for: \n> ")
    parm = inp.lower() # <~~ Convert input to all lower, avoids duplicate DB's
    test = re.sub('\.com$', '', parm) # <~~ Strip user input of .com suffix, stored in var test
    print("\nQuerying Dehashed... \n")
    response = requests.get("https://api.dehashed.com/search?query=\"" + parm + "\"", auth=(dehashed_email, dehashed_api_key), headers={'Accept':'application/json'}) # QUERY
    data = response.json().get('entries')
    writer = csv.writer(open(test+'_dehashed.csv', 'w', newline='\n'))
    writer.writerow(['ID', 'Email', 'Password', 'Hashed_Password', 'Obtained_From'])
    for i in range(len(data)):
        writer.writerow([data[i]['id'], data[i]['email'], data[i]['password'], data[i]['hashed_password'], data[i]['obtained_from']]) 
        
def sho_query():
    try:    
        # Connect to Shodan API
        api = shodan.Shodan(s_api_key)
        inp = input('Query term: \n> ')
        result = api.search(inp)

        for service in result['matches']:
            print(service['ip_str'])
    except Exception as e:
        print('Error: %s' % e)
        sys.exit(1)


# Binary Edge 
def bin_edge ():
    print(colored(r"""
     ____  _                        ______    _                
    |  _ \(_)                      |  ____|  | |           
    | |_) |_ _ __   __ _ _ __ _   _| |__   __| | __ _  ___ 
    |  _ <| | '_ \ / _` | '__| | | |  __| / _` |/ _` |/ _ \ 
    | |_) | | | | | (_| | |  | |_| | |___| (_| | (_| |  __/
    |____/|_|_| |_|\__,_|_|   \__, |______\__,_|\__, |\___|
                               __/ |             __/ |     
                              |___/             |___/      
    """, "red"))                                                               
    
    print(colored("Using BinaryEdge...\n\n"
                  "Choose a mode... \n\n", "white"))
    
    bin_mode = input(colored("""\
    Select "X" to preempitvely enter target information.
    
    OPTIONS:
    [1] Query data on single host: XXX.XXX.XXX.XXX
    [2] Query data on single host dating back 6 months
    [3] Query data on a user specific email 
    [4] Query data by domain
    [5] Subdomain Enumeration 
    [6] CVE details recorded for host IP
    [7] DNS exposure
    [X] Target data
    Type "back" to return to the previous menu  
    \n""", "magenta") + "> ")

    # Query info about specific host
    if bin_mode == "1":
        try:
            # The host variable is the value being applied to the GET request, domain is used for SQL queries and CSV creation
            host = input("Enter target IP address or CIDR up to /24 \n"
                         "> ")
            domain = input("Company name associated with IP range: \n> ")

            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/ip/' + host, headers=headers)
            data = response.json()   
            str(data) # <~~ Typecast json response as string
            # Iterate through nested json data, grab key:values based on object name            
            def findkeys(node, kv):
                if isinstance(node, list):
                    for i in node:
                        for x in findkeys(i, kv):
                            yield x
                elif isinstance(node, dict):
                    if kv in node:
                        yield node[kv]
                    for j in node.values():
                        for x in findkeys(j, kv):
                            yield x
            # referencing the object name in the json
            oput = list(findkeys(data, 'target'))            
            keys = oput[0].keys()
            # Create CSV
            with open(domain + '_targetdata.csv', 'w') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(oput)
        except:
            pass
        bin_edge()

    # Queries data on host for past 6 months records !!! Cannot confirm functionality until target with historical data is tested
    if bin_mode == "2":
        try:
            # The host variable is the value being applied to the GET request, domain is used for SQL queries and CSV creation
            host = input("Enter target IP address or CIDR up to /24 \n"
                         "> ")
            domain = input("Company name associated with IP range: \n> ")
            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/ip/historical/' + host, headers=headers)
            data = response.json()
            str(data) # <~~ Typecast json response as string
            # referencing the object name in the json, device built in previous function
            oput = list(findkeys(data, 'target'))
            keys = oput[0].keys()
            # Create CSV
            with open(domain + '_targetdata_hist.csv', 'w') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(oput)
        except:
            pass
        bin_edge()

    # Queries data for specific email address
    if bin_mode == "3":
        try:
            # usr is the variable whos value is used in the GET request,
            email = input("Enter user specific email \n"
                         "> ")

            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/dataleaks/email/' + email, headers=headers)
            data = response.json().get('events')
            writer = csv.writer(open(email+'.csv', 'w', newline='\n'))
            writer.writerow(['Name of Breach'])
            for i in data:
                writer.writerow(i.split())
        except:
            pass
        bin_edge()

    # Query databreach information about a Target by its domain
    if bin_mode == "4":
        try:    
            # domain is the variable whos value is used in the GET request
            domain = input("Enter Domain: \n")
            parm = domain.lower() # <~~ Convert input to all lower, avoids duplicate DB's
            test = re.sub('\.com$', '', parm) # <~~ Strip user input of .com suffix, stored in var test

            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/dataleaks/organization/' + domain, headers=headers)
            data = response.json().get('groups')
            writer = csv.writer(open(test+'_bin_edge_domain.csv', 'w', newline='\n'))
            writer.writerow(['Leak', 'Count'])
            for i in range(len(data)):
                writer.writerow([data[i]['leak'], data[i]['count']])
        except:
            pass
        bin_edge()
    
    # Subdomain Enumeration
    if bin_mode == "5":
        try:
            domain = input("Enter target domain to enumerate \n"
                         "> ")
            parm = domain.lower() # <~~ Convert input to all lower, avoids duplicate DB's
            test = re.sub('\.com$', '', parm) # <~~ Strip user input of .com suffix, stored in var test
            
            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/domains/subdomain/' + domain, headers=headers) 
            data = response.json().get('events')
            print(data)
            writer = csv.writer(open(test + '_bin_edge_subdomain.csv', 'w', newline='\n'))
            writer.writerow(['Subdomains'])
            for i in data:
                writer.writerow(i.split())

        #bin_edge()
        except:
            pass
        bin_edge()

    # Get all available information about the dataleaks !!! Cant figure out the GET
    if bin_mode == "8":
        try:    
            domain = input("Enter Leak: \n")
            parm = domain.lower() # <~~ Convert input to all lower, avoids duplicate DB's
            test = re.sub('\.com$', '', parm) # <~~ Strip user input of .com suffix, stored in var test

            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/dataleaks/info/' + domain, headers=headers)
            data = response.json()
            print(data)
        except:
            pass
        #bin_edge()


def hunter_io():
    def operation_1():
        if platform_1 == "1":
            try:
                hunter_io_domain()
            except:
                pass 
            landing()

        if platform_1 == "2":
            try:
                hunter_io_email()
            except:
                pass
            landing()

        if platform_1 == "3":
            try:
                hunter_io_email_verify()
            except:
                pass
            landing()

    def hunter_io_domain():
        domain = input('Enter domain to to enumerate: \n> ')
        parm = domain.lower() # <~~ Convert input to all lower, avoids duplicate DB's
        stripped = re.sub('\.com$', '', parm) # <~~ Strip user input of .com suffix, stored in var test
        try:  
            response = requests.get('https://api.hunter.io/v2/domain-search?domain=' + domain + '&api_key=' + hunter_api)
            data = response.json().get('data')
            new_dict = data['emails'] # Grab nested list emails
            list_1 = []
            list_2 = []
            writer = csv.writer(open(stripped + '_hunter_io.csv', 'w', newline='\n'))
            writer.writerow(['First', 'Last','Position', 'Email','URI','Extracted Data','Last Seen Date','Still On Page'])
            def task_a():
                for i in range(len(new_dict)):
                    h = (new_dict[i]['first_name'], new_dict[i]['last_name'], new_dict[i]['position'], new_dict[i]['value'])
                    list_1.append(h)
            def task_b():    
                for d in new_dict:
                    for x in d['sources']:
                        k = (x['uri'], x['extracted_on'], x['last_seen_on'], x['still_on_page'])
                        list_2.append(k)
            def task_c():
                for g in range(len(list_2)):
                    writer.writerow(list_1[g] + list_2[g])
            task_a()
            task_b()
            task_c()
        except:
            pass

    def hunter_io_email():
        print('This will attempt to find the work related email of an individual whos name you have enumerated...\n')
        domain = input('Enter domain to to enumerate: \n> ')
        first_name = input('First name of individual: \n')
        last_name = input('Enter last name of individual: \n')
        try:  
            response = requests.get('https://api.hunter.io/v2/email-finder?domain=' + domain + '&first_name=' + first_name + '&last_name=' + last_name + '&api_key=' + hunter_api)
            data = response.json().get('data')
            writer = csv.writer(open(first_name+'_'+last_name+'.csv', 'w', newline='\n'))
            writer.writerow(['First', 'Last', 'Email', 'Domain'])
            list1 = (data['first_name'], data['last_name'], data['email'], data['domain'])
            writer.writerow(list1)
        except:
            pass

    def hunter_io_email_verify():
        email = input('Enter email to attempt to verify: \n> ')
        try:  
            response = requests.get('https://api.hunter.io/v2/email-verifier?email=' + email + '&api_key=' + hunter_api)
            data = response.json().get('data')
            writer = csv.writer(open(email+'.csv', 'w', newline='\n'))
            writer.writerow(['Result', 'Score(level of confidence)','Email', 'MX_records'])
            list3 = (data['result'], data['score'], data['email'], data['mx_records'])
            writer.writerow(list3)
        except:
            pass
    def landing():
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
        global platform_1
        # Get user input
        platform_1 = input(colored("""\
        OPTIONS:
        [1] Domain search (ex. megacorp.com)
        [2] Email search (ex. fidel.castro@megacorp.com, Requires company domain and an individuals first and last name)
        [3] Email verification 
        \n""", "magenta") + "> ")         
        operation_1() # Calling to the function whos IF statements launch the function associated with selected platform, located at bottom of code  
    landing()

# global operation
def operation():
    if platform == "1":
        try:
            dehashed_func()
        except:
            pass # <~~ If error, just continue; display nothing; Usually caused by existing DB
        dehashed_func()
        start()

    if platform == "2":
        try:
            table_create()
        except:
            pass
        sho_query()
        start()

    if platform == "3":
        try:
            hunter_io()
        except:
            pass
        hunter_io()
        start()

    if platform == "5":
        try:
            #table_create()
            bin_edge()
        except:
            pass
        bin_edge()
        start()
    
try:
    start()
except KeyboardInterrupt: # Keyboard interrupt supported
    print("\n\nExiting...\n")
    sys.exit()
