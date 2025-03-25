
# To build exe, run: pyinstaller --onefile --noconsole playground.py

import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import requests
import json
import time
import threading

response_for_copy = ""

# 请求的 URL 和头部信息
url = "http://10.119.11.146:3000/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-eBdspKZFfH70b8SfBaCcE9Ee7e7a4b3b87A46421B714F09e",
    "Content-Type": "application/json"
}

loading = False  # 全局变量，用于控制加载动画

def show_loading_animation():
    """显示加载动画"""
    global loading
    loading = True
    animation = ["-", "\\", "|", "/"]
    i = 0
    output_box.insert(tk.END, f"{animation[0]}")
    while loading:
        output_box.configure(state="normal")
        # 删除最后一行的动画字符
        output_box.delete("end-2c", tk.END)
        # 插入新的动画字符
        output_box.insert(tk.END, f"{animation[i % len(animation)]}")
        output_box.configure(state="disabled")
        i += 1
        time.sleep(0.1)  # 控制动画速度

# 发送请求并获取响应
def send_request(event=None):
    """发送请求的主函数"""
    def request_thread():
        global response_for_copy, loading
        user_input = input_box.get("1.0", tk.END).strip()  # 获取输入框内容
        current_time = time.strftime("[%H:%M:%S]", time.localtime())  # 获取当前时间
        if not user_input:
            output_box.configure(state="normal")
            output_box.insert(tk.END, f"\n\n---------------------------------------[{current_time}]---------------------------------------\nI haven't got any messages!")
            output_box.configure(state="disabled")
            output_box.see(tk.END)
            loading = False  # 停止动画
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
                    except Exception:
                        pass

            # 更新输出框
            output_box.configure(state="normal")
            # 删除动画字符
            output_box.delete("end-2c", tk.END)
            output_box.insert(tk.END, f"\n\n---------------------------------------[{current_time}]---------------------------------------\n{full_response}")
            response_for_copy = full_response  # 保存最新的回答
            output_box.see(tk.END)
            output_box.configure(state="disabled")
        except Exception as e:
            output_box.configure(state="normal")
            # 删除动画字符
            output_box.delete("end-2c", tk.END)
            output_box.insert(tk.END, f"\n\n---------------------------------------[{current_time}]---------------------------------------\nSomething happened: {e}")
            output_box.configure(state="disabled")
            # 划到最底下
            output_box.see(tk.END)
            response_for_copy = ""  # 清空回答
        finally:
            loading = False  # 停止动画

        input_box.delete("1.0", tk.END)  # 清空输入框

    # 启动加载动画线程
    threading.Thread(target=show_loading_animation, daemon=True).start()

    # 启动请求线程
    threading.Thread(target=request_thread, daemon=True).start()

# 定义复制功能
def copy_to_clipboard():
    output_box.configure(state="normal")  # 允许读取内容
    content = response_for_copy  # 获取输出框内容
    if content:
        root.clipboard_clear()  # 清空剪贴板
        root.clipboard_append(content)  # 将内容复制到剪贴板
        root.update()  # 更新剪贴板
    output_box.configure(state="disabled")  # 禁止编辑

# 定义刷新功能
def refresh_output(event=None):
    output_box.configure(state="normal")  # 允许编辑
    output_box.delete("1.0", tk.END)  # 清空输出框内容
    output_box.configure(state="disabled")  # 禁止编辑
    return "break"  # 阻止默认行为

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

input_box = scrolledtext.ScrolledText(
    root, wrap=tk.WORD, width=90, height=20, bg="#c4e4f3",
    fg="black", bd=0, relief="flat", font=(18), undo=True  # 启用撤销功能
)
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

# 绑定 Ctrl+Z 快捷键
def handle_undo(event=None):
    input_box.edit_undo()  # 调用撤销功能
    return "break"  # 阻止默认行为

input_box.bind("<Control-z>", handle_undo)

# 绑定 Ctrl+N 快捷键
root.bind("<Control-n>", refresh_output)

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

# 添加复制按钮
copy_button = tk.Button(
    root,
    text="Copy the latest answer",  # 按钮文字
    command=copy_to_clipboard,  # 绑定复制功能
    bg="#0e4764",
    fg="white",
    font=("Arial", 14),
    bd=0,
    relief="flat",
    width=20,
    height=1
)
copy_button.pack(pady=(0, 10))  # 放置按钮

# 输出框
output_label = tk.Label(root, text="Output", bg="#6f94a7", fg="white", font=("Courier", 28, "bold"))
output_label.pack()

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=30, bg="#c4e4f3", 
                                       fg="black", bd=0, relief="flat", font=(18))
output_box.pack(pady=(5, 10))
output_box.configure(state="disabled")  # 禁止用户编辑

# 运行主循环
root.mainloop()