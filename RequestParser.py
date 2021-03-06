"""Selfbot's request parser"""
from CommandExec import CommandExec
from Flags import ResponseFlag, MessageEventFlag


class RequestParser:
    """Class validating the command, checking it for existence and running it"""

    def __init__(self, prefix):
        self.prefix = prefix
        self.executor = CommandExec()

        self.exit_cmds = ['kys', 'exit']

        self.event_flag = MessageEventFlag.NONE

    def parse_command(self, message: str, ommit_prefix: bool = False) -> (str, str):
        """
            Returns the command
            :rtype: str, str
            :param message: message to parse
            :param ommit_prefix: True if prefix should be ignored
            :return: tuple with command and arguments.
            Will return (command, None) if there is no arguments
            Will return (None, None) if command is invalid
        """
        if ommit_prefix or message.startswith(self.prefix):
            message = message[len(self.prefix):] if not ommit_prefix else message
            arg_split = message.split(' ', 1)
            if (len(arg_split)) == 1:
                return arg_split[0], ""
            return arg_split[0], arg_split[1]
        return None, None

    def execute(self, message: str, ommit_prefix: bool = False) -> (str, ResponseFlag):
        """Executes the command and returns result
        :rtype: str, ResponseFlag
        :param message: Message to execute
        :param ommit_prefix: True if prefix should be ommited
        :return: Tuple with return message and flag
        """
        command, args = self.parse_command(message, ommit_prefix)

        if command is None:
            return None, ResponseFlag.WRONG_REQUEST

        if command in self.exit_cmds:
            return None, ResponseFlag.KYS

        if not self.executor.command_exists(command):
            return None, ResponseFlag.NOT_FOUND

        return_data = self.executor.run(command, args)
        if isinstance(return_data, MessageEventFlag):
            self.event_flag = return_data
            return "OK", ResponseFlag.OKAY

        return str(return_data), ResponseFlag.OKAY
