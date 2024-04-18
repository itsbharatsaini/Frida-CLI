""" COMMANDS MESSAGES """

class CommandMessage:
    def __init__(self, status_code: int, description: str):
        self.status_code = status_code
        self.description = description

    def __repr__(self):
        return str(self.status_code)

    def __str__(self):
        return str(self.status_code)

    def __eq__(self, other):
        return self.status_code == other.status_code
    


ERROR_PATH_DOES_NOT_EXIST = CommandMessage(0, "Error: Project does not exist")
ERROR_PATH_NOT_GIVEN = CommandMessage(0, "Error: No project given")
GET_RESULT_SUCCESS = CommandMessage(1, "Sucess: Project open")

