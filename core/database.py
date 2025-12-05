# -*- coding: utf-8 -*-

"""
数据库操作模块
负责与数据库交互，记录邮件发送状态
"""

import os
import sqlite3

import mysql.connector

from ..config.config_manager import config_manager


class EmailDatabase:
    def __init__(self):
        """
        初始化数据库连接
        """
        self.db_config = config_manager.get_db_config()
        self.db_type = config_manager.get_db_type()
        self.connection = None
        self.connect()
        self.create_table()
    
    def connect(self):
        """建立数据库连接"""
        if self.db_type == 'sqlite':
            sqlite_config = config_manager.get_sqlite_config()
            db_file = sqlite_config.get('database_file', '../data/email_records.db')
            # 确保data目录存在
            os.makedirs(os.path.dirname(db_file) if os.path.dirname(db_file) else '.', exist_ok=True)
            self.connection = sqlite3.connect(db_file)
            print(f"使用SQLite数据库存储邮件发送记录: {db_file}")
        elif self.db_type == 'mysql':
            try:
                mysql_config = config_manager.get_mysql_config()
                self.connection = mysql.connector.connect(**mysql_config)
                print("成功连接到MySQL数据库")
            except mysql.connector.Error as err:
                print(f"连接MySQL数据库失败: {err}")
                print("回退到使用SQLite数据库...")
                self.db_type = 'sqlite'
                sqlite_config = config_manager.get_sqlite_config()
                db_file = sqlite_config.get('database_file', '../data/email_records.db')
                os.makedirs(os.path.dirname(db_file) if os.path.dirname(db_file) else '.', exist_ok=True)
                self.connection = sqlite3.connect(db_file)
                print(f"使用SQLite数据库存储邮件发送记录: {db_file}")
            except Exception as e:
                print(f"连接MySQL数据库时发生未知错误: {e}")
                print("回退到使用SQLite数据库...")
                self.db_type = 'sqlite'
                sqlite_config = config_manager.get_sqlite_config()
                db_file = sqlite_config.get('database_file', '../data/email_records.db')
                os.makedirs(os.path.dirname(db_file) if os.path.dirname(db_file) else '.', exist_ok=True)
                self.connection = sqlite3.connect(db_file)
                print(f"使用SQLite数据库存储邮件发送记录: {db_file}")
    
    def create_table(self):
        """创建邮件发送记录表"""
        cursor = self.connection.cursor()
        
        if self.db_type == 'sqlite':
            # SQLite 表结构
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    qq_number TEXT UNIQUE NOT NULL,
                    email_address TEXT NOT NULL,
                    sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL
                )
            ''')
        elif self.db_type == 'mysql':
            # MySQL 表结构
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_emails (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    qq_number VARCHAR(20) UNIQUE NOT NULL,
                    email_address VARCHAR(100) NOT NULL,
                    sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) NOT NULL,
                    INDEX idx_qq_number (qq_number),
                    INDEX idx_sent_time (sent_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
        
        self.connection.commit()
        cursor.close()
        print(f"数据库表创建完成 ({self.db_type})")
    
    def is_email_sent(self, qq_number):
        """
        检查QQ号码是否已经发送过邮件
        :param qq_number: QQ号码
        :return: bool
        """
        cursor = self.connection.cursor()
        
        if self.db_type == 'sqlite':
            cursor.execute('SELECT COUNT(*) FROM sent_emails WHERE qq_number = ?', (str(qq_number),))
        elif self.db_type == 'mysql':
            cursor.execute('SELECT COUNT(*) FROM sent_emails WHERE qq_number = %s', (str(qq_number),))
        
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    
    def record_sent_email(self, qq_number, status='success'):
        """
        记录已发送的邮件
        :param qq_number: QQ号码
        :param status: 发送状态 ('success', 'failed')
        """
        cursor = self.connection.cursor()
        email_address = f"{qq_number}@qq.com"
        
        try:
            if self.db_type == 'sqlite':
                cursor.execute('''
                    INSERT OR REPLACE INTO sent_emails (qq_number, email_address, status) 
                    VALUES (?, ?, ?)
                ''', (str(qq_number), email_address, status))
            elif self.db_type == 'mysql':
                cursor.execute('''
                    INSERT INTO sent_emails (qq_number, email_address, status) 
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE sent_time=CURRENT_TIMESTAMP, status=%s
                ''', (str(qq_number), email_address, status, status))
            
            self.connection.commit()
        except Exception as e:
            print(f"记录邮件发送状态时出错: {e}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def get_last_sent_qq(self):
        """
        获取最后发送的QQ号码
        :return: 最后发送的QQ号码，如果没有记录则返回None
        """
        cursor = self.connection.cursor()
        
        if self.db_type == 'sqlite':
            cursor.execute('''
                SELECT qq_number FROM sent_emails 
                WHERE sent_time = (SELECT MAX(sent_time) FROM sent_emails)
                ORDER BY id DESC LIMIT 1
            ''')
        elif self.db_type == 'mysql':
            cursor.execute('''
                SELECT qq_number FROM sent_emails 
                WHERE sent_time = (SELECT MAX(sent_time) FROM sent_emails)
                ORDER BY id DESC LIMIT 1
            ''')
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return int(result[0])
        return None
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print(f"数据库连接已关闭 ({self.db_type})")