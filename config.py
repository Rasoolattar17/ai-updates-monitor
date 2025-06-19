import os
from dotenv import load_dotenv

load_dotenv()

# Notification settings
EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')

DESKTOP_NOTIFICATIONS = os.getenv('DESKTOP_NOTIFICATIONS', 'true').lower() == 'true'

# Monitoring intervals (in minutes)
RSS_CHECK_INTERVAL = int(os.getenv('RSS_CHECK_INTERVAL', '30'))
GITHUB_CHECK_INTERVAL = int(os.getenv('GITHUB_CHECK_INTERVAL', '60'))
NEWS_CHECK_INTERVAL = int(os.getenv('NEWS_CHECK_INTERVAL', '45'))

# AI Sources to monitor
AI_SOURCES = {
    'rss_feeds': [
        {
            'name': 'OpenAI Blog',
            'url': 'https://openai.com/blog/rss.xml',
            'keywords': ['gpt', 'chatgpt', 'dalle', 'api', 'update', 'release']
        },
        {
            'name': 'AI News - MIT Technology Review',
            'url': 'https://www.technologyreview.com/feed/',
            'keywords': ['ai', 'artificial intelligence', 'chatgpt', 'claude', 'cursor', 'perplexity']
        },
        {
            'name': 'Hacker News - AI',
            'url': 'https://hnrss.org/frontpage?q=AI+OR+artificial+intelligence+OR+chatgpt+OR+claude+OR+cursor+OR+perplexity',
            'keywords': ['ai', 'artificial intelligence', 'chatgpt', 'claude', 'cursor', 'perplexity']
        },

    ],
    'github_repos': [
        {
            'name': 'microsoft/vscode',
            'description': 'VS Code (for Cursor AI updates)',
            'track_releases': True
        },
        {
            'name': 'openai/openai-python',
            'description': 'OpenAI Python Library',
            'track_releases': True
        },
        {
            'name': 'microsoft/semantic-kernel',
            'description': 'Microsoft Semantic Kernel',
            'track_releases': True
        },
        {
            'name': 'langchain-ai/langchain',
            'description': 'LangChain Framework',
            'track_releases': True
        }
    ],
    'news_sources': [
        {
            'name': 'AI News - The Verge',
            'url': 'https://www.theverge.com/ai-artificial-intelligence',
            'selector': 'article h2 a',
            'keywords': ['chatgpt', 'cursor', 'perplexity', 'ai', 'openai', 'anthropic']
        },
        {
            'name': 'TechCrunch AI',
            'url': 'https://techcrunch.com/category/artificial-intelligence/',
            'selector': 'h2 a',
            'keywords': ['chatgpt', 'cursor', 'perplexity', 'ai', 'openai', 'anthropic']
        }
    ],
    'direct_checks': [
        {
            'name': 'Anthropic News',
            'url': 'https://www.anthropic.com/news',
            'selector': 'h3 a, .card-title a, article h2 a',
            'keywords': ['claude', 'update', 'release', 'new', 'feature', 'model']
        },
        {
            'name': 'Cursor AI',
            'url': 'https://cursor.sh/',
            'selector': '.changelog, .updates, .news, h2, h3',
            'keywords': ['update', 'release', 'new', 'feature', 'changelog']
        },
        {
            'name': 'Perplexity Blog',
            'url': 'https://blog.perplexity.ai/',
            'selector': 'article h2, .blog-post-title, h1 a, .post-title',
            'keywords': ['update', 'release', 'new', 'feature', 'model']
        },
        {
            'name': 'OpenAI News',
            'url': 'https://openai.com/news/',
            'selector': 'h3 a, .card-title a, article h2 a',
            'keywords': ['gpt', 'chatgpt', 'dalle', 'api', 'update', 'release']
        }
    ]
}

# Database settings
DATABASE_PATH = 'ai_monitoring.db' 