from pathlib import Path
import threading
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sb

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import utils


def df_construct():
    seasons = utils.season_grab()
    teams = utils.team_grab()
    bullpens = utils.bp_grab()
    bullpens['bpera'] = bullpens['era']
    bullpens = bullpens.drop('era', 1)
    bullpens['bp_wins'] = bullpens['wins']
    bullpens['bp_losses'] = bullpens['losses']
    bullpens['bp_ip'] = bullpens['ip']
    bullpens = bullpens.drop('wins', 1)
    bullpens = bullpens.drop('losses', 1)
    bullpens = bullpens.drop('ip', 1)
    bullpens['lobp'] = pd.to_numeric(bullpens['lobp'].str.replace("%", ""))
    teams['team'] = teams['id']
    big_df = pd.merge(teams, pd.merge(seasons, bullpens, on=['year', 'team', 'sv']), on=['team'])
    big_df['bpgp'] = big_df['gp'] - big_df['cg']
    big_df['sv/gp'] = big_df['sv']/big_df['bpgp']
    big_df['non_bp_losses'] = big_df['losses'] - big_df['bp_losses']
    return big_df


def bpera_era(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='era', y='bpera', hue='season_result', )
        ax.set_title('Total Era vs Bullpen ERA for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['era'], row['bpera']))
        plt.savefig('visuals/total-era-vs-bp-era-' + str(year) + '.png')


def bpera_wins(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='wins', y='bpera', hue='season_result', )
        ax.set_title('Wins vs Bullpen ERA for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['wins'], row['bpera']))
        plt.savefig('visuals/wins-vs-bp-era-' + str(year) + '.png') 


def bpera_svpgp(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='sv/gp', y='bpera', hue='season_result', )
        ax.set_title('Saves/GP vs Bullpen ERA for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['sv/gp'], row['bpera']))
        plt.savefig('visuals/svpgp-vs-bp-era-' + str(year) + '.png')     


def bp_era_lobp(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='lobp', y='bpera', hue='season_result', )
        ax.set_title('Left on Base (%) and ERA for MLB Bullpens in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['lobp'], row['bpera']))
        plt.savefig('visuals/lobp-vs-era-bp-' + str(year) + '.png') 


def loss_analysis(df):
    groups = df.groupby('year')
    for year, group in groups:
        x_plot = np.linspace(group['non_bp_losses'].min()-5, group['non_bp_losses'].max()+5, 1000)
        y_plot = np.linspace(group['bp_losses'].min()-5, group['bp_losses'].max()+5, 1000)
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='non_bp_losses', y='bp_losses', hue='season_result', )
        ax.set_title('Losses Bullpen is Responsible For, MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['non_bp_losses'], row['bp_losses']))
        plt.plot(x_plot, y_plot, color='r')
        plt.savefig('visuals/bp-losses-' + str(year) + '.png') 


if __name__ == "__main__":
    #bpera_era(df_construct())
    #bpera_wins(df_construct())
    #bpera_svpgp(df_construct())
    #bp_era_lobp(df_construct())
    #loss_analysis(df_construct())