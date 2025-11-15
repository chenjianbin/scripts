import whois
import os
import datetime
import asyncio
from telegram import Bot

# 从文件中读取域名列表
def read_domains(file_path):
    with open(file_path, 'r') as file:
        domains = file.read().splitlines()
    return domains

# 获取域名的到期时间
def get_domain_expiry_date(domain):
    domain_info = whois.whois(domain)
    expiry_date = domain_info.expiration_date
    if isinstance(expiry_date, list):
        expiry_date = expiry_date[0]
    return expiry_date

# 发送 Telegram 消息
async def send_telegram_message(token, chat_id, message):
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)

# 检查域名到期时间并发送消息
async def check_domains(domains, token, chat_id):
    for domain in domains:
        try:
            expiry_date = get_domain_expiry_date(domain)
            if expiry_date:
                days_to_expiry = (expiry_date - datetime.datetime.utcnow()).days
                if days_to_expiry < 30:
                    message = f"Warning: The domain {domain} will expire in {days_to_expiry} days."
                    await send_telegram_message(token, chat_id, message)
                    print(message)
                else:
                    print(f"The domain {domain} is valid for {days_to_expiry} more days.")
            else:
                print(f"Could not determine the expiry date for {domain}.")
        except Exception as e:
            print(f"Failed to get domain information for {domain}: {e}")

if __name__ == '__main__':
    # 配置参数
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

    domain_file_path = f"{os.path.dirname(os.path.abspath(__file__))}/domains.txt"
    domains = read_domains(domain_file_path)
    asyncio.run(check_domains(domains, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID))

