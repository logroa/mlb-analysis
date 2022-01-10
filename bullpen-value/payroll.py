# -*- coding: utf-8 -*-
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
    payrolls = utils.pr_grab()
    bullpens['bp_era'] = bullpens['era']
    bullpens = bullpens.drop('era', 1)
    bullpens['bp_wins'] = bullpens['wins']
    bullpens['bp_losses'] = bullpens['losses']
    bullpens['bp_ip'] = bullpens['ip']
    bullpens['bp_war'] = bullpens['war']
    bullpens = bullpens.drop('wins', 1)
    bullpens = bullpens.drop('losses', 1)
    bullpens = bullpens.drop('ip', 1)
    bullpens = bullpens.drop('war', 1)
    bullpens['lobp'] = pd.to_numeric(bullpens['lobp'].str.replace("%", ""))
    teams['team'] = teams['id']
    big_df = pd.merge(teams, pd.merge(seasons, bullpens, on=['year', 'team', 'sv']), on=['team'])
    big_df = pd.merge(big_df, payrolls, on=['year', 'team'])
    big_df['bpgp'] = big_df['gp'] - big_df['cg']
    big_df['sv/gp'] = big_df['sv']/big_df['bpgp']
    big_df['non_bp_losses'] = big_df['losses'] - big_df['bp_losses']
    big_df['bp_payroll_perc'] = big_df['bullpen_payroll']/big_df['total_payroll']
    big_df['sp_payroll_perc'] = big_df['sp_payroll']/big_df['total_payroll']
    big_df['pp_payroll'] = big_df['total_payroll'] - big_df['sp_payroll'] - big_df['bullpen_payroll']
    big_df['pp_payroll_perc'] = big_df['pp_payroll']/big_df['total_payroll']
    big_df['bp/sp_pr'] = big_df['bullpen_payroll']/big_df['sp_payroll']
    return big_df


def bp_payroll(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='total_payroll', y='bullpen_payroll', hue='season_result', )
        ax.set_title('Proportion of Payroll towards Bullpen for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['total_payroll'], row['bullpen_payroll']))
        plt.savefig('visuals/prop-payroll-bp-' + str(year) + '.png') 
        
        
def perc_bppr_wins(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='wins', y='bp_payroll_perc', hue='season_result', )
        ax.set_title('Wins vs BP Payroll Dist for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['wins'], row['bp_payroll_perc']))
        plt.savefig('visuals/wins-bp-payroll-dist-' + str(year) + '.png')     


def perc_sppr_wins(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='wins', y='sp_payroll_perc', hue='season_result', )
        ax.set_title('Wins vs SP Payroll Dist for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['wins'], row['sp_payroll_perc']))
        plt.savefig('visuals/wins-sp-payroll-dist-' + str(year) + '.png')     


def perc_pppr_wins(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='wins', y='pp_payroll_perc', hue='season_result', )
        ax.set_title('Wins vs PP Payroll Dist for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['wins'], row['pp_payroll_perc']))
        plt.savefig('visuals/wins-pp-payroll-dist-' + str(year) + '.png') 


def perc_bpsp_wins(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='wins', y='bp/sp_pr', hue='season_result', )
        ax.set_title('Wins vs BP/SP Payroll Dist for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['wins'], row['bp/sp_pr']))
        plt.savefig('visuals/wins-bpsp-payroll-dist-' + str(year) + '.png') 
        

def perc_bpsp_era(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='era', y='bp/sp_pr', hue='season_result', )
        ax.set_title('ERA vs BP/SP Payroll Dist for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['era'], row['bp/sp_pr']))
        plt.savefig('visuals/era-bpsp-payroll-dist-' + str(year) + '.png') 


def bp_payroll_war(df):
    groups = df.groupby('year')
    for year, group in groups:
        fig, ax = plt.subplots()
        sb.scatterplot(data=group, x='bullpen_payroll', y='bp_war', hue='season_result', )
        ax.set_title('BP Payroll vs WAR for MLB Teams in ' + str(year))
        for idx, row in group.iterrows():
            ax.annotate(row['abbr'], (row['bullpen_payroll'], row['bp_war']))
        plt.savefig('visuals/bp-payroll-war-' + str(year) + '.png')


if __name__ == '__main__':
    #bp_payroll(df_construct())
    #perc_bppr_wins(df_construct())
    #perc_sppr_wins(df_construct())
    #perc_pppr_wins(df_construct())
    #perc_bpsp_wins(df_construct())
    #perc_bpsp_era(df_construct())
    bp_payroll_war(df_construct())