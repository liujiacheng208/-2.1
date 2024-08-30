import tkinter as tk
from tkinter import scrolledtext, Entry, Button
import socket
import threading

class ChatApp:
    def __init__(self, root, client):
        self.root = root
        self.root.title("聊天应用1.4")
        self.client = client

        # 设置聊天消息框
        self.chat_messages = scrolledtext.ScrolledText(self.root, width=80, height=20, wrap=tk.WORD)
        self.chat_messages.pack(pady=20, side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 设置发送消息的输入框
        self.entry_message = Entry(self.root, width=80)
        self.entry_message.pack(pady=10, side=tk.BOTTOM, fill=tk.X)

        # 设置发送按钮
        self.send_button = Button(self.root, text="发送", command=self.send_message)
        self.send_button.pack(pady=10, side=tk.RIGHT)

        # 启动消息接收线程
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def send_message(self):
        message = self.entry_message.get()
        if message:
            self.chat_messages.insert(tk.END, f"我: {message}\n")
            self.client.send(message.encode('utf-8'))
            self.entry_message.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                reply = self.client.recv(1024).decode('utf-8')
                if reply:
                    self.chat_messages.insert(tk.END, f"对方: {reply}\n")
            except Exception as e:
                print(f"接收消息时发生错误: {e}")
                break

def main():
    # 创建主窗口
    root = tk.Tk()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8080))
    app = ChatApp(root, client)
    root.mainloop()

if __name__ == "__main__":
    main()

