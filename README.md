# cc-
# 基础用法
python3 cc.py -u http://example.com -t 500 -d 300

# 使用代理文件
python3 cc.py -u http://example.com -p proxies.txt

# 混合参数
python3 cc.py -u https://target.com -t 1000 -d 600 -p socks5_proxies.txt
# 手动配置socks格式
[socks5://127.0.0.1:1080
http://proxy1.example.com:8080
192.168.1.100:7890  # 自动识别为socks5]
# 本脚本为测试自己网站欠压测试脚本非法使用后果自负

