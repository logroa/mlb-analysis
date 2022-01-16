# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sb

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import utils

def grapher(df, x, y, tit, fil):
    #groups = df.groupby('year')
    #for year, group in groups:
    fig, ax = plt.subplots()
    sb.scatterplot(data=df, x=x, y=y)
    ax.set_title(tit)
    #for idx, row in df.iterrows():
    #    ax.annotate(str(row['year']) + ' ' + row['abbr'], (row['Composite Value'], row['PR Composite Value']))
    
    subfolder_path = os.path.join(os.getcwd(), 'visuals/report')

    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)
    
    file_path = os.path.join(subfolder_path, fil + '.png')

    plt.savefig(file_path)


seasons = utils.season_grab()
teams = utils.team_grab()
bullpens = utils.bp_grab()
payrolls = utils.pr_grab()

bullpens['bp_era'] = bullpens['era']
bullpens = bullpens.drop('era', 1)
bullpens['bp_wins'] = bullpens['wins']
bullpens['bp_losses'] = bullpens['losses']
bullpens['bp_ip'] = bullpens['ip']
bullpens = bullpens.drop('wins', 1)
bullpens = bullpens.drop('losses', 1)
bullpens = bullpens.drop('ip', 1)
bullpens['lobp'] = pd.to_numeric(bullpens['lobp'].str.replace("%", ""))
bullpens['gbp'] = pd.to_numeric(bullpens['gbp'].str.replace("%", ""))
bullpens['hrpfb'] = pd.to_numeric(bullpens['hrpfb'].str.replace("%", ""))

big_df = pd.merge(seasons, pd.merge(bullpens, payrolls, on=['year','team']), on=['year','team'])
teams['team'] = teams['id']
big_df = pd.merge(big_df, teams, on=['team'])

big_df['er'] = pd.to_numeric(big_df['er'])
big_df['bp_era'] = pd.to_numeric(big_df['bp_era'])
big_df['bp_ip'] = pd.to_numeric(big_df['bp_ip'])
big_df['ip'] = pd.to_numeric(big_df['ip'].str.replace(',', ''))

big_df['sp_era'] = round(9*((big_df['er'] - ((big_df['bp_era']/9)*big_df['bp_ip']))/(big_df['ip']-big_df['bp_ip'])), 2)

big_df['bpgp'] = big_df['gp'] - big_df['cg']
big_df['sv'] = big_df['sv_x']
big_df['sv/gp'] = big_df['sv']/big_df['bpgp']
big_df['bpw/w'] = big_df['bp_wins']/big_df['wins']
big_df['bpl/l'] = big_df['bp_losses']/big_df['losses']
big_df['non_bp_losses'] = big_df['losses'] - big_df['bp_losses']
big_df['bp_payroll_perc'] = big_df['bullpen_payroll']/big_df['total_payroll']
big_df['sp_payroll_perc'] = big_df['sp_payroll']/big_df['total_payroll']
big_df['pp_payroll'] = big_df['total_payroll'] - big_df['sp_payroll'] - big_df['bullpen_payroll']
big_df['pp_payroll_perc'] = big_df['pp_payroll']/big_df['total_payroll']
big_df['bp/sp_pr'] = big_df['bullpen_payroll']/big_df['sp_payroll']

reduced = pd.concat(
    [big_df['year'], big_df['abbr'], big_df['bpgp'], big_df['bp_wins'], big_df['bp_losses'], big_df['bp_ip'], big_df['sv'], big_df['bp_era'], big_df['sp_era'] - big_df['bp_era'],
     big_df['bullpen_payroll'], big_df['bullpen_payroll']/big_df['total_payroll'], big_df['total_payroll'], big_df['lobp'], big_df['bbp9'],
     big_df['kp9'], big_df['gbp'], big_df['hrpfb'], big_df['sv/gp'], big_df['bpw/w'], big_df['bpl/l'], big_df['war']],
    axis=1,
    keys= [
    'year', 'abbr', 'bpgp', 'bp_ip', 'bp_wins', 'bp_losses', 'sv', 'bp_era', 'era_diff', 'bullpen_payroll', 'bullpen_marketshare', 'team_marketshare', 'lobp',
    'bbp9', 'kp9', 'gbp', 'hrpfb', 'sv/gp', 'bpw/w', 'bpl/l', 'war'
    ]
)

# no 2020
indexes = reduced[ reduced['year'] == 2020 ].index
reduced.drop(indexes, inplace = True)
reduced = reduced.reset_index()
reduced = reduced.drop('index', 1)

# scale money separated by year
# don't like scaling from min 0 to max 1, to minimize difference, think we need 0 0 to max 1
x = pd.DataFrame()
groups = reduced.groupby('year')
for key, group in groups:
    temp = pd.concat(
        [group['year'], group['abbr'], (group['bullpen_marketshare']*group['team_marketshare'].max())/group['team_marketshare'],
         group['bullpen_payroll']/group['bullpen_payroll'].max(), ],
        axis=1
    )
    x = x.append(temp, ignore_index=True)
x = x.rename({0: 'scale', 'bullpen_payroll': 'bp_scale'}, axis=1)
reduced = pd.merge(reduced, x, on=['year','abbr'])

payroll = reduced

money = reduced[['year', 'abbr', 'bullpen_payroll']]

tested_vars = ['bpgp', 'bp_ip', 'sv', 'bp_era', 'era_diff',  'lobp',
    'bbp9', 'kp9', 'gbp', 'hrpfb', 'sv/gp', 'bpw/w', 'bpl/l', 'bp_wins', 'bp_losses']

# no payroll scaling

scaler = preprocessing.MinMaxScaler()

no_names = reduced.loc[:, ~reduced.columns.isin(['year', 'abbr'])]
labs = no_names.columns
sc = scaler.fit_transform(no_names)
added = pd.DataFrame(sc, columns=labs)
scaled_df = pd.concat(
    [reduced[['year', 'abbr']], added],
    axis=1
)

scaled_reduced = scaled_df.drop(['bullpen_payroll', 'bullpen_marketshare', 'team_marketshare'], 1)
neg_vals = ['bp_losses', 'bp_era', 'bbp9', 'bpl/l', 'hrpfb', 'lobp']
for n in neg_vals:
    scaled_reduced[n] = 1 - scaled_reduced[n]

var_r2 = {}
total_r2 = 0

# need better variable incorporating saves and wins

lin_models_coefs = {}

for v in tested_vars:
    lin_reg = LinearRegression()
    x_train, x_test, y_train, y_test = train_test_split(scaled_reduced[v], scaled_reduced['war'], test_size=.3, random_state=19)
    
    x_train = x_train.values.reshape(-1, 1)
    x_test = x_test.values.reshape(-1, 1)
    y_train = y_train.values.reshape(-1, 1)
    y_test = y_test.values.reshape(-1, 1)
    
    lin_reg.fit(x_train, y_train)
    y_pred = lin_reg.predict(x_test)
    r2 = r2_score(y_test, y_pred)
    var_r2[v] = r2
    total_r2 += r2
    
    lin_models_coefs[v] = lin_reg.coef_[0][0]

# do i include war_scaled in my calculation or not?
#tested_vars.append('war_scaled')
#var_r2['war_scaled'] = 1
#lin_models_coefs['war_scaled'] = 1
#total_r2 += 1

# do i include coefs in this calculation or not?
scaled_reduced['Composite Value'] = scaled_reduced['year'] - scaled_reduced['year']
for v in tested_vars:
    scaled_reduced['Composite Value'] += scaled_reduced[v]*var_r2[v]#*lin_models_coefs[v]
scaled_reduced['Composite Value'] = scaled_reduced['Composite Value']/total_r2

scaled_reduced.sort_values(by=['Composite Value'], inplace=True, ascending=False)

# payroll scaling

payroll['war_shifted'] = payroll['war'] + abs(payroll['war'].min()) + 1
payroll['war_scaled'] = payroll['war_shifted']/payroll['bp_scale']

for v in tested_vars:
    payroll[v] = payroll[v]/payroll['bp_scale']

scaler = preprocessing.MinMaxScaler()

no_names = payroll.loc[:, ~payroll.columns.isin(['year', 'abbr'])]
labs = no_names.columns
sc = scaler.fit_transform(no_names)
added = pd.DataFrame(sc, columns=labs)
pr_scaled_df = pd.concat(
    [payroll[['year', 'abbr']], added],
    axis=1
)

pr_scaled_reduced = pr_scaled_df.drop(['bullpen_payroll', 'bullpen_marketshare', 'team_marketshare', 'war_shifted', 'war'], 1)
neg_vals = ['bp_losses', 'bp_era', 'bbp9', 'bpl/l', 'hrpfb', 'lobp']
for n in neg_vals:
    pr_scaled_reduced[n] = 1 - pr_scaled_reduced[n]

pr_var_r2 = {}
pr_total_r2 = 0

# need better variable incorporating saves and wins

pr_lin_models_coefs = {}

for v in tested_vars:
    lin_reg = LinearRegression()
    x_train, x_test, y_train, y_test = train_test_split(pr_scaled_reduced[v], pr_scaled_reduced['war_scaled'], test_size=.3, random_state=19)
    
    x_train = x_train.values.reshape(-1, 1)
    x_test = x_test.values.reshape(-1, 1)
    y_train = y_train.values.reshape(-1, 1)
    y_test = y_test.values.reshape(-1, 1)
    
    lin_reg.fit(x_train, y_train)
    y_pred = lin_reg.predict(x_test)
    r2 = r2_score(y_test, y_pred)
    pr_var_r2[v] = r2
    pr_total_r2 += r2
    
    pr_lin_models_coefs[v] = lin_reg.coef_[0][0]

# do i include war_scaled in my calculation or not?
#tested_vars.append('war_scaled')
#var_r2['war_scaled'] = 1
#lin_models_coefs['war_scaled'] = 1
#total_r2 += 1

# do i include coefs in this calculation or not?
pr_scaled_reduced['PR Composite Value'] = pr_scaled_reduced['year'] - pr_scaled_reduced['year']
for v in tested_vars:
    pr_scaled_reduced['PR Composite Value'] += pr_scaled_reduced[v]*pr_var_r2[v]#*lin_models_coefs[v]
pr_scaled_reduced['PR Composite Value'] = pr_scaled_reduced['PR Composite Value']/pr_total_r2

pr_scaled_reduced.sort_values(by=['PR Composite Value'], inplace=True, ascending=False)

scaled_reduced = scaled_reduced.reset_index()
pr_scaled_reduced = pr_scaled_reduced.reset_index()

scaled_reduced['Composite Rank'] = scaled_reduced['Composite Value'].rank(ascending = False)
pr_scaled_reduced['PR Composite Rank'] = pr_scaled_reduced['PR Composite Value'].rank(ascending = False)

huge = pd.merge(scaled_reduced, pr_scaled_reduced, on=['year', 'abbr'])
huge = pd.merge(huge, reduced, on=['year', 'abbr'])
deliv = pd.concat(
    [huge[['year', 'abbr', 'bullpen_payroll', 'Composite Value', 'Composite Rank', 'PR Composite Value', 'PR Composite Rank']]],
    axis=1
)

deliv['PR Difference'] = deliv['Composite Rank'] - deliv['PR Composite Rank']
deliv['Composite Difference'] = deliv['PR Composite Value'] - deliv['Composite Value']
deliv['Improvement'] = np.where((deliv['Composite Difference'] > 0), 1, 0)
deliv.sort_values(by=['PR Composite Value'], inplace=True, ascending=False)
deliv = deliv.reset_index()

grapher(deliv, 'bullpen_payroll', 'Composite Value', 'BP Payroll vs Composite Score', 'bp-payroll-vs-composite-score')
grapher(deliv, 'bullpen_payroll', 'PR Composite Value', 'BP Payroll vs PR Composite Score', 'bp-payroll-vs-pr-composite-score')