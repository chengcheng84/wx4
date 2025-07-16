import os
import time
import random
from pathlib import Path

import uiautomation as uia
from loguru import logger

from .utils import *


class WeChat:
    VERSION: str = "4.x"

    def __init__(self) -> None:
        """微信UI自动化实例"""
        self.WXwindow: uia.WindowControl = uia.WindowControl(searchDepth=3, Name="微信")
        if not self.WXwindow.Exists(0.1):
            uia.SendKeys("{Ctrl}{Alt}w")
        # 日志
        self.logger = logger
        self.logger.remove()
        if os.getenv("Logs") is None:
            self.logger.add(os.path.join(".", "wx.log"))
            print(f"日志将保存到{os.path.join('.', 'wx.log')},使用Logs环境变量修改")
        else:
            self.logger.add(os.getenv("Logs"))
        # 清理缓存
        CacheFolder: Path = Path("wxdata") / "cache"
        for file in CacheFolder.iterdir():
            if file.is_file():
                file.unlink()

        self._show()
        self.RuntimeID2Data: dict = {}
        self.Runtimes_Msg: list = []
        self.AllMsgList: list = []
        self.A_Search: uia.EditControl = self.WXwindow.EditControl(Name="搜索")
        self.B_MsgList: uia.ListControl = self.WXwindow.ListControl(Name="消息")
        self.possible_fastest_message_sending_speed = 0.5
        self.MsgEditorBox = self.WXwindow.EditControl(AutomationId="chat_input_field")
        self.SaveTo = 0
        self.TheLastRuntimeID = None
        self.InitGetAllMessage()

        # GetNewMsgThread = threading.Thread(target=self._getnewmessage, daemon=True)
        # GetNewMsgThread.start()

    def send_enter(self) -> None:
        """按下回车键"""
        editbox = self.MsgEditorBox
        editbox.SendKeys("{ENTER}")

    def SendFiles(self, filepath: str | list[str], who: str | None = None) -> bool:
        """向当前聊天窗口发送文件

        Args:
            filepath (str|list): 要复制文件的绝对路径
            who (str): 要发送给谁，如果为None，则发送到当前聊天页面。  *最好完整匹配，优先使用备注

        Returns:
            bool: 是否成功发送文件
        """
        raise NotImplementedError("SendFiles方法未实现")

    # def GetAllMessage(
    #     self,
    #     savepic: bool = False,
    #     savefile: bool = False,
    #     savevoice: bool = False,
    #     readto: int = 0,
    # ) -> list:

    def InitGetAllMessage(self) -> list:
        """
        # To Fix
        获取所有消息的时候,RuntimeID可能重复，导致错误
        ## 方法
        1. 获取所有消息的RuntimeID（OK）
        2. 在每4个控件就生成MSG对象防止RuntimeID重复
        3. 获取每个控件的发送者（Bug, can't run）
        """
        self.LoadMoreMessage()
        self.logger.info("开始获取所有消息")
        Msg = self.B_MsgList
        # 按顺序的RuntimeId列表
        NoMore: int = 0
        while True:
            BeforeFirst = Msg.GetFirstChildControl().GetRuntimeId()
            if BeforeFirst == Msg.GetFirstChildControl().GetRuntimeId():
                NoMore += 1
                if NoMore > 2:  # 确保没有更多消息
                    break
            else:
                NoMore = 0
            IntheViewContralAllRuntimeID: list = []
            for i in Msg.GetChildren():
                sender: str = ""
                sender = GetSender(i)
                IntheViewContralAllRuntimeID.append(i.GetRuntimeId())
                self.RuntimeID2Data[str(i.GetRuntimeId())] = [i.Name, sender]
            self.Runtimes_Msg = merge_lists(
                self.Runtimes_Msg, IntheViewContralAllRuntimeID
            )
            Msg.WheelDown(wheelTimes=3, waitTime=random.random() / 3)
            if len(self.Runtimes_Msg) > self.SaveTo + 4:
                self.UpdataMsgList()
        self.TheLastRuntimeID = self.B_MsgList.GetLastChildControl().GetRuntimeId()

    def UpdataMsgList(self) -> None:
        # 将Runtimes_Msg中的消息整理为ALlMsgList，并清空Runtimes_Msg
        for index, runtime_id in enumerate(
            self.Runtimes_Msg[self.SaveTo :], start=len(self.AllMsgList) + 1
        ):
            data = self.RuntimeID2Data.get(str(runtime_id))
            if data:
                content, sender = data
                msg = MSG(index=index, sender=sender, content=content)
                self.AllMsgList.append(msg)
        self.SaveTo = len(self.Runtimes_Msg)

    def GetAllMessage(self) -> list[MSG]:
        self.UpdataMsgList()
        return self.AllMsgList

    def LoadMoreMessage(self) -> None:
        NoMore = 0
        while True:
            if self.B_MsgList.GetFirstChildControl().GetRuntimeId() is None:
                break
            BeforeFirst = self.B_MsgList.GetFirstChildControl().GetRuntimeId()
            self.B_MsgList.WheelUp(wheelTimes=30, waitTime=random.random())
            if BeforeFirst == self.B_MsgList.GetFirstChildControl().GetRuntimeId():
                NoMore += 1
                if NoMore > 3:
                    break
            else:
                NoMore = 0

    def GetAllFriends(self, keywords: str | None = None) -> list:
        """获取所有好友列表
        注：
            1. 该方法运行时间取决于好友数量，约每秒6~8个好友的速度
            2. 该方法未经过大量测试，可能存在未知问题，如有问题请微信群内反馈

        Args:
            keywords (str, optional): 搜索关键词，只返回包含关键词的好友列表

        Returns:
            list: 所有好友列表
        """
        return NotImplementedError("GetAllFriends无法使用")

    def get_new_message(self) -> None:
        # 监听新消息
        self.logger.info("开始监听新消息")
        LastRuntimeID = self.B_MsgList.GetLastChildControl().GetRuntimeId()
        if LastRuntimeID != self.TheLastRuntimeID:
            self.Runtimes_Msg.append(LastRuntimeID)
            control = self.B_MsgList.GetLastChildControl()
            sender: str = GetSender(control)
            self.RuntimeID2Data[str(control.GetRuntimeId())] = [
                control.Name,
                sender,
            ]
            self.TheLastRuntimeID = LastRuntimeID
        else:
            time.sleep(self.possible_fastest_message_sending_speed)

    def _checkversion(self):
        pass

    def _show(self) -> None:
        self.WXwindow.SetTopmost(True)

    def _refresh(self) -> None:
        self.WXwindow.SendKeys("{Ctrl}{Alt}w")
        self.WXwindow.SendKeys("{Ctrl}{Alt}w")
        self._show()

    def CheckNewMessage(self) -> bool:
        """是否有新消息"""
        pass

    def DownloadImage(self, imcontrol: uia.ImageControl) -> str:
        """
        Args:
            imcontrol (uia.ImageControl): 图片控件

        Returns:
            imgpath (str): 图片路径
        """
        impath = self._download_file(imcontrol)
        return impath if impath else "无法保存图片"

    def GetSessionList(self, reset: bool = False, newmessage: bool = False) -> dict:
        """获取当前聊天列表中的所有聊天对象

        Args:
            reset (bool): 是否重置SessionItemList
            newmessage (bool): 是否只获取有新消息的聊天对象

        Returns:
            SessionList (dict): 聊天对象列表，键为聊天对象名，值为新消息条数
        """
        pass

    def ChatWith(self, who: str, timeout: int = 2) -> bool:
        pass

    def SendMsg(
        self,
        msg: str,
        clear: bool = True,
        send: bool = True,
    ) -> None:
        """发送文本消息

        Args:
            msg (str): 要发送的文本消息
            who (str): 要发送给谁，如果为None，则发送到当前聊天页面。  *最好完整匹配，优先使用备注
            clear (bool, optional): 是否清除原本的内容，
            send (bool, optional): 是否发送，默认为True
        """
        self._show()
        if not self.MsgEditorBox.HasKeyboardFocus:
            self.MsgEditorBox.Click(simulateMove=False)
        if clear:
            self.MsgEditorBox.SendKeys("{Ctrl}a", waitTime=0)

        if msg:
            t0 = time.time()
            while True:
                if time.time() - t0 > 10:
                    self.logger.error(
                        f"发送消息超时 --> {self.MsgEditorBox.Name} - {msg}"
                    )
                SetClipboardText(msg)
                self.MsgEditorBox.SendKeys("{Ctrl}v")
                if self.MsgEditorBox.GetValuePattern().Value:
                    break
        if send:
            self.MsgEditorBox.SendKeys("{Enter}")

    def GetWeiXinID(self, index=-1):
        MsgControl = self.B_MsgList.GetChildren()[index]
        rect = MsgControl.BoundingRectangle
        left = rect.left
        top = rect.top
        pyautogui.click(left + 40, top + 30)
        automation_id = (
            "right_v_view.user_info_center_view.basic_line_view.ContactProfileTextView"
        )
        time.sleep(0.5)
        weixin = uia.WindowControl(Name="Weixin")
        WeiXinId = (
            weixin.TextControl(
                AutomationId=automation_id, ClassName="mmui::ContactProfileTextView"
            )
            .GetParentControl()
            .GetParentControl()
            .GetChildren()[1]
            .GetChildren()[-1]
            .Name
        )
        return WeiXinId
