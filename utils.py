import os.path
import time

import pyperclip
import pyautogui
import uiautomation as uia
from PIL import Image, ImageFile
from loguru import logger

logger.add(os.getenv("Logs"))


def SetClipboardText(text: str):
    pyperclip.copy(text)


class MSG:
    """
    wx的消息
    """

    def __init__(self, index: int, sender: str, content: str) -> None:
        self.sender = sender
        self.content = content
        self.index = index

    def __str__(self):
        return f"MSG(index={self.index}, sender={self.sender}, content={self.content})"

    def __repr__(self):
        return f"MSG(index={self.index}, sender={self.sender}, content={self.content})"


def merge_lists(a: list, b: list) -> list:
    """
    合并两个列表,去除重复部分
    Example:
        ```
        merge_lists([1,2,3,4,5],[3,4,5,6,7,8])
        ```
        Return [1,2,3,4,5,6,7,8]
    """

    def find_overlap(a: list, b: list) -> int:
        max_len = min(len(a), len(b))
        # Check for end of a and start of b overlap
        max_overlap = 0
        for overlap in range(max_len, -1, -1):
            if overlap == 0:
                break
            if a[-overlap:] == b[:overlap]:
                max_overlap = overlap
                break
        return max_overlap

    overlap = find_overlap(a, b)
    if overlap > 0:
        merged = a + b[overlap:]
    else:
        overlap_start = find_overlap(b, a)
        if overlap_start > 0:
            merged = b + a[overlap_start:]
        else:
            merged = a + b
    return merged


def capture_control_image(control):
    """
    根据控件对象截取屏幕上的控件图像。
    """
    rect = control.BoundingRectangle
    left = rect.left
    top = rect.top
    right = rect.right
    bottom = rect.bottom
    width = right - left
    height = bottom - top
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    return screenshot


def is_fully_visible(control):
    """
    判断控件是否完全可见
    :param control: uiautomation控件对象
    :return: True如果控件完全可见，False否则
    """
    # 首先检查控件是否在屏幕上
    if control.IsOffscreen:
        return False

    # 获取控件的边界矩形
    try:
        rect = control.BoundingRectangle
        if not rect:
            return False

        # 使用Rect对象的属性而不是下标访问
        left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom

        # 检查控件是否有有效的尺寸
        if right <= left or bottom <= top:
            return False

        # 获取桌面窗口（用于比较屏幕尺寸）
        desktop = uia.GetRootControl()
        desktop_rect = desktop.BoundingRectangle

        # 检查控件是否完全在桌面可见区域内
        return (
            left >= desktop_rect.left
            and top >= desktop_rect.top
            and right <= desktop_rect.right
            and bottom <= desktop_rect.bottom
        )
    except Exception as e:
        logger.error(f"检查可见性时出错: {e}")
        return False


def image_contains_color(image_path, tolerance=0) -> bool:
    """
    检查图片中是否包含(149, 236, 105)。

    :param image_path: 图片路径
    :param tolerance: 颜色容差
    :return: 如果图片中包含目标颜色，返回True，否则返回False
    """
    image: ImageFile = Image.open(image_path)
    image: ImageFile = image.convert("RGB")
    width, height = image.size
    count: int = 0
    for x in range(width):
        for y in range(height):
            pixel_color = image.getpixel((x, y))
            diff = sum(
                abs(a - b) for a, b in zip(pixel_color, (149, 236, 105))
            )  # 计算当前颜色与目标颜色之间的差值

            if diff <= tolerance:  # 如果差值小于容差，则认为颜色匹配
                count += 1
            if count > 50:
                return True
    return False


def GetSender(i) -> str:
    save_path = f"wxdata\\cache\\{str(i.GetRuntimeId())}.png"
    if (
        (i.Name != "图片")  # 是图片
        and (str(i.AutomationId) != "")  # 不是时间
        and (is_fully_visible(i))  # 控件完全可见
        and (i.Name != "文件")  # 是文件
    ):
        if not os.path.exists(save_path):
            screenshot = capture_control_image(i)
            screenshot.save(save_path)
        if image_contains_color(save_path):
            sender = "Self"
        else:
            sender = "Other"
    elif str(i.AutomationId) == "":
        sender = "SYS"
    else:
        sender = ""
    return sender

