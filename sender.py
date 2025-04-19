import socket
import struct
import random
import time
from datetime import datetime
import threading

# === 配置项 ===
DEVICE_IDS = [i for i in range(10)]  # 模拟设备列表
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9527
SEND_INTERVAL = 1.0  # 每条报文的发送间隔（秒）


# === 随机生成报文 ===
def generate_message(device_id: int):
    timestamp = int(time.time())  # 当前UTC时间戳

    # 电流（2位有效数字）单位A
    current_a = round(random.uniform(0, 100), 2)
    current_b = round(random.uniform(0, 100), 2)
    current_c = round(random.uniform(0, 100), 2)

    # 电压（1位有效数字）单位V
    voltage_a = round(random.uniform(210, 230), 1)
    voltage_b = round(random.uniform(210, 230), 1)
    voltage_c = round(random.uniform(210, 230), 1)

    # 正向有功功率（2位有效数字）单位W
    power_a = round(random.uniform(0, 10000), 2)
    power_b = round(random.uniform(0, 10000), 2)
    power_c = round(random.uniform(0, 10000), 2)

    # 小端打包（2x INT32 + 9x FLOAT32）
    packed = struct.pack(
        "<2I9f",
        device_id,
        timestamp,
        current_a,
        current_b,
        current_c,
        voltage_a,
        voltage_b,
        voltage_c,
        power_a,
        power_b,
        power_c,
    )
    return packed


# === 每个设备运行一个发送线程 ===
def device_worker(device_id: int):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((SERVER_HOST, SERVER_PORT))
                print(f"[{datetime.now()}] 设备 {device_id} 已连接服务器")

                while True:
                    msg = generate_message(device_id)
                    sock.sendall(msg)
                    print(f"[{datetime.now()}] 设备 {device_id} 发送报文")
                    time.sleep(SEND_INTERVAL)

        except Exception as e:
            print(f"[{datetime.now()}] 设备 {device_id} 连接异常: {e}")
            time.sleep(3)  # 等待后重连


# === 启动线程 ===
def main():
    for device_id in DEVICE_IDS:
        t = threading.Thread(target=device_worker, args=(device_id,), daemon=True)
        t.start()
    print("所有设备已启动模拟发送")
    while True:
        time.sleep(3600)  # 主线程挂起防止退出


if __name__ == "__main__":
    main()
