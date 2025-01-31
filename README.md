# Telegram Bot for News RSS feeds  
Read RSS feeds and post news to Telegram Channel 

## Usage  
1. Create filr feeds.json with format:  
[  
    {  
        "channel": "Latest News",  # Telegram channel name  
        "chat_id": "-1002269414045",   # Telegram channel id  
        "url": "https://guardian.ng/feed/"  # Url of RSS feed  
    }  
]  
2. Run script  
python main.py  