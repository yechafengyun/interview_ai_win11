import sys

sys.coinit_flags = 2

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QTabWidget,
    QComboBox,
    QGroupBox,
    QScrollArea,
    QKeySequenceEdit,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer
import keyboard
from PIL import ImageGrab
import io
import base64
from openai import OpenAI
from pywinauto import Application
import ctypes

from ..config.config import Config
from ..modules.worker import WorkerThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.init_ui()
        self.setup_hotkeys()
        self.live_captions_app = None
        self.worker = None

    def init_ui(self):
        self.setWindowTitle("Interview AI Assistant")
        self.setGeometry(100, 100, 1200, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Create main tab
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)

        # Input area (1/5 of the height)
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(150)
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group, 1)

        # Output area (4/5 of the height)
        output_group = QGroupBox("Response")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group, 4)

        # Buttons
        button_layout = QHBoxLayout()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_text)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.clear_button)
        main_layout.addLayout(button_layout)

        tabs.addTab(main_tab, "Main")

        # Create settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        # Create scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create widget to hold all settings
        settings_widget = QWidget()
        settings_widget_layout = QVBoxLayout(settings_widget)

        # API Settings
        api_group = QGroupBox("API Settings")
        api_layout = QVBoxLayout()

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.config.api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.textChanged.connect(self.save_settings)
        api_key_layout.addWidget(self.api_key_input)
        api_layout.addLayout(api_key_layout)

        # Base URL
        base_url_layout = QHBoxLayout()
        base_url_layout.addWidget(QLabel("Base URL:"))
        self.base_url_combo = QComboBox()
        self.base_url_combo.setEditable(True)
        self.base_url_combo.addItems(
            [
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "https://api.siliconflow.cn/v1",
                "https://api.deepseek.com/v1",
                "https://api.openai.com/v1",
                "https://api.moonshot.cn/v1",
            ]
        )
        self.base_url_combo.setCurrentText(self.config.base_url)
        self.base_url_combo.currentTextChanged.connect(self.save_settings)
        self.base_url_combo.lineEdit().editingFinished.connect(self.save_settings)
        base_url_layout.addWidget(self.base_url_combo)
        api_layout.addLayout(base_url_layout)

        api_group.setLayout(api_layout)
        settings_widget_layout.addWidget(api_group)

        # Model Settings
        model_group = QGroupBox("Model Settings")
        model_layout = QVBoxLayout()

        # Language
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.setEditable(True)
        self.language_combo.addItems(["中文", "日本語", "English"])
        self.language_combo.setCurrentText(self.config.language)
        self.language_combo.currentTextChanged.connect(self.save_settings)
        self.language_combo.lineEdit().editingFinished.connect(self.save_settings)
        language_layout.addWidget(self.language_combo)
        model_layout.addLayout(language_layout)

        # Model Selection
        model_selection_layout = QHBoxLayout()
        model_selection_layout.addWidget(QLabel("LLM Model:"))
        self.llm_model_combo = QComboBox()
        self.llm_model_combo.setEditable(True)
        self.llm_model_combo.addItems(
            [
                "qwen-turbo-latest",
                "qwen-plus",
                "deepseek-v3",
                "gpt-3.5-turbo",
                "gpt-4o",
                "gpt-4",
                "glm-4",
                "yi-34b-chat",
                "moonshot-v1-128k",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
            ]
        )
        self.llm_model_combo.setCurrentText(self.config.llm_model)
        self.llm_model_combo.currentTextChanged.connect(self.save_settings)
        self.llm_model_combo.lineEdit().editingFinished.connect(self.save_settings)
        model_selection_layout.addWidget(self.llm_model_combo)
        model_layout.addLayout(model_selection_layout)

        # Multi-model Selection
        multi_model_layout = QHBoxLayout()
        multi_model_layout.addWidget(QLabel("Multi-model:"))
        self.multi_model_combo = QComboBox()
        self.multi_model_combo.setEditable(True)
        self.multi_model_combo.addItems(
            [
                "qwen-vl-max-latest",
                "qwen-vl-plus-latest",
                "gpt-4-vision-preview",
                "deepseek-vl",
                "moonshot-v1-128k",
                "yi-vision",
                "gemini-pro-vision",
            ]
        )
        self.multi_model_combo.setCurrentText(self.config.multimodel)
        self.multi_model_combo.currentTextChanged.connect(self.save_settings)
        self.multi_model_combo.lineEdit().editingFinished.connect(self.save_settings)
        multi_model_layout.addWidget(self.multi_model_combo)
        model_layout.addLayout(multi_model_layout)

        model_group.setLayout(model_layout)
        settings_widget_layout.addWidget(model_group)

        # Hotkey Settings
        hotkey_group = QGroupBox("Hotkey Settings")
        hotkey_layout = QVBoxLayout()

        # Voice Recognition Hotkey
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice Recognition:"))
        self.voice_hotkey_input = QKeySequenceEdit()
        self.voice_hotkey_input.setKeySequence(self.config.hotkey_voice)
        self.voice_hotkey_input.editingFinished.connect(self.update_voice_hotkey)
        voice_layout.addWidget(self.voice_hotkey_input)
        hotkey_layout.addLayout(voice_layout)

        # Screenshot Hotkey
        screenshot_layout = QHBoxLayout()
        screenshot_layout.addWidget(QLabel("Screenshot Recognition:"))
        self.screenshot_hotkey_input = QKeySequenceEdit()
        self.screenshot_hotkey_input.setKeySequence(self.config.hotkey_screenshot)
        self.screenshot_hotkey_input.editingFinished.connect(self.update_screenshot_hotkey)
        screenshot_layout.addWidget(self.screenshot_hotkey_input)
        hotkey_layout.addLayout(screenshot_layout)

        hotkey_group.setLayout(hotkey_layout)
        settings_widget_layout.addWidget(hotkey_group)

        # Prompt Templates
        prompt_group = QGroupBox("Prompt Templates")
        prompt_layout = QVBoxLayout()

        # Coding Prompt
        prompt_layout.addWidget(QLabel("Coding Prompt:"))
        self.coding_prompt_input = QTextEdit()
        self.coding_prompt_input.setText(self.config.coding_prompt)
        self.coding_prompt_input.textChanged.connect(self.save_settings)
        prompt_layout.addWidget(self.coding_prompt_input)

        # LLM Prompt
        prompt_layout.addWidget(QLabel("LLM Prompt:"))
        self.llm_prompt_input = QTextEdit()
        self.llm_prompt_input.setText(self.config.llm_prompt)
        self.llm_prompt_input.textChanged.connect(self.save_settings)
        prompt_layout.addWidget(self.llm_prompt_input)

        prompt_group.setLayout(prompt_layout)
        settings_widget_layout.addWidget(prompt_group)

        # Set the scroll area's widget
        scroll.setWidget(settings_widget)
        settings_layout.addWidget(scroll)

        tabs.addTab(settings_tab, "Settings")

    def try_register_hotkey(self, hotkey, callback):
        try:
            if hotkey and hotkey.strip():
                keyboard.add_hotkey(hotkey, callback)
                return True
        except Exception as e:
            print(f"注册快捷键失败: {hotkey}, 错误: {e}")
        return False

    def setup_hotkeys(self):
        # 注册 voice_hotkey
        hotkey = self.config.hotkey_voice
        if not self.try_register_hotkey(hotkey, lambda: QTimer.singleShot(0, self.capture_caption)):
            default_hotkey = self.config.DEFAULT_CONFIG["hotkey_voice"]
            if self.try_register_hotkey(default_hotkey, lambda: QTimer.singleShot(0, self.capture_caption)):
                self.config.hotkey_voice = default_hotkey
                self.voice_hotkey_input.setKeySequence(default_hotkey)
                self.config.save_config()
        # 注册 screenshot_hotkey
        hotkey = self.config.hotkey_screenshot
        if not self.try_register_hotkey(hotkey, lambda: QTimer.singleShot(0, self.capture_image)):
            default_hotkey = self.config.DEFAULT_CONFIG["hotkey_screenshot"]
            if self.try_register_hotkey(default_hotkey, lambda: QTimer.singleShot(0, self.capture_image)):
                self.config.hotkey_screenshot = default_hotkey
                self.screenshot_hotkey_input.setKeySequence(default_hotkey)
                self.config.save_config()

    def update_voice_hotkey(self):
        new_hotkey = self.voice_hotkey_input.keySequence().toString()
        old_hotkey = self.config.hotkey_voice
        if new_hotkey and new_hotkey.strip():
            if self.try_register_hotkey(new_hotkey, lambda: QTimer.singleShot(0, self.capture_caption)):
                # 新的注册成功，移除旧的
                try:
                    if old_hotkey and old_hotkey.strip():
                        keyboard.remove_hotkey(old_hotkey)
                except Exception:
                    pass
                self.config.hotkey_voice = new_hotkey
                self.save_settings()
            else:
                # 注册失败，恢复旧值
                self.voice_hotkey_input.setKeySequence(old_hotkey)
                # 可弹窗提示
        else:
            # 清空时移除旧的
            try:
                if old_hotkey and old_hotkey.strip():
                    keyboard.remove_hotkey(old_hotkey)
            except Exception:
                pass
            self.config.hotkey_voice = ""
            self.save_settings()

    def update_screenshot_hotkey(self):
        new_hotkey = self.screenshot_hotkey_input.keySequence().toString()
        old_hotkey = self.config.hotkey_screenshot
        if new_hotkey and new_hotkey.strip():
            if self.try_register_hotkey(new_hotkey, lambda: QTimer.singleShot(0, self.capture_image)):
                try:
                    if old_hotkey and old_hotkey.strip():
                        keyboard.remove_hotkey(old_hotkey)
                except Exception:
                    pass
                self.config.hotkey_screenshot = new_hotkey
                self.save_settings()
            else:
                self.screenshot_hotkey_input.setKeySequence(old_hotkey)
        else:
            try:
                if old_hotkey and old_hotkey.strip():
                    keyboard.remove_hotkey(old_hotkey)
            except Exception:
                pass
            self.config.hotkey_screenshot = ""
            self.save_settings()

    def save_settings(self):
        self.config.api_key = (
            self.api_key_input.text()
            if hasattr(self, "api_key_input")
            else self.config.api_key
        )
        self.config.base_url = (
            self.base_url_combo.currentText()
            if hasattr(self, "base_url_combo")
            else self.config.base_url
        )
        self.config.language = (
            self.language_combo.currentText()
            if hasattr(self, "language_combo")
            else self.config.language
        )
        self.config.llm_model = (
            self.llm_model_combo.currentText()
            if hasattr(self, "llm_model_combo")
            else self.config.llm_model
        )
        self.config.multimodel = (
            self.multi_model_combo.currentText()
            if hasattr(self, "multi_model_combo")
            else self.config.multimodel
        )
        self.config.coding_prompt = (
            self.coding_prompt_input.toPlainText()
            if hasattr(self, "coding_prompt_input")
            else self.config.coding_prompt
        )
        self.config.llm_prompt = (
            self.llm_prompt_input.toPlainText()
            if hasattr(self, "llm_prompt_input")
            else self.config.llm_prompt
        )
        self.config.save_config()

    def cleanup_worker(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.worker = None

    def send_message(self):
        self.capture_caption()

    def update_output(self, text):
        self.output_text.setMarkdown(text)
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )

    def clear_text(self):
        self.cleanup_worker()
        self.input_text.clear()
        self.output_text.clear()

    def launch_live_captions(self):
        try:
            if self.live_captions_app is None:
                self.live_captions_app = Application(backend="uia").connect(
                    path="LiveCaptions.exe"
                )
                print("Connected to existing Live Captions instance.")
        except Exception:
            print("Starting a new Live Captions instance.")
            self.live_captions_app = Application(backend="uia").start(
                "LiveCaptions.exe"
            )
        try:
            SW_MINIMIZE = 6
            for window in self.live_captions_app.windows():
                hwnd = window.handle
                ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
        except Exception as e:
            print(f"Failed to minimize Live Captions window: {e}")
        return self.live_captions_app

    def find_live_captions_window(self, app):
        for window in app.windows():
            for child_window in window.descendants():
                properties = child_window.get_properties()
                if properties["class_name"] == "TextBlock":
                    return child_window
        return None

    def capture_caption(self):
        try:
            self.cleanup_worker()

            if self.live_captions_app is None:
                self.live_captions_app = self.launch_live_captions()

            child_window = self.find_live_captions_window(self.live_captions_app)
            if child_window:
                full_text = child_window.texts()[0].strip()
                if full_text:
                    self.input_text.setPlainText(full_text)
                    client = OpenAI(
                        api_key=self.config.api_key, base_url=self.config.base_url
                    )
                    prompt = self.config.llm_prompt.format(
                        language=self.config.language
                    )
                    self.worker = WorkerThread(
                        client, f"{prompt}\n{full_text}", self.config.llm_model
                    )
                    self.worker.response_ready.connect(self.update_output)
                    self.worker.start()
            else:
                self.output_text.setPlainText(
                    "Error: Could not find Live Captions text window"
                )
        except Exception as e:
            self.output_text.setPlainText(f"Error capturing caption: {str(e)}")
            self.live_captions_app = None

    def capture_image(self):
        try:
            self.cleanup_worker()

            image = ImageGrab.grabclipboard()
            if not image:
                image = ImageGrab.grab()

            buffered = io.BytesIO()
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image.save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode()

            client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
            prompt = self.config.coding_prompt.format(language=self.config.language)

            self.worker = WorkerThread(
                client=client,
                prompt=prompt,
                model=self.config.multimodel,
                image_base64=base64_image,
            )
            self.worker.response_ready.connect(self.update_output)
            self.worker.start()

        except Exception as e:
            self.output_text.setPlainText(f"Error capturing image: {str(e)}")

    def closeEvent(self, event):
        self.cleanup_worker()
        super().closeEvent(event)
