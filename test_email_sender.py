# -*- coding: utf-8 -*-

"""
测试邮件发送功能
"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.email_sender import QQEmailSender

# 创建一个小范围的测试配置
test_config = {
    "smtp_server": "mail.haokancenter.top",
    "smtp_port": 25,
    "sender_email": "movie@haokancenter.top",
    "sender_password": "123qwe!@#QWE",
    "start_id": 3099628,
    "end_id": 3099628,  # 小范围用于测试
    "send_interval": 1
}

# 保存测试配置
test_config_path = 'config/test_config.json'
os.makedirs(os.path.dirname(test_config_path), exist_ok=True)
with open(test_config_path, 'w') as f:
    json.dump(test_config, f, indent=4)

# 使用测试配置创建测试发送器
test_sender = QQEmailSender(test_config_path)

# 打印配置以验证
print("\n测试配置：")
print(f"从 {test_sender.start_id} 到 {test_sender.end_id} 发送邮件")
print(f"发送间隔: {test_sender.send_interval} 秒")

# 实际发送一封测试邮件
print("\n正在发送测试邮件...")
recipient_email = f"{test_sender.start_id}@qq.com"
success, message = test_sender.send_email(recipient_email, test_sender.start_id)
if success:
    print(f"[成功] 邮件已发送至 {recipient_email}")
else:
    print(f"[失败] 邮件发送失败 {recipient_email}: {message}")

print("\n测试完成。请检查邮件是否成功发送。")