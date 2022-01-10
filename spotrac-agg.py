import json
import os
from bs4 import BeautifulSoup
import requests
import pandas as pd
import threading
import sqlite3
import os
from dotenv import load_dotenv
import utils


def session_log():
    load_dotenv()

    user = os.getenv('SPOTRAC_UN')
    password = os.getenv('SPOTRAC_PW')
    
    session = requests.Session()
    
    logme = {
        'email': user,
        'password': password
    }
    
    log_url = 'https://www.spotrac.com/signin/submit/'
    
    s = session.post(log_url, data=logme)
    return session


def souper(s, url, typ, dic):
    s1 = s.get(url)

    soup = BeautifulSoup(s1.text, 'html.parser')
    t = soup.find('table').find('tbody').find_all('tr')
    
    mula = []
    
    for ts in t:
        mula.append(int(ts.find_all('td')[-1].text.strip()[1:].replace(',', '')))
    
    dic[typ] = sum(mula)


def data_insert(id, year, dic):
   try:
       connection = sqlite3.connect("var/mlb.sqlite3")
   except:
       print("Connection to database failed.")
       exit(1)
   cur = connection.cursor()
   cur.execute('''INSERT INTO payrolls (year, team, total_payroll, bullpen_payroll, sp_payroll)
               VALUES (?, ?, ?, ?, ?);''', (year, id, dic['all'], dic['bp'], dic['sp']))
   connection.commit()


def data_grab(s):
    teams = utils.team_grab()
    
    for year in range(2013, 2022):
        for index, team in teams.iterrows():
            dic = {}
            name = team['name'].lower().replace(' ', '-').replace('.', '')
            all_url = 'https://www.spotrac.com/mlb/rankings/' + str(year) + '/salary/' + name + '/'
            bp_url = 'https://www.spotrac.com/mlb/rankings/' + str(year) + '/salary/' + name + '/relief-pitcher/'
            sp_url = 'https://www.spotrac.com/mlb/rankings/' + str(year) + '/salary/' + name + '/starting-pitcher/'
            thread_all = threading.Thread(target=souper, args=(s, all_url, 'all', dic))
            thread_all.start()
            thread_bp = threading.Thread(target=souper, args=(s, bp_url, 'bp', dic))
            thread_bp.start()
            thread_sp = threading.Thread(target=souper, args=(s, sp_url, 'sp', dic))
            thread_sp.start()
            thread_all.join()
            thread_bp.join()
            thread_sp.join()
            data_insert(team['id'], year, dic)
            

def table_setup():
    connection = sqlite3.connect("var/mlb.sqlite3")
    cur = connection.cursor()
    cur.execute('''DELETE FROM payrolls;''')
    connection.commit()


if __name__ == '__main__':
    table_setup()
    data_grab(session_log())