import time
import random
from pathlib import Path

import uiautomation as uia
from dotenv import load_dotenv
import pyautogui

from utils.utils import get_logger
from .utils import *
# from wx.anti_detection import anti_detection_start


if load_dotenv(dotenv_path=".env") is None:
    print("Error to load env")
    exit(1)


class WeChat:
    VERSION: str = "4.x"

    def __init__(self, init_msglist: bool = True, chat_with: str | None = None) -> None:
        """微信UI自动化实例"""
        self.WXwindow: uia.WindowControl = uia.WindowControl(searchDepth=3, Name="微信")
        if not self.WXwindow.Exists(0.1):
            uia.SendKeys("{Ctrl}{Alt}w")
        # 日志
        self.logger = get_logger()
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
        self.A_contacts: uia.ListControl = self.WXwindow.ListControl(Name="会话")
        self.possible_fastest_message_sending_speed = 0.5
        self.MsgEditorBox = self.WXwindow.EditControl(AutomationId="chat_input_field")
        self.SaveTo = 0
        self.TheLastRuntimeID = None
        if chat_with is not None:
            print(self.ChatWith(chat_with))
        if init_msglist:
            self.InitGetAllMessage()

    def send_enter(self) -> None:
        """按下回车键"""
        editbox = self.MsgEditorBox
        editbox.SendKeys("{ENTER}")

    def ChatWith(self, contact_name: str) -> tuple[str, int] | tuple[None, None]:
        """切换聊天列表
        Args:
            contact_name:联系人的名字
        """
        for i, contact in enumerate(self.A_contacts.GetChildren()):
            print(str(contact.Name).split(" "), contact_name)
            if str(contact.Name).split(" ")[0] == contact_name:
                contact.Click()
                return (contact.Name, i)
        return (None, None)

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

    def InitGetAllMessage(self) -> None:
        """
        # To Fix
        获取所有消息的时候,RuntimeID可能重复，导致错误
        ## 方法
        1. 获取所有消息的RuntimeID（OK）
        2. 在每4个控件就生成MSG对象防止RuntimeID重复
        3. 获取每个控件的发送者（Bug, can't run）
        """
        self.move_to_msglist()
        self.LoadMoreMessage()
        self.logger.info("开始获取所有消息")
        Msg = self.B_MsgList
        # 按顺序的RuntimeId列表
        NoMore: int = 0
        while True:
            BeforeFirst = Msg.GetFirstChildControl().GetRuntimeId()
            if BeforeFirst == Msg.GetFirstChildControl().GetRuntimeId():
                NoMore += 1
                if NoMore > 10:  # 确保没有更多消息
                    break
            else:
                NoMore = 0
            IntheViewContralAllRuntimeID: list = []
            msg_children = Msg.GetChildren()
            if NoMore < 8:
                msg_children = msg_children[:-1]
            for i in msg_children:
                sender: str = ""
                time.sleep(0.1)
                sender = GetSender(i)
                IntheViewContralAllRuntimeID.append(i.GetRuntimeId())
                self.RuntimeID2Data[str(i.GetRuntimeId())] = [i.Name, sender]
            self.Runtimes_Msg = merge_lists(
                self.Runtimes_Msg, IntheViewContralAllRuntimeID
            )
            wheel_control(Msg, wheel_range=[-1500, -1000])
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
            wheel_control(self.B_MsgList, wheel_range=[4900, 6000])
            if BeforeFirst == self.B_MsgList.GetFirstChildControl().GetRuntimeId():
                NoMore += 1
                if NoMore > 3:
                    break
            else:
                NoMore = 0

    def GetAllFriends(self, keywords: str | None = None) -> list:
        """获取所有好友列表
        Args:
            keywords (str, optional): 搜索关键词，只返回包含关键词的好友列表

        Returns:
            list: 所有好友列表
        """
        return NotImplementedError("GetAllFriends无法使用")

    def get_new_message(self) -> None:
        # 监听新消息
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
        if random.randint(0, 50) == 20:
            # anti_detection_start("000000")
            pass

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
            time.sleep(random.random())  # anti detection
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

    def move_to_msglist(self):
        """移动到消息列表"""
        rect = self.B_MsgList.BoundingRectangle
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        center_x = int(rect.left) + width / 2
        center_y = int(rect.top) + height / 2
        pyautogui.moveTo(int(center_x), int(center_y))
