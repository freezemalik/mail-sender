import smtplib
import socket
import ssl
import dns.resolver
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_connection(smtp_server, smtp_port, sender_email, sender_password, use_tls=True):
    """
    测试SMTP连接
    """
    print(f"正在测试连接到 {smtp_server}:{smtp_port}")
    
    try:
        # 测试DNS解析
        print("1. 测试DNS解析...")
        socket.gethostbyname(smtp_server)
        print("   DNS解析成功")
    except socket.gaierror as e:
        print(f"   DNS解析失败: {e}")
        return False
    
    try:
        # 测试端口连通性
        print("2. 测试端口连通性...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((smtp_server, smtp_port))
        sock.close()
        
        if result == 0:
            print("   端口连接成功")
        else:
            print(f"   端口连接失败，错误码: {result}")
            return False
    except Exception as e:
        print(f"   端口测试异常: {e}")
        return False
    
    try:
        # 测试SMTP连接
        print("3. 测试SMTP连接和认证...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        print(f"   SMTP服务器响应: {server.ehlo()[1][:50]}...")
        
        if use_tls:
            server.starttls()
            print("   TLS连接建立成功")
        
        server.login(sender_email, sender_password)
        print("   认证成功")
        
        server.quit()
        print("   连接测试完成")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   认证失败: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"   连接失败: {e}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        print(f"   服务器断开连接: {e}")
        return False
    except socket.timeout as e:
        print(f"   连接超时: {e}")
        return False
    except Exception as e:
        print(f"   其他错误: {e}")
        return False

def test_network_connectivity():
    """
    测试基本网络连接
    """
    print("测试基本网络连接...")
    
    try:
        # 测试DNS解析
        socket.gethostbyname('www.qq.com')
        print("DNS解析测试: 成功")
    except socket.gaierror:
        print("DNS解析测试: 失败")
        return False
    
    try:
        # 测试HTTP连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('www.qq.com', 80))
        sock.close()
        
        if result == 0:
            print("HTTP连接测试: 成功")
        else:
            print("HTTP连接测试: 失败")
            return False
    except Exception as e:
        print(f"HTTP连接测试异常: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== 邮件系统网络连接测试 ===\n")
    
    # 测试基本网络连接
    if not test_network_connectivity():
        print("\n网络连接存在问题，请检查您的网络设置")
        exit(1)
    
    print("\n=== SMTP连接测试 ===")
    # 从配置文件读取设置
    import json
    try:
        with open('email_config.json', 'r') as f:
            config = json.load(f)
        
        smtp_server = config.get('smtp_server', 'smtp.qq.com')
        smtp_port = config.get('smtp_port', 587)
        sender_email = config.get('sender_email', '')
        sender_password = config.get('sender_password', '')
        
        if not sender_email or not sender_password:
            print("请先在 email_config.json 中配置邮箱账号和授权码")
            exit(1)
            
        success = test_smtp_connection(smtp_server, smtp_port, sender_email, sender_password)
        
        if success:
            print("\n✅ SMTP连接测试成功！")
        else:
            print("\n❌ SMTP连接测试失败！")
            print("\n常见问题及解决方案:")
            print("1. 检查网络连接是否正常")
            print("2. 确认QQ邮箱账号和授权码是否正确")
            print("3. 检查防火墙是否阻止了程序的网络连接")
            print("4. 尝试使用端口 465 (SSL) 或 25 替代 587 (TLS)")
            print("5. 联系您的网络管理员确认SMTP端口未被屏蔽")
            
    except FileNotFoundError:
        print("找不到配置文件 email_config.json")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")