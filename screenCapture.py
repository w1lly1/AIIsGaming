import win32process
import win32api
import pygetwindow as gw
import psutil
import os
from PIL import ImageGrab  # 新增截图库
from ctypes import windll


# 获取所有显示器信息
def get_screen_info():
    monitors = []
    for i in range(win32api.GetSystemMetrics(80)):  # 获取显示器数量
        # print(f'screen id: {i+1}')
        monitor = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[i][0])
        # print(f'screen {i+1} para: "left"= {monitor["Monitor"][0]},\
        #     "top"={monitor["Monitor"][1]},\
        #     "width"={monitor["Monitor"][2] - monitor["Monitor"][0]},\
        #     "height"={monitor["Monitor"][3] - monitor["Monitor"][1]}')
        monitors.append({
            "screen_num": i + 1,
            "left": monitor["Monitor"][0],
            "top": monitor["Monitor"][1],
            "width": monitor["Monitor"][2] - monitor["Monitor"][0],
            "height": monitor["Monitor"][3] - monitor["Monitor"][1]
        })
    return monitors

def cache_cleanup():
    cache_path = "Cache/ScreenSnapshot"
    if os.path.exists(cache_path):
        for root, _, files in os.walk(cache_path):
            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    os.remove(os.path.join(root, f))
        print(f"已清理缓存目录: {cache_path}")

# 问题在于我不知道桌面上的是父进程还是子进程-。-
def get_process_window(process_name: str):
    # 通过进程名查找进程
    target_pid = None
    # 先查找主进程
    for proc in psutil.process_iter(['pid', 'name', 'ppid']):
        print(f"进程: {proc.info['name']}")
        if proc.info['name'] == process_name:
            # 查找其子进程（VS Code窗口通常由子进程创建）
            target_pid = proc.info['pid']
            break

    if not target_pid:
        raise Exception(f"未找到{process_name}进程")

    # 窗口匹配
    for window in gw.getAllWindows():
        try:
            _, pid = win32process.GetWindowThreadProcessId(window._hWnd)
            # 匹配进程及其子进程
            if pid == target_pid or psutil.Process(pid).ppid() == target_pid:
                # 添加窗口标题验证
                # if "Visual Studio Code" in window.title:
                return window
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    raise Exception(f"找到进程但未找到有效窗口（尝试通过标题查找：{gw.getWindowsWithTitle('Visual Studio Code')}")

def screen_capture():
    cache_cleanup()
    try:
        screens = get_screen_info()
        # 查找屏幕1
        screen1 = next((s for s in screens if s["screen_num"] == 1), None)
        if not screen1:
            raise Exception("未找到屏幕1")

        # 仅截取屏幕1
        rect = (
            screen1["left"],
            screen1["top"],
            screen1["left"] + screen1["width"],
            screen1["top"] + screen1["height"]
        )
        ImageGrab.grab(bbox=rect).save("Cache/ScreenSnapshot/screen.png")
        print("屏幕截图已保存")
        return rect

    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    screen_capture()