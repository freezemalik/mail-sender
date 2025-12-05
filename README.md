# 邮件发送系统

这是一个功能强大的自动化邮件发送系统，支持QQ邮箱群发、防重复发送、断点续传等功能。

## 快速开始

最简单的使用方式是从根目录运行主入口文件：

```
python main.py
```

然后根据菜单提示选择相应操作。

## 目录结构

```
mail/
├── config/                 # 配置文件
│   ├── config_manager.py   # 配置管理模块
│   ├── email_config.json   # 邮件配置文件
│   └── db_config.json      # 数据库配置文件
├── core/                   # 核心模块
│   ├── email_sender.py     # 基础邮件发送模块
│   ├── enhanced_email_sender.py  # 增强版邮件发送模块
│   └── database.py         # 数据库操作模块
├── data/                   # 数据文件
├── docs/                   # 文档
├── scripts/                # 脚本文件
│   ├── run_enhanced_sender.py  # 增强版邮件发送器入口
│   └── setup_database.py   # 数据库初始化脚本
├── templates/              # 模板文件
│   └── email_template.html # 邮件模板
└── tests/                  # 测试文件
    └── test_email_sender.py # 测试脚本
```

## 功能特点

- 可配置地向QQ邮箱地址发送邮件（5-11位数字，即常见的QQ号）
- 可配置的邮件发送间隔，避免被识别为垃圾邮件
- 支持HTML邮件模板
- 详细的邮件发送状态报告
- 邮件账户信息使用独立配置文件
- 邮箱格式验证功能
- 数据库记录已发送邮件，防止重复发送
- 断点续传功能，从中断处继续发送

## 使用方法

### 方法一：使用主入口（推荐）

在项目根目录下运行：

```
python main.py
```

然后根据菜单选择对应功能。

### 方法二：直接运行特定脚本

1. 运行增强版邮件发送器：
   ```
   python scripts/run_enhanced_sender.py
   ```

2. 初始化数据库：
   ```
   python scripts/setup_database.py
   ```

3. 运行测试：
   ```
   python tests/test_email_sender.py
   ```

## 配置说明

在开始使用之前，请根据需要修改以下配置文件：

### config/email_config.json
- `smtp_server`：SMTP服务器地址
- `smtp_port`：SMTP端口
- `sender_email`：发件人邮箱地址
- `sender_password`：发件人邮箱密码或授权码
- `start_id`：起始QQ号
- `end_id`：结束QQ号
- `send_interval`：发送间隔（秒）

### config/db_config.json
- `type`：数据库类型（"sqlite" 或 "mysql"）
- `sqlite.database_file`：SQLite数据库文件路径
- `mysql.host`：MySQL服务器地址
- `mysql.user`：MySQL用户名
- `mysql.password`：MySQL密码
- `mysql.database`：MySQL数据库名
- `mysql.charset`：字符集

## 更多文档

详细使用说明请参见 [docs/README.md](file:///D:/Workspaces/mail/docs/README.md)
