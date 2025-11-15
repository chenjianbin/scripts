import json
import os
import requests
from alibabacloud_bssopenapi20171214.client import Client
from alibabacloud_tea_openapi import models as open_api_models

def main():
    """
    阿里云余额监控函数
    """
    
    # 配置参数（建议使用环境变量）
    ACCESS_KEY_ID = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID')
    ACCESS_KEY_SECRET = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    
    # 告警阈值配置
    ALERT_THRESHOLDS = [
        {'level': '严重', 'amount': 50, 'emoji': '🚨'},
        {'level': '警告', 'amount': 100, 'emoji': '⚠️'},
        {'level': '提醒', 'amount': 200, 'emoji': '💰'}
    ]
    
    try:
        # 查询账户余额
        balance = get_account_balance(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
        #print(balance)

        # 检查是否需要告警
        alert_info = check_balance_alert(balance, ALERT_THRESHOLDS)
        
        if alert_info:
            # 发送告警消息
            send_telegram_alert(
                TELEGRAM_BOT_TOKEN, 
                TELEGRAM_CHAT_ID, 
                balance, 
                alert_info
            )
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'余额检查完成，当前余额: ¥{balance}',
                'alert_sent': bool(alert_info)
            })
        }
        
    except Exception as e:
        # 发送错误通知
        error_msg = f"❌ 阿里云余额监控异常：{str(e)}"
        send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, error_msg)
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_account_balance(access_key_id, access_key_secret):
    """
    获取阿里云账户余额 - 使用新版SDK
    """
    # 创建访问配置
    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        endpoint='business.aliyuncs.com'
    )
    
    # 创建客户端
    client = Client(config)
    
    try:
        # 直接调用API，不需要额外的request对象和runtime配置
        response = client.query_account_balance()
        
        # 解析响应数据
        if response.body.success:
            available_amount_string = response.body.data.available_amount
            available_amount = float(available_amount_string.replace(",", ""))
            return round(available_amount, 2)
        else:
            raise Exception(f"API调用失败: {response.body.message}")
            
    except Exception as e:
        raise Exception(f"查询余额失败: {str(e)}")

def check_balance_alert(balance, thresholds):
    """
    检查余额是否需要告警
    """
    for threshold in thresholds:
        if balance <= threshold['amount']:
            return threshold
    return None

def send_telegram_alert(bot_token, chat_id, balance, alert_info):
    """
    发送Telegram告警消息
    """
    message = f"""
{alert_info['emoji']} **阿里云余额告警**

📊 **当前余额**: ¥{balance}
⚡ **告警级别**: {alert_info['level']}
🕐 **检查时间**: {get_current_time()}

💡 **建议**: 请及时充值以避免服务中断
    """.strip()
    
    send_telegram_message(bot_token, chat_id, message)

def send_telegram_message(bot_token, chat_id, message):
    """
    发送Telegram消息
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(url, json=payload, timeout=10)
    
    if not response.ok:
        raise Exception(f"Telegram消息发送失败: {response.text}")

def get_current_time():
    """
    获取当前时间字符串
    """
    from datetime import datetime, timezone, timedelta
    
    # 北京时间
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    return now.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    main()
