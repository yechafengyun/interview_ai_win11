# Interview AI Windows11

![Platforms](https://img.shields.io/badge/platform-Windows%2011-blue)

AI面试助手，适用于 Windows 11，基本开箱即用，完全免费。希望改变诸多AI面试工具又贵又不好用还抠搜的现状。  
This tool is based on Windows LiveCaptions, which is available since Windows 11 22H2.


## 功能简介
- **实时语音转文字**：借助Windows11自带实时字幕软件（Live Captions）自动抓取对话，可配置语言，是否包含麦克风音频等，相比其他开源面试AI，不需要再手动安装音频捕获软件以及音频识别API
- **AI自动答题**：集成多种大模型（如qwen-turbo、deepseek等），支持多语言（中文/日语/英文）自动生成高质量答案。
- **快捷键设置**：默认使用`Ctrl+[`触发对话回答，默认使用`Ctrl+\`触发截屏Coding题解答
- **自定义配置**：支持自定义API Key、模型、提示词、热键等，满足个性化需求。
    - prompt设置建议保留其中的`{language}`文本



## AI大模型配置
> ⚠️ **警告**: 为了获得更快的响应速度，建议优先使用轻量级模型，如:
> - qwen-turbo-latest (推荐)
> - qwen-vl-plus-latest (推荐)
> - gpt-3.5-turbo
> - 大规模模型(如qwen-max、gpt-4等)虽然效果更好，但响应速度会明显变慢。请根据实际需求权衡选择。


- 模板使用**阿里云**(新注册赠送大量Token)，[如何获取API Key](https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key)
[KIMI API](https://platform.moonshot.cn/docs/guide/start-using-kimi-api)  
- **硅基流动**（[官网链接](https://cloud.siliconflow.cn/i/VDi0mdMO)）获取`API_KEY`，新用户受邀可获取14元额度（邀请码`VDi0mdMO`），足够用一段时间了（此时，模型名称格式为deepseek-ai/DeepSeek-R1, deepseek-ai/deepseek-vl2形式）

| Base URL  | 文本模型（LLM Model） | 多模态\识图（Multi Model） | 验证通过 |
| --- | --- | --- | --- |
| https://api.siliconflow.cn/v1 | Qwen/Qwen3-32B | deepseek-ai/deepseek-vl2 | ✔️ |
| https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-turbo-latest | qwen-vl-max-latest | ✔️ |





## 安装与使用

### 方式一：源码运行（推荐开发者/高级用户）

1. **从GitHub下载项目**
   ```bash
   git clone https://github.com/yechafengyun/interview_ai_win11.git
   cd interview_ai_win11
   ```
2. **（可选）创建并激活虚拟环境**
   - Windows:
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
4. **运行程序**
   ```bash
   python main.py
   ```

### 方式二：直接运行打包好的exe（推荐普通用户）

1. 进入 [Releases](https://github.com/yechafengyun/interview_ai_win11/releases) 页面，下载最新的 [`main.exe`](https://github.com/yechafengyun/interview_ai_win11/releases/download/exe/main.exe)。
2. 双击 `main.exe` 即可直接运行，无需安装Python环境。

> 配置和使用过程中生成的 `config.json` 会自动保存在exe同目录下。

---

## 赞赏
- 如果你喜欢作者的项目，可以给作者一个免费的Star或者Follow。
- 如果该项目帮助到了你，欢迎赞赏与激励。

| 支付宝赞赏码 |
| --- |
| <img src="./.doc/支付宝二维码.jpg" width="200"> |


## TODO
- [ ] 后台运行，结果发送手机
- [ ] 从任务栏隐藏，计划用ctypes实现
- [ ] 分享屏幕不可见，该需求可以优先了解[interview-coder-withoupaywall-opensource项目](https://github.com/Ornithopter-pilot/interview-coder-withoupaywall-opensource)，以及




## 免责声明

本项目仅用于学习和研究目的，用户需自行承担使用风险。

## 致谢
[HIllya51/LunaTranslator](https://github.com/HIllya51/LunaTranslator)  
[SakiRinn/LiveCaptions-Translator](https://github.com/SakiRinn/LiveCaptions-Translator)  
本项目使用cursor开发，确实nb