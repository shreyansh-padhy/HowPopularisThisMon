import time
import random
from pytrends.request import TrendReq
import json

def get_pokemon_trends(pokemon_list):
    pytrends = TrendReq(hl='en-US', tz=360)  # Initialize pytrends here

    trends = {}
    for pokemon in pokemon_list:
        pytrends.build_payload([pokemon], cat=0, timeframe='today 5-y', geo='', gprop='')  # Build payload
        data = pytrends.interest_over_time()  # Get the trend data

        # Check if the data frame is empty or has no results
        if data.empty:
            trends[pokemon] = "No data available"
        else:
            # You can either get the values directly or return the data in the correct format
            trends[pokemon] = data[pokemon].values.tolist()  # List of trends for the Pokémon
    
    return trends

if __name__ == "__main__":
    pokemon_list = ["Pikachu", "Charizard", "Bulbasaur"]
    trends = get_pokemon_trends(pokemon_list)
    print(json.dumps(trends, indent=2))
