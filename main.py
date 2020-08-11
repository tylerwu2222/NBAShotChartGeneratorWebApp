# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 21:44:55 2020

@author: tyler
"""
#call virt\Scripts\activate.bat
# import io
import time
import matplotlib
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
matplotlib.use('Agg')
from flask import Flask, render_template, request
import nba_viz
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://0477d0948dba4b9780474b3bd60c0723@o432433.ingest.sentry.io/5385137",
    integrations=[FlaskIntegration()]
)


app = Flask(__name__)

@app.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0

@app.route('/', methods=['GET']) 
def index():
    if 'g' in request.args:
        # season = request.args.get('s')
        group_type = request.args.get('g')
        if(group_type == 'plyr'):
            group = request.args.get('p')
        elif (group_type == 'team'):
            group = request.args.get('t')
        stat = request.args.get('stat')
        shots = request.args.get('shots')
        if(len(shots) == 0):
            shots = 10
        else:
            shots = int(shots)
        nba_viz.fn_handler(stat,group_type,group,shots) # will update the png or gif via save
        t = int(round(time.time() * 1000))
        non_gif_ind = [0,2,3]
        if(stat in nba_viz.stats[non_gif_ind]): # non-gif -> get png
            url_r ='/static/images/new_plot.png?' + str(t)
        else: # gif -> get gif
            url_r ='/static/images/new_plot_qtr.gif?' + str(t)
        return render_template(
            'main.html',
            # seasonData = ['All Seasons'] + nba_viz.get_nba_seasons(),
            year = nba_viz.get_nba_season(),
            # teamData = ['All Teams'] + nba_viz.get_all_team_names(),
            teamData = nba_viz.get_all_team_names(),
            # playerData = ['All Players'] + nba_viz.get_all_player_names(),
            playerData = nba_viz.get_all_player_names(),
            statOptions = nba_viz.available_stats(),
            url = url_r
        )
    else: # else first load, DN Return image
        return render_template(
            'main.html',
            # seasonData = ['All Seasons'] + nba_viz.get_nba_seasons(),
            year = nba_viz.get_nba_season(),
            teamData = nba_viz.get_all_team_names(),
            playerData = nba_viz.get_all_player_names(),
            statOptions = nba_viz.available_stats()
        )

if __name__=='__main__':
    app.run(debug=True)