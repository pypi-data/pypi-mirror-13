class WorkerMessage:
    def __init__(self, basic_deliver, properties, body):
        self.basic_deliver = basic_deliver
        self.properties = properties
        self.body = body
