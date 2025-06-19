import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from plyer import notification
from config import (
    EMAIL_ENABLED, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, 
    EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_TO,
    DESKTOP_NOTIFICATIONS
)

class NotificationManager:
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for notifications"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_monitoring.log'),
                logging.StreamHandler()
            ]
        )
    
    def format_items_for_email(self, items):
        """Format items for email notification with exciting template"""
        if not items:
            return "No new AI updates found."
        
        html_content = """
        <html>
        <head>
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container { 
                    max-width: 600px; 
                    margin: 20px auto; 
                    background: white; 
                    border-radius: 15px; 
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }
                .header { 
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); 
                    color: white; 
                    padding: 30px 20px; 
                    text-align: center; 
                }
                .header h1 { 
                    margin: 0; 
                    font-size: 2.2em; 
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    animation: pulse 2s infinite;
                }
                .subtitle { 
                    font-size: 1.1em; 
                    margin-top: 10px; 
                    opacity: 0.9;
                }
                .content-area { padding: 30px 20px; }
                .item { 
                    margin: 25px 0; 
                    padding: 20px; 
                    border-radius: 12px;
                    background: linear-gradient(135deg, #f8f9ff 0%, #f0f2f5 100%);
                    border-left: 5px solid #3498db; 
                    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
                    transition: transform 0.3s ease;
                }
                .item:hover { transform: translateY(-2px); }
                .source { 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 8px 15px;
                    border-radius: 20px;
                    font-size: 0.85em; 
                    font-weight: bold;
                    display: inline-block;
                    margin-bottom: 12px;
                }
                .title { 
                    color: #2c3e50; 
                    font-size: 1.3em; 
                    font-weight: bold; 
                    margin: 10px 0; 
                    line-height: 1.4;
                }
                .content { 
                    color: #34495e; 
                    margin: 15px 0; 
                    font-size: 1.05em;
                    line-height: 1.6;
                }
                .url-button { 
                    display: inline-block;
                    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                    color: white !important; 
                    text-decoration: none;
                    padding: 12px 25px;
                    border-radius: 25px;
                    margin: 10px 0;
                    font-weight: bold;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
                }
                .url-button:hover { 
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
                }
                .date { 
                    color: #7f8c8d; 
                    font-size: 0.9em; 
                    background: #ecf0f1;
                    padding: 5px 10px;
                    border-radius: 10px;
                    display: inline-block;
                    margin-top: 10px;
                }
                .footer {
                    background: #2c3e50;
                    color: white;
                    text-align: center;
                    padding: 20px;
                    font-size: 0.9em;
                }
                .emoji-large { font-size: 1.3em; }
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 BREAKING AI NEWS! 🚀</h1>
                    <div class="subtitle">🔥 Fresh AI developments just dropped! 🔥</div>
                </div>
                <div class="content-area">
                    <p style="font-size: 1.2em; color: #2c3e50; text-align: center; margin-bottom: 30px;">
                        <strong>⚡ Get ready to be amazed! Here's what's happening in AI right now:</strong>
                    </p>
        """
        
        text_content = """
🚀 BREAKING AI NEWS! 🚀
🔥 Fresh AI developments just dropped! 🔥

⚡ Get ready to be amazed! Here's what's happening in AI right now:

"""
        
        for item in items:
            # HTML version
            html_content += f"""
                    <div class="item">
                        <div class="source"><span class="emoji-large">🎯</span> {item.get('source', 'Unknown')}</div>
                        <div class="title"><span class="emoji-large">⚡</span> {item.get('title', 'No title')}</div>
            """
            
            if item.get('content'):
                html_content += f'<div class="content"><span class="emoji-large">📝</span> {item.get("content")}</div>'
            
            if item.get('url'):
                html_content += f'<div><a href="{item.get("url")}" class="url-button">🚀 Dive In & Explore!</a></div>'
            
            if item.get('published_date'):
                html_content += f'<div class="date"><span class="emoji-large">⏰</span> {item.get("published_date")}</div>'
            
            html_content += "</div>"
            
            # Text version
            text_content += f"🎯 Source: {item.get('source', 'Unknown')}\n"
            text_content += f"⚡ BREAKING: {item.get('title', 'No title')}\n"
            
            if item.get('content'):
                text_content += f"📝 Details: {item.get('content')}\n"
            
            if item.get('url'):
                text_content += f"🚀 Link: {item.get('url')}\n"
            
            if item.get('published_date'):
                text_content += f"⏰ When: {item.get('published_date')}\n"
            
            text_content += "\n" + "🔥"*20 + "\n\n"
        
        html_content += """
                </div>
                <div class="footer">
                    <p>🤖 Powered by Your AI Monitoring System 🤖</p>
                    <p>Stay ahead of the AI revolution! 🌟</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content += """
🤖 Powered by Your AI Monitoring System 🤖
Stay ahead of the AI revolution! 🌟

Don't miss out - the future is happening NOW! 🚀
        """
        
        return html_content, text_content
    
    def send_email_notification(self, items):
        """Send email notification with new items"""
        if not EMAIL_ENABLED or not EMAIL_USERNAME or not EMAIL_PASSWORD or not EMAIL_TO:
            logging.warning("Email notifications are not properly configured")
            return False
        
        if not items:
            return True
        
        try:
            html_content, text_content = self.format_items_for_email(items)
            
            # Create message
            msg = MIMEMultipart('alternative')
            subject_variations = [
                f"🚀 BREAKING: {len(items)} Hot AI Updates Just Dropped! 🔥",
                f"⚡ AI ALERT: {len(items)} Game-Changing Updates! 🎯",
                f"🔥 HOT OFF THE PRESS: {len(items)} AI Breakthroughs! ⚡",
                f"🚀 AI REVOLUTION UPDATE: {len(items)} Fresh Developments! 🌟",
                f"⚡ URGENT AI NEWS: {len(items)} Major Updates Inside! 🔥"
            ]
            import random
            msg['Subject'] = random.choice(subject_variations)
            msg['From'] = EMAIL_USERNAME
            msg['To'] = EMAIL_TO
            
            # Add both text and HTML versions
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            if EMAIL_SMTP_PORT == 465:
                # Use SMTP_SSL for port 465 (like Zoho)
                with smtplib.SMTP_SSL(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
                    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                    server.send_message(msg)
            else:
                # Use SMTP with STARTTLS for port 587 (like Gmail)
                with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
                    server.starttls()
                    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                    server.send_message(msg)
            
            logging.info(f"Email notification sent successfully for {len(items)} items")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")
            return False
    
    def send_desktop_notification(self, items):
        """Send exciting desktop notification"""
        if not DESKTOP_NOTIFICATIONS or not items:
            return True
        
        try:
            count = len(items)
            
            # Exciting title variations
            title_variations = [
                f"🚀 BREAKING: {count} AI Updates!",
                f"⚡ HOT AI NEWS: {count} Updates!",
                f"🔥 AI ALERT: {count} Fresh Updates!",
                f"🎯 URGENT: {count} AI Breakthroughs!",
                f"🌟 AMAZING: {count} AI Updates!"
            ]
            
            import random
            title = random.choice(title_variations)
            
            if count == 1:
                message = f"🚀 {items[0].get('title', 'Unknown')[:60]}..."
            else:
                exciting_messages = [
                    f"🔥 {count} game-changing AI developments just dropped!",
                    f"⚡ {count} hot AI updates are waiting for you!",
                    f"🚀 {count} breakthrough AI updates discovered!",
                    f"🎯 {count} must-see AI developments found!"
                ]
                message = random.choice(exciting_messages)
            
            notification.notify(
                title=title,
                message=message,
                app_name="🤖 AI Revolution Monitor",
                timeout=15  # Longer timeout for excitement
            )
            
            logging.info(f"🚀 Exciting desktop notification sent for {count} items!")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send desktop notification: {e}")
            return False
    
    def log_console_notification(self, items):
        """Log notification to console"""
        if not items:
            logging.info("No new AI updates found")
            return True
        
        try:
            logging.info(f"\n{'='*60}")
            logging.info(f"🤖 NEW AI UPDATES DETECTED - {len(items)} items")
            logging.info(f"{'='*60}")
            
            for item in items:
                logging.info(f"\n📍 Source: {item.get('source', 'Unknown')}")
                logging.info(f"📰 Title: {item.get('title', 'No title')}")
                
                if item.get('content'):
                    content = item.get('content')
                    if len(content) > 100:
                        content = content[:97] + "..."
                    logging.info(f"📝 Content: {content}")
                
                if item.get('url'):
                    logging.info(f"🔗 URL: {item.get('url')}")
                
                if item.get('published_date'):
                    logging.info(f"📅 Published: {item.get('published_date')}")
                
                logging.info("-" * 40)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to log console notification: {e}")
            return False
    
    def send_notifications(self, items):
        """Send all configured notifications"""
        if not items:
            logging.info("No new items to notify about")
            return True
        
        success_count = 0
        total_methods = 0
        
        # Console notification (always enabled)
        total_methods += 1
        if self.log_console_notification(items):
            success_count += 1
        
        # Desktop notification
        if DESKTOP_NOTIFICATIONS:
            total_methods += 1
            if self.send_desktop_notification(items):
                success_count += 1
        
        # Email notification
        if EMAIL_ENABLED:
            total_methods += 1
            if self.send_email_notification(items):
                success_count += 1
        
        logging.info(f"Notifications sent: {success_count}/{total_methods} methods successful")
        return success_count > 0
    
    def send_test_notification(self):
        """Send an exciting test notification to verify configuration"""
        test_items = [{
            'id': 'test',
            'source': '🧪 AI Monitor Test Lab',
            'title': '🚀 SYSTEM TEST: Your AI Monitoring is LIVE and Ready!',
            'url': 'https://example.com',
            'content': '🎉 Congratulations! Your AI monitoring system is working perfectly and ready to catch all the exciting AI developments as they happen. Get ready for the future! 🌟',
            'published_date': datetime.now()
        }]
        
        logging.info("🚀 Sending exciting test notification...")
        return self.send_notifications(test_items)
    
    def send_summary_notification(self, summary_data):
        """Send a summary notification with statistics"""
        try:
            total_items = summary_data.get('total_new_items', 0)
            sources_checked = summary_data.get('sources_checked', 0)
            errors = summary_data.get('errors', 0)
            
            if total_items == 0:
                logging.info(f"Monitoring complete: {sources_checked} sources checked, no new items found")
                return True
            
            # Create summary message
            summary_msg = f"""
🤖 AI MONITORING SUMMARY
{'='*30}
📊 Total new items found: {total_items}
🔍 Sources checked: {sources_checked}
❌ Errors encountered: {errors}
🕐 Check completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            logging.info(summary_msg)
            
            # Send desktop notification for summary if there were new items
            if DESKTOP_NOTIFICATIONS and total_items > 0:
                notification.notify(
                    title="🤖 AI Monitoring Complete",
                    message=f"Found {total_items} new items across {sources_checked} sources",
                    app_name="AI Monitor",
                    timeout=5
                )
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to send summary notification: {e}")
            return False 