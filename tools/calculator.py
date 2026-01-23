def calculator(expression: str):
    """安全计算工具"""
    try:
        return eval(expression, {"__builtins__": {}})
    except Exception as e:
        return f"计算错误: {e}"
