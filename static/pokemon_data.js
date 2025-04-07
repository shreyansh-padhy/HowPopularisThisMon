const VALID_POKEMON = new Set([
    "bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard",
    // ... (copy all Pokemon names from pokemon_data.py)
]);

function is_valid_pokemon(name) {
    return VALID_POKEMON.has(name.toLowerCase());
} 