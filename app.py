from flask import Flask, jsonify, request
from fetch_pytrends import get_pokemon_trends

app = Flask(__name__)

@app.route('/trends', methods=['GET'])
def trends():
    pokemon = request.args.get('pokemon')
    if not pokemon:
        return jsonify({"error": "Please provide a Pokémon name"}), 400

    data = get_pokemon_trends([pokemon])
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
