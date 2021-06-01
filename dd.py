import requests
from See import data_private


class Wall_Use():
    def __init__(self, token: str, versionApiVk: str, ID: str):
        self.token = token
        self.v = versionApiVk

        self.namId = self.getIdUser(ID)
        self.getWallUser()

    def getIdUser(self, ID):
        response = requests.get('https://api.vk.com/method/users.get', params={
            "access_token": self.token,
            'v': self.v,
            "user_ids": ID,
        })
        tmp = str(response.json()["response"][0]["id"])
        return tmp

    def getWallUser(self) -> int:
        """
        https://vk.com/dev/wall.get
        https://vk.com/dev/objects/user


        offset = смещение, необходимое для выборки определенного подмножества записей.
        положительное число

        count = количество записей, которое необходимо получить. Максимальное значение: 100.
        положительное число

        filter = определяет, какие типы записей на стене необходимо получить. Возможные значения:
            suggests — предложенные записи на стене сообщества (доступно только при вызове с передачей access_token);
            postponed — отложенные записи (доступно только при вызове с передачей access_token);
            owner — записи владельца стены;
            others — записи не от владельца стены;
            all — все записи на стене (owner + others).

            По умолчанию: all.

        """

        response = requests.get('https://api.vk.com/method/wall.get', params={
            "access_token": self.token,
            'v': self.v,
            "owner_id": self.namId,
            'count': 10,
            'offset': 0,
            "filter": "owner",
            "extended": 1,
        })
        tmp = response.json()

        return 1


if __name__ == "__main__":
    ID = "171923853"

    dt = data_private()
    WU = Wall_Use(dt["token"],
                  versionApiVk="5.131",
                  ID=ID)
