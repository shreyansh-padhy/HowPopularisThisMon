import time
import random
from pytrends.request import TrendReq
import requests
from datetime import datetime, timedelta
import json
import os
from typing import Dict, Any
import logging
import praw  # For Reddit API
import tweepy  # For Twitter API
from bs4 import BeautifulSoup
from config import (
    API_KEYS, 
    METRIC_WEIGHTS, 
    RATE_LIMITS, 
    CACHE_CONFIG, 
    NORMALIZATION, 
    ERROR_MESSAGES
)
from googleapiclient.discovery import build
import math

logger = logging.getLogger(__name__)

class PokemonMetricsCollector:
    def __init__(self):
        """Initialize the collector with only necessary services"""
        self.initialize_pytrends()
        self.initialize_reddit()
        # Remove Twitter initialization since we're not using it
        # self.initialize_twitter()
        # Initialize other API clients here
        # self.twitter_api = ...
        # self.reddit_api = ...
    
    def initialize_pytrends(self):
        """Initialize pytrends with caching but without testing connection"""
        # Create cache directory if it doesn't exist
        if not os.path.exists('cache'):
            os.makedirs('cache')
        
        # Don't initialize or test pytrends at startup
        self.pytrends = None
        self.use_cache = True

    def initialize_reddit(self):
        """Initialize Reddit API client"""
        try:
            self.reddit = praw.Reddit(
                client_id=API_KEYS['reddit']['client_id'],
                client_secret=API_KEYS['reddit']['client_secret'],
                user_agent=API_KEYS['reddit']['user_agent'],
                read_only=True
            )
            logger.debug("Reddit API initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Reddit API: {str(e)}")
            self.reddit = None

    def initialize_twitter(self):
        """Initialize Twitter API client"""
        try:
            auth = tweepy.OAuthHandler(
                API_KEYS['twitter']['api_key'],
                API_KEYS['twitter']['api_secret']
            )
            auth.set_access_token(
                API_KEYS['twitter']['access_token'],
                API_KEYS['twitter']['access_token_secret']
            )
            self.twitter = tweepy.API(auth, wait_on_rate_limit=True)
        except Exception as e:
            logger.error(f"Twitter initialization error: {str(e)}")
            self.twitter = None

    def get_cached_trends(self, pokemon: str) -> dict:
        """Get cached Google Trends data if available"""
        cache_file = f'cache/trends_{pokemon.lower()}.json'
        if os.path.exists(cache_file):
            # Check if cache is less than 24 hours old
            if time.time() - os.path.getmtime(cache_file) < 86400:  # 24 hours
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error reading cache: {str(e)}")
        return None

    def save_to_cache(self, pokemon: str, data: dict):
        """Save Google Trends data to cache"""
        cache_file = f'cache/trends_{pokemon.lower()}.json'
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")

    def get_google_trends(self, pokemon: str) -> dict:
        """Get Google Trends data using fallback system"""
        # Try to get cached data first
        cached_data = self.get_cached_trends(pokemon)
        if cached_data:
            logger.debug(f"Using cached trends data for {pokemon}")
            return cached_data

        # Use fallback data
        fallback_data = self.get_fallback_trends(pokemon)
        
        # Save fallback data to cache
        self.save_to_cache(pokemon, fallback_data)
        
        return fallback_data

    def get_fallback_trends(self, pokemon: str) -> dict:
        """Get fallback trends data based on Pokemon tiers"""
        # Define popularity tiers for Gen 1 Pokemon
        high_tier = {
            'pikachu', 'charizard', 'mewtwo', 'mew', 'dragonite', 
            'gyarados', 'gengar', 'snorlax'
        }
        mid_tier = {
            'bulbasaur', 'squirtle', 'eevee', 'arcanine', 'alakazam',
            'blastoise', 'venusaur', 'lapras', 'raichu', 'machamp'
        }
        low_tier = {
            'rattata', 'pidgey', 'weedle', 'caterpie', 'metapod',
            'kakuna', 'magikarp', 'zubat', 'ekans', 'spearow'
        }
        
        # Generate synthetic trend data based on tiers
        if pokemon.lower() in high_tier:
            base_value = random.uniform(70, 100)
            variance = 15
        elif pokemon.lower() in mid_tier:
            base_value = random.uniform(40, 70)
            variance = 10
        elif pokemon.lower() in low_tier:
            base_value = random.uniform(5, 20)
            variance = 5
        else:
            base_value = random.uniform(20, 40)
            variance = 8
        
        # Generate 260 weekly data points (5 years) with seasonal variations
        trend_values = []
        for i in range(260):
            # Add seasonal variation (higher in summer and winter)
            seasonal = 10 * math.sin(2 * math.pi * i / 52)  # 52 weeks per year
            # Add random variation
            random_variation = random.uniform(-variance, variance)
            # Calculate final value with constraints
            value = max(0, min(100, base_value + seasonal + random_variation))
            trend_values.append(value)
        
        return {
            'trend_values': trend_values,
            'max_value': max(trend_values),
            'avg_value': sum(trend_values) / len(trend_values),
            'success': True,
            'is_fallback': True
        }
    
    def get_wikipedia_views(self, pokemon: str) -> dict:
        """Get Wikipedia page views with proper headers"""
        headers = {
            'User-Agent': 'PokemonPopularityApp/1.0 (https://github.com/yourusername/pokemon-popularity; your@email.com)',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        }
        
        try:
            # Format pokemon name for Wikipedia
            wiki_pokemon = pokemon.capitalize()
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{wiki_pokemon}/monthly/{start_date.strftime('%Y%m%d')}00/{end_date.strftime('%Y%m%d')}00"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data:
                views = [item['views'] for item in data['items']]
                return {
                    'total_views': int(sum(views)),
                    'monthly_avg': float(sum(views) / len(views)) if views else 0.0,
                    'success': True
                }
        except Exception as e:
            logger.error(f"Wikipedia API error: {str(e)}")
        
        return {
            'total_views': 0,
            'monthly_avg': 0.0,
            'success': False
        }
    
    def get_reddit_metrics(self, pokemon: str) -> dict:
        """Get Reddit metrics for a Pokemon"""
        if not self.reddit:
            logger.warning("Reddit API not initialized")
            return {
                'total_posts': 0,
                'total_upvotes': 0,
                'avg_upvotes': 0.0,
                'success': False
            }
        
        try:
            # Search for posts about the Pokemon in the last year
            subreddit = self.reddit.subreddit('pokemon+pokemongo+pokemontcg')
            posts = list(subreddit.search(f'title:{pokemon}', time_filter='year', limit=100))
            
            total_posts = len(posts)
            total_upvotes = sum(post.score for post in posts)
            avg_upvotes = total_upvotes / total_posts if total_posts > 0 else 0
            
            return {
                'total_posts': total_posts,
                'total_upvotes': total_upvotes,
                'avg_upvotes': avg_upvotes,
                'success': True
            }
        except Exception as e:
            logger.error(f"Error fetching Reddit metrics: {str(e)}")
            return {
                'total_posts': 0,
                'total_upvotes': 0,
                'avg_upvotes': 0.0,
                'success': False
            }

    def get_twitter_metrics(self, pokemon: str) -> dict:
        """Get Twitter metrics for the Pokemon"""
        if not self.twitter:
            return {
                'total_tweets': 0,
                'total_likes': 0,
                'total_retweets': 0,
                'engagement_rate': 0,
                'success': False
            }
        
        try:
            # Search recent tweets with Pokemon name and "pokemon" to improve relevance
            query = f"{pokemon} pokemon"
            tweets = self.twitter.search_tweets(
                q=query,
                lang="en",
                count=100,
                result_type='mixed'  # Get both popular and recent tweets
            )
            
            total_tweets = 0
            total_likes = 0
            total_retweets = 0
            
            for tweet in tweets:
                total_tweets += 1
                total_likes += tweet.favorite_count
                total_retweets += tweet.retweet_count
                
            return {
                'total_tweets': total_tweets,
                'total_likes': total_likes,
                'total_retweets': total_retweets,
                'engagement_rate': (total_likes + total_retweets) / total_tweets if total_tweets > 0 else 0,
                'success': True
            }
        except Exception as e:
            logger.error(f"Twitter API error: {str(e)}")
            return {
                'total_tweets': 0,
                'total_likes': 0,
                'total_retweets': 0,
                'engagement_rate': 0,
                'success': False
            }

    def get_youtube_metrics(self, pokemon: str) -> dict:
        """Get YouTube metrics for a Pokemon"""
        try:
            if not API_KEYS['youtube']['api_key'] or API_KEYS['youtube']['api_key'] == 'YOUR_YOUTUBE_API_KEY':
                logger.error("YouTube API key not configured")
                return {
                    'total_videos': 0,
                    'total_views': 0,
                    'total_likes': 0,
                    'avg_views': 0,
                    'success': False,
                    'error': 'API key not configured'
                }

            youtube = build('youtube', 'v3', developerKey=API_KEYS['youtube']['api_key'])
            
            # Search for videos about the Pokemon
            logger.debug(f"Searching YouTube for: pokemon {pokemon}")
            search_response = youtube.search().list(
                q=f'pokemon {pokemon}',
                part='id,snippet',
                maxResults=50,
                type='video',
                order='relevance',
                regionCode='US',
                relevanceLanguage='en'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            if not video_ids:
                logger.warning(f"No YouTube videos found for {pokemon}")
                return {
                    'total_videos': 0,
                    'total_views': 0,
                    'total_likes': 0,
                    'avg_views': 0,
                    'success': True,  # This is still a valid response
                    'message': 'No videos found'
                }
            
            logger.debug(f"Found {len(video_ids)} videos, fetching statistics")
            # Get video statistics
            videos_response = youtube.videos().list(
                part='statistics',
                id=','.join(video_ids)
            ).execute()
            
            total_views = 0
            total_likes = 0
            for video in videos_response.get('items', []):
                stats = video.get('statistics', {})
                try:
                    total_views += int(stats.get('viewCount', 0))
                    total_likes += int(stats.get('likeCount', 0))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing video statistics: {e}")
                    continue
            
            total_videos = len(video_ids)
            avg_views = total_views / total_videos if total_videos > 0 else 0
            
            logger.debug(f"Successfully retrieved YouTube metrics for {pokemon}")
            return {
                'total_videos': total_videos,
                'total_views': total_views,
                'total_likes': total_likes,
                'avg_views': avg_views,
                'success': True
            }
        except Exception as e:
            logger.error(f"Error fetching YouTube metrics: {str(e)}")
            return {
                'total_videos': 0,
                'total_views': 0,
                'total_likes': 0,
                'avg_views': 0,
                'success': False,
                'error': str(e)
            }

    def calculate_popularity_score(self, pokemon: str) -> Dict[str, Any]:
        """Calculate overall popularity score with fallback handling"""
        metrics = {
            'google_trends': self.get_google_trends(pokemon),
            'wikipedia': self.get_wikipedia_views(pokemon),
            'reddit': self.get_reddit_metrics(pokemon),
            'youtube': self.get_youtube_metrics(pokemon)
        }
        
        # Use weights from config
        weights = METRIC_WEIGHTS.copy()
        
        # Calculate normalized scores
        score_components = {
            'google_trends': metrics['google_trends']['avg_value'] / 100,
            'wikipedia': min(metrics['wikipedia']['monthly_avg'] / NORMALIZATION['wikipedia_views'], 1),
            'reddit': min(metrics['reddit']['avg_upvotes'] / NORMALIZATION['reddit_upvotes'], 1),
            'youtube': min(metrics['youtube']['avg_views'] / NORMALIZATION['youtube_views'], 1)
        }
        
        # Calculate final score
        total_score = sum(weights[k] * score_components[k] for k in weights.keys())
        
        return {
            'pokemon': pokemon,
            'timestamp': datetime.now().isoformat(),
            'total_score': float(total_score),
            'score_components': score_components,
            'metrics': metrics,
            'using_fallback_trends': metrics['google_trends'].get('is_fallback', False)
        } 