import win32api
import win32con
from screenCapture import screen_capture
import time

def draw_line(rect, duration=0.5):
    """使用绝对坐标映射的可靠绘制"""
    # 将屏幕坐标转换为绝对坐标（0-65535）
    def to_abs(x, y):
        return (
            int(x * 65535 / win32api.GetSystemMetrics(0)),
            int(y * 65535 / win32api.GetSystemMetrics(1))
        )

    # 计算绝对坐标
    start_x, start_y = rect[0] + 300, rect[1] + 300
    end_x, end_y = rect[2] - 200, rect[3] - 150

    # 转换为绝对坐标
    abs_start = to_abs(start_x, start_y)
    abs_end = to_abs(end_x, end_y)

    # 设置初始位置
    win32api.SetCursorPos((start_x, start_y))
    time.sleep(0.1)  # 增加初始延迟

    # 发送绝对坐标的鼠标事件
    flags = win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE
    win32api.mouse_event(flags, abs_start[0], abs_start[1])
    time.sleep(0.1)  # 增加点击延迟
    
    # 移动鼠标
    flags = win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE
    win32api.mouse_event(flags, abs_end[0], abs_end[1], 0, 0)
    time.sleep(duration)
    
    # 释放鼠标
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

if __name__ == "__main__":
    captured_rect = screen_capture()
    draw_line(captured_rect)