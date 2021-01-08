# Telegram bot for getting top posts from Instagram  
Telegram bot for get top N posts and video by likes and viewsfrom instagram account

[Implementation](https://t.me/top_insta_posts_bot)

## Getting Started

1. Create own telegram bot. Manual: https://core.telegram.org/bots
2. Insert your bot token to config.yml.
3. Register on https://chatbase.com/ for storing bot usage statistics and insert chatbase token
4. Install requirements.
5. Run main.py.
```
python3 main.py
```
If you want to run this bot on the server, you can run:
```
nohup python3 main.py & tail -f nohup.out
```
## Hosting this bot on pythonanywhere.com

1. Sign up on [pythonanywhere.com](https://www.pythonanywhere.com/).
2. Upload files to server.
```
git clone https://github.com/lbulygin/telegram-top-posts-bot
```
3. Add always-on task:
```
python3 /home/{YOUR_USERNAME}/telegram-top-posts-bot/main.py
``` 
4. Add daily scheduled task for purging messages limits:
```
rm -rf /home/{YOUR_USERNAME}/telegram-top-posts/db_users_limits.json
```

## Database of users and mailing

This bot saves usernames and their chat_id to *db_users.json* for sending messages.

Users have messages limits in config.yml (messages_limit parameter). Limits are stored in  *db_users_limits.json*.

You can send a message to all your users with this command:
```
python3 mailing_users.py --message "YOUR MESSAGE"
```

## Instagram Authorization 
Same as there: https://github.com/lbulygin/telegram-saver-bot