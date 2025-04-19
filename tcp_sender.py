import socket
import struct
import time
import threading
import random

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080
REPORT_INTERVAL = 1  # 每秒上报

def generate_packet(device_id: int) -> bytes:
    timestamp = int(time.time())
    
    # 模拟数据（可以替换成真实采样值或按规律生成）
    current_a = round(random.uniform(0, 20), 2)
    current_b = round(random.uniform(0, 20), 2)
    current_c = round(random.uniform(0, 20), 2)
    
    voltage_a = round(random.uniform(200, 240), 1)
    voltage_b = round(random.uniform(200, 240), 1)
    voltage_c = round(random.uniform(200, 240), 1)
    
    power_a = round(random.uniform(0, 5000), 2)
    power_b = round(random.uniform(0, 5000), 2)
    power_c = round(random.uniform(0, 5000), 2)
    
    # 按协议打包为二进制数据（小端）
    packet = struct.pack('<ii' + 'f'*9,
                         device_id,
                         timestamp,
                         current_a, current_b, current_c,
                         voltage_a, voltage_b, voltage_c,
                         power_a, power_b, power_c)
    return packet

def simulate_device(device_id: int):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_HOST, SERVER_PORT))
            print(f"[设备 {device_id}] 已连接服务器")
            
            while True:
                packet = generate_packet(device_id)
                sock.sendall(packet)
                print(f"[设备 {device_id}] 已发送报文")
                time.sleep(REPORT_INTERVAL)
        except Exception as e:
            print(f"[设备 {device_id}] 出现异常：{e}，3秒后重连")
            time.sleep(3)
        finally:
            try:
                sock.close()
            except:
                pass

def start_simulation(device_count: int):
    for i in range(device_count):
        device_id = 1000 + i
        t = threading.Thread(target=simulate_device, args=(device_id,))
        t.daemon = True
        t.start()
    print(f"已启动 {device_count} 台模拟设备")

if __name__ == '__main__':
    device_total = 2# 可调整模拟设备数量
    start_simulation(device_total)
    
    # 主线程保持运行
    while True:
        time.sleep(10)
