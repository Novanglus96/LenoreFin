from ninja import Schema


class PushSubscribeIn(Schema):
    endpoint: str
    p256dh: str
    auth: str


class VapidPublicKeyOut(Schema):
    public_key: str
