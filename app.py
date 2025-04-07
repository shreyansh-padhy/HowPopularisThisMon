from flask import Flask, jsonify, request, render_template
from metrics_collector import PokemonMetricsCollector
from pokemon_data import is_valid_pokemon
from config import API_KEYS
import logging
from dotenv import load_dotenv
import os

app = Flask(__name__)
metrics_collector = PokemonMetricsCollector()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

# Update config with environment variables
API_KEYS['reddit']['client_id'] = os.getenv('REDDIT_CLIENT_ID')
API_KEYS['reddit']['client_secret'] = os.getenv('REDDIT_CLIENT_SECRET')
API_KEYS['youtube']['api_key'] = os.getenv('YOUTUBE_API_KEY')

@app.route('/')
def home():
    return render_template('index.html')  # Serve the HTML file from templates

@app.route('/metrics', methods=['GET'])
def get_metrics():
    pokemon = request.args.get('pokemon')
    if not pokemon:
        return jsonify({"error": "Please provide a Pokémon name"}), 400
    
    logger.debug(f"Received request for Pokemon: {pokemon}")
    
    if not is_valid_pokemon(pokemon):
        logger.debug(f"Invalid Pokemon name: {pokemon}")
        return jsonify({"error": "Please enter a valid Pokémon name"}), 400

    try:
        metrics = metrics_collector.calculate_popularity_score(pokemon)
        logger.debug(f"Successfully calculated metrics for {pokemon}")
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error calculating metrics for {pokemon}: {str(e)}")
        return jsonify({"error": "An error occurred while calculating metrics"}), 500

if __name__ == "__main__":
    app.run(debug=True)
