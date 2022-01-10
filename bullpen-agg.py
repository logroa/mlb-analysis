import json
import os
from bs4 import BeautifulSoup
import requests
import pandas as pd
import threading
import sqlite3

def requester(url):
    r = requests.get(url)
    return BeautifulSoup(r.text, 'html.parser')


def team_return(conn):
    cur = conn.cursor()
    teams = cur.execute('SELECT abbr FROM teams;').fetchall()
    tea = [t for team in teams for t in team]
    tea[tea.index('KC')] = 'KCR'
    tea[tea.index('TB')] = 'TBR'
    tea[tea.index('WSH')] = 'WSN'
    tea[tea.index('SF')] = 'SFG'
    tea[tea.index('SD')] = 'SDP'
    return tea


def db_inserter(conn, data):
    cur = conn.cursor()
    cur.execute("""INSERT INTO bullpens (year, team, wins, losses, sv, ip,
                kp9, bbp9, hrp9, babip, lobp, gbp, hrpfb, vfa, era, fip, xfip, war)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                data)
    conn.commit()


def data_grab(conn, url, year):
    soup = requester(url)
    tab = soup.find('table', {'class':'rgMasterTable'}).find('tbody').find_all('tr')
    teams = team_return(conn)
    for t in tab:
        dat = t.find_all('td')
        next_bp = [year, teams.index(dat[1].text)+1, dat[2].text, dat[3].text, dat[4].text,
                   dat[7].text, dat[8].text, dat[9].text, dat[10].text,
                   dat[11].text, dat[12].text, dat[13].text, dat[14].text, dat[15].text,
                   dat[16].text, dat[18].text, dat[19].text, dat[20].text]
        db_inserter(conn, next_bp)
        

def runner(conn):
    for i in range(2013,2022):
        url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=8&season='+str(i)+'&month=0&season1='+str(i)+'&ind=0&team=0,ts&rost=0&age=0&filter=&players=0&startdate=&enddate='
        data_grab(conn, url, i)


if __name__ == "__main__":
   pd.set_option("display.max_rows", None, "display.max_columns", None)
   try:
       connection = sqlite3.connect("var/mlb.sqlite3")
   except:
       print("Connection to database failed.")
       exit(1)
   runner(connection)
   