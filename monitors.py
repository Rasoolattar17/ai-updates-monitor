import requests
import feedparser
import logging
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dateutil import parser as date_parser
from database import AIMonitoringDB
from config import AI_SOURCES

class BaseMonitor:
    def __init__(self):
        self.db = AIMonitoringDB()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
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

class RSSMonitor(BaseMonitor):
    def __init__(self):
        super().__init__()
        self.source_type = "rss"
    
    def check_feed(self, feed_config):
        """Check a single RSS feed for new items"""
        new_items = []
        
        try:
            logging.info(f"Checking RSS feed: {feed_config['name']}")
            
            response = self.session.get(feed_config['url'], timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries:
                # Create unique ID for this entry
                item_id = entry.get('id', entry.get('link', entry.get('title', '')))
                if not item_id:
                    continue
                
                # Check if we've already seen this item
                if self.db.is_item_exists(self.source_type, feed_config['name'], item_id):
                    continue
                
                # Extract relevant information
                title = entry.get('title', 'No title')
                url = entry.get('link', '')
                content = entry.get('summary', entry.get('description', ''))
                
                # Check if this item matches our keywords
                full_text = f"{title} {content}"
                if not self.contains_keywords(full_text, feed_config.get('keywords', [])):
                    continue
                
                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'published'):
                    try:
                        published_date = date_parser.parse(entry.published)
                    except:
                        pass
                
                # Clean content
                clean_content = self.sanitize_content(content)
                
                # Add to database
                db_id = self.db.add_item(
                    source_type=self.source_type,
                    source_name=feed_config['name'],
                    item_id=item_id,
                    title=title,
                    url=url,
                    content=clean_content,
                    published_date=published_date
                )
                
                if db_id:
                    new_items.append({
                        'id': db_id,
                        'source': feed_config['name'],
                        'title': title,
                        'url': url,
                        'content': clean_content,
                        'published_date': published_date
                    })
                    logging.info(f"New RSS item found: {title}")
        
        except Exception as e:
            logging.error(f"Error checking RSS feed {feed_config['name']}: {e}")
        
        return new_items
    
    def check_all_feeds(self):
        """Check all configured RSS feeds"""
        all_new_items = []
        
        for feed_config in AI_SOURCES['rss_feeds']:
            new_items = self.check_feed(feed_config)
            all_new_items.extend(new_items)
        
        return all_new_items

class GitHubMonitor(BaseMonitor):
    def __init__(self):
        super().__init__()
        self.source_type = "github"
        self.github_api_base = "https://api.github.com"
    
    def check_repo_releases(self, repo_config):
        """Check a GitHub repository for new releases"""
        new_items = []
        
        try:
            logging.info(f"Checking GitHub repo: {repo_config['name']}")
            
            url = f"{self.github_api_base}/repos/{repo_config['name']}/releases"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            releases = response.json()
            
            for release in releases[:5]:  # Check last 5 releases
                item_id = f"release_{release['id']}"
                
                # Check if we've already seen this release
                if self.db.is_item_exists(self.source_type, repo_config['name'], item_id):
                    continue
                
                title = f"New release: {release['name']} ({release['tag_name']})"
                url = release['html_url']
                content = self.sanitize_content(release.get('body', ''))
                
                # Parse published date
                published_date = None
                if release.get('published_at'):
                    try:
                        published_date = date_parser.parse(release['published_at'])
                    except:
                        pass
                
                # Add to database
                db_id = self.db.add_item(
                    source_type=self.source_type,
                    source_name=repo_config['name'],
                    item_id=item_id,
                    title=title,
                    url=url,
                    content=content,
                    published_date=published_date
                )
                
                if db_id:
                    new_items.append({
                        'id': db_id,
                        'source': repo_config['name'],
                        'title': title,
                        'url': url,
                        'content': content,
                        'published_date': published_date
                    })
                    logging.info(f"New GitHub release found: {title}")
        
        except Exception as e:
            logging.error(f"Error checking GitHub repo {repo_config['name']}: {e}")
        
        return new_items
    
    def check_all_repos(self):
        """Check all configured GitHub repositories"""
        all_new_items = []
        
        for repo_config in AI_SOURCES['github_repos']:
            if repo_config.get('track_releases', True):
                new_items = self.check_repo_releases(repo_config)
                all_new_items.extend(new_items)
        
        return all_new_items

class NewsMonitor(BaseMonitor):
    def __init__(self):
        super().__init__()
        self.source_type = "news"
    
    def check_news_source(self, source_config):
        """Check a news source for relevant articles"""
        new_items = []
        
        try:
            logging.info(f"Checking news source: {source_config['name']}")
            
            response = self.session.get(source_config['url'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.select(source_config['selector'])
            
            for article in articles[:10]:  # Check top 10 articles
                # Get article title and URL
                if article.name == 'a':
                    title = article.get_text().strip()
                    url = article.get('href', '')
                else:
                    link = article.find('a')
                    if not link:
                        continue
                    title = article.get_text().strip()
                    url = link.get('href', '')
                
                if not title or not url:
                    continue
                
                # Make URL absolute
                if url.startswith('/'):
                    base_url = f"{urlparse(source_config['url']).scheme}://{urlparse(source_config['url']).netloc}"
                    url = urljoin(base_url, url)
                
                # Create unique ID
                item_id = url
                
                # Check if we've already seen this article
                if self.db.is_item_exists(self.source_type, source_config['name'], item_id):
                    continue
                
                # Check if this article matches our keywords
                if not self.contains_keywords(title, source_config.get('keywords', [])):
                    continue
                
                # Add to database
                db_id = self.db.add_item(
                    source_type=self.source_type,
                    source_name=source_config['name'],
                    item_id=item_id,
                    title=title,
                    url=url,
                    content="",  # We could fetch full article content if needed
                    published_date=None
                )
                
                if db_id:
                    new_items.append({
                        'id': db_id,
                        'source': source_config['name'],
                        'title': title,
                        'url': url,
                        'content': "",
                        'published_date': None
                    })
                    logging.info(f"New news article found: {title}")
        
        except Exception as e:
            logging.error(f"Error checking news source {source_config['name']}: {e}")
        
        return new_items
    
    def check_all_sources(self):
        """Check all configured news sources"""
        all_new_items = []
        
        for source_config in AI_SOURCES['news_sources']:
            new_items = self.check_news_source(source_config)
            all_new_items.extend(new_items)
        
        return all_new_items

class DirectMonitor(BaseMonitor):
    def __init__(self):
        super().__init__()
        self.source_type = "direct"
    
    def check_direct_source(self, source_config):
        """Check a website directly for updates"""
        new_items = []
        
        try:
            logging.info(f"Checking direct source: {source_config['name']}")
            
            response = self.session.get(source_config['url'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for update sections
            update_elements = soup.select(source_config['selector'])
            
            for element in update_elements[:5]:  # Check top 5 elements
                title = element.get_text().strip()
                url = source_config['url']  # Use source URL as base
                
                if not title:
                    continue
                
                # Check if this matches our keywords
                if not self.contains_keywords(title, source_config.get('keywords', [])):
                    continue
                
                # Create unique ID based on content hash
                import hashlib
                item_id = hashlib.md5(title.encode()).hexdigest()
                
                # Check if we've already seen this
                if self.db.is_item_exists(self.source_type, source_config['name'], item_id):
                    continue
                
                # Add to database
                db_id = self.db.add_item(
                    source_type=self.source_type,
                    source_name=source_config['name'],
                    item_id=item_id,
                    title=title,
                    url=url,
                    content="",
                    published_date=None
                )
                
                if db_id:
                    new_items.append({
                        'id': db_id,
                        'source': source_config['name'],
                        'title': title,
                        'url': url,
                        'content': "",
                        'published_date': None
                    })
                    logging.info(f"New direct update found: {title}")
        
        except Exception as e:
            logging.error(f"Error checking direct source {source_config['name']}: {e}")
        
        return new_items
    
    def check_all_sources(self):
        """Check all configured direct sources"""
        all_new_items = []
        
        for source_config in AI_SOURCES['direct_checks']:
            new_items = self.check_direct_source(source_config)
            all_new_items.extend(new_items)
        
        return all_new_items 