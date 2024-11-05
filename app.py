from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# 配置OpenAI客户端
client = OpenAI(
    api_key="sk-a4156f5fe5db4412a9020740eedf888b",  # 替换为你的API密钥
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    text = request.form.get('text')
    image_file = request.files.get('image')

    if not image_file:
        return jsonify({"error": "No image file provided"}), 400

    # 将文件转换为base64编码的字符串
    image_stream = BytesIO(image_file.read())
    image = Image.open(image_stream)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # 构建消息列表
    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
        ]}
    ]

    # 调用大模型API
    try:
        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=messages
        )
        response_content = completion.choices[0].message.content
        return jsonify({"response": response_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)