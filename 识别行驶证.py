import os
import subprocess
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import json
import re

def process_file(filepath):
    """处理单个文件，调用外部程序并解析结果"""
    try:
        # 获取当前脚本的目录
        script_dir = os.path.dirname(os.path.realpath(__file__))
        print(f"当前脚本所在目录: {script_dir}")
        
        # 构造 exe 文件的路径
        exe_path = os.path.join(script_dir, 'x64', 'Release', 'XingshizhengSDK.exe')
        print(f"构造的 exe 路径: {exe_path}")

        # 检查路径是否正确
        if not os.path.exists(exe_path):
            print(f"路径检查失败: {exe_path} 不存在！")
            text_output_process.insert(tk.END, f"程序路径不存在: {exe_path}\n")
            return
        else:
            print(f"程序路径存在: {exe_path}")

        # 调用 exe
        command = f'"{exe_path}" "{filepath}"'
        print(f"准备执行命令: {command}")

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        
        text_output_process.insert(tk.END, f"正在处理文件: {filepath}\n")
        text_output_process.see(tk.END)
        
        output_lines = []
        raw_json_output = ""  # 用来存储原始 JSON 输出
        
        for line in process.stdout:
            output_lines.append(line.strip())
            text_output_process.insert(tk.END, f"{line.strip()}\n")  # 实时输出到第一个文本框
            text_output_process.see(tk.END)  # 滚动到最新行
            root.update()  # 更新界面
            
            # 检测到 "Processing complete!" 时尝试提取 JSON 数据
            if "Processing complete!" in line:
                match = re.search(r'(\{.*\})', "\n".join(output_lines), re.DOTALL)
                if match:
                    raw_json_output = match.group(0)
                    print(f"提取到的 JSON 输出：{raw_json_output}")  # 输出原始 JSON 字符串
                break
        
        process.wait()  # 等待进程结束
        
        if process.returncode != 0:
            error_message = process.stderr.read().strip()
            print(f"程序执行错误: {error_message}")
            text_output_process.insert(tk.END, f"程序运行错误：{error_message}\n")
            text_output_process.see(tk.END)
            return

        # 处理并显示 JSON 输出
        if raw_json_output:
            handle_json_output(filepath, raw_json_output)
        else:
            text_output_result.insert(tk.END, f"未提取到有效的 JSON 数据：{filepath}\n")

    except Exception as e:
        print(f"发生错误: {e}")
        text_output_process.insert(tk.END, f"发生错误: {e}\n")
    finally:
        text_output_process.see(tk.END)  # 确保滚动到最新行

def handle_json_output(filepath, raw_json_output):
    """处理并格式化 JSON 输出"""
    try:
        # 去除多余的换行符和空格
        raw_json_output = raw_json_output.replace('\n', '').replace('\r', '').strip()

        # 尝试解析 JSON
        data = json.loads(raw_json_output)
        
        if data.get("err_no") == 0:
            ret_data = data.get("ret", {})
            formatted_data = "\n".join([
                f"文件: {filepath}",
                f"号牌号码: {ret_data.get('号牌号码', 'N/A')}",
                f"车辆类型: {ret_data.get('车辆类型', 'N/A')}",
                f"所有人: {ret_data.get('所有人', 'N/A')}",
                f"品牌型号: {ret_data.get('品牌型号', 'N/A')}",
                f"车辆识别代号: {ret_data.get('车辆识别代号', 'N/A')}",
                f"发动机号码: {ret_data.get('发动机号码', 'N/A')}",
                f"注册日期: {ret_data.get('注册日期', 'N/A')}",
                f"发证日期: {ret_data.get('发证日期', 'N/A')}",
                "----------"
            ])
            text_output_result.insert(tk.END, f"{formatted_data}\n")
        else:
            text_output_result.insert(tk.END, f"文件: {filepath}\n识别失败: {data.get('err_msg')}\n----------\n")
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"原始输出: {raw_json_output}")  # 打印原始输出，帮助调试
        text_output_result.insert(tk.END, f"文件: {filepath}\nJSON 解析失败，原始输出: {raw_json_output}\n----------\n")

def on_drop(event):
    """处理拖放事件，支持多个文件"""
    filepaths = event.data.strip().split()  # 获取拖放的文件路径列表
    for filepath in filepaths:
        process_file(filepath)

# 创建 Tkinter 窗体
root = TkinterDnD.Tk()
root.title("智能识别行驶证")

# 获取屏幕尺寸和窗口尺寸，使窗口居中
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 800
window_height = 600
x_cordinate = (screen_width // 2) - (window_width // 2)
y_cordinate = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

# 创建两个文本框，分别用于显示过程和最终结果
frame = tk.Frame(root)
frame.pack(expand=1, fill="both")

text_output_process = tk.Text(frame, wrap="word", font=("Courier", 10))
text_output_process.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

text_output_result = tk.Text(frame, wrap="word", font=("Courier", 10))
text_output_result.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

frame.grid_rowconfigure(0, weight=1)
frame.grid_rowconfigure(1, weight=1)
frame.grid_columnconfigure(0, weight=1)

# 绑定拖放事件
root.drop_target_register(DND_FILES)
root.dnd_bind("<<Drop>>", on_drop)

# 启动应用程序
text_output_process.insert(tk.END, "请将图片拖放到窗口中以开始识别。\n")
root.mainloop()

