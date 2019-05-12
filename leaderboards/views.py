from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
import json
import requests
import mysql.connector
from ppl.settings import sql_options, SECRET_API_KEY

def home(request):
    cnx = mysql.connector.connect(**sql_options)
    cursor = cnx.cursor(prepared=True)

    stmt = 'SELECT * FROM teams WHERE id != 10 ORDER BY mmr DESC'
    cursor.execute(stmt)
    column_names = cursor.column_names
    rows = cursor.fetchall()
    teams = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    cnx.close()

    for team in teams:
        # Calculate the series win percentage.
        if team['series_won'] == 0:
            team['win_percent'] = 0
        elif team['series_played'] == 0:
            team['win_percent'] == '-'
        else:
            team['win_percent'] = round((team['series_won'] / team['series_played']) * 100)

    return render(request, 'leaderboards/home.html', {'teams': teams})

def teams(request):
    cnx = mysql.connector.connect(**sql_options)
    cursor = cnx.cursor(prepared=True)

    stmt = 'SELECT * FROM teams WHERE id != 10 ORDER BY mmr DESC'
    cursor.execute(stmt)
    column_names = cursor.column_names
    rows = cursor.fetchall()
    teams = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    cnx.close()

    for team in teams:
        # Calculate the series win percentage
        if team['series_won'] == 0:
            team['win_percent'] = 0
        elif team['series_played'] == 0:
            team['win_percent'] == '-'
        else:
            team['win_percent'] = round((team['series_won'] / team['series_played']) * 100)

    return render(request, 'leaderboards/teams.html', {'teams': teams})

def team_detail(request, id):
    cnx = mysql.connector.connect(**sql_options)
    cursor = cnx.cursor(prepared=True)

    # Get the team.
    stmt = 'SELECT * FROM teams WHERE id = ?'
    cursor.execute(stmt, (id,))
    column_names = cursor.column_names
    row = cursor.fetchone()
    result = dict(zip(column_names, row))

    # Set the rank variable to 0.
    stmt = 'SET @rank := 0'
    cursor.execute(stmt)

    # Select all teams with this rank. WHERE id != 10 for discarding Wowzers.
    stmt = 'SELECT teams.*, @rank := @rank + 1 AS rank FROM teams WHERE id != 10 ORDER BY mmr DESC'
    cursor.execute(stmt)
    column_names = cursor.column_names
    rows = cursor.fetchall()
    teams = [dict(zip(column_names, row)) for row in rows]

    #Select roster
    stmt = 'SELECT * FROM players WHERE team = ?'
    cursor.execute(stmt, (result['id'],))
    column_names = cursor.column_names
    rows = cursor.fetchall()
    roster = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    cnx.close()

    teams = [t for t in teams if t['id'] == id][0]
    result['rank'] = teams['rank']

    # Calculate the series win percentage
    if result['series_won'] == 0:
        result['win_percent'] = 0
    elif result['series_played'] == 0:
        result['win_percent'] == '-'
    else:
        result['win_percent'] = round((result['series_won'] / result['series_played']) * 100)

    return render(request, 'leaderboards/team_detail.html', {'team': result, 'roster': roster})

def players(request):
    cnx = mysql.connector.connect(**sql_options)
    cursor = cnx.cursor(prepared=True)

    stmt = 'SELECT * FROM players WHERE team != 10 ORDER BY score DESC'
    cursor.execute(stmt)
    column_names = cursor.column_names
    rows = cursor.fetchall()
    players = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    cnx.close()
    
    #Calculate the goals percentage
    for player in players:
        if player['goals'] == 0:
            player['goal_percent'] = 0
        elif player['shots'] == 0:
            player['goal_percent'] == '-'
        else:
            player['goal_percent'] = round((player['goals'] / player['shots']) * 100)

    return render(request, 'leaderboards/players.html', {'players': players})

def player_detail(request, id):
    cnx = mysql.connector.connect(**sql_options)
    cursor = cnx.cursor(prepared=True)

    # Get the player
    stmt = 'SELECT * FROM players WHERE id = ?'
    cursor.execute(stmt, (id,))
    column_names = cursor.column_names
    row = cursor.fetchone()
    result = dict(zip(column_names, row))

    # Set the rank variable to 0
    stmt = 'SET @rank := 0'
    cursor.execute(stmt)

    # Select all players with this rank. WHERE team != 10 for discarding Wowzers
    stmt = 'SELECT players.*, @rank := @rank + 1 AS rank FROM players WHERE team != 10 ORDER BY score DESC'
    cursor.execute(stmt)
    column_names = cursor.column_names
    rows = cursor.fetchall()
    players = [dict(zip(column_names, row)) for row in rows]

    # Set the team_rank variable to 0
    stmt = 'SET @team_rank := 0'
    cursor.execute(stmt)

    # Select all teams with this rank WHERE team != 10 for discarding Wowzers.
    stmt = 'SELECT teams.*, @team_rank := @team_rank + 1 AS team_rank FROM teams WHERE id != 10 ORDER BY mmr DESC'
    cursor.execute(stmt)
    column_names = cursor.column_names
    rows = cursor.fetchall()
    teams = [dict(zip(column_names, row)) for row in rows]

    #Select teammates
    stmt = 'SELECT * FROM players WHERE team = ? and id != ?'
    cursor.execute(stmt, (result['team'], id,))
    column_names = cursor.column_names
    rows = cursor.fetchall()
    teammates = [dict(zip(column_names, row)) for row in rows]

    # Get the team
    stmt = 'SELECT * FROM teams WHERE id = ?'
    cursor.execute(stmt, (result['team'],))
    column_names = cursor.column_names
    row = cursor.fetchone()
    team = dict(zip(column_names, row))

    cursor.close()
    cnx.close()

    players = [p for p in players if p['id'] == id][0]
    result['rank'] = players['rank']

    teams = [t for t in teams if t['id'] == result['team']][0]
    team['rank'] = teams['team_rank']

    #Calculate the goals percentage
    if result['goals'] == 0:
        result['goal_percent'] = 0
    elif result['shots'] == 0:
        result['goal_percent'] == '-'
    else:
        result['goal_percent'] = round((result['goals'] / result['shots']) * 100)

    # Calculate the series win percentage
    if team['series_won'] == 0:
        team['win_percent'] = 0
    elif team['series_played'] == 0:
        team['win_percent'] == '-'
    else:
        team['win_percent'] = round((team['series_won'] / team['series_played']) * 100)

    return render(request, 'leaderboards/player_detail.html', {'player': result, 'teammates': teammates,'team': team})