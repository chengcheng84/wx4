from fastapi import FastAPI
from wx.wx4.wx4 import WeChat


app = FastAPI()
wx = WeChat()


@app.route("/send_enter")
def send_enter():
    return wx.send_enter()


@app.route("/ChatWith")
def ChatWith(contact_name: str) -> tuple[str, int] | tuple[None, None]:
    """切换聊天列表
    Args:
        contact_name:联系人的名字
    """
    return wx.ChatWith(contact_name=contact_name)


@app.route("/InitGetAllMessage")
def InitGetAllMessage() -> None:
    """
    # To Fix
    获取所有消息的时候,RuntimeID可能重复，导致错误
    ## 方法
    1. 获取所有消息的RuntimeID（OK）
    2. 在每4个控件就生成MSG对象防止RuntimeID重复
    3. 获取每个控件的发送者（Bug, can't run）
    """
    return wx.InitGetAllMessage()


@app.route("/GetAllMessage")
def GetAllMessage() -> dict:
    return {"data": wx.GetAllMessage()}


@app.route("/LoadMoreMessage")
def LoadMoreMessage() -> None:
    return wx.LoadMoreMessage()


@app.route("/get_new_message")
def get_new_message() -> None:
    # 监听新消息
    return wx.get_new_message()


@app.route("/SendMsg")
def SendMsg(
    msg: str,
    clear: bool = True,
    send: bool = True,
) -> None:
    """发送文本消息

    Args:
        msg (str): 要发送的文本消息
        clear (bool, optional): 是否清除原本的内容，
        send (bool, optional): 是否发送，默认为True
    """
    return wx.SendMsg(msg, clear, send)


@app.route("/GetWeiXinID")
def GetWeiXinID(index=-1):
    return wx.GetWeiXinID(index=index)


@app.route("/move_to_msglist")
def move_to_msglist():
    """移动到消息列表"""
    return wx.move_to_msglist()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8010, reload=True)
