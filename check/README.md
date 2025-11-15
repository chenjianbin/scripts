### 根据需要设置环境变量
> vim /etc/profile

```
# Telegram
export TELEGRAM_BOT_TOKEN="00000000:AxxxxxxxxxxxxxxxxxxxxxxY"
export TELEGRAM_CHAT_ID="-11111111"

# Alicloud
export ALIBABA_CLOUD_ACCESS_KEY_ID="xxxxxxxxxxxxx"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="xxxxxxxxxxxxxx"

```

### 添加需要检查是否过期域名
> vim domains.txt

```
baidu.com
jd.com
```

### 添加需要检查ssl过期的域名
> vim ssl_domains.txt

```
www.baidu.com
order.jd.com
```

### 设置crontab
```
一定需要bash -lc,否则无法加载脚本所需环境变量
30 4 * * * bash -lc "python3 /data0/scripts/check/check_ssl_expiry.py"
40 4 * * * bash -lc "python3 /data0/scripts/check/check_domain_expiry.py"
40 9 * * * bash -lc "python3 /data0/scripts/check/check_alicloud_balance.py"
```
