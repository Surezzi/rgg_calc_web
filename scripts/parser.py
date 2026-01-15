import requests
from bs4 import BeautifulSoup
import re
import json

URL = "https://rgg.land/checkers"

def main():
    # fetch the HTML
    url = URL
    response = requests.get(url)
    html = response.text

    # parse with Beautiful Soup
    soup = BeautifulSoup(html, features="html.parser")

    # main data structure
    data = {}
    # icon color to team binding
    color_to_team = {}

    # parse CSS for retrieving color of the icons
    css_text = soup.find("head").find_all("style")[-1].text
    # helper function that converts icon class to icon color
    def getColorFromIconClass(icon_class):
        color = re.search(re.compile("\." + icon_class + "{.+?color:(#.{6});.+?}"), css_text).group(1)
        return color

    # extract list containers
    [container_teams, container_players] = [h.parent for h in soup.find_all("h6")][:2]

    # parse teams table
    div_teams = container_teams.find_all("div", recursive=False)
    for div_team in div_teams:
        [team_name, team_score] = [span.text for span in div_team.find_all("span")[:2]]
        # fill data
        data[team_name] = {
            "score": team_score,
            "games_completed": 0,
            "games_dropped": 0,
            "kills": 0
        }
        # fill color_to_team mapping object
        icon_class = div_team.find("svg").attrs["class"][-1]
        team_color = getColorFromIconClass(icon_class)
        color_to_team[team_color] = team_name

    # parse players table
    div_players = container_players.find_all("div", recursive=False)
    for div_player in div_players:
        # retrieve player's team from icon
        icon_class = div_player.find("svg").attrs["class"][-1]
        team_color = getColorFromIconClass(icon_class)
        team_name = color_to_team[team_color]
        # parse player stats
        player_stats_text = div_player.find_all("div", string=True)[1].text
        player_games_completed, player_games_dropped, player_kills = re.match(r"Пройден. (\d+).+, дропнут. (\d+).+, забран. (\d+)", player_stats_text).groups()
        # fill data
        data[team_name]["games_completed"] += int(player_games_completed)
        data[team_name]["games_dropped"] += int(player_games_dropped)
        data[team_name]["kills"] += int(player_kills)

    # convert data to JSON
    json_data = []
    for team_name in data:
        json_team_data = {
            "team": team_name,
            "score": data[team_name]["score"],
            "games_completed": data[team_name]["games_completed"],
            "games_dropped": data[team_name]["games_dropped"],
            "kills": data[team_name]["kills"],
        }
        json_data.append(json_team_data)

    # save to JSON file
    with open("data/out.json", "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
