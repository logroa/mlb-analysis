# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 04:10:56 2021

@author: Owner
"""

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


def mlb_basic_datagrab(url, datalist):
    # Beautiful Soup request
    soup = requester(url)
    output = []
    leagues = ['AL ', 'NL ']
    # Grabbing divisions, team abbreviations, and team names
    divisions = soup.find_all('div', {'class': 'standings__table'})
    for q in [0,1]:
        future_df = []
        al_teams = divisions[q].find_all('tbody', {'class': 'Table__TBODY'})
        div = al_teams[0].find_all('tr', {'class': 'subgroup-headers'})
        names = al_teams[0].find_all('a')
    
        team_stats = al_teams[1].find_all('tr', {'class': 'Table__TR'})
    
        for i in [12, 6, 0]: team_stats.pop(i)
        # Creating first columns of future dataframe
        for n in range(1, len(names), 3):
            future_df.append([url[-4:], names[n].text, names[n+1].text, leagues[q] + div[n//15].text, (n//3)%5+1])
        for s in range(0, len(team_stats)):
            stats = team_stats[s].find_all('span')
            stat_list = [stats[0].text, stats[1].text, stats[4].text, stats[5].text, stats[8].text]
            future_df[s] += stat_list
        output += future_df
    datalist += output


def depth_stats(url, datalist, year):
    soup = requester(url)
    boxes = soup.find_all('div', {'class':'flex'})
    output = []
    names = boxes[2].find('table')
    names = names.find_all('tr')
    #Data Cleaning
    for n in range(1, len(names)):
        try:
            a = int(names[n].text[1])
            output.append([year, names[n].text[2:]])
        except:
            output.append([year, names[n].text[1:]])
    stats = boxes[2].find('div', {'class':'Table__ScrollerWrapper'})
    stats = stats.find_all('tr')
    for s in range(1, len(stats)):
        tds = stats[s].find_all('td')
        temp = []
        for i in tds:
            temp.append(i.text)
        output[s-1] += temp
    datalist += output


def df_maker(lis, col):
    return pd.DataFrame(lis, columns=col)


def db_setup(conn):
    divisions = ["AL East", "AL Central", "AL West",
                 "NL East", "NL Central", "NL West"]
    cur = conn.cursor()
    
    cur.execute('''DELETE FROM divisions;''')
    cur.execute('''DELETE FROM teams;''')
    cur.execute('''DELETE FROM seasons;''')
    cur.execute('''DELETE FROM season_results;''')
    
    for i in divisions:
        cur.execute('''INSERT INTO divisions (title)
                           VALUES (?);''', (i,))
        conn.commit()
    results = ["MPO", "WCL", "DRL", "CSL", "WSL", "WSW"]
    for i in results:
        cur.execute('''INSERT INTO season_results (result)
                           VALUES (?);''', (i,))
        conn.commit()


def stat_filler(conn, big_data, big_df):
    cur = conn.cursor()
    for i in range(0, 30):
        cur.execute('''INSERT INTO teams (name, abbr) VALUES
                    (?, ?);''', (big_data[i][2], big_data[i][1]))
        conn.commit()

    for index, row in big_df.iterrows():
        cur.execute('''SELECT id FROM teams WHERE name = ?;''',
                    (row['team'],))
        team = cur.fetchone()[0]
        cur.execute('''SELECT id from divisions WHERE title = ?;''',
                    (row['division'],))
        division = cur.fetchone()[0]
        season_result = 1
        cur.execute('''INSERT INTO seasons
                    (year, team, division, division_rank, season_result,
                     wins, losses, home_wins, home_losses, run_diff, gp,
                     abs, runs, hits, doubles, triples, homeruns, rbis,
                     tb, bb, so, sb, avg, obp, slg, ops, lob, ra, era, sv, cg,
                     sho, qs, ip, hits_allowed, er, homeruns_allowed,
                     walks_allowed, ks, opponent_avg, whip) VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?, ?, ?, ?, ?, ?);''', (row['season'], team,
                    division, row['div_rank'], season_result, row['W'],
                    row['L'], int(row['home'].split('-')[0]), int(row['home'].split('-')[1]),
                    int(row['run_diff']), row['gp'], row['ab'], row['r'],
                    row['h'], row['2b'], row['3b'], row['hr'], row['rbi'],
                    row['tb'], row['bb'], row['so'], row['sb'], row['avg'],
                    row['obp'], row['slg'], row['ops'], row['lob'], row['ra'], row['era'],
                    row['sv'], row['cg'], row['sho'], row['qs'], row['ip'], row['p_h'],
                    row['er'], row['p_hr'], row['p_bb'], row['p_so'],
                    row['oba'], row['whip']))
        conn.commit()


def po_stat_filler(conn, big_po):
    cur = conn.cursor()
    big_po['W'] = pd.to_numeric(big_po['W'])
    big_po = big_po.sort_values(by=['season', 'W'])
    for index, row in big_po.iterrows():
         cur.execute('''SELECT id FROM teams WHERE name = ?;''',
                     (row['team'],))
         team = cur.fetchone()[0]
         w = int(row['W'])
         l = int(row['L'])
         if w == 0 and l == 1:
             cur.execute('''UPDATE seasons
                         SET season_result = 2
                         WHERE year = ? AND
                         team = ?''',
                         (row['season'], team))
             conn.commit()
         elif w <= 3 and l == 3:
             cur.execute('''UPDATE seasons
                         SET season_result = 3
                         WHERE year = ? AND
                         team = ?''',
                         (row['season'], team)) 
             conn.commit()
         elif w <= 7 and l >= 4:
             cur.execute('''UPDATE seasons
                         SET season_result = 4
                         WHERE year = ? AND
                         team = ?''',
                         (row['season'], team)) 
             conn.commit() 
         else:
             cur.execute('''UPDATE seasons
                         SET season_result = 5
                         WHERE year = ? AND
                         team = ?''',
                         (row['season'], team)) 
             conn.commit()
         
         cur.execute('''INSERT INTO postseasons
                     (year, team, wins, losses, gp,
                      abs, runs, hits, doubles, triples, homeruns, rbis,
                      tb, bb, so, sb, avg, obp, slg, ops, era, sv, cg,
                      sho, qs, ip, hits_allowed, er, homeruns_allowed,
                      walks_allowed, ks, opponent_avg, whip) VALUES
                     (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
                     (row['season'], team,
                     row['W'],row['L'], row['gp'], row['ab'], row['r'],
                     row['h'], row['2b'], row['3b'], row['hr'], row['rbi'],
                     row['tb'], row['bb'], row['so'], row['sb'], row['avg'],
                     row['obp'], row['slg'], row['ops'], row['era'], row['sv'],
                     row['cg'], row['sho'], row['qs'], row['ip'], row['p_h'],
                     row['er'], row['p_hr'], row['p_bb'], row['p_so'],
                     row['oba'], row['whip']))
         conn.commit()


def extra_stats(data, year):
    soup = requester("https://www.baseball-reference.com/leagues/majors/" + str(year) + ".shtml")
    box = soup.find('div', {'id':'all_teams_standard_batting'})
    rows = box.find('tbody').find_all('tr')
    scale = (year-2013)*30
    for r in range(0, len(rows)-1):
        season = [str(year)]
        season.append(rows[r].find('th').text)
        s = rows[r].find_all('td')
        season.append(s[len(s)-1].text)
        data.append(season) 
    other_data = []
    soup = requester("https://www.mlb.com/stats/team/pitching/" + str(year) + "/regular-season?sortState=asc")
    box1 = soup.find('section', {'class':'stats-type-body stats-type-teamPitching'})
    b = box1.find('table')
    rows1 = b.find('tbody').find_all('tr')
    for r in range(0, len(rows1)):
        season = [str(year)]
        season.append(rows1[r].find('th').find('a').text)
        s = rows1[r].find_all('td')
        season.append(s[12].text)
        other_data.append(season)
    other_data = sorted(other_data, key= lambda x: x[1])
    for i in range(0, 30):
        data[i+scale].append(other_data[i][2])
                        
def stat_runner(conn):
    big_data = []
    hitting = []
    pitching = []
    playoff_pitching = []
    playoff_hitting = []
    extras = []
    labels = ['season', 'abbr', 'team', 'division', 'div_rank', 'W', 'L',
              'home', 'away', 'run_diff']
    hit_labels = ['season', 'team', 'gp', 'ab', 'r', 'h', '2b', '3b', 'hr',
                  'rbi', 'tb', 'bb', 'so', 'sb', 'avg', 'obp', 'slg', 'ops']
    pitch_labels = ['season', 'team', 'gp', 'W', 'L', 'era', 'sv', 'cg', 'sho',
                    'qs', 'ip', 'p_h', 'er', 'p_hr', 'p_bb', 'p_so', 'oba', 'whip']
    extra_labels = ['season', 'team', 'lob', 'ra']
    for i in range(2013, 2022):
        thread1 = threading.Thread(target=mlb_basic_datagrab, args=("https://www.espn.com/mlb/standings/_/season/" + str(i), big_data))
        thread1.start()
        thread2 = threading.Thread(target=depth_stats, args=('https://www.espn.com/mlb/stats/team/_/season/' + str(i) + '/seasontype/2', hitting, str(i)))
        thread2.start()
        thread3 = threading.Thread(target=depth_stats, args=('https://www.espn.com/mlb/stats/team/_/view/pitching/season/' + str(i) + '/seasontype/2', pitching, str(i)))
        thread3.start()
        thread4 = threading.Thread(target=depth_stats, args=('https://www.espn.com/mlb/stats/team/_/view/pitching/season/' + str(i) + '/seasontype/3/table/pitching/sort/wins/dir/desc',
                                                             playoff_pitching, str(i)))
        thread4.start()
        thread5 = threading.Thread(target=depth_stats, args=('https://www.espn.com/mlb/stats/team/_/season/' + str(i) + '/seasontype/3',
                                                             playoff_hitting, str(i)))
        thread5.start()
        thread6 = threading.Thread(target=extra_stats, args=(extras, i))
        thread6.start()
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        thread5.join()
        thread6.join()
    big_frame = df_maker(big_data, labels)
    hitting_frame = df_maker(hitting, hit_labels)
    pitching_frame = df_maker(pitching, pitch_labels)
    pitching_frame = pitching_frame.drop('gp', 1)
    pitching_frame = pitching_frame.drop('W', 1)
    pitching_frame = pitching_frame.drop('L', 1)
    extras_frame = df_maker(extras, extra_labels)
    po_pitching_frame = df_maker(playoff_pitching, pitch_labels)
    po_hitting_frame = df_maker(playoff_hitting, hit_labels)
    big = pd.merge(pd.merge(big_frame, hitting_frame, on=['season', 'team']), pitching_frame, on=['season', 'team'])
    big = pd.merge(big, extras_frame, on=['season', 'team'])
    po_hitting_frame = po_hitting_frame.drop('gp', 1)
    big_po = pd.merge(po_pitching_frame, po_hitting_frame, on=['season', 'team'])
    stat_filler(conn, big_data, big)
    po_stat_filler(conn, big_po)


if __name__ == "__main__":
   pd.set_option("display.max_rows", None, "display.max_columns", None)
   try:
       connection = sqlite3.connect("var/mlb.sqlite3")
   except:
       print("Connection to database failed.")
       exit(1)
   db_setup(connection)
   stat_runner(connection)