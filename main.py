#!/usr/bin/env python3
"""
AI Updates Monitor - Main Application
Monitors various AI sources for updates and sends notifications
"""

import time
import logging
import argparse
import schedule
from datetime import datetime
from database import AIMonitoringDB
from monitors import RSSMonitor, GitHubMonitor, NewsMonitor, DirectMonitor
from twitter_monitor import TwitterMonitor
from notifications import NotificationManager
from config import RSS_CHECK_INTERVAL, GITHUB_CHECK_INTERVAL, NEWS_CHECK_INTERVAL

class AIMonitor:
    def __init__(self):
        self.db = AIMonitoringDB()
        self.notification_manager = NotificationManager()
        
        # Initialize monitors
        self.rss_monitor = RSSMonitor()
        self.github_monitor = GitHubMonitor()
        self.news_monitor = NewsMonitor()
        self.direct_monitor = DirectMonitor()
        self.twitter_monitor = TwitterMonitor()
        
        self.setup_logging()
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_monitoring.log'),
                logging.StreamHandler()
            ]
        )
        
        logging.info("AI Monitor initialized successfully")
    
    def run_full_check(self):
        """Run a complete check of all sources"""
        logging.info("🔍 Starting full AI monitoring check...")
        
        all_new_items = []
        sources_checked = 0
        errors = 0
        
        # Check RSS feeds
        try:
            logging.info("Checking RSS feeds...")
            rss_items = self.rss_monitor.check_all_feeds()
            all_new_items.extend(rss_items)
            sources_checked += len(rss_monitor_config_count())
            logging.info(f"RSS check complete: {len(rss_items)} new items found")
        except Exception as e:
            logging.error(f"RSS monitoring failed: {e}")
            errors += 1
        
        # Check GitHub repositories
        try:
            logging.info("Checking GitHub repositories...")
            github_items = self.github_monitor.check_all_repos()
            all_new_items.extend(github_items)
            sources_checked += len(github_config_count())
            logging.info(f"GitHub check complete: {len(github_items)} new items found")
        except Exception as e:
            logging.error(f"GitHub monitoring failed: {e}")
            errors += 1
        
        # Check news sources
        try:
            logging.info("Checking news sources...")
            news_items = self.news_monitor.check_all_sources()
            all_new_items.extend(news_items)
            sources_checked += len(news_config_count())
            logging.info(f"News check complete: {len(news_items)} new items found")
        except Exception as e:
            logging.error(f"News monitoring failed: {e}")
            errors += 1
        
        # Check direct sources
        try:
            logging.info("Checking direct sources...")
            direct_items = self.direct_monitor.check_all_sources()
            all_new_items.extend(direct_items)
            sources_checked += len(direct_config_count())
            logging.info(f"Direct check complete: {len(direct_items)} new items found")
        except Exception as e:
            logging.error(f"Direct monitoring failed: {e}")
            errors += 1
        
        # Check Twitter sources
        try:
            logging.info("Checking Twitter sources...")
            twitter_items = self.twitter_monitor.monitor_twitter_accounts()
            all_new_items.extend(twitter_items)
            sources_checked += 5  # Number of Twitter accounts
            logging.info(f"Twitter check complete: {len(twitter_items)} new items found")
        except Exception as e:
            logging.error(f"Twitter monitoring failed: {e}")
            errors += 1
        
        # Send notifications if new items found
        if all_new_items:
            logging.info(f"📧 Sending notifications for {len(all_new_items)} new items...")
            self.notification_manager.send_notifications(all_new_items)
            
            # Mark items as notified
            for item in all_new_items:
                self.db.mark_as_notified(item['id'])
        
        # Send summary notification
        summary_data = {
            'total_new_items': len(all_new_items),
            'sources_checked': sources_checked,
            'errors': errors
        }
        self.notification_manager.send_summary_notification(summary_data)
        
        # Clean up old items
        self.db.cleanup_old_items()
        
        logging.info(f"✅ Monitoring cycle complete: {len(all_new_items)} new items, {errors} errors")
        return all_new_items
    
    def run_rss_check(self):
        """Run RSS feeds check only"""
        logging.info("🔍 Running RSS check...")
        try:
            new_items = self.rss_monitor.check_all_feeds()
            if new_items:
                self.notification_manager.send_notifications(new_items)
                for item in new_items:
                    self.db.mark_as_notified(item['id'])
            logging.info(f"RSS check complete: {len(new_items)} new items")
            return new_items
        except Exception as e:
            logging.error(f"RSS check failed: {e}")
            return []
    
    def run_github_check(self):
        """Run GitHub repositories check only"""
        logging.info("🔍 Running GitHub check...")
        try:
            new_items = self.github_monitor.check_all_repos()
            if new_items:
                self.notification_manager.send_notifications(new_items)
                for item in new_items:
                    self.db.mark_as_notified(item['id'])
            logging.info(f"GitHub check complete: {len(new_items)} new items")
            return new_items
        except Exception as e:
            logging.error(f"GitHub check failed: {e}")
            return []
    
    def run_news_check(self):
        """Run news sources check only"""
        logging.info("🔍 Running news check...")
        try:
            new_items = self.news_monitor.check_all_sources()
            if new_items:
                self.notification_manager.send_notifications(new_items)
                for item in new_items:
                    self.db.mark_as_notified(item['id'])
            logging.info(f"News check complete: {len(new_items)} new items")
            return new_items
        except Exception as e:
            logging.error(f"News check failed: {e}")
            return []
    
    def start_scheduler(self):
        """Start the scheduled monitoring"""
        logging.info("🕐 Starting scheduled monitoring...")
        
        # Schedule different types of checks
        schedule.every(RSS_CHECK_INTERVAL).minutes.do(self.run_rss_check)
        schedule.every(GITHUB_CHECK_INTERVAL).minutes.do(self.run_github_check)
        schedule.every(NEWS_CHECK_INTERVAL).minutes.do(self.run_news_check)
        
        # Schedule a full check every 2 hours
        schedule.every(2).hours.do(self.run_full_check)
        
        logging.info(f"📅 Scheduled checks:")
        logging.info(f"  - RSS feeds: every {RSS_CHECK_INTERVAL} minutes")
        logging.info(f"  - GitHub repos: every {GITHUB_CHECK_INTERVAL} minutes")
        logging.info(f"  - News sources: every {NEWS_CHECK_INTERVAL} minutes")
        logging.info(f"  - Full check: every 2 hours")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logging.info("👋 Monitoring stopped by user")
        except Exception as e:
            logging.error(f"Scheduler error: {e}")
    
    def get_recent_items(self, days=7):
        """Get recent items from the database"""
        return self.db.get_recent_items(days)
    
    def send_test_notification(self):
        """Send a test notification"""
        return self.notification_manager.send_test_notification()

def rss_monitor_config_count():
    """Get count of RSS feed configurations"""
    from config import AI_SOURCES
    return AI_SOURCES.get('rss_feeds', [])

def github_config_count():
    """Get count of GitHub repo configurations"""
    from config import AI_SOURCES
    return AI_SOURCES.get('github_repos', [])

def news_config_count():
    """Get count of news source configurations"""
    from config import AI_SOURCES
    return AI_SOURCES.get('news_sources', [])

def direct_config_count():
    """Get count of direct source configurations"""
    from config import AI_SOURCES
    return AI_SOURCES.get('direct_checks', [])

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Updates Monitor')
    parser.add_argument('--run-once', action='store_true', 
                        help='Run a single check and exit')
    parser.add_argument('--test-notification', action='store_true',
                        help='Send a test notification and exit')
    parser.add_argument('--recent', type=int, metavar='DAYS',
                        help='Show recent items from the last N days')
    parser.add_argument('--rss-only', action='store_true',
                        help='Check only RSS feeds')
    parser.add_argument('--github-only', action='store_true',
                        help='Check only GitHub repositories')
    parser.add_argument('--news-only', action='store_true',
                        help='Check only news sources')
    
    args = parser.parse_args()
    
    monitor = AIMonitor()
    
    if args.test_notification:
        logging.info("📧 Sending test notification...")
        success = monitor.send_test_notification()
        if success:
            logging.info("✅ Test notification sent successfully!")
        else:
            logging.error("❌ Test notification failed!")
        return
    
    if args.recent:
        logging.info(f"📋 Showing recent items from the last {args.recent} days...")
        recent_items = monitor.get_recent_items(args.recent)
        if recent_items:
            for item in recent_items:
                print(f"\n📍 {item['source_type']} - {item['source_name']}")
                print(f"📰 {item['title']}")
                if item['url']:
                    print(f"🔗 {item['url']}")
                print(f"📅 {item['discovered_date']}")
                print("-" * 50)
        else:
            logging.info("No recent items found")
        return
    
    if args.run_once:
        if args.rss_only:
            logging.info("🔍 Running single RSS check...")
            monitor.run_rss_check()
        elif args.github_only:
            logging.info("🔍 Running single GitHub check...")
            monitor.run_github_check()
        elif args.news_only:
            logging.info("🔍 Running single news check...")
            monitor.run_news_check()
        else:
            logging.info("🔍 Running single full check...")
            monitor.run_full_check()
        return
    
    # Default: start scheduled monitoring
    logging.info("🚀 Starting AI Updates Monitor...")
    logging.info("Press Ctrl+C to stop")
    monitor.start_scheduler()

if __name__ == "__main__":
    main() 