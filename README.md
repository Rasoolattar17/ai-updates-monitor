# 🤖 AI Updates Monitor

A comprehensive monitoring system that tracks updates and new features from major AI companies and tools including ChatGPT, Cursor AI, Perplexity, and other significant AI developments.

## Features

- **Multiple Source Monitoring**: Tracks RSS feeds, GitHub releases, news sources, and direct website checks
- **Smart Notifications**: Email, desktop notifications, and console alerts
- **Duplicate Prevention**: Avoids sending the same notification twice
- **Configurable Intervals**: Customizable monitoring frequencies for different source types
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Database Storage**: SQLite database to track monitored items
- **Flexible Scheduling**: Different check intervals for different source types

## Monitored Sources

### RSS Feeds
- OpenAI Blog
- Anthropic Blog (Claude)
- Google AI Blog (Bard/Gemini)

### GitHub Repositories
- Microsoft VS Code (Cursor AI updates)
- OpenAI Python Library
- Microsoft Semantic Kernel
- LangChain Framework

### News Sources
- The Verge AI News
- TechCrunch AI Category

### Direct Website Checks
- Cursor AI official site
- Perplexity AI blog

## Installation

1. **Clone or download the files to your directory**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your settings**:
   ```bash
   cp env_example.txt .env
   ```
   Edit the `.env` file with your preferred settings.

## Configuration

### Email Notifications (Optional)
To enable email notifications, set these in your `.env` file:
```env
EMAIL_ENABLED=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=notification_recipient@gmail.com
```

**For Gmail users**: You'll need to use an App Password instead of your regular password. [Learn how to create an App Password](https://support.google.com/accounts/answer/185833).

### Desktop Notifications
Desktop notifications are enabled by default. To disable:
```env
DESKTOP_NOTIFICATIONS=false
```

### Monitoring Intervals
Customize how often each source type is checked (in minutes):
```env
RSS_CHECK_INTERVAL=30
GITHUB_CHECK_INTERVAL=60
NEWS_CHECK_INTERVAL=45
```

## Usage

### Start Continuous Monitoring
```bash
py main.py
```
This starts the scheduler and monitors all sources continuously.

### One-Time Check
```bash
# Check all sources once
py main.py --run-once

# Check only RSS feeds
py main.py --run-once --rss-only

# Check only GitHub repositories
py main.py --run-once --github-only

# Check only news sources
py main.py --run-once --news-only
```

### Test Notifications
```bash
py main.py --test-notification
```

### View Recent Items
```bash
# Show items from the last 7 days
py main.py --recent 7

# Show items from the last 30 days
py main.py --recent 30
```

## Customizing Sources

You can modify the monitored sources by editing `config.py`:

### Adding New RSS Feeds
```python
{
    'name': 'New AI Company Blog',
    'url': 'https://example.com/rss.xml',
    'keywords': ['ai', 'update', 'release']
}
```

### Adding New GitHub Repositories
```python
{
    'name': 'owner/repository-name',
    'description': 'Description of what this repo tracks',
    'track_releases': True
}
```

### Adding New News Sources
```python
{
    'name': 'News Source Name',
    'url': 'https://example.com/ai-news',
    'selector': 'article h2 a',  # CSS selector for articles
    'keywords': ['ai', 'chatgpt', 'cursor']
}
```

## Notification Examples

### Desktop Notification
![Desktop notification showing "🤖 AI Updates Alert - 3 new AI updates found!"]

### Email Notification
- **Subject**: 🤖 AI Updates Alert - 3 new items found
- **Content**: Formatted HTML email with source, title, content preview, and links

### Console Output
```
============================================================
🤖 NEW AI UPDATES DETECTED - 3 items
============================================================

📍 Source: OpenAI Blog
📰 Title: Introducing GPT-4 Turbo with Vision
📝 Content: We're excited to announce GPT-4 Turbo with vision capabilities...
🔗 URL: https://openai.com/blog/gpt-4-turbo-with-vision
📅 Published: 2024-01-15 10:30:00
----------------------------------------
```

## File Structure

```
ai-monitor/
├── main.py              # Main application entry point
├── config.py            # Configuration and source definitions
├── database.py          # Database operations
├── monitors.py          # Source monitoring logic
├── notifications.py     # Notification handling
├── requirements.txt     # Python dependencies
├── env_example.txt      # Example environment configuration
├── README.md           # This file
├── ai_monitoring.db    # SQLite database (created automatically)
└── ai_monitoring.log   # Log file (created automatically)
```

## Troubleshooting

### Common Issues

1. **Email notifications not working**:
   - Verify your email credentials
   - For Gmail, use an App Password
   - Check firewall/antivirus settings

2. **Desktop notifications not appearing**:
   - On Windows: Check notification settings
   - On Linux: Ensure `notify-send` is available
   - On macOS: Grant notification permissions

3. **No new items found**:
   - Check your internet connection
   - Some sources may be temporarily unavailable
   - Check the log file for detailed error messages

4. **High memory usage**:
   - The system automatically cleans up old items after 30 days
   - You can manually clean the database by deleting `ai_monitoring.db`

### Logs

Check `ai_monitoring.log` for detailed information about:
- Which sources were checked
- Any errors encountered
- Items found and notifications sent

## Customization Tips

### Adding Your Own Keywords
Modify the `keywords` arrays in `config.py` to focus on specific topics:
```python
'keywords': ['gpt-5', 'claude-3', 'cursor-composer', 'perplexity-pro']
```

### Changing Check Intervals
For more frequent monitoring of important sources:
```env
RSS_CHECK_INTERVAL=15  # Check RSS feeds every 15 minutes
```

### Adding Custom Sources
The system is designed to be extensible. You can add new monitor types by:
1. Creating a new class in `monitors.py`
2. Adding configuration in `config.py`
3. Integrating with the main loop in `main.py`

## Security Notes

- Store sensitive credentials in the `.env` file (never commit this to version control)
- The system respects robots.txt and implements reasonable delays between requests
- Email passwords should use App Passwords when available

## Contributing

Feel free to:
- Add new AI sources to monitor
- Improve the notification formatting
- Add new notification methods (Slack, Discord, etc.)
- Enhance the web scraping logic

## License

This project is open source and available under the MIT License.

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy and edit the environment configuration:
```bash
copy env_example.txt .env
```

Edit `.env` with your settings:
- **Email notifications**: Configure SMTP settings for email alerts
- **X API (Optional)**: For direct tweet access instead of news-based monitoring

### 3. X (Twitter) API Setup (Optional but Recommended)
For direct access to tweets (more reliable than news sources):

<!-- 1. **Create X Developer Account**:
   - Go to [developer.twitter.com](https://developer.twitter.com)
   - Apply for developer access
   - Create a new app

2. **Get Bearer Token**:
   - In your app dashboard, go to "Keys and Tokens"
   - Generate "Bearer Token"
   - Add it to your `.env` file as `X_BEARER_TOKEN=your_token_here`

3. **API Limits**: 
   - Free tier: 500,000 tweets/month (perfect for daily monitoring)
   - 100 requests per 15 minutes per endpoint

**Without X API**: The system will still work using news sources and social media aggregators to find Twitter mentions and discussions.  -->