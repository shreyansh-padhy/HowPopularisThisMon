import time
import random
from pytrends.request import TrendReq
import json

def get_pokemon_trends(pokemon_list):
    pytrends = TrendReq(hl='en-US', tz=360)
    
    # Introduce a delay to avoid rate limiting
    time.sleep(random.uniform(2, 5))  # Wait for 2 to 5 seconds
    
    pytrends.build_payload(pokemon_list, timeframe='now 7-d', geo='US')

    data = pytrends.interest_over_time()
    if data.empty:
        return {}

    data = data.drop(columns=['isPartial'])  # Remove unnecessary column
    data.index = data.index.astype(str)  # Convert index to string

    return data.to_dict()

if __name__ == "__main__":
    pokemon_list = ["Pikachu", "Charizard", "Bulbasaur"]
    trends = get_pokemon_trends(pokemon_list)
    print(json.dumps(trends, indent=2))
