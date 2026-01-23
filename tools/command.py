import subprocess


def run_command(cmd, capture_output=True, text=True, shell=True):
    """
    通用执行系统命令的方法
    参数:
        cmd: str 或 list, 要执行的命令
        capture_output: 是否捕获输出
        text: 输出是否解码为字符串
        shell: 是否通过 shell 执行 (Windows 下某些命令需要 True)
    返回:
        dict:
            stdout: 标准输出
            stderr: 错误输出
            returncode: 返回码
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=text,
            shell=shell,
            encoding='utf-8',
            errors='ignore'
        )
        return {
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else "",
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }
