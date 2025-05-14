import os
import json
import sys

def get_config_dir():
    if getattr(sys, 'frozen', False):
        # 打包后
        return os.path.dirname(sys.executable)
    else:
        # 源码运行
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Config:
    DEFAULT_CONFIG = {
        "api_key": "",
        # base_url 可选值：
        # https://dashscope.aliyuncs.com/compatible-mode/v1
        # https://api.siliconflow.cn/v1
        # https://api.deepseek.com/v1
        # https://api.openai.com/v1
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        # multimodel 可选值：
        # qwen-vl-max-latest, qwen-vl-plus-latest, gpt-4-vision-preview, deepseek-vl, moonshot-v1-128k, yi-vision, gemini-pro-vision
        "multimodel": "qwen-vl-max-latest",
        # llm_model 可选值：
        # qwen-turbo-latest, qwen-plus, deepseek-v3, gpt-3.5-turbo, gpt-4o, gpt-4, glm-4, yi-34b-chat, moonshot-v1-128k, claude-3-opus-20240229, claude-3-sonnet-20240229
        "llm_model": "qwen-turbo-latest",
        "language": "中文",
        "coding_prompt": "作为一位AI代码专家，您将收到一张图片，其中包含算法问题或数据库查询问题。请根据图片中的问题，使用{language}提供详细的解决思路及所采用的算法，并给出Python或SQL的代码实现。在编写代码时，请确保其不仅高效而且能够妥善处理各种边界情况。",
        "llm_prompt": """你是一位经验丰富的数据科学与AI算法面试助手。你的任务是根据提供的面试官与面试者之间的对话内容，针对最新提出的问题给出准确的回答。请遵循以下步骤：\n1. **理解上下文**：仔细阅读整个对话记录，以确保能够准确识别出最新的问题及其提问意图。\n2. **识别问题类型**：\n   - 如果问题是关于模型的，请解释该模型的基本结构和工作原理。\n   - 如果需要编写代码来解答问题，请尽量避免直接使用现成的库函数，而是展示基础实现方法。\n   - 对于数学统计相关的问题，在必要时引用相关的公式进行解释。\n3. **回答格式**：\n   - 首先简明扼要地指出答案的关键点。\n   - 然后提供一个更详细的解释或解决方案。\n   - 使用{language}语言作答。\n   - 无需对整个对话做总结。\n   - 直接回答问题，不要反问。\n面试对话记录如下:""",
        "hotkey_voice": "ctrl+[",
        "hotkey_screenshot": "ctrl+\\",
    }

    def __init__(self):
        # Initialize with default values
        for key, value in self.DEFAULT_CONFIG.items():
            setattr(self, key, value)

        # Load config if exists
        self.load_config()

    def load_config(self):
        """Load configuration from file, falling back to defaults if file doesn't exist"""
        config_path = os.path.join(get_config_dir(), "config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Update only the keys that exist in the loaded config
                    for key, value in config.items():
                        if key in self.DEFAULT_CONFIG:
                            setattr(self, key, value)
        except Exception as e:
            print(f"Error loading config: {e}")
            # If there's an error, keep using default values

    def save_config(self):
        """Save current configuration to file"""
        config_path = os.path.join(get_config_dir(), "config.json")
        try:
            config = {key: getattr(self, key) for key in self.DEFAULT_CONFIG.keys()}
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
