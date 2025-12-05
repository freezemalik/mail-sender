#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
用于创建MySQL数据库和表结构
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mysql.connector
from mysql.connector import errorcode
from config.config_manager import config_manager

def create_database_and_table():
    # 从配置管理器获取MySQL配置
    mysql_config = config_manager.get_mysql_config()
    
    # 移除数据库名称以连接到服务器
    server_config = mysql_config.copy()
    db_name = server_config.pop('database', 'email_system')
    
    # 创建数据库的SQL语句
    create_database_sql = f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    
    # 创建表的SQL语句
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS `{db_name}`.`sent_emails` (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `qq_number` VARCHAR(20) UNIQUE NOT NULL,
        `email_address` VARCHAR(100) NOT NULL,
        `sent_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `status` VARCHAR(20) NOT NULL,
        INDEX `idx_qq_number` (`qq_number`),
        INDEX `idx_sent_time` (`sent_time`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    
    try:
        # 连接到MySQL服务器
        print("正在连接到MySQL服务器...")
        cnx = mysql.connector.connect(**server_config)
        cursor = cnx.cursor()
        
        # 创建数据库
        print("正在创建数据库...")
        cursor.execute(create_database_sql)
        print(f"数据库 '{db_name}' 创建成功或已存在")
        
        # 选择数据库
        cursor.execute(f"USE {db_name}")
        
        # 创建表
        print("正在创建数据表...")
        cursor.execute(create_table_sql)
        print("数据表 'sent_emails' 创建成功或已存在")
        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("用户名或密码错误")
            print("请检查以下几点:")
            print("1. MySQL服务是否正在运行")
            print("2. 用户名和密码是否正确")
            print("3. 用户是否有足够的权限")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("数据库不存在")
        else:
            print(f"数据库操作出错: {err}")
    else:
        # 提交事务并关闭连接
        cnx.commit()
        cursor.close()
        cnx.close()
        print("数据库初始化完成")

def test_connection():
    # 从配置管理器获取MySQL配置
    mysql_config = config_manager.get_mysql_config()
    
    # 移除数据库名称以测试连接
    server_config = mysql_config.copy()
    server_config.pop('database', None)
    
    try:
        print("测试数据库连接...")
        cnx = mysql.connector.connect(**server_config)
        print("数据库连接成功!")
        cnx.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("连接失败：用户名或密码错误")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("连接失败：数据库不存在")
        else:
            print(f"连接失败: {err}")
    except Exception as e:
        print(f"连接时发生未知错误: {e}")

if __name__ == "__main__":
    print("选项:")
    print("1. 测试数据库连接")
    print("2. 创建数据库和表")
    choice = input("请选择操作 (1 或 2): ")
    
    if choice == "1":
        test_connection()
    elif choice == "2":
        create_database_and_table()
    else:
        print("无效的选择")