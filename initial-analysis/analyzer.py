from pathlib import Path
import threading
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import utils


def pythagorean_wins_calc(seasons):
    seasons["runs_allowed"] = seasons["runs"] - seasons["run_diff"]
    seasons["expected_wins"] = seasons["gp"]*(seasons["runs"]**1.81 / (seasons["runs"]**1.81 + seasons["runs_allowed"]**1.81))
    seasons["win_diff"] = seasons["wins"] - seasons["expected_wins"]


def season_setup():
    seasons = utils.season_grab()
    teams = utils.team_grab()
    teams['team'] = teams['id']
    seasons = pd.merge(seasons, teams, on=['team'])
    divisions = utils.division_grab()
    divisions['division'] = divisions['id']
    seasons = pd.merge(seasons, divisions, on=['division'])
    return seasons


def expected_wins(year):
    seasons = season_setup()
    pythagorean_wins_calc(seasons)
    #non2020 = seasons.loc[seasons["year"] != 2020]
    #plt.plot(seasons["era"], seasons["sv"], 'o')
    #divwins = non2020.groupby(['year', 'division'])['wins'].agg('sum').reset_index()
    #colors = np.where(non2020["division"] <= 3, 'b', 'y')
    #print(divwins)
    #divwins.plot.scatter(x='year', y='wins', c=colors)
    #non2020.plot.scatter(x='wins', y='win_diff', c=colors)
    #non2020.plot.scatter(x='runs', y='lob', c=colors)
    #non2020.plot.scatter(x='wins', y='runs', c=colors)
    #non2020['r/w'] = non2020['runs']/non2020['wins']
    #non2020['r/g'] = non2020['runs']/non2020['gp'] 
    #non2020.plot.scatter(x='r/g', y='r/w', c=colors)
    dyear = seasons.loc[seasons["year"] == year]
    colors_year = np.where(dyear["division"] <= 3, 'b', 'y')
    
    fig, ax = plt.subplots()
    ax.scatter(x=dyear['wins'], y=dyear['win_diff'], c=colors_year)
    ax.set_xlabel('Wins in ' + str(year) + ' Season')
    ax.set_ylabel('Wins over Expected by Pythagorean Expectation')
    ax.set_title('MLB Wins Compared to Pythagorean Expectation (' + str(year) + ')')
    for idx, row in dyear.iterrows():
        ax.annotate(row['abbr'], (row['wins'], row['win_diff']))
    plt.savefig('visuals/wins-over-expected' + str(year) + '.png')


def sv_winsoverexpected(dyear, year, colors_year):
    fig, ax = plt.subplots()
    ax.scatter(x=dyear['sv'], y=dyear['win_diff'], c=colors_year)
    ax.set_xlabel('Saves in ' + str(year) + ' Season')
    ax.set_ylabel('Wins over Expected by Pythagorean Expectation')
    ax.set_title('MLB Saves Compared to Pythagorean Expectation (' + str(year) + ')')
    for idx, row in dyear.iterrows():
        ax.annotate(row['abbr'], (row['sv'], row['win_diff']))
    plt.savefig('visuals/saves-compared-to-wins-ovver-expected' + str(year) + '.png')


def svperwin_winsoverexpected(dyear, year, colors_year):
    fig, ax = plt.subplots()
    ax.scatter(x=dyear['sv/w'], y=dyear['win_diff'], c=colors_year)
    ax.set_xlabel('Saves Per Win in ' + str(year) + ' Season')
    ax.set_ylabel('Wins over Expected by Pythagorean Expectation')
    ax.set_title('MLB Saves/Win Compared to Pythagorean Expectation (' + str(year) + ')')
    for idx, row in dyear.iterrows():
        ax.annotate(row['abbr'], (row['sv/w'], row['win_diff']))
    plt.savefig('visuals/saves-per-win-compared-to-wins-ovver-expected' + str(year) + '.png')


def save_analysis(year):
    seasons = season_setup()
    pythagorean_wins_calc(seasons)
    seasons['sv/w'] = seasons['sv']/seasons['wins']
    dyear = seasons.loc[seasons["year"] == year]
    colors_year = np.where(dyear["division"] <= 3, 'b', 'y')
    
    sv_winsoverexpected(dyear, year, colors_year)
    svperwin_winsoverexpected(dyear, year, colors_year)    


if __name__ == '__main__':
    for i in range(2013,2022):
        expected_wins(i)
        save_analysis(i)