#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版邮件发送器入口文件
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.enhanced_email_sender import EnhancedQQEmailSender

def main():
    try:
        # 创建增强版邮件发送器实例
        # 所有配置现在都从配置文件中读取
        sender = EnhancedQQEmailSender()
        
        # 开始批量发送邮件
        sender.send_bulk_emails()
        
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()