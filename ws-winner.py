# -*- coding: utf-8 -*-
import sqlite3

winners = [
    [2013, 1],
    [2014, 28],
    [2015, 8],
    [2016, 25],
    [2017, 15],
    [2018, 1],
    [2019, 17],
    [2020, 26],
    [2021, 16],
]

connection = sqlite3.connect("var/mlb.sqlite3")
cur = connection.cursor()

for w in winners:
    cur.execute('''UPDATE seasons SET season_result = 6
                WHERE team = ? AND year = ?;''',
                (w[1], w[0]))
    connection.commit()