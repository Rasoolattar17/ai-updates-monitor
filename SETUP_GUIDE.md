# 🚀 Quick Setup Guide

This guide will help you set up the AI Updates Monitor after cloning from GitHub.

## Prerequisites

- Python 3.7 or higher
- Internet connection
- Email account for notifications (optional)

## Step-by-Step Setup

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd ai-updates-monitor
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Your Settings

#### Create Environment File
```bash
# Windows
copy env_example.txt .env

# Linux/Mac
cp env_example.txt .env
```

#### Edit Your .env File
Open `.env` in any text editor and configure:

**Required Settings:**
```env
# Enable/disable email notifications
EMAIL_ENABLED=true

# Desktop notifications (works on all platforms)
DESKTOP_NOTIFICATIONS=true
```

**Email Configuration (if EMAIL_ENABLED=true):**
```env
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=where-to-send@gmail.com
```

**Popular Email Providers:**
- **Gmail**: `smtp.gmail.com:587` (use App Password)
- **Outlook**: `smtp-mail.outlook.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Zoho**: `smtp.zoho.com:465`

### 4. Test Your Setup
```bash
# Test notifications
py main.py --test-notification

# Run a single check
py main.py --run-once
```

### 5. Start Monitoring
```bash
# Start continuous monitoring
py main.py
```

## Gmail Setup (Most Common)

1. **Enable 2-Factor Authentication** on your Google account
2. **Create App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use in .env**:
   ```env
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=the-16-character-app-password
   ```

## X/Twitter API Setup (Optional)

For direct tweet access instead of news-based monitoring:

1. **Apply for X Developer Account**: https://developer.twitter.com/
2. **Create App** and get Bearer Token
3. **Add to .env**:
   ```env
   X_BEARER_TOKEN=your-bearer-token-here
   ```

**Note**: X API costs $100/month for basic access. The system works fine without it using news sources.

## Troubleshooting

### Email Not Working?
- Check your email/password
- For Gmail: Use App Password, not regular password
- Check spam folder for test emails
- Try different SMTP settings

### No Notifications?
- Check that `EMAIL_ENABLED=true` or `DESKTOP_NOTIFICATIONS=true`
- Run `py main.py --test-notification` to test
- Check logs in `ai_monitoring.log`

### Permission Errors?
```bash
# Windows: Run as administrator
# Linux/Mac: Check file permissions
chmod +x main.py
```

## Quick Commands

```bash
# One-time check all sources
py main.py --run-once

# Check only RSS feeds
py main.py --run-once --rss-only

# Test email notification
py main.py --test-notification

# View recent finds
py main.py --recent 7

# Start monitoring (runs continuously)
py main.py
```

## Security Notes

- ✅ **DO**: Keep your `.env` file private
- ❌ **DON'T**: Commit `.env` to version control
- ✅ **DO**: Use App Passwords for email
- ✅ **DO**: Regularly update your credentials

## Need Help?

- Check `ai_monitoring.log` for detailed error messages
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Test individual components with `--test-notification` and `--run-once`

---

**Happy Monitoring! 🤖** You'll now receive notifications about the latest AI developments from ChatGPT, Cursor AI, Perplexity, and more! 