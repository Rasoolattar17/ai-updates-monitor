#!/usr/bin/env python3
"""
Show Recent AI News from Database
"""

import sqlite3
import sys
import os

def show_recent_news():
    """Show recent news from the database"""
    db_path = 'ai_monitoring.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found. The monitoring system hasn't been run yet.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='monitored_items'
        """)
        
        if not cursor.fetchone():
            print("❌ No monitored_items table found in database.")
            conn.close()
            return
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM monitored_items")
        total_count = cursor.fetchone()[0]
        
        print(f"🤖 AI Monitoring Database Status")
        print("=" * 50)
        print(f"📊 Total items in database: {total_count}")
        print()
        
        # Get recent items from last 30 days
        cursor.execute("""
            SELECT source_name, title, url, discovered_date, content
            FROM monitored_items 
            WHERE discovered_date >= datetime('now', '-30 days')
            ORDER BY discovered_date DESC 
            LIMIT 15
        """)
        
        recent_items = cursor.fetchall()
        
        if recent_items:
            print(f"📰 Recent AI Updates (Last 30 days) - {len(recent_items)} items:")
            print("=" * 50)
            
            for i, item in enumerate(recent_items, 1):
                print(f"{i}. 📍 Source: {item[0]}")
                print(f"   📰 Title: {item[1]}")
                if item[4]:  # content
                    content_preview = item[4][:100] + "..." if len(item[4]) > 100 else item[4]
                    print(f"   📝 Preview: {content_preview}")
                print(f"   🔗 URL: {item[2]}")
                print(f"   📅 Date: {item[3]}")
                print("-" * 40)
        else:
            print("📭 No recent updates found in the last 30 days.")
            
            # Check for any items at all
            cursor.execute("SELECT COUNT(*) FROM monitored_items")
            if cursor.fetchone()[0] > 0:
                print("💡 There are older items in the database. Try running the monitoring system to get fresh updates.")
        
        # Show sources breakdown
        cursor.execute("""
            SELECT source_name, COUNT(*) as count 
            FROM monitored_items 
            GROUP BY source_name 
            ORDER BY count DESC
        """)
        
        sources = cursor.fetchall()
        
        if sources:
            print("\n📊 Items by Source:")
            print("=" * 30)
            for source, count in sources:
                print(f"  {source}: {count} items")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def main():
    print("🤖 AI News Database Viewer")
    print("=" * 50)
    show_recent_news()
    
    print("\n💡 To get fresh updates, run the full monitoring system:")
    print("   python main.py --run-once")

if __name__ == "__main__":
    main() 