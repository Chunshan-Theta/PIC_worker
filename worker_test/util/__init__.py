class Job:
    def __init__(self, request_id, content):
        self.request_id = request_id
        self.content = content
        self.worker_label = "test worker"

    def to_json(self):
        return {
            "content": self.content,
            "from": self.worker_label
        }
