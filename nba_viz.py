# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 21:44:55 2020

@author: tyler
"""

from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import commonplayerinfo, commonteamroster, shotchartdetail
# from nba_api.stats.library.parameters import SeasonYear
from collections import OrderedDict
import datetime

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
from adjustText import adjust_text
import imageio
import os

import pandas as pd
import numpy as np

stats = np.array(['Fave Shots',
         '   Fave Shots by Qtr',
         'Highest Efficiency Shots',
         # '   Highest Efficiency Shots by Qtr',
         'Shot Chart',
         '   Shot Chart by Qtr',
         ])

# missing headers?
headers = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'
}

# fns list and fn switchboard
def available_stats():
    return stats


def fn_handler(fn_name,group_type,group,shots):
    # General plot parameters
    mpl.rcParams['font.family'] = 'MS Gothic'
    mpl.rcParams['font.size'] = 10
    mpl.rcParams['axes.linewidth'] = 2
    
    # get shot chart for group
    if group_type == 'plyr':
        chart = get_player_chart(group)
    elif group_type == 'team':
        chart = get_team_chart((get_team_id(group)))
    else:
        chart=0
    
    switcher={stats[0]:favorite_shots,
              stats[1]:favorite_shots_by_qtr,
              stats[2]:highest_eff_shots, # stats[3]:highest_eff_shots_by_qtr,
              stats[3]:shot_chart,
              stats[4]:shot_chart_by_qtr,
              }
    if fn_name in stats[0:3]:
        params = [chart,group,group_type,shots]
    else:
        params = [chart,group,group_type]
    func = switcher.get(fn_name,lambda: 'Stat DNE')
    return func(*params)

# dropdown generators / name and id getters
def get_nba_season():
    if datetime.datetime.now().month >= 10:
        start_year = datetime.datetime.today().year
        end_year = start_year + 1
    else:
        end_year = datetime.datetime.today().year
        start_year = end_year - 1
    # start_years = list(range(start_year,1945,-1))
    # start_years = [str(yr) for yr in start_years]
    # end_years = list(range(end_year, 1946, -1))
    # end_years = [str(yr) for yr in end_years]
    # seasons = [i + '-' + j[2:4] for i, j in zip(start_years, end_years)] 
    # return seasons
    season = str(start_year) + '-' + str(end_year)[2:4]
    return season

year = get_nba_season()

def get_team_id(key):
    team_dict = teams.get_teams()
    team = [team for team in team_dict if team['abbreviation'] == key or team['city'] == key or
            team['full_name'] == key or team['nickname'] == key or team['state'] == key][0]
    return team['id']

def get_all_team_ids():
    team_dict = teams.get_teams()
    team_names = [sub['full_name'] for sub in team_dict]
    team_ids = [sub['id'] for sub in team_dict] 
    team_dict = dict(zip(team_names, team_ids))
    
    sorted_names = sorted(team_dict.keys(), key=lambda x:x.lower())
    sorted_ids = []
    for i in sorted_names:
        value=team_dict[i]
        sorted_ids.append(value)
    return tuple(zip(sorted_names,sorted_ids)) # list of tuples

def get_team_name(key):
    team_dict = teams.get_teams()
    team_names = [sub['full_name'] for sub in team_dict]
    team_ids = [sub['id'] for sub in team_dict] 
    team_dict = dict(zip(team_ids, team_names))
    return team_dict[key]
    
def get_all_team_names():
    '''
    Returns
    -------
    list of strings
        list of team names

    '''
    all_team_ids = OrderedDict(get_all_team_ids())
    return [key for key in all_team_ids.keys()] # keys for team id dict

def get_player_id(key, active = 0):
    '''
    Parameters
    ----------
    key : string
        a name (first, last, or full)
    active : int, optional
        0: all players, 1: active players, else: inactive players. The default is 0.

    Returns
    -------
    if one player:
    int
        the player's id
    more than one player:
    dict
        player_name:player_id

    '''
    # define search range
    key = key.lower()
    if active == 0:
        player_dict = players.get_players()
    elif active == 1:
        player_dict = players.get_active_players()
    else:
        player_dict = players.get_inactive_players()
    player = [player for player in player_dict if player['first_name'].lower() == key or 
              player['last_name'].lower() == key or
              player['full_name'].lower() == key]
    # if only 1 player, drop list wrapper and return id
    if len(player) == 1: 
        return player[0]['id']
    # if multiple players, return dictionary with name and id
    else:
        player_names = [sub['full_name'] for sub in player]
        player_ids = [sub['id'] for sub in player] 
        return dict(zip(player_names, player_ids))

def get_all_player_ids(team_name):
    '''
    Parameters
    ----------
    team_name : string
        The name of the team
    Returns
    -------
    dict of player_name:player_id for all players on a team

    '''
    all_team_ids = OrderedDict(get_all_team_ids()) # dict of team names: IDs; maintain alphabetical order for shot chart
    team_id = all_team_ids[team_name]
    team_rost = commonteamroster.CommonTeamRoster(team_id,
                                                  # headers=headers
                                                  ).common_team_roster.get_data_frame()
    team_player_ids = team_rost['PLAYER_ID']
    team_player_names = team_rost['PLAYER']
    return dict(zip(team_player_names,team_player_ids))

def get_all_player_names():
    # player_dict = players.get_players()
    player_dict = players.get_active_players()
    # player_f_names = [sub['full_name'].split(" ",1)[0] for sub in player_dict]
    # player_l_names = [sub['full_name'].split(" ",1)[1] if len(sub['full_name'].split(" ",1)) > 1
    #                   else '' for sub in player_dict]
    # player_names = [last + ', ' + first for first,last in zip(player_f_names,player_l_names)]
    # return player_names
    player_full_names = [sub['full_name'] for sub in player_dict]
    return player_full_names

def get_player_team_id(key):
    if type(key) is str:
        key=get_player_id(key)
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=key,
                                                    # headers=headers
                                                    ).common_player_info.get_data_frame()
    return player_info['TEAM_ID'][0]


# shot chart getters
def get_player_chart(full_name, measure = 'FGA'):
    return shotchartdetail.ShotChartDetail(get_player_team_id(full_name),
                                           get_player_id(full_name),
                                           # season_nullable = '2018-19',
                                           # headers=headers,
                                           context_measure_simple = measure).shot_chart_detail.get_data_frame()

def get_team_chart(team_id,measure = 'FGA'):
    # setting player_id 
    return shotchartdetail.ShotChartDetail(team_id = team_id,
                                           player_id = 0,
                                           # season_nullable = season,
                                           # headers=headers,
                                           context_measure_simple = measure).shot_chart_detail.get_data_frame()

def add_bins(data):
    # first, need to bin x and y in 25 by 25 bins (will be a 20 x 20 grid)
    x_bins = np.arange(-250,260,25)
    y_bins = np.arange(-50,460,25)
    data['BIN_X'] = pd.cut(data['LOC_X'],bins=x_bins,include_lowest=True)
    data['BIN_Y'] = pd.cut(data['LOC_Y'],bins=y_bins,include_lowest=True)
    # then, find make % and count for each bin (take mean of SHOT_MADE_FLAG for each bin)
    bin_pct = data.groupby(['BIN_X', 'BIN_Y'])['SHOT_MADE_FLAG'].mean().dropna()
    bin_ct = data.groupby(['BIN_X', 'BIN_Y'])['SHOT_ATTEMPTED_FLAG'].sum().dropna()
    data = data.set_index(['BIN_X','BIN_Y']) # set index so new cols can be added accor. to index
    data['BIN_PCT'] = bin_pct
    data['BIN_CT'] = bin_ct
    data = data.reset_index(0).reset_index(0)
    # only keep 1 shot per bin
    data = data.sort_values(by=['BIN_CT','LOC_Y'], ascending = False)
    data = data.drop_duplicates(subset=['BIN_X','BIN_Y'], keep="first")
    # label zones frequent/infrequent based on if ct > median ct/5
    # use player/team's median shots from zone as cutoff if infrequent shooter
    if np.median(data['BIN_CT']) < 5:
        data['FREQ_FLAG'] = data['BIN_CT'] > np.median(data['BIN_CT'])
    # otherwise use 5 for cutoff
    else:
        data['FREQ_FLAG'] = data['BIN_CT'] >= 5
    data = data.loc[data['FREQ_FLAG'] == True] # filter out low freq shots
    
    # convert SHOT_TYPE to num
    to_nums = {"SHOT_TYPE": {"2PT Field Goal": 2, "3PT Field Goal": 3}}
    data.replace(to_nums, inplace=True)
    # multiply each bin by shot type (2 or 3) -> expected val for each bin
    data['ZONE_VALUE'] = data['SHOT_TYPE'] * data['BIN_PCT']
    
    return data

# coloring fns
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def colormap_maker(rgb):
    N = 256
    vals = np.ones((N, 4))
     # divide by 256 b/c mpl requires RGBA btwn 0 and 1
    vals[:, 0] = np.linspace(237/256, rgb[0]/256,N)
    vals[:, 1] = np.linspace(237/256, rgb[1]/256, N)
    vals[:, 2] = np.linspace(237/256, rgb[2]/256, N)
    newcmp = ListedColormap(vals)
    return newcmp

def colormap_maker2(rgb1,rgb2):
    N = 256
    vals = np.ones((N, 4))
     # divide by 256 b/c mpl requires RGBA btwn 0 and 1
    vals[:, 0] = np.linspace(rgb1[0]/256, rgb2[0]/256, N)
    vals[:, 1] = np.linspace(rgb1[1]/256, rgb2[1]/256, N)
    vals[:, 2] = np.linspace(rgb1[2]/256, rgb2[2]/256, N)
    newcmp = ListedColormap(vals)
    return newcmp

# define teamColors for charts
teamNames = get_all_team_names()
# lighter/main color first, darker color sexond
teamColors = [('#e03a3e','#26282a','#c1d32f',), # hawks
              ('#008348','#bb9753'), # celts
              ('#000000','#fefefe'), # nets
              ('#00788c','#1d1160'), # hornets
              ('#ce1141','#000000'), # bulls
              ('#6f263d','#ffb81c'), # cavs
              ('#0053bc','#00285e'), # mavs
              ('#0e2240','#fec524'), # nugs
              ('#c8102e','#bec0c2','#1d428a',), # pistons
              ('#006bb6','#fdb927'), # warriors
              ('#ce1141','#c4ced4'), # rockets
              ('#002d62','#fdbb30'), # pacers
              ('#000000','#bec0c2','#1d428a','#c8102e'), # clips
              ('#552583','#fdb927'), # lakeshow
              ('#5d76a9','#12173f'), # grizz
              ('#98002e','#000000'), # heat
              ('#00471b','#eee1c6'), # bucks
              ('#78be20','#0c2340'), # wolves
              ('#002b5c','#b4975a'), # pels
              ('#f58426','#006bb6'), # knicks
              ('#ef3b24','#007ac1'), # thunder
              ('#0077c0','#000000'), # magic
              ('#006bb6','#c4ced4'), # 6ers
              ('#e56020','#1d1160'), # suns
              ('#e03a3e','#000000'), # blazers
              ('#5a2b81','#63727a'), # kings
              ('#000000','#c4ced4'), # spurs
              ('#ce1141','#000000'), # raps
              ('#002b5c','#f9a01b'), # jazz
              ('#002b5c','#e31837','#c4ced4') # wizARds
              ]
teamColorDict = dict(zip(teamNames,teamColors))

teamColorMaps = [colormap_maker(hex_to_rgb(c[0])) for c in teamColors]
teamColorMapDict = dict(zip(teamNames,teamColorMaps))

def get_team_color(team_name):
    color = teamColorDict[team_name][0]
    return color

def get_player_color(player_name):
    team_id = get_player_team_id(player_name)
    team_name = get_team_name(team_id)
    color = get_team_color(team_name)
    return color

def get_team_colormap(team_name):
    colors = teamColorMapDict[team_name]
    return colors

def get_player_colormap(player_name):
    team_id = get_player_team_id(player_name)
    team_name = get_team_name(team_id)
    colors = get_team_colormap(team_name)
    return colors

# plotters
def draw_court(ax,color,alpha=0.5):
    # Short corner 3PT lines
    ax.plot([-220, -220], [0, 140], linewidth=2, color=color,alpha=alpha)
    ax.plot([220, 220], [0, 140], linewidth=2, color=color,alpha=alpha)
    # 3PT Arc
    ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0,
                                  theta2=180, facecolor='none', edgecolor=color, lw=2,alpha=alpha))
    # Lane and Key
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color,alpha=alpha)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color,alpha=alpha)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color,alpha=alpha)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color,alpha=alpha)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color,alpha=alpha)
    ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2,alpha=alpha))
    
    # Rim
    ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=1.5,alpha=alpha))  
    # Backboard
    ax.plot([-30, 30], [40, 40], linewidth=1.5, color=color,alpha=alpha)
    
    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])
    # Set axis limits
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)
    
def favorite_shots(data,title,group,n=10):
    fig = plt.figure(figsize=(4, 3.76),dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    draw_court(ax, 'black')
    ax.text(0.02, 0.95, title + ' ' + str(n) + ' Most Frequent Shots ' + year,
            transform=ax.transAxes, ha='left', va='baseline')
    # bin data
    data = add_bins(data)
    # find n most frequent shots
    data = data.head(n)
    # add labels
    texts = []
    for index, row in data.iterrows():
        if -60 <= row['LOC_X'] < 60 and -50 <= row['LOC_Y'] <= 80 :
            fs1 = 5
        else:
            fs1 = 7
        x = row['LOC_X']
        y = row['LOC_Y']
        texts.append(ax.text(x,y  + 60, str(int(row['BIN_CT'])),
                fontsize=fs1,alpha=0.7))
    adjust_text(texts,avoid_points=False)
    # find color
    if group == 'plyr':
        color =  get_player_color(title)
    elif group == 'team':
        color = get_team_color(title)
    # plot only max bin using index
    ax.scatter(data['LOC_X'], data['LOC_Y'] + 60 , 
                c = color, alpha = 0.3,s = data['BIN_CT'].astype(int))
    fig.savefig('static\\images\\new_plot.png', dpi=150)
    
def favorite_shots_by_qtr(data,title,group,n=10):
    folder='static\\images\\gif_src\\'
    # create and save a png for each quarter
    for qtr in range(1,5):
        # intialize figure, add court lines
        fig = plt.figure(figsize=(4, 3.76))
        ax = fig.add_axes([0, 0, 1, 1])
        draw_court(ax, 'black')
        data_qtr = data.loc[data['PERIOD'] == qtr]
        ax.text(0.02, 0.95, title + ' Most Freq. Shots, QTR ' + str(qtr) + ' ' + year,
                transform=ax.transAxes, ha='left', va='baseline')
        # bin data
        data_qtr = add_bins(data_qtr)
        # find n most frequent shots
        data_qtr = data_qtr.head(n)
        # add labels
        texts = []
        for index, row in data_qtr.iterrows():
            if -60 <= row['LOC_X'] < 60 and -50 <= row['LOC_Y'] <= 80 :
                fs1 = 5
            else:
                fs1 = 7
            x = row['LOC_X']
            y = row['LOC_Y']
            texts.append(ax.text(x,y  + 60, str(int(row['BIN_CT'])),
                    fontsize=fs1,alpha=0.7))
        adjust_text(texts,avoid_points=False)
        # find color
        if group == 'plyr':
            color =  get_player_color(title)
        elif group == 'team':
            color = get_team_color(title)
        # plot
        ax.scatter(data_qtr['LOC_X'], data_qtr['LOC_Y'] + 60, 
                c = color, alpha = 0.3, s=data_qtr['BIN_CT'].astype(int))
   
        fname = 'qtr' + str(qtr)
        fig.savefig(folder + fname)
    # create gif from images
    files = [f"{folder}\\{file}" for file in os.listdir(folder) if file != 'new_plot.png']
    images = [imageio.imread(file) for file in files]
    imageio.mimwrite('static\\images\\new_plot_qtr.gif', images, fps=1) 
  
def highest_eff_shots(data,title,group,n=10,color = '#b80f0f'):
    fig = plt.figure(figsize=(4, 3.76),dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    draw_court(ax, 'black')
    ax.text(0.02, 0.95, title + ' ' + str(n) + ' Highest Efficiency Shots ' + year,
            transform=ax.transAxes, ha='left', va='baseline')
    # bin data
    data = add_bins(data)
    # sort highest pct, then take top n
    data = data.sort_values(by=['BIN_PCT','LOC_Y'], ascending = False)
    data = data.head(n)
    # add labels
    texts = []
    for index, row in data.iterrows():
        if -60 <= row['LOC_X'] < 60 and -50 <= row['LOC_Y'] <= 80 :
            fs1 = 5
        else:
            fs1 = 7
        x = row['LOC_X']
        y = row['LOC_Y']
        texts.append(ax.text(x,y  + 60, str(round(float(row['BIN_PCT']),2)) + ' (' + str(int(row['BIN_CT']))+' att.)',
                fontsize=fs1,alpha=0.7))
    adjust_text(texts)
    
    # find color
    if group == 'plyr':
        color =  get_player_color(title)
    elif group == 'team':
        color = get_team_color(title)
    # plot only max bin using index
    ax.scatter(data['LOC_X'], data['LOC_Y'] + 60, 
                c = color, alpha = 0.6, s=data['BIN_CT'].astype(int))
    fig.savefig('static\\images\\new_plot.png', dpi=150)

def highest_eff_shots_by_qtr(data,title,group,n=10):
    folder='static\\images\\gif_src\\'
    # create and save a png for each quarter
    for qtr in range(1,5):
        # intialize figure, add court lines
        fig = plt.figure(figsize=(4, 3.76))
        ax = fig.add_axes([0, 0, 1, 1])
        draw_court(ax, 'black')
        data_qtr = data.loc[data['PERIOD'] == qtr]
        ax.text(0.02, 0.95, title + ' ' + str(n) + ' Highest Eff. Shots, QTR ' + str(qtr)  + ' ' + year,
                transform=ax.transAxes, ha='left', va='baseline')
        # bin data
        data_qtr = add_bins(data_qtr)
        # sort highest pct, then take top n
        data_qtr = data_qtr.sort_values(by=['BIN_PCT','LOC_Y'], ascending = False)
        data_qtr = data_qtr.head(n)
        # add labels
        texts=[]
        for index, row in data.iterrows():
            if -60 <= row['LOC_X'] < 60 and -50 <= row['LOC_Y'] <= 80 :
                fs1 = 5; fs2 = 4
            else:
                fs1 = 7; fs2 = 5
            x = row['LOC_X']
            y = row['LOC_Y']
            texts.append(ax.text(x,y  + 60, str(round(float(row['BIN_PCT']),2)) + ' (' + str(int(row['BIN_CT']))+' att.)',
                    fontsize=fs1,alpha=0.7))
            adjust_text(texts,avoid_points=False)
        # find color
        if group == 'plyr':
            color =  get_player_color(title)
        elif group == 'team':
            color = get_team_color(title)
        # plot
        ax.scatter(data_qtr['LOC_X'], data_qtr['LOC_Y'] + 60, 
                c = color, alpha = 0.6, s=data['BIN_CT'].astype(int))
        fname = 'qtr' + str(qtr)
        fig.savefig(folder + fname)
    # create gif from images
    files = [f"{folder}\\{file}" for file in os.listdir(folder) if file != 'new_plot.png']
    images = [imageio.imread(file) for file in files]
    imageio.mimwrite('static\\images\\new_plot_qtr.gif', images, fps=1) 
    
def shot_chart(data, title, group):
    fig = plt.figure(figsize=(4, 3.76),dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    draw_court(ax, 'black')
    ax.text(0.02, 0.95, title + ' FGA ' + year, 
            transform=ax.transAxes, ha='left', va='baseline')
    # find colors
    if group == 'plyr':
        colors =  get_player_colormap(title)
    elif group == 'team':
        colors = get_team_colormap(title)
    # plot
    ax.hexbin(data['LOC_X'], data['LOC_Y'] + 60, 
                gridsize=(50, 50), extent=(-300, 300, 0, 940), bins='log', cmap=colors,alpha=1)
    fig.savefig('static\\images\\new_plot.png', dpi=150)

def shot_chart_by_qtr(data, title, group):
    folder='static\\images\\gif_src\\'
    # create and save a png for each quarter
    for qtr in range(1,5):
        # intialize figure, add court lines
        fig = plt.figure(figsize=(4, 3.76))
        ax = fig.add_axes([0, 0, 1, 1])
        draw_court(ax, 'black')
        data_qtr = data.loc[data['PERIOD'] == qtr]
        ax.text(0.02, 0.95, title + ' FGA, QTR ' + str(qtr)  + ' ' + year,
                transform=ax.transAxes, ha='left', va='baseline')
        # find colors
        if group == 'plyr':
            colors =  get_player_colormap(title)
        elif group == 'team':
            colors = get_team_colormap(title)
        # plot
        ax.hexbin(data_qtr['LOC_X'], data_qtr['LOC_Y'] + 60, 
                  gridsize=(50, 50), extent=(-300, 300, 0, 940), bins='log', cmap=colors)
        fname = 'qtr' + str(qtr)
        fig.savefig(folder + fname)
    # create gif from images
    files = [f"{folder}\\{file}" for file in os.listdir(folder) if file != 'new_plot.png']
    images = [imageio.imread(file) for file in files]
    imageio.mimwrite('static\\images\\new_plot_qtr.gif', images, fps=1)
    
## doesn't look as good
# ax.hist2d(data_qtr['LOC_X'], data_qtr['LOC_Y'] + 60, 
#           range = [[-250,250],[0,450]], bins=[100,100], norm=mpl.colors.LogNorm(0.5), cmap=colors)