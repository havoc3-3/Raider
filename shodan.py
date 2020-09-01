import shodan 
import sys
from secret import *
import csv
import requests
import json
import re

# Get all the subdomains and other DNS entries for the given domain.
def shodan_dns():
    try:
        domain = input('Domain to query: \n> ')
        parm = domain.lower() # <~~ Convert input to all lower
        test = re.sub('\.com$', '', parm) # <~~ Strip user input of .com suffix, stored in var test
        response = requests.get('https://api.shodan.io/dns/domain/' + domain + '?key=' + s_api_key)
        data = response.json().get('data') 
        writer = csv.writer(open(test+'_shodan_dns.csv', 'w', newline='\n'))
        writer.writerow(['Subdomain', 'Record Type', 'Address'])
        #print(data)
        for i in range(len(data)):
            writer.writerow([data[i]['subdomain'], data[i]['type'], data[i]['value']])
    except:
        pass
shodan_dns()

def shodan_honey():
    target_ip = input('IP honeypot probability: \n> ')
    response = requests.get('https://api.shodan.io/labs/honeyscore/' + target_ip + '?key=' + s_api_key)
    data = response.json()
    print(data)
    writer = csv.writer(open(target_ip+'.csv', 'w', newline='/n'))
    writer.writerow([''])
    """
    for i in range(len(data)):
        print()
    """