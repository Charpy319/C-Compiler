class ErrorManager:
    def __init__(self):
        self.errors = []
        self.error_count = 0

    def report(self, error_msg: str, line: int, type: str):
        self.error_count += 1
        error = (error_msg, line, type)
        self.errors.append(error)
    
    def display(self, step: str):
        msg = f"There are {self.error_count} errors"
        if self.error_count == 0:
            return msg + f"in {step}\n"
        
        msg += f".\nCompilation stopped at {step}\nErrors are...\n"

        for error in self.errors:
            msg += f"{error[2]}: {error[0]} on line {error[1]}\n"

        raise ErrorManager.Stop(msg)
        
    class Stop(Exception):
        def __init__(self, message: str):
            super().__init__(message)

error = ErrorManager()