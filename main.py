#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
邮件发送系统主入口文件
提供统一的程序启动接口
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_enhanced_sender import main as run_enhanced_sender


def show_menu():
    """显示菜单选项"""
    print("\n========== 邮件发送系统 ==========")
    print("1. 运行增强版邮件发送器（推荐）")
    print("2. 测试数据库连接")
    print("3. 初始化数据库")
    print("4. 运行测试脚本")
    print("0. 退出")
    print("================================")


def setup_database():
    """初始化数据库"""
    try:
        from setup_database import create_database_and_table
        create_database_and_table()
    except Exception as e:
        print(f"数据库初始化失败: {e}")


def test_database_connection():
    """测试数据库连接"""
    try:
        from setup_database import test_connection
        test_connection()
    except Exception as e:
        print(f"数据库连接测试失败: {e}")


def run_tests():
    """运行测试脚本"""
    try:
        from tests.test_email_sender import test_config
        print("测试配置已加载:")
        for key, value in test_config.items():
            print(f"  {key}: {value}")
        print("\n测试环境准备就绪，请手动运行具体测试。")
    except Exception as e:
        print(f"测试脚本运行失败: {e}")


def main():
    """主函数"""
    while True:
        show_menu()
        try:
            choice = input("请选择操作 (0-4): ").strip()
            
            if choice == "1":
                print("正在启动增强版邮件发送器...")
                run_enhanced_sender()
            elif choice == "2":
                print("正在测试数据库连接...")
                test_database_connection()
            elif choice == "3":
                print("正在初始化数据库...")
                setup_database()
            elif choice == "4":
                print("正在运行测试脚本...")
                run_tests()
            elif choice == "0":
                print("感谢使用邮件发送系统，再见！")
                break
            else:
                print("无效的选择，请重新输入。")
                
        except KeyboardInterrupt:
            print("\n\n程序已被用户中断，正在退出...")
            break
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    main()