# NBAShotChartGeneratorWebApp

A Python web-app built with the [Flask](https://flask.palletsprojects.com/en/1.1.x/) framework that uses [nba-api](https://github.com/swar/nba_api) to pull shot chart information on active players in the current NBA Season.
The app works well on a local server, but I'm currently running into ReadTimeoutErrors on live. If/when the app is fully functional, it will be available [here](https://nba-shot-chart-generator.herokuapp.com/).


If you clone this repository and follow the first few steps in this [Medium article](https://medium.com/free-code-camp/how-to-build-a-web-app-using-pythons-flask-and-google-app-engine-52b1bb82b221) on running your app locally, you should be able to test out this app.

# Features to add:
- Display a card with basic player/team stats and profile picture/team logo adjacent to the shot chart
- Update favortie shots and most efficient shots to the actual shot zones in basketball (Corner 3, In the paint, Mid-range, etc.)
- Block and Assist Charts (if that's available)
