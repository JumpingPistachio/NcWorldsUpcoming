import json
import requests
import datetime
from dotenv import dotenv_values

# - Configs - 
# Number of matches ahead to check
CONFIG_MATCH_RANGE = 8

YEAR_PATH = "year/2024.json"
TBA = "https://www.thebluealliance.com/api/v3"
AUTH = dotenv_values()["TBA_AUTH"]
AUTH_HEADER = {'X-TBA-Auth-Key': AUTH}

URL_EVENT = "/event/"
URL_MATCHES_SIMPLE = "/matches/simple"

# Parse stuff from the year-specific JSON file into a variable called 'year'
year = {}
with open(YEAR_PATH, "r") as year_file:
    year = json.load(year_file)

def main():
    file_path = "schedules/schedule_{:%Y_%m_%d_%H-%M.%S}.txt".format(datetime.datetime.now())

    division_data = [
    parse_division_matches(division_year("arc")),
    parse_division_matches(division_year("cur")),
    parse_division_matches(division_year("dal")),
    parse_division_matches(division_year("gal")),
    parse_division_matches(division_year("hop")),
    parse_division_matches(division_year("joh")),
    parse_division_matches(division_year("mil")),
    parse_division_matches(division_year("new"))]

    nc_quals = []

    for div in division_data:
        nc_quals.extend(find_upcoming_quals(CONFIG_MATCH_RANGE, find_latest_qual_match(div), div))
    
    # Sort by predicted time
    nc_quals = sorted(nc_quals, key= lambda d: d["predicted_time"])

    with open(file_path, 'w') as file:
        for qual in nc_quals:
            file.write("- {} ({}) - {} {} - Est: <t:{}:f> (<t:{}:R>)\n".format(
                qual["team"],
                qual["alliance"],
                qual["match_number"],
                parse_division_name(qual["event_key"]),
                qual["predicted_time"],
                qual["predicted_time"]
            ))
        


# Returns a list of the latest quals matches, with the same syntax as most of the other "ist of dictionaries" stuff in TBA
def find_upcoming_quals(match_range: int, latest_qual: int, cleaned_division_data: list) -> list:
    quals_list = []
    index_max = len(cleaned_division_data)-1

    # Since latest qual refers to the latest played match, and since index = match_number-1,
    # we end up with the proper index for the *next* qual
    for i in range(latest_qual, latest_qual+match_range):
        if i > index_max:
            break

        for team in year["teams"]:
            if cleaned_division_data[i]["alliances"]["red"]["team_keys"].count(team_key(team)) > 0: # Red
                quals_list.append(upcoming_qual_itemizer(team, cleaned_division_data[i]["match_number"], "red", cleaned_division_data[i]["predicted_time"]))
            elif cleaned_division_data[i]["alliances"]["blue"]["team_keys"].count(team_key(team)) > 0: # Blue 
                quals_list.append(upcoming_qual_itemizer(team, cleaned_division_data[i]["match_number"], "blue", cleaned_division_data[i]["predicted_time"]))
    
    # Add event key to values
    for qual in quals_list:
        qual["event_key"] = cleaned_division_data[0]["event_key"]
    
    return quals_list

        



# Based on the cleaned division data, find the latest qualification match that has been played (according to whether or not actual time has been filled).
# Will return -1 if quals are finished.
def find_latest_qual_match(cleaned_division_data: list) -> int:
    for match in cleaned_division_data:
        if match["comp_level"] != "qm":
            continue
        if match["actual_time"] == None:
            return match["match_number"]-1
    
    # No more upcoming matches
    return -1



# Returns a list of matches (stored as dictionaries) from a division, based on an ID,
# all cleaned up and ready to take on the world!
def parse_division_matches(division_id: str) -> list:
    req = requests.get(TBA+URL_EVENT+division_id+URL_MATCHES_SIMPLE, headers=AUTH_HEADER)
    raw_matches = req.json()

    cleanded_matches = []
    
    # Cleanup match data (most of this stuff is pretty useless to what we need to do)
    for match in raw_matches:
        match.pop("winning_alliance")
        match.pop("key")
        match.pop("time")
        match["alliances"]["blue"].pop("score")
        match["alliances"]["red"].pop("score")
        match["alliances"]["blue"].pop("dq_team_keys")
        match["alliances"]["red"].pop("dq_team_keys")
        cleanded_matches.append(match)
    
    # Sort based on actual match number (yippie!)
    return sorted(cleanded_matches, key=lambda d: d['match_number'])

def upcoming_qual_itemizer(team: int, match_number: int, alliance: str, predicted_time: int):
    return {"team": team, "match_number": match_number, "alliance": alliance, "predicted_time": predicted_time}

def team_key(team_number: int) -> str:
    return "frc{}".format(team_number)

def division_year(division: str):
    return "{}{}".format(year["year"], division)

def parse_division_name(unparsed_name: str) -> str:
    return ''.join([i for i in unparsed_name if not i.isdigit()]).replace(' ', '')

    
    


if __name__ == "__main__":
    main()