import requests
import numpy
import pandas

# Set up the API call variables
season_game_counts = []
header = ['Date', 'Home Team', 'Away Team', 'Period', 'Time Remaining', 'Strength', 'Game Winning Goal', 'Empty Net']
firstYear = 2010
lastYear = 2020
season_type = '02'


#function to get the number of games in a year. This will also involve an API Call.
def getNumberOfGamesInSingleSeason(year):
    #build API GET url
    #see https://statsapi.web.nhl.com/api/v1/standings?season=20192020 for reference JSON
    urlQuery = 'https://statsapi.web.nhl.com//api/v1/standings?season=' + str(year) + str(year+1)

    totalGames = 0

    r = requests.get(url = urlQuery)
    data = r.json()

    #parse through the json, we are interested in each team's gamesPlayed attribute
    recordList = data['records']
    for division in recordList:
        for team in division['teamRecords']:
            totalGames += team['gamesPlayed']

    #divide by two so we do not double count
    totalGames /= 2

    return totalGames

#get the number of games in each relevant season
for i in range(firstYear, lastYear):
    season_game_counts.append([i, int(getNumberOfGamesInSingleSeason(i))])

pandas.DataFrame(season_game_counts).to_csv('reference/season_game_counts.csv', header=None, index=None)

#now, we can loop over each of the years (firstYear -> lastYear) to get the goal timing data.
for year in range (firstYear, lastYear):
    game_data = []
    # Loop over the games in each season and format the API call
    for gameId in range(1, season_game_counts[year-firstYear][1]):
        gameUrlString = 'https://statsapi.web.nhl.com/api/v1/game/'+ str(year) + season_type +str(gameId).zfill(4)+'/feed/live'

        r = requests.get(url=gameUrlString)

        data = r.json()

        #parse the data. I would recommend actually going to the API to see the JSON visualized to help with this.
        #here is a sample link: http://statsapi.web.nhl.com/api/v1/game/2019020001/feed/live
        dateOfGame = data['gameData']['datetime']['dateTime']
        dateOfGame = dateOfGame.split('T')[0]

        homeTeam = data['gameData']['teams']['home']['name']
        awayTeam = data['gameData']['teams']['away']['name']

        allEventsJson = data['liveData']['plays']['allPlays']

        for event in allEventsJson:
            #we only want goal events that are not shootout goals.
            if event['result']['event'] == 'Goal' and event['about']['periodType'] != "SHOOTOUT":
                game_data.append([dateOfGame,
                                    homeTeam,
                                    awayTeam,
                                    str(event['about']['period']), #period number
                                    event['about']['periodTimeRemaining'], #time remaining in period
                                    event['result']['strength']['name'], #power play/Short Handed/even
                                    event['result']['gameWinningGoal'], #boolean
                                    event['result']['emptyNet'] #boolean
                                ])

    #now we print to a csv!
    print(year)
    pandas.DataFrame(game_data).to_csv('data/' + str(year) + '.csv', header=header, index=None)
