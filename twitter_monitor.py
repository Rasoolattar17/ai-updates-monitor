#!/usr/bin/env python3
"""
Twitter/X Monitor for AI Updates
Monitors Twitter activity via X API and news reports
"""

import requests
import logging
import re
import hashlib
import feedparser
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from database import AIMonitoringDB
import time

class TwitterMonitor:
    def __init__(self):
        self.db = AIMonitoringDB()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.source_type = "social_media"
        
        # X API credentials (optional - will use news methods if not available)
        self.x_bearer_token = os.getenv('X_BEARER_TOKEN', '')
        self.x_api_available = bool(self.x_bearer_token)
        
        if self.x_api_available:
            self.x_headers = {
                'Authorization': f'Bearer {self.x_bearer_token}',
                'User-Agent': 'AI-Monitor-Bot/1.0'
            }
    
    def contains_keywords(self, text, keywords):
        """Check if text contains any of the specified keywords"""
        if not keywords:
            return True
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)
    
    def sanitize_content(self, content):
        """Clean up content for storage and display"""
        if not content:
            return ""
        
        # Remove HTML tags
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit length
        if len(text) > 500:
            text = text[:497] + "..."
        
        return text
    
    def monitor_twitter_accounts(self):
        """Monitor Twitter activity via X API (preferred) or news reports (fallback)"""
        all_new_items = []
        
        # Try X API first if available
        if self.x_api_available:
            try:
                logging.info("🐦 Using X API for Twitter monitoring...")
                x_items = self.check_via_x_api()
                all_new_items.extend(x_items)
                logging.info(f"X API found {len(x_items)} new items")
            except Exception as e:
                logging.error(f"X API monitoring failed: {e}")
        
        # Always also check news sources for Twitter mentions (additional coverage)
        try:
            news_items = self.check_twitter_news()
            all_new_items.extend(news_items)
        except Exception as e:
            logging.error(f"Twitter news monitoring failed: {e}")
        
        # Check social media aggregators
        try:
            social_items = self.check_social_media_aggregators()
            all_new_items.extend(social_items)
        except Exception as e:
            logging.error(f"Social media aggregator monitoring failed: {e}")
        
        return all_new_items
    
    def check_via_x_api(self):
        """Monitor Twitter using X API v2 with rate limit handling"""
        new_items = []
        
        # Define accounts to monitor (reduced for rate limit efficiency)
        accounts_to_monitor = [
            {'username': 'OpenAI', 'name': 'OpenAI', 'keywords': ['gpt', 'chatgpt', 'dalle', 'api', 'update', 'release']},
            {'username': 'AnthropicAI', 'name': 'Anthropic', 'keywords': ['claude', 'ai', 'update', 'release', 'model']},
            {'username': 'sama', 'name': 'Sam Altman', 'keywords': ['openai', 'ai', 'gpt', 'update']},
        ]
        
        for i, account in enumerate(accounts_to_monitor):
            try:
                # Add delay between API calls to respect rate limits
                if i > 0:
                    time.sleep(2)  # 2 second delay between accounts
                
                # Get user ID first
                user_id = self.get_user_id_cached(account['username'])
                if not user_id:
                    continue
                
                # Get recent tweets
                tweets = self.get_user_tweets(user_id, account)
                new_items.extend(tweets)
                
                logging.info(f"X API: Checked @{account['username']}, found {len(tweets)} new tweets")
                
            except Exception as e:
                logging.error(f"Error checking X API for {account['username']}: {e}")
        
        return new_items
    
    def get_user_id_cached(self, username):
        """Get user ID with basic caching to reduce API calls"""
        # Simple hardcoded cache for common usernames to avoid repeated lookups
        user_id_cache = {
            'OpenAI': '1358836358901501952',
            'AnthropicAI': '1397906446765400065', 
            'sama': '3456423612',
        }
        
        if username in user_id_cache:
            return user_id_cache[username]
        
        # Fall back to API lookup for other usernames
        return self.get_user_id(username)
    
    def get_user_id(self, username):
        """Get user ID from username using X API"""
        try:
            url = f"https://api.twitter.com/2/users/by/username/{username}"
            response = requests.get(url, headers=self.x_headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('id')
            else:
                logging.error(f"Failed to get user ID for {username}: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting user ID for {username}: {e}")
            return None
    
    def get_user_tweets(self, user_id, account):
        """Get recent tweets from user using X API"""
        new_items = []
        
        try:
            # X API v2 endpoint for user tweets
            url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': 10,  # Get last 10 tweets
                'tweet.fields': 'created_at,public_metrics,text',
                'exclude': 'retweets,replies'  # Only original tweets
            }
            
            response = requests.get(url, headers=self.x_headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tweets = data.get('data', [])
                
                for tweet in tweets:
                    tweet_text = tweet.get('text', '')
                    tweet_id = tweet.get('id', '')
                    created_at = tweet.get('created_at', '')
                    
                    # Check if tweet is recent (last 24 hours for daily check)
                    if created_at and not self.is_tweet_recent(created_at, hours=24):
                        continue
                    
                    # Check if tweet matches keywords
                    if not self.contains_keywords(tweet_text, account['keywords']):
                        continue
                    
                    # Create unique ID
                    item_id = f"tweet_{tweet_id}"
                    
                    # Check if already exists
                    source_name = f"X @{account['username']}"
                    if self.db.is_item_exists(self.source_type, source_name, item_id):
                        continue
                    
                    # Create tweet URL
                    tweet_url = f"https://twitter.com/{account['username']}/status/{tweet_id}"
                    
                    # Add to database
                    db_id = self.db.add_item(
                        source_type=self.source_type,
                        source_name=source_name,
                        item_id=item_id,
                        title=f"@{account['username']}: {tweet_text[:100]}...",
                        url=tweet_url,
                        content=self.sanitize_content(tweet_text),
                        published_date=created_at
                    )
                    
                    if db_id:
                        new_items.append({
                            'id': db_id,
                            'source': source_name,
                            'title': f"@{account['username']}: {tweet_text[:100]}...",
                            'url': tweet_url,
                            'content': self.sanitize_content(tweet_text),
                            'published_date': created_at
                        })
                        logging.info(f"New X API tweet: @{account['username']}: {tweet_text[:50]}...")
            else:
                logging.error(f"X API error for user {user_id}: {response.status_code} - {response.text}")
                
        except Exception as e:
            logging.error(f"Error getting tweets for user {user_id}: {e}")
        
        return new_items
    
    def is_tweet_recent(self, created_at_str, hours=24):
        """Check if tweet is within the last N hours"""
        try:
            from dateutil.parser import parse
            tweet_time = parse(created_at_str)
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return tweet_time.replace(tzinfo=None) > cutoff_time
        except:
            return True  # If we can't parse, assume it's recent
    
    def check_twitter_news(self):
        """Check news sources that report on Twitter/X activity"""
        new_items = []
        
        # News sources that often report Twitter activity
        news_sources = [
            {
                'name': 'OpenAI Twitter News',
                'url': 'https://news.google.com/rss/search?q=OpenAI%20twitter%20OR%20OpenAI%20tweets%20OR%20Sam%20Altman%20twitter',
                'keywords': ['twitter', 'tweet', 'posts', 'announces', 'says', 'x.com']
            },
            {
                'name': 'Anthropic Twitter News',
                'url': 'https://news.google.com/rss/search?q=Anthropic%20twitter%20OR%20Claude%20twitter%20OR%20Anthropic%20tweets',
                'keywords': ['twitter', 'tweet', 'posts', 'announces', 'anthropic', 'claude']
            },
            {
                'name': 'AI Companies Social Media',
                'url': 'https://news.google.com/rss/search?q=ChatGPT%20twitter%20OR%20Cursor%20AI%20twitter%20OR%20Perplexity%20twitter',
                'keywords': ['twitter', 'tweet', 'social media', 'announces', 'posts']
            },
            {
                'name': 'Tech Leaders Twitter Activity',
                'url': 'https://news.google.com/rss/search?q=Sam%20Altman%20twitter%20OR%20Dario%20Amodei%20twitter%20OR%20AI%20CEO%20twitter',
                'keywords': ['twitter', 'tweet', 'ceo', 'leader', 'announces']
            }
        ]
        
        for source in news_sources:
            try:
                logging.info(f"Checking Twitter news: {source['name']}")
                feed = feedparser.parse(source['url'])
                
                for entry in feed.entries[:8]:  # Check last 8 entries
                    title = entry.title if hasattr(entry, 'title') else ''
                    link = entry.link if hasattr(entry, 'link') else ''
                    description = entry.description if hasattr(entry, 'description') else ''
                    published = entry.published if hasattr(entry, 'published') else None
                    
                    # Check if mentions Twitter and AI keywords
                    content_text = f"{title} {description}"
                    if not self.contains_keywords(content_text, source['keywords']):
                        continue
                    
                    # Skip if older than 7 days
                    if published and not self.is_recent_item(published):
                        continue
                    
                    # Create unique ID
                    item_id = hashlib.md5(f"{source['name']}_{title}_{link}".encode()).hexdigest()
                    
                    # Check if already exists
                    if self.db.is_item_exists(self.source_type, source['name'], item_id):
                        continue
                    
                    # Add to database
                    db_id = self.db.add_item(
                        source_type=self.source_type,
                        source_name=source['name'],
                        item_id=item_id,
                        title=title,
                        url=link,
                        content=self.sanitize_content(description),
                        published_date=published
                    )
                    
                    if db_id:
                        new_items.append({
                            'id': db_id,
                            'source': source['name'],
                            'title': title,
                            'url': link,
                            'content': self.sanitize_content(description),
                            'published_date': published
                        })
                        logging.info(f"New Twitter news item: {title}")
                        
            except Exception as e:
                logging.error(f"Error checking Twitter news {source['name']}: {e}")
        
        return new_items
    
    def check_social_media_aggregators(self):
        """Check social media aggregator sites"""
        new_items = []
        
        # Social media aggregators and discussion sites
        aggregator_sources = [
            {
                'name': 'AI Social Media Updates',
                'url': 'https://hnrss.org/frontpage?q=twitter%20AND%20(OpenAI%20OR%20Anthropic%20OR%20ChatGPT%20OR%20Claude)',
                'keywords': ['twitter', 'tweet', 'openai', 'anthropic', 'chatgpt', 'claude']
            },
            {
                'name': 'Tech Twitter Discussions',
                'url': 'https://hnrss.org/newest?q=Sam%20Altman%20OR%20Dario%20Amodei%20OR%20AI%20twitter',
                'keywords': ['sam altman', 'dario amodei', 'ai', 'twitter', 'ceo']
            }
        ]
        
        for source in aggregator_sources:
            try:
                logging.info(f"Checking social aggregator: {source['name']}")
                feed = feedparser.parse(source['url'])
                
                for entry in feed.entries[:5]:  # Check last 5 entries
                    title = entry.title if hasattr(entry, 'title') else ''
                    link = entry.link if hasattr(entry, 'link') else ''
                    description = entry.description if hasattr(entry, 'description') else ''
                    published = entry.published if hasattr(entry, 'published') else None
                    
                    # Check if matches keywords
                    content_text = f"{title} {description}"
                    if not self.contains_keywords(content_text, source['keywords']):
                        continue
                    
                    # Create unique ID
                    item_id = hashlib.md5(f"{source['name']}_{title}_{link}".encode()).hexdigest()
                    
                    # Check if already exists
                    if self.db.is_item_exists(self.source_type, source['name'], item_id):
                        continue
                    
                    # Add to database
                    db_id = self.db.add_item(
                        source_type=self.source_type,
                        source_name=source['name'],
                        item_id=item_id,
                        title=title,
                        url=link,
                        content=self.sanitize_content(description),
                        published_date=published
                    )
                    
                    if db_id:
                        new_items.append({
                            'id': db_id,
                            'source': source['name'],
                            'title': title,
                            'url': link,
                            'content': self.sanitize_content(description),
                            'published_date': published
                        })
                        logging.info(f"New social aggregator item: {title}")
                        
            except Exception as e:
                logging.error(f"Error checking social aggregator {source['name']}: {e}")
        
        return new_items
    
    def check_reddit_twitter_discussions(self):
        """Check Reddit for Twitter/X discussions about AI"""
        new_items = []
        
        # Reddit RSS feeds for AI discussions that mention Twitter
        reddit_sources = [
            {
                'name': 'Reddit AI Twitter Discussions',
                'url': 'https://www.reddit.com/r/artificial+ChatGPT+OpenAI+MachineLearning/search.rss?q=twitter+OR+tweet&sort=new&t=week',
                'keywords': ['twitter', 'tweet', 'openai', 'anthropic', 'ai']
            },
            {
                'name': 'Reddit OpenAI Discussions',
                'url': 'https://www.reddit.com/r/OpenAI/new.rss',
                'keywords': ['twitter', 'tweet', 'sam altman', 'announcement', 'update']
            }
        ]
        
        for source in reddit_sources:
            try:
                logging.info(f"Checking Reddit: {source['name']}")
                feed = feedparser.parse(source['url'])
                
                for entry in feed.entries[:5]:  # Check last 5 entries
                    title = entry.title if hasattr(entry, 'title') else ''
                    link = entry.link if hasattr(entry, 'link') else ''
                    description = entry.description if hasattr(entry, 'description') else ''
                    published = entry.published if hasattr(entry, 'published') else None
                    
                    # Check if matches keywords
                    content_text = f"{title} {description}"
                    if not self.contains_keywords(content_text, source['keywords']):
                        continue
                    
                    # Create unique ID
                    item_id = hashlib.md5(f"{source['name']}_{title}_{link}".encode()).hexdigest()
                    
                    # Check if already exists
                    if self.db.is_item_exists(self.source_type, source['name'], item_id):
                        continue
                    
                    # Add to database
                    db_id = self.db.add_item(
                        source_type=self.source_type,
                        source_name=source['name'],
                        item_id=item_id,
                        title=title,
                        url=link,
                        content=self.sanitize_content(description),
                        published_date=published
                    )
                    
                    if db_id:
                        new_items.append({
                            'id': db_id,
                            'source': source['name'], 
                            'title': title,
                            'url': link,
                            'content': self.sanitize_content(description),
                            'published_date': published
                        })
                        logging.info(f"New Reddit Twitter discussion: {title}")
                        
            except Exception as e:
                logging.error(f"Error checking Reddit {source['name']}: {e}")
        
        return new_items
    
    def is_recent_item(self, published_str):
        """Check if item is from the last 7 days"""
        try:
            from dateutil.parser import parse
            published_date = parse(published_str)
            cutoff_date = datetime.now() - timedelta(days=7)
            return published_date.replace(tzinfo=None) > cutoff_date
        except:
            return True  # If we can't parse date, assume it's recent

def main():
    """Test the Twitter monitor"""
    monitor = TwitterMonitor()
    print("Testing improved Twitter/Social Media monitoring...")
    
    # Test individual methods
    print("\n1. Testing Twitter news sources...")
    news_items = monitor.check_twitter_news()
    print(f"Twitter news items found: {len(news_items)}")
    if news_items:
        for item in news_items[:2]:
            print(f"  - {item['title']}")
    
    print("\n2. Testing social media aggregators...")
    social_items = monitor.check_social_media_aggregators()
    print(f"Social aggregator items found: {len(social_items)}")
    if social_items:
        for item in social_items[:2]:
            print(f"  - {item['title']}")
    
    print("\n3. Testing Reddit discussions...")
    reddit_items = monitor.check_reddit_twitter_discussions()
    print(f"Reddit discussion items found: {len(reddit_items)}")
    if reddit_items:
        for item in reddit_items[:2]:
            print(f"  - {item['title']}")
    
    # Test all together
    print("\n4. Testing all methods together...")
    all_items = monitor.monitor_twitter_accounts()
    
    if all_items:
        print(f"\nFound {len(all_items)} new social media updates:")
        for item in all_items[:3]:  # Show first 3
            print(f"  - {item['title']}")
            print(f"    Source: {item['source']}")
            print(f"    URL: {item['url']}")
            print()
    else:
        print("No new social media updates found")

if __name__ == "__main__":
    main() 