# FRC Upcoming NC teams @ Worlds
A really simple tool that generates the upcoming matches for NC teams at the FIRST Robotics Championship. It creates a text file with information about the match, specialized to be sent in discord.

# Usage
## Setup
Setup assumes [python](https://www.get-python.org/downloads/release/python-3118/) version `3.11.1` is installed. Other versions may work, but have not been tested.

Installing dependencies:
- All dependencies required are stored in [requirements.txt](requirements.txt). 
- To install these to your python intallation / venv, run the following command: `python -m pip install -r requirements.txt`

## Generating Schedule
To generate a schedule, simply run the main python file: `python main.py`. This wil generate a txt file with the schedule in `/schedules`.