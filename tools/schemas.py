"""
OpenAI tool schemas for the agent.
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "安全计算工具，计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 '2 + 3 * 4'"
                    }
                },
                "required": ["expression"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径"
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file_safe",
            "description": "安全写入文件，如果目录不存在则创建",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径"
                    },
                    "mode": {
                        "type": "string",
                        "description": "写入模式，例如 'w' 表示写入，'a' 表示追加"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的内容"
                    }
                },
                "required": ["path", "mode", "content"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_folder",
            "description": "列出文件夹中的文件和文件夹",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件夹路径"
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tail_file",
            "description": "读取文件最后n行",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "文件路径"
                    },
                    "n": {
                        "type": "integer",
                        "description": "要读取的行数"
                    }
                },
                "required": ["file_path", "n"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "执行系统命令",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "要执行的命令字符串"
                    },
                    "capture_output": {
                        "type": "boolean",
                        "description": "是否捕获输出，默认为True"
                    },
                    "text": {
                        "type": "boolean",
                        "description": "输出是否解码为字符串，默认为True"
                    },
                    "shell": {
                        "type": "boolean",
                        "description": "是否通过shell执行，默认为True"
                    }
                },
                "required": ["cmd"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": "完成当前任务并返回最终答案",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "最终答案"
                    }
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        }
    }
]