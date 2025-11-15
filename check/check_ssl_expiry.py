import os
import ssl
import socket
import datetime
import asyncio
from OpenSSL import crypto
from telegram import Bot

# 从文件中读取域名列表
def read_domains(file_path):
    with open(file_path, 'r') as file:
        domains = file.read().splitlines()
    return domains

# 获取 SSL 证书的到期时间
def get_ssl_expiry_date(domain, port=443):
    context = ssl.create_default_context()
    with socket.create_connection((domain, port)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            cert_bin = ssock.getpeercert(True)
            x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_bin)
            expiry_date = datetime.datetime.strptime(x509.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ')
    return expiry_date

# 发送 Telegram 消息
async def send_telegram_message(token, chat_id, message):
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)

# 检查域名 SSL 证书到期时间并发送消息
async def check_domains(domains, token, chat_id):
    for domain in domains:
        try:
            expiry_date = get_ssl_expiry_date(domain)
            days_to_expiry = (expiry_date - datetime.datetime.utcnow()).days
            if days_to_expiry < 10:
                message = f"Warning: The SSL certificate for {domain} will expire in {days_to_expiry} days."
                await send_telegram_message(token, chat_id, message)
                print(message)
            else:
                print(f"The SSL certificate for {domain} is valid for {days_to_expiry} more days.")
        except Exception as e:
            print(f"Failed to get SSL certificate for {domain}: {e}")

if __name__ == '__main__':
    # 配置参数
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

    domain_file_path = f"{os.path.dirname(os.path.abspath(__file__))}/ssl_domains.txt"
    domains = read_domains(domain_file_path)
    asyncio.run(check_domains(domains, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID))



