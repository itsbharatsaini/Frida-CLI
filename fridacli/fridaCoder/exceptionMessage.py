class ExceptionMessage:
    class Message:
        def __init__(self, status_code: int, description: str):
            self.status_code = status_code

        def __repr__(self):
            return str(self.status_code)

        def __str__(self):
            return str(self.status_code)

        def __eq__(self, other):
            return self.status_code == other.status_code

    EXEC_ERROR = Message(0, "")
    EXEC_SUCCESS = Message(1, "SUCCESS")
    GET_RESULT_SUCCESS = Message(2, "")
    GET_RESULT_ERROR = Message(3, "")
    RESULT_ERROR = Message(4, "")
