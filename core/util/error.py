class ErrorManager:
    def __init__(self):
        self.errors = []
        self.error_count = 0

    def report(self, error_msg: str, line: int, type: str):
        self.error_count += 1
        error = (error_msg, line, type)
        self.errors.append(error)

error = ErrorManager()