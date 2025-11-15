### 设置环境变量
> vim /etc/profile

```
# Telegram
export TELEGRAM_BOT_TOKEN="00000000:AxxxxxxxxxxxxxxxxxxxxxxY"
export TELEGRAM_CHAT_ID="-11111111"

# Slack
export SLACK_URL="https://hooks.slack.com/services/xxxxxx/xxxxx/xxxxxxxxxxxx"
```

### 设置crontab
```
一定需要bash -lc,否则无法加载脚本所需环境变量
00 6 * * * bash -lc "python3 /data0/scripts/mysql/backup/backup.py &>/dev/null"
```
