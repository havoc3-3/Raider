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
    print(colored("Welcome to GK, an OSINT Framework\n\n"
                "Ensure that your API keys are located where they need to be...\n\n"
                "Which platform would you like to use?\n", "white"))
    global platform
    # Get user input
    platform = input(colored("""\
    OPTIONS:
    [1] Dehashed
    [2] Shodan
    [3] Snusbase
    [4] Darksearch
    [5] BinaryEdge

    \n""", "magenta") + "> ")         
    operation() # Calling to the function whos IF statements launch the function associated with selected platform, located at bottom of code  
 
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
            # Connect to SQL server            
            db_connect = pymysql.connect(sql_ip,user,passwd,db) # <~~ Connect to MySQL DB using creds from secret.py
            cursor = db_connect.cursor()
            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS " + domain + " (protocol text, ip VARCHAR(15), port integer)")
                db_connect.commit()
            except:
                print("An error occured")
                pass

            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/ip/' + host, headers=headers)
            data = response.json()    
            
            str(data) # <~~ Typecast json response as string
            # dumps converts data to json string
            json_obj = json.loads(json.dumps(data)) # <~~ Loads converts json string to python object

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
            # This command copies the newly created CSV into the secure serer configured by MySQL, this is to be able to load the data into the SQL server
            cmd = ('cp ' + domain + '_targetdata.csv /var/lib/mysql-files/')
            subprocess.call(cmd, shell=True)
            
            query = ("LOAD DATA INFILE '/var/lib/mysql-files/" + domain + 
                     "_targetdata.csv' INTO TABLE test_db." + domain + 
                     " FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\n' IGNORE 1 ROWS")            
            cursor.execute(query)
            db_connect.commit()
        #bin_edge()
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
            # Connect to SQL server 
            db_connect = pymysql.connect(sql_ip,user,passwd,db) # <~~ Connect to MySQL DB using creds from secret.py
            cursor = db_connect.cursor()
            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS " + domain + " (protocol text, ip VARCHAR(15), port integer)")
                db_connect.commit()
            except:
                print("An error occured")
                pass

            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/ip/historical/' + host, headers=headers)
            data = response.json()    
            
            str(data) # <~~ Typecast json response as string
            # dumps converts data to json string
            json_obj = json.loads(json.dumps(data)) # <~~ Converts json string to python object
            # referencing the object name in the json, device built in previous function
            oput = list(findkeys(data, 'target'))
            #print(oput)
            keys = oput[0].keys()
            # Create CSV
            with open(domain + '_targetdata_hist.csv', 'w') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(oput)
            # This command copies the newly created CSV into the secure serer configured by MySQL, this is to be able to load the data into the SQL server
            cmd = ('cp ' + domain + '_targetdata_hist.csv /var/lib/mysql-files/')
            subprocess.call(cmd, shell=True)
            
            query = ("LOAD DATA INFILE '/var/lib/mysql-files/" + domain + 
                     "_targetdata_hist.csv' INTO TABLE test_db." + domain + 
                     " FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\n' IGNORE 1 ROWS")
            cursor.execute(query)
            db_connect.commit()

        #bin_edge()
        except:
            pass
        bin_edge()

    # Queries data for specific email address
    if bin_mode == "3":
        try:
            # usr is the variable whos value is used in the GET request,
            usr = input("Name of sql table: \n>")
            email = input("Enter user specific email \n"
                         "> ")
            #domain = input("Enter the companies domain name associated with email... \n>")
            db_connect = pymysql.connect(sql_ip,user,passwd,db) # <~~ Connect to MySQL DB using creds from secret.py
            cursor = db_connect.cursor()
            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS " + usr + " (event text)")
                db_connect.commit()
            except:
                pass
            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }

            response = requests.get('https://api.binaryedge.io/v2/query/dataleaks/email/' + email, headers=headers)
            data = response.json()
            str(data)
            json_obj = json.loads(json.dumps(data))

            cursor.executemany("INSERT INTO test_db." + usr + " (event) VALUES (%s)", json_obj["events"])
            db_connect.commit()
            
            # MySQL command to Pull newly discovered data
            query = 'SELECT event FROM ' + usr
            cursor.execute(query)
            
            # Create a .csv file with values from DB
            with open(usr + "_binaryedge_email","w") as outfile:
                writer = csv.writer(outfile)
                writer.writerow(col[0] for col in cursor.description)
                for row in cursor:
                    writer.writerow(row)
            
        #bin_edge()
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
            # Connect to MySQL server
            db_connect = pymysql.connect(sql_ip,user,passwd,db) # <~~ Connect to MySQL DB using creds from secret.py
            cursor = db_connect.cursor()
            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS " + test + " (leak text, count text)")
                db_connect.commit()
            except:
                pass
            
            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/dataleaks/organization/' + domain, headers=headers)

            data = response.json()
            # print(data)
            str(data) # <~~ Typecast json response as string
            # dumps converts data to json string
            json_obj = json.loads(json.dumps(data)) # <~~ Converts json string to python object

            for group in json_obj["groups"]: # <~~ Check json output for this; Top of file
                cursor.execute("INSERT INTO test_db." + test + " (leak, count) VALUES (%s,%s)", (group["leak"], group["count"]))
            db_connect.commit()
            
            # MySQL command to Pull newly discovered data
            query = 'SELECT leak, count FROM ' + test
            cursor.execute(query)

            # Create a .csv file with values from DB
            with open(test + "_binaryedge_dataleak.csv","w") as outfile:
                writer = csv.writer(outfile)
                writer.writerow(col[0] for col in cursor.description)
                for row in cursor:
                    writer.writerow(row)
        except:
            pass
        #bin_edge()
    
    # Subdomain Enumeration
    if bin_mode == "5":
        try:
            domain = input("Enter target domain to enumerate \n"
                         "> ")
            parm = domain.lower() # <~~ Convert input to all lower, avoids duplicate DB's
            test = re.sub('\.com$', '', parm) # <~~ Strip user input of .com suffix, stored in var test
            # Connect to MySQL server
            db_connect = pymysql.connect(sql_ip,user,passwd,db) # <~~ Connect to MySQL DB using creds from secret.py
            cursor = db_connect.cursor()
            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS " + test + " (event text)")
                db_connect.commit()
            except:
                pass
            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }
            response = requests.get('https://api.binaryedge.io/v2/query/domains/subdomain/' + domain, headers=headers) 
            data = response.json()
            str(data) # <~~ Typecast json response as string
            # Convert json object to json string
            json_obj = json.loads(json.dumps(data)) # <~~ Converts json string to python object
            #list1 = json_obj["events"]

            cursor.executemany("INSERT INTO test_db." + test + " (event) VALUES (%s)", json_obj["events"])
            db_connect.commit()

            # MySQL command to Pull newly discovered data
            query = 'SELECT event FROM ' + test
            cursor.execute(query)

            # Create a .csv file with values from DB
            with open(test + "_binaryedge_subdom.csv","w") as outfile:
                writer = csv.writer(outfile)
                writer.writerow(col[0] for col in cursor.description)
                for row in cursor:
                    writer.writerow(row)
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
            
            db_connect = pymysql.connect(sql_ip,user,passwd,db) # <~~ Connect to MySQL DB using creds from secret.py
            cursor = db_connect.cursor()
            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS " + test + " (leak text, count text)")
                db_connect.commit()
            except:
                pass
            
            # GET request to query BinaryEdge API
            headers = {
                'X-Key': binary_api,
            }

            response = requests.get('https://api.binaryedge.io/v2/query/dataleaks/info/' + domain, headers=headers)

            data = response.json()
            str(data) # <~~ Typecast json response as string
            json.dumps(data) # <~~ Convert json object to json string
            json_obj = json.loads(json.dumps(data)) # <~~ Converts json string to python object

            for group in json_obj["groups"]: # <~~ Check json output for this; Top of file
                cursor.execute("INSERT INTO test_db." + test + " (leak, count) VALUES (%s,%s)", (group["leak"], group["count"]))
            db_connect.commit()
            
            # MySQL command to Pull newly discovered data
            query = 'SELECT leak, count FROM ' + test
            cursor.execute(query)

            # Create a .csv file with values from DB
            with open(test + "_binaryedge_dataleak.csv","w") as outfile:
                writer = csv.writer(outfile)
                writer.writerow(col[0] for col in cursor.description)
                for row in cursor:
                    writer.writerow(row)
        except:
            pass
        #bin_edge()

# Function to query Dehashed API, parse data, store in DB, output to .csv file unique to target
def dehashed_func():
    inp = input("Parameter to test for: \n> ")
    parm = inp.lower() # <~~ Convert input to all lower, avoids duplicate DB's
    test = re.sub('\.com$', '', parm) # <~~ Strip user input of .com suffix, stored in var test
    db_connect = pymysql.connect(sql_ip,user,passwd,db) # <~~ Connect to MySQL DB using
    cursor = db_connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS " + test + " (id text, email text, password text)")
    db_connect.commit()

    
    print("\nQuerying Dehashed... \n")
    response = requests.get("https://api.dehashed.com/search?query=\"" + parm + "\"", auth=(dehashed_email, dehashed_api_key), headers={'Accept':'application/json'}) # QUERY
    data = response.json()
    str(data) # <~~ Typecast json response as string
    json.dumps(data) # <~~ Convert json object to json string
    json_obj = json.loads(json.dumps(data)) # <~~ Converts json string to python object 

    # Iterate through the python object and grab specified values and pump them into corresponding columns in the DB table
    for entry in json_obj["entries"]: # <~~ Check json output for this; Top of file
        cursor.execute("INSERT INTO test_db." + test + " (id, email, password) VALUES (%s,%s,%s)", (entry["id"], entry["email"], entry["password"]))
    db_connect.commit()

    # MySQL command to Pull newly discover /v2/query/image/search 
    query = 'SELECT id, email, password FROM ' + test
    cursor.execute(query)
    
    # Create a .csv file with values from DB
    with open(test + ".csv","w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(col[0] for col in cursor.description)
        for row in cursor:
            writer.writerow(row)
    
    print("Results located in " + test + ".csv")

def sho_query(): # Shodan wrapper !!! Needs muchhhh more to be useful
    # Connect to API
    api = shodan.Shodan(s_api_key)
    try:
        # Perform the search
        query = ' '.join(parm) # Uses same parameter provided by user
        result = api.search(query)
    except Exception as e:
        print('Error: %s' % e)
        sys.exit(1)
    # Connect to MySQL DB    
    db_connect = pymysql.connect(sql_ip,user,passwd,db) # <~~ Connect to MySQL DB using auth-data from config file
    cursor = db_connect.cursor()
    # Iterate through the results and pipe them into the DB
    for entry in result['matches']: # <~~ Check json output for this; Top of file /v2/query/image/search 
        cursor.execute("INSERT INTO test_db." + test + " (id, email, password, ip_discovery) VALUES (NOT NULL,NOT NULL,NOT NULL,%s)", (entry["ip_str"]))
    db_connect.commit()

"""
    # Output IP list to textfile 
    query = 'SELECT ip_discovery FROM ' + test
    out = cursor.execute(query)    
    with open(test + "_ip_list.txt","w") as outfile:
        for row in cursor:
            db_connect = pymysql.connect(sql_ip,user,passwd,db) # <~~ Connect to MySQL DB using auth-data from config file
            cursor = db_connect.cursor()
            print("\nQuerying Dehashed... \n")
            response = requests.get("", auth=(dehashed_email, dehashed_api_key), headers={'Accept':'application/json'}) # QUERY
            data = response.json()
            str(data) # <~~ Typecast json response as string
            json.dumps(data) # <~~ Convert json object to json string /v2/query/image/search 
            json_obj = json.loads(json.dumps(data)) # <~~ Converts json string to python object 
    
    # Iterate through the python object and grab specified values and pump them into corresponding columns in the DB table
    for entry in json_obj["entries"]: # <~~ Check json output for this; Top of file
        cursor.execute("INSERT INTO test_db." + test + " (id, email, password) VALUES (%s,%s,%s)", (entry["id"], entry["email"], entry["password"]))
    db_connect.commit()
"""    

# global operation
def operation():
    if platform == "1":
        try:
            table_create()
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