# X (Twitter) API Setup Guide

## Quick Setup for Direct Tweet Access

### Step 1: Get X Developer Access
1. Go to [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard)
2. Sign in with your Twitter/X account
3. Apply for developer access (usually approved quickly)
4. Create a new "Project" and "App"

### Step 2: Get Your Bearer Token
1. In your app dashboard, click "Keys and Tokens"
2. Under "Bearer Token", click "Generate"
3. Copy the Bearer Token (starts with `AAAA...`)

### Step 3: Add to Environment
1. Open your `.env` file
2. Add this line:
   ```
   X_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...
   ```
3. Save the file

### Step 4: Test
Run the monitor to test X API access:
```bash
py twitter_monitor.py
```

## What You Get with X API

✅ **Direct tweet access** from @OpenAI, @AnthropicAI, @sama, @cursor_ai, @perplexity_ai  
✅ **Real-time tweets** instead of news reports about tweets  
✅ **24-hour monitoring** - checks for tweets from last 24 hours  
✅ **Keyword filtering** - only AI-related content  
✅ **500,000 tweets/month** limit (more than enough)  

## Fallback Without X API

If you don't set up X API, the system still works by:
- Monitoring news reports about Twitter activity
- Checking social media aggregators (Hacker News, Reddit)
- Finding discussions about AI companies' social media posts

## API Rate Limits

- **Free Tier**: 500,000 tweets per month
- **Per Account**: 100 requests per 15 minutes
- **Daily Check**: Uses ~5-10 requests per day
- **Perfect for** once-daily monitoring

## Cost

- **Free tier** covers daily monitoring completely
- **No payment required** for this use case 