class WorkerMessage:
    def __init__(self, message, body):
        self.headers = message.headers
        self.properties = message.properties
        self.body = body
        self.content_encoding = message.content_encoding
        self.content_type = message.content_type
        self.delivery_info = message.delivery_info
        self.delivery_tag = message.delivery_tag
        self.payload = message.payload
