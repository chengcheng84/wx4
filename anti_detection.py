from random import random
import pyautogui
import time
import json
from loguru import logger


def gather(duration, data_id="000000") -> dict[str, list]:
    time.sleep(2)
    print("Start to gather anti detection data")
    start = time.time()  # record start time
    move_history: list = []
    while (time.time() - start) < duration:
        x, y = pyautogui.position()
        move_history.append([x, y])
        # print(x, y)
        time.sleep(1 / 200)  # 200 times per second
    return {data_id: move_history}


def anti_detection_start(data_key: str, about_duration=5) -> None:
    with open("wx\\anti_detection.json", "r", encoding="utf-8") as f:
        anti_detection_data: dict = json.load(f)
        if anti_detection_start is None:
            logger
    for x, y in anti_detection_data[data_key]:
        pyautogui.moveTo((int(x * random()), int(y * random())))


if __name__ == "__main__":
    # with open("wx\\anti_detection.json", "w", encoding="utf-8") as f:
    # json.dump(gather(5), f)
    anti_detection_start("000000")
