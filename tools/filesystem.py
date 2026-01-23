import os


def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "文件不存在"
    except Exception as e:
        return str(e)


def write_file_safe(path, mode, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        return "创建成功"
    except Exception as e:
        return str(e)


def list_folder(path):
    """
    遍历指定文件夹，返回文件和文件夹列表
    出参为字符串，每行格式：
    <全路径> <类型：文件/文件夹>
    """
    if not os.path.exists(path):
        return ""  # 文件夹不存在，返回空字符串

    lines = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isfile(full_path):
            lines.append(f"{full_path} 文件")
        elif os.path.isdir(full_path):
            lines.append(f"{full_path} 文件夹")
        else:
            lines.append(f"{full_path} 其他")

    return "\n".join(lines)


def tail_file(file_path, n):
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)  # 定位到文件末尾
        filesize = f.tell()
        buffer = bytearray()
        lines = []

        pointer = filesize - 1
        while pointer >= 0 and len(lines) < n:
            f.seek(pointer)
            char = f.read(1)
            if char == b'\n':
                lines.append(buffer[::-1].decode('utf-8', errors='ignore'))
                buffer = bytearray()
            else:
                buffer.append(char[0])
            pointer -= 1

        # 添加最后一行（文件第一行）
        if buffer:
            lines.append(buffer[::-1].decode('utf-8', errors='ignore'))

        return lines[::-1]  # 反转顺序，保证原来的顺序
