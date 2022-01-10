import sqlite3
import pandas as pd
import os, sys

def team_grab():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(currentdir + "/var/mlb.sqlite3")
    return pd.read_sql_query("SELECT * FROM teams", conn)


def division_grab():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(currentdir + "/var/mlb.sqlite3")
    return pd.read_sql_query("SELECT * FROM divisions", conn)


def sr_grab():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(currentdir + "/var/mlb.sqlite3")
    return pd.read_sql_query("SELECT * FROM season_results", conn)


def ps_grab():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(currentdir + "/var/mlb.sqlite3")
    return pd.read_sql_query("SELECT * FROM postseasons", conn)


def season_grab():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(currentdir + "/var/mlb.sqlite3")
    return pd.read_sql_query("SELECT * FROM seasons", conn)   


def bp_grab():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(currentdir + "/var/mlb.sqlite3")
    return pd.read_sql_query("SELECT * FROM bullpens", conn) 


def pr_grab():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(currentdir + "/var/mlb.sqlite3")
    return pd.read_sql_query("SELECT * FROM payrolls", conn)     