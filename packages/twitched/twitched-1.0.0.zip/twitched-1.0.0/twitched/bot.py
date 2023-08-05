from twitched.chat import ChatClient


class TwitchBot(ChatClient):
    """
    A simple TwitchBot class that allows defining of bot commands. This should
    serve as a good base class for any additional custom bot objects.
    """

    def __init__(self, *args, **kwargs):
        """ Constructor. """
        super().__init__(*args, **kwargs)
        self.commands = {}

        def handler(user, message):
            """ Handler for parsing incoming chat messages and looking for any
            defined commands.

            :param user:    the user who sent the message
            :param message: the message sent
            :return:        None
            """
            dommand, payload = None, None

            try:
                command, payload = message.split(" ", 1)
            except ValueError:
                # handles a case where only a command is sent
                command = message
            self.invoke_command(command, user, payload)

        # register the command handler for all messages
        self.handlers['message'].append(handler)

    def command(self, *names):
        """ Decorator for registering command handlers.

        :param names:   a list of command names
        :return:        func
        """
        def decorator(func):
            for name in names:
                self.commands[name] = func
        return decorator

    def invoke_command(self, name, *args, **kwargs):
        """ Invokes a command's handler function.

        :param name:    the name of the command
        :param args:    a list of arguments to pass to the handler
        :param kwargs:  a dict of keyword arguments to pass to the handler
        :return:        None
        """
        if name in self.commands:
            self.commands[name](*args, **kwargs)
