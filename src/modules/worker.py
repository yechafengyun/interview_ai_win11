from PyQt6.QtCore import QThread, pyqtSignal
from openai import OpenAI

class WorkerThread(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, client, prompt, model, stream=True, image_base64=None):
        super().__init__()
        self.client = client
        self.prompt = prompt
        self.model = model
        self.stream = stream
        self.image_base64 = image_base64

    def run(self):
        try:
            if self.image_base64:
                # Image-based completion
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": [
                                {
                                    "type": "text",
                                    "text": self.prompt,
                                }
                            ],
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{self.image_base64}"
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": "请找出并解决图中的问题，回答尽量简洁",
                                },
                            ],
                        },
                    ],
                    stream=self.stream,
                )
            else:
                # Text-based completion
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": self.prompt}],
                    stream=self.stream,
                )

            if self.stream:
                response = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content is not None:
                        response += chunk.choices[0].delta.content
                        self.response_ready.emit(response)
            else:
                response = completion.choices[0].message.content
                self.response_ready.emit(response)

        except Exception as e:
            self.response_ready.emit(f"Error: {str(e)}") 