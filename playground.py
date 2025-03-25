import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import requests
import json
import time


# 请求的 URL 和头部信息
url = "http://10.119.11.146:3000/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-eBdspKZFfH70b8SfBaCcE9Ee7e7a4b3b87A46421B714F09e",
    "Content-Type": "application/json"
}

# 发送请求并获取响应
def send_request(event=None):  # 支持绑定事件
    user_input = input_box.get("1.0", tk.END).strip()  # 获取输入框内容
    current_time = time.strftime("[%H:%M:%S]", time.localtime())  # 获取当前时间
    if not user_input:
        output_box.configure(state="normal")
        output_box.insert(tk.END, f"[{current_time}]\nI haven't got any messages!\n\n")
        output_box.configure(state="disabled")
        return

    # 获取当前选择的模型
    model = selected_model.get()

    data = {
        "model": model,  # 动态设置模型
        "stream": True,
        "messages": [
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.encoding = 'utf-8'  # 确保以 UTF-8 解码
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:  # 忽略空行
                if line.strip() == "[DONE]":  # 忽略结束标记
                    break
                try:
                    chunk = json.loads(line[5:])  # 去掉 "data: "
                    if "choices" in chunk:
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            full_response += delta["content"]
                except Exception as e:
                    output_box.configure(state="normal")
                    output_box.insert(tk.END, f"")
                    output_box.configure(state="disabled")

        output_box.configure(state="normal")
        output_box.insert(tk.END, f"[{current_time}]\n{full_response}\n\n")
        output_box.configure(state="disabled")
    except Exception as e:
        output_box.configure(state="normal")
        output_box.insert(tk.END, f"[{current_time}]\nSomething happened: {e}\n\n")
        output_box.configure(state="disabled")

    input_box.delete("1.0", tk.END)  # 清空输入框

# 创建主窗口
root = tk.Tk()
root.title("Chat with GPT")
root.configure(bg="#6f94a7")  # 设置深灰色背景

# 添加一个变量用于存储当前选择的模型
selected_model = tk.StringVar(value="gpt-4o")  # 默认值为 "gpt-4o"

# 创建一个下拉菜单
model_label = tk.Label(root, text="Model", bg="#6f94a7", fg="white", font=("Courier", 16, "bold"))
model_label.place(x=825, y=19)  # 将标签放置在右上角

model_menu = tk.OptionMenu(root, selected_model, "gpt-4o", "gpt-o3")
model_menu.config(bg="#8ba1ad", fg="white", font=("Courier", 12, "bold"), relief="flat")
model_menu.place(x=900, y=15)  # 将下拉菜单放置在右上角

# 设置窗口大小
root.geometry("1050x1250")  # 宽800，高600

# 输入框
input_label = tk.Label(root, text="Input", bg="#6f94a7", fg="white", font=("Courier", 28, "bold"))
input_label.pack(pady=(10, 0))

input_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=20, bg="#c4e4f3", 
                                      fg="black", bd=0, relief="flat", font=(18))
input_box.pack(pady=(5, 10))
input_box.configure(insertbackground="black")  # 设置光标颜色

# 绑定键盘事件
def handle_keypress(event):
    if event.keysym == "Return":  # 检测 Enter 键
        if event.state & 0x0001:  # 检测 Shift 键是否按下
            input_box.insert(tk.INSERT, "\n")  # 换行
        else:
            send_request()  # 发送消息
            return "break"  # 阻止默认的换行行为

input_box.bind("<KeyPress-Return>", handle_keypress)

# 发送按钮
send_button = tk.Button(
    root,
    text="➤",  # 使用箭头符号
    command=send_request,
    bg="#0e4764",
    fg="white",
    font=("Arial", 14),
    bd=0,
    relief="flat",
    width=20,
    height=1
)
send_button.pack(pady=(0, 10))

# 输出框
output_label = tk.Label(root, text="Output", bg="#6f94a7", fg="white", font=("Courier", 28, "bold"))
output_label.pack()

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=30, bg="#c4e4f3", 
                                       fg="black", bd=0, relief="flat", font=(18))
output_box.pack(pady=(5, 10))
output_box.configure(state="disabled")  # 禁止用户编辑

# 运行主循环
root.mainloop()