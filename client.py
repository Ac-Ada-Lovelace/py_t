import socket
import threading
import struct
import time

HOST = "0.0.0.0"
PORT = 9527
MSG_LENGTH = 44
OUTPUT_FILE = "data_log.csv"


def parse_message(data: bytes):
    """
    解析44字节定长电力报文（小端序）
    """
    if len(data) != MSG_LENGTH:
        raise ValueError(
            f"数据长度错误，应为 {MSG_LENGTH} 字节，实际为 {len(data)} 字节"
        )

    # 小端序（<），2个int32，9个float32
    unpacked = struct.unpack("<2I9f", data)

    result = {
        "设备ID": unpacked[0],
        "上报时间": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(unpacked[1])),
        "电流A": round(unpacked[2], 2),
        "电流B": round(unpacked[3], 2),
        "电流C": round(unpacked[4], 2),
        "电压A": round(unpacked[5], 1),
        "电压B": round(unpacked[6], 1),
        "电压C": round(unpacked[7], 1),
        "正向有功功率A": round(unpacked[8], 2),
        "正向有功功率B": round(unpacked[9], 2),
        "正向有功功率C": round(unpacked[10], 2),
    }

    return result


# ===============================
# 数据处理：写入CSV文件
# ===============================
def handle_parsed_data(parsed_data: dict):
    """
    将解析后的数据按CSV格式写入文件
    """
    line = ",".join(str(value) for value in parsed_data.values()) + "\n"
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"[保存成功] {line.strip()}")


# ===============================
# 客户端连接处理线程
# ===============================
def handle_client(conn: socket.socket, addr):
    print(f"[连接] 客户端地址: {addr}")
    try:
        while True:
            data = conn.recv(MSG_LENGTH)
            if not data:
                break
            if len(data) < MSG_LENGTH:
                print(f"[警告] 收到不完整数据（{len(data)} 字节）")
                continue
            try:
                parsed = parse_message(data)
                handle_parsed_data(parsed)
            except Exception as e:
                print(f"[错误] 报文解析失败: {e}")
    finally:
        conn.close()
        print(f"[断开] 客户端地址: {addr}")


# ===============================
# TCP服务器主函数
# ===============================
def start_server():
    print(f"[启动] TCP服务器监听端口 {PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(
                target=handle_client, args=(conn, addr), daemon=True
            )
            thread.start()


if __name__ == "__main__":
    # 写入文件头（如果文件不存在）
    try:
        with open(OUTPUT_FILE, "x", encoding="utf-8") as f:
            header = "设备ID,上报时间,电流A,电流B,电流C,电压A,电压B,电压C,正向有功功率A,正向有功功率B,正向有功功率C\n"
            f.write(header)
    except FileExistsError:
        pass

    start_server()
