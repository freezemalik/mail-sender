# 自动推广邮件发送系统

该系统可自动向指定范围内的QQ邮箱地址发送推广邮件。

## 功能特点

- 可配置地向QQ邮箱地址发送邮件（5-11位数字，即常见的QQ号）
- 可配置的邮件发送间隔，避免被识别为垃圾邮件
- 支持HTML邮件模板
- 详细的邮件发送状态报告
- 邮件账户信息使用独立配置文件
- 邮箱格式验证功能
- 数据库记录已发送邮件，防止重复发送
- 断点续传功能，从中断处继续发送

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
│   └── run_enhanced_sender.py  # 增强版邮件发送器入口
├── templates/              # 模板文件
│   └── email_template.html # 邮件模板
└── tests/                  # 测试文件
    └── test_email_sender.py # 测试脚本
```

## 安装设置

### 方式一：手动安装
1. 安装所需依赖包：
   ```
   pip install -r requirements.txt
   ```

### 方式二：使用安装脚本
1. 双击 `install_requirements.bat` 安装所需依赖包

2. 更新 `config/email_config.json` 中的QQ邮箱账户信息：
   - `sender_email`：您的QQ邮箱地址
   - `sender_password`：您的QQ邮箱授权码（不是登录密码）
   - `start_id` 和 `end_id`：要发送邮件的QQ号范围
   - `send_interval`：邮件发送间隔秒数

3. 自定义 `templates/email_template.html` 中的推广内容

## 数据库设置

系统支持两种数据库：
1. SQLite（默认，无需配置）
2. MySQL（需要配置）

### 使用SQLite（推荐新手使用）
系统默认使用SQLite数据库，无需额外配置，适合测试和小规模使用。

### 使用MySQL数据库

#### 配置数据库连接信息

编辑 `config/db_config.json` 文件：
```json
{
    "type": "mysql",
    "sqlite": {
        "database_file": "../data/email_records.db"
    },
    "mysql": {
        "host": "localhost",
        "user": "your_mysql_username",
        "password": "your_mysql_password",
        "database": "email_system",
        "charset": "utf8mb4"
    }
}
```

将 `"type"` 设置为 `"mysql"` 使用MySQL数据库，设置为 `"sqlite"` 使用SQLite数据库。

#### MySQL数据库初始化

运行数据库初始化脚本：
```
python setup_database.py
```

选择选项2创建数据库和表

或者手动创建：
```sql
CREATE DATABASE IF NOT EXISTS email_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE email_system;

CREATE TABLE IF NOT EXISTS sent_emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    qq_number VARCHAR(20) UNIQUE NOT NULL,
    email_address VARCHAR(100) NOT NULL,
    sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    INDEX idx_qq_number (qq_number),
    INDEX idx_sent_time (sent_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 测试MySQL连接

运行以下命令测试数据库连接：
```
python setup_database.py
```

选择选项1测试连接

## 使用方法

### 基础版本（无数据库记录）
```
python core/email_sender.py
```

### 增强版本（带数据库记录）
```
python scripts/run_enhanced_sender.py
```

如果MySQL连接失败，系统会自动回退到SQLite数据库。

## 测试

使用小范围邮箱进行测试：
1. 更新 `config/test_config.json` 中的QQ邮箱凭证
2. 运行：
   ```
   python tests/test_email_sender.py
   ```

## 配置说明

### config/email_config.json
- `smtp_server`：SMTP服务器地址（默认QQ邮箱为smtp.qq.com）
- `smtp_port`：SMTP端口（默认：587）
- `sender_email`：您的QQ邮箱地址
- `sender_password`：您的QQ邮箱授权码
- `start_id`：邮件发送起始QQ号（最少5位：10000）
- `end_id`：邮件发送结束QQ号（最大11位：99999999999）
- `send_interval`：邮件发送间隔秒数

### config/db_config.json
- `type`：数据库类型（"sqlite" 或 "mysql"）
- `sqlite.database_file`：SQLite数据库文件路径
- `mysql.host`：MySQL服务器地址
- `mysql.user`：MySQL用户名
- `mysql.password`：MySQL密码
- `mysql.database`：MySQL数据库名
- `mysql.charset`：字符集

### templates/email_template.html
自定义此HTML文件以更改推广邮件内容。
您可以使用Jinja2模板语法，`{{ user_id }}`可用于个性化邮件。

## 邮箱验证说明

系统实现了两种邮箱验证方式：

1. 格式验证：检查QQ号是否符合标准格式（5-11位数字）
2. SMTP验证：尝试通过SMTP协议验证邮箱（功能有限，大多数邮件服务器禁用了此功能）

需要注意的是，目前没有可靠的技术手段可以在不实际发送邮件的情况下100%确认一个邮箱地址的存在。

## 重要提示

- 请确保使用授权码而非登录密码用于QQ邮箱
- 谨慎设置发送间隔以避免被标记为垃圾邮件
- 建议先用小范围测试确保一切正常工作
- QQ邮箱号码为5-11位数字（10000到99999999999）
- 不建议使用GitHub上基于MD5破解的方式验证邮箱，这种方式在现实中不可行

## 故障排除

### MySQL连接问题

如果遇到如下错误：
```
连接MySQL数据库失败: 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)
```

请检查以下几点：
1. MySQL服务是否正在运行
2. 用户名和密码是否正确
3. 用户是否有足够的权限访问指定数据库
4. 防火墙是否阻止了连接

### 其他网络连接问题

如果遇到网络连接问题（如 [WinError 10060] 连接超时），请尝试以下解决方案：

1. 使用网络测试工具诊断问题：
   ```
   python network_test.py
   ```

2. 检查网络连接和防火墙设置

3. 尝试调整配置文件中的 connection_timeout 值（建议设置为30-60秒）

4. 增加 send_interval 值，避免发送过于频繁

5. 确认QQ邮箱的SMTP服务已开启并使用授权码而非登录密码