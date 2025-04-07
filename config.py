"""
Configuration file for Pokemon Popularity Metrics
Contains API keys and other configuration settings
"""

# API Keys and Authentication
API_KEYS = {
    'reddit': {
        'client_id': 'CfSC1FjuKnz2LE8qOtRxyw',
        'client_secret': 'K3vvsiX9iS-KVWhvY6HiyLdiUfQEaw',
        'user_agent': 'PokemonPopularityApp/1.0'
    },
    'youtube': {
        'api_key': 'AIzaSyCjtDcztt3-OYVg1SMGFveUCmRIMuuJceY'
    }
}

# Metric Weights for Popularity Score
METRIC_WEIGHTS = {
    'google_trends': 0.35,    # 35%
    'wikipedia': 0.25,        # 25%
    'reddit': 0.20,          # 20%
    'youtube': 0.20          # 20%
}

# API Rate Limiting Settings
RATE_LIMITS = {
    'youtube': {
        'requests_per_day': 10000,
        'requests_per_100seconds': 100
    },
    'reddit': {
        'requests_per_minute': 30
    }
}

# Cache Settings
CACHE_CONFIG = {
    'enabled': True,
    'expire_after': 3600,  # Cache data for 1 hour
    'cache_dir': 'cache'
}

# Metric Normalization Factors
NORMALIZATION = {
    'youtube_views': 100000,      # Divide by 100k for normalization
    'wikipedia_views': 10000,     # Divide by 10k for normalization
    'reddit_upvotes': 1000,       # Divide by 1k for normalization
}

# Error Messages
ERROR_MESSAGES = {
    'invalid_pokemon': 'Please enter a valid Pokémon name',
    'api_error': 'Error fetching data from {service}',
    'rate_limit': 'Rate limit exceeded for {service}'
} 