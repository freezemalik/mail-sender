# -*- coding: utf-8 -*-

"""
配置管理模块
集中管理系统的所有配置参数
"""

import json
import os


class ConfigManager:
    def __init__(self, config_dir='.'):
        self.config_dir = config_dir
        self.email_config = self._load_email_config()
        self.db_config = self._load_db_config()
        
    def _load_email_config(self):
        """加载邮件配置"""
        config_path = os.path.join(self.config_dir, 'config', 'email_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            return {
                "smtp_server": "smtp.qq.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "start_id": 10000,
                "end_id": 99999999999,
                "send_interval": 5
            }
    
    def _load_db_config(self):
        """加载数据库配置"""
        config_path = os.path.join(self.config_dir, 'config', 'db_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置（SQLite）
            return {
                "type": "sqlite",
                "sqlite": {
                    "database_file": "email_records.db"
                },
                "mysql": {
                    "host": "localhost",
                    "user": "root",
                    "password": "",
                    "database": "email_system",
                    "charset": "utf8mb4"
                }
            }
    
    def get_email_config(self):
        """获取邮件配置"""
        return self.email_config
    
    def get_db_config(self):
        """获取数据库配置"""
        return self.db_config
    
    def get_mysql_config(self):
        """获取MySQL配置"""
        return self.db_config.get('mysql', {})
    
    def get_sqlite_config(self):
        """获取SQLite配置"""
        return self.db_config.get('sqlite', {})
    
    def get_db_type(self):
        """获取数据库类型"""
        return self.db_config.get('type', 'sqlite')


# 全局配置管理器实例
config_manager = ConfigManager()