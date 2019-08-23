from flask import Flask
from dreamteam import DreamTeam

app = Flask(__name__)

@app.route('/')
def index():
    dt = DreamTeam()
    dreamteams = dt.get_best()

    page = ''

    for i, week in enumerate(dreamteams):
        page += f'<h1>Gameweek {i + 1}</h1>'        
        best = max(team[0] for team in week)
        team = []

        for t in week:
            if t[0] == best:
                team = t
                break

        page += f'<h2>Formation: {team[2]}-{team[3]}-{team[4]} Points: {team[0]}</h2>'
        page += '<br>'
        for player in team[-1]:
            page += f'<h3>{player}</h3>'

    return page