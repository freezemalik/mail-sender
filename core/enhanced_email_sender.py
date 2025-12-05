# -*- coding: utf-8 -*-

"""
增强版邮件发送模块
在基础邮件发送功能基础上增加了数据库记录和断点续传功能
"""

import smtplib
import socket
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.config_manager import config_manager
from .database import EmailDatabase
from .email_sender import QQEmailSender


class EnhancedQQEmailSender(QQEmailSender):
    def __init__(self):
        """
        使用配置管理器初始化增强版邮件发送器
        """
        # 获取邮件配置
        email_config = config_manager.get_email_config()
        
        # 调用父类初始化方法
        super().__init__()
        
        # 重写配置参数
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
        self._initialize_log_file()

    def send_email(self, recipient_email, user_id):
        """
        向指定收件人发送邮件（重写父类方法，增加数据库记录功能）
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
    
    def send_bulk_emails(self):
        """
        向一系列QQ邮箱地址发送邮件（重写父类方法，增加跳过已发送邮件的处理）
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
        with open("logs/email_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(summary)
        
        # 关闭数据库连接
        self.database.close()