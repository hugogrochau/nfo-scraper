#!/usr/bin/env python

import argparse
from BeautifulSoup import BeautifulSoup
import re
import urllib
import urllib2

def login(login_data):
    '''Logs in to nfoservers and returns the session cookie'''
    
    post_data = urllib.urlencode(login_data) 
    login_request = urllib2.Request('https://www.nfoservers.com/control/status.pl')
    login_response = urllib2.urlopen(login_request, post_data)
    return login_response.headers.get('Set-Cookie')

def get_payment_page(cookie):
    '''Sends a request to the payments page with the
    session cookie and returns the page'''
    
    payment_request = urllib2.Request('https://www.nfoservers.com/control/account_payments.pl')
    payment_request.add_header('cookie', cookie)
    return BeautifulSoup(urllib2.urlopen(payment_request).read())

def scrape(page):
    '''Scrapes the page for the donation entries
    and parses them into an array size 4'''

    donation_entries = []
    email_pattern = re.compile('(\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,6})')
    table = page.findAll('table', { 'class' : 'generictable'})[2]
    rows = table.findAll('tr')
    rows.pop(0) #remove table header
    for row in rows:
        columns = row.findAll('td')
        if columns[0].text.lower().find('donation') != -1:
            donation_data = [str(column.text) for column in columns]
            donation_entry = {
                'email' : re.findall(email_pattern, donation_data[0].replace('Note', ' '))[0],
                'amount': int(float(donation_data[1])),
                'datetime': donation_data[2],
                'note': str(columns[0].i.string),
            } 
            donation_entries.append(donation_entry)
    return donation_entries

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email', help='NFOServers email', required=True)
    parser.add_argument('-p', '--password', help='NFOServers password', required=True)
    args = parser.parse_args()

    login_data = {
        'email': args.email,
        'password': args.password
    }
    session_cookie = login(login_data)

    if session_cookie == None:
        print 'Wrong email or password'
    else:
        payment_page = get_payment_page(session_cookie)
        print scrape(payment_page)
    
