import requests


class WeChatRemote:
    def __init__(self, host="http://127.0.0.1:8010"):
        self.host = host.rstrip("/")

    def send_enter(self):
        requests.get(f"{self.host}/send_enter")

    def chat_with(self, contact_name: str):
        params = {"contact_name": contact_name}
        return requests.get(f"{self.host}/ChatWith", params=params)

    def init_get_all_message(self):
        requests.get(f"{self.host}/InitGetAllMessage").json()

    def get_all_message(self):
        resp = requests.get(f"{self.host}/GetAllMessage")
        if resp.status_code == 200:
            data = resp.json()
            # 只返回有数据的情况
            if isinstance(data, dict) and data.get("data"):
                return data["data"]
        return None

    def load_more_message(self):
        requests.get(f"{self.host}/LoadMoreMessage").json()

    def get_new_message(self):
        requests.get(f"{self.host}/get_new_message").json()

    def SendMsg(self, msg: str, clear: bool = True, send: bool = True):
        params = {"msg": msg, "clear": clear, "send": send}
        requests.get(f"{self.host}/SendMsg", params=params)

    def get_weixin_id(self, index=-1):
        params = {"index": index}
        resp = requests.get(f"{self.host}/GetWeiXinID", params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data:  # 只返回有数据的情况
                return data
        return None

    def move_to_msglist(self):
        requests.get(f"{self.host}/move_to_msglist")


# 示例用法
if __name__ == "__main__":
    client = WeChatRemote()
    print(client.get_all_message())
