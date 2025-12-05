# -*- coding: utf-8 -*-

"""
增强版邮件发送模块
在基础邮件发送功能基础上增加了数据库记录和断点续传功能
"""

import json
import os
import re
import smtplib
import socket
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Template
from database import EmailDatabase
from ..config.config_manager import config_manager


class EnhancedQQEmailSender:
    def __init__(self):
        """
        使用配置管理器初始化增强版邮件发送器
        """
        # 获取邮件配置
        email_config = config_manager.get_email_config()
        
        self.smtp_server = email_config['smtp_server']
        self.smtp_port = email_config['smtp_port']
        self.sender_email = email_config['sender_email']
        self.sender_password = email_config['sender_password']
        self.start_id = email_config['start_id']
        self.end_id = email_config['end_id']
        self.send_interval = email_config['send_interval']
        
        # 初始化数据库
        self.database = EmailDatabase()
        
        # 检查是否有之前的发送记录，如果有，则从最后一条记录之后开始发送
        last_sent_qq = self.database.get_last_sent_qq()
        if last_sent_qq:
            self.start_id = last_sent_qq + 1
            print(f"检测到已有发送记录，从QQ号 {self.start_id} 开始继续发送")
        
        # 验证QQ号码范围
        if len(str(self.start_id)) < 6 or len(str(self.end_id)) > 13:
            raise ValueError("QQ号码应在6到13位之间")
        
        # 初始化日志文件
        log_file_path = "../data/email_log.txt"
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        if not os.path.exists(log_file_path):
            with open(log_file_path, "w") as log_file:
                log_file.write("邮件发送日志\n===============\n\n")

    def load_email_template(self, template_file='../templates/email_template.html'):
        """
        加载HTML邮件模板
        """
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        return Template(template_content)

    def validate_qq_email_format(self, qq_number):
        """
        验证QQ邮箱地址格式是否正确
        QQ邮箱号码为5-11位数字（加上@qq.com后缀为完整的QQ邮箱）
        """
        # 检查QQ号是否符合格式（5-11位数字）
        qq_str = str(qq_number)
        if not re.match(r'^[1-9][0-9]{4,10}$', qq_str):
            return False, "QQ号格式不正确，应为5-11位数字"
        
        return True, "QQ号格式正确"
    
    def verify_email_smtp(self, recipient_email):
        """
        通过SMTP连接初步验证邮箱是否存在
        注意：这种方法并不完全可靠，某些邮件服务器可能会接受所有地址
        大多数邮件服务器出于安全考虑禁用了VRFY命令
        """
        try:
            # 创建SMTP连接
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            server.set_debuglevel(0)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            # 尝试验证邮箱地址
            # 注意：大多数公共邮件服务器禁用了VRFY命令
            code, message = server.verify(recipient_email)
            server.quit()
            
            # 如果服务器支持并确认邮箱存在
            if code == 250:
                return True, "邮箱验证成功"
            elif code == 252:
                # 服务器无法验证但接受消息
                return True, "服务器无法验证但接受消息"
            else:
                return False, f"邮箱验证失败: {message.decode() if isinstance(message, bytes) else message}"
        except smtplib.SMTPRecipientsRefused:
            return False, "收件人被拒绝"
        except smtplib.SMTPServerDisconnected:
            return False, "SMTP服务器断开连接"
        except Exception as e:
            return False, f"验证过程中出错: {str(e)}"
    
    def send_email(self, recipient_email, user_id):
        """
        向指定收件人发送邮件
        """
        # 首先验证QQ邮箱格式
        qq_number = recipient_email.split('@')[0]
        is_valid, validation_message = self.validate_qq_email_format(qq_number)
        if not is_valid:
            self.log_email_status(recipient_email, False, validation_message)
            return False, validation_message
        
        # 检查是否已经发送过
        if self.database.is_email_sent(qq_number):
            return False, "邮件已发送过，跳过"
        
        try:
            # 创建消息容器
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "欢迎为您提供服务！"

            # 使用user_id渲染HTML内容
            template = self.load_email_template()
            html_content = template.render(user_id=user_id)

            # 将HTML内容附加到邮件中
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 创建SMTP会话，增加超时设置
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.starttls()  # 启用TLS加密
            server.login(self.sender_email, self.sender_password)
            
            # 发送邮件
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()
            
            # 记录成功发送到数据库和日志
            self.database.record_sent_email(qq_number, 'success')
            self.log_email_status(recipient_email, True, "邮件发送成功")
            return True, "邮件发送成功"
        except smtplib.SMTPRecipientsRefused:
            # 收件人被拒绝，邮箱可能不存在
            error_msg = "收件人被拒绝，邮箱可能不存在"
            self.database.record_sent_email(qq_number, 'failed')
            self.log_email_status(recipient_email, False, error_msg)
            return False, error_msg
        except smtplib.SMTPAuthenticationError:
            # SMTP认证失败
            error_msg = "SMTP认证失败，请检查邮箱账号和授权码"
            self.log_email_status(recipient_email, False, error_msg)
            return False, error_msg
        except smtplib.SMTPConnectError:
            # SMTP连接失败
            error_msg = "SMTP连接失败，请检查网络连接和SMTP服务器设置"
            self.log_email_status(recipient_email, False, error_msg)
            return False, error_msg
        except smtplib.SMTPServerDisconnected:
            # SMTP服务器断开连接
            error_msg = "SMTP服务器断开连接"
            self.log_email_status(recipient_email, False, error_msg)
            return False, error_msg
        except socket.timeout:
            # 连接超时
            error_msg = "连接超时，请检查网络连接"
            self.log_email_status(recipient_email, False, error_msg)
            return False, error_msg
        except socket.gaierror:
            # DNS解析错误
            error_msg = "DNS解析错误，请检查SMTP服务器地址"
            self.log_email_status(recipient_email, False, error_msg)
            return False, error_msg
        except Exception as e:
            # 记录其他发送失败
            error_msg = f"邮件发送失败: {str(e)}"
            self.database.record_sent_email(qq_number, 'failed')
            self.log_email_status(recipient_email, False, error_msg)
            return False, error_msg

    def log_email_status(self, email, success, message):
        """
        将邮件发送状态记录到文件
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "成功" if success else "失败"
        log_entry = f"[{timestamp}] [{status}] {email}: {message}\n"
        
        with open("../data/email_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
    
    def send_bulk_emails(self):
        """
        向一系列QQ邮箱地址发送邮件
        """
        print(f"开始批量发送邮件，从 {self.start_id} 到 {self.end_id}")
        successful_sends = 0
        failed_sends = 0
        skipped_emails = 0
        
        # 分别处理不同位数
        current_id = self.start_id
        
        while current_id <= self.end_id:
            # 构造QQ邮箱地址
            recipient_email = f"{current_id}@qq.com"
            
            # 发送邮件
            success, message = self.send_email(recipient_email, current_id)
            
            if success:
                successful_sends += 1
                print(f"[成功] 邮件已发送至 {recipient_email}")
            else:
                failed_sends += 1
                if "格式不正确" in message:
                    skipped_emails += 1
                    print(f"[跳过] QQ号格式不正确 {recipient_email}: {message}")
                elif "已发送过" in message:
                    skipped_emails += 1
                    print(f"[跳过] 邮件已发送过 {recipient_email}: {message}")
                else:
                    print(f"[失败] 邮件发送失败 {recipient_email}: {message}")
            
            # 移动到下一个ID
            current_id += 1
            
            # 每100封邮件记录一次统计信息
            if (current_id - self.start_id) % 100 == 0:
                print(f"进度: {current_id - self.start_id}/{self.end_id - self.start_id + 1} 封邮件已处理. "
                      f"成功: {successful_sends}, 失败: {failed_sends}, 跳过: {skipped_emails}")
            
            # 等待指定的时间间隔以避免被当作垃圾邮件
            if current_id <= self.end_id:  # 最后一封邮件后不需要等待
                time.sleep(self.send_interval)
        
        print(f"批量邮件发送完成！")
        print(f"总邮件数: {self.end_id - self.start_id + 1}")
        print(f"成功发送: {successful_sends}")
        print(f"发送失败: {failed_sends}")
        print(f"跳过数量: {skipped_emails}")
        
        # 总结日志
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = f"\n[{timestamp}] 总结: 总计={self.end_id - self.start_id + 1}, 成功={successful_sends}, 失败={failed_sends}, 跳过={skipped_emails}\n"
        with open("../data/email_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(summary)
        
        # 关闭数据库连接
        self.database.close()