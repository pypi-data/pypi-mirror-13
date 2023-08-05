import re
import socket

from collections import defaultdict


#-------------------------------------------------------------------
# Twitch Settings
#-------------------------------------------------------------------

TWITCH_SERVER_ADDR = "irc.twitch.tv"        # hostname of the Twitch IRC chat server
TWITCH_SERVER_PORT = 6667                   # port number of the Twitch IRC chat server

#-------------------------------------------------------------------
# IRC Regular Expression Patterns
#-------------------------------------------------------------------

JOIN_PATTERN = r"^:(.+)!\1@\1.tmi.twitch.tv JOIN #(.+)$"                # IRC JOIN message
PART_PATTERN = r"^:(.+)!\1@\1.tmi.twitch.tv PART #(.+)$"                # IRC PART message pattern
PRIV_PATTERN = r"^:(.+)!\1@\1.tmi.twitch.tv PRIVMSG #(.+) :(.+)$"       # IRC PRIVMSG pattern


class ChatClient(object):
    """
    A TwitchChat client that connects to a Twitch channel's chat and processes messages
    sent by users. It also exposes most of the Twitch chat commands as methods.
    """

    def __init__(self, username, password):
        """ Constructor.

        :param username:        the Twitch username
        :param password:        the Twitch OAuth password
        :return:                TwitchClient
        """
        self.username = username.lower()
        self.password = password
        self.handlers = defaultdict(list)
        self.channel = None
        self.sock = None
        self.users = []

    @property
    def user_count(self):
        """ Returns the number of users in chat. """
        return len(self.users)

    #---------------------------------------------------------------
    # Decorators
    #---------------------------------------------------------------

    def on_message(self, func):
        """ Decorator for registering a message handler function.

        :param func:            the function being decorated
        :return:                None
        """
        self.handlers['message'].append(func)

    def on_connected(self, func):
        """ Decorator for registering a handler function for connecting to the channel.

        :param func:            the function being decorated
        :return:                None
        """
        self.handlers['connected'].append(func)

    def on_disconnected(self, func):
        """ Decorator for registering a handler function for disconnecting from the channel.

        :param func:            the function being decorated
        :return:                None
        """
        self.handlers['disconnected'].append(func)

    def on_join(self, func):
        """ Decorator for registering a handler function for users joining a channel.

        :param func:            the function being decorated
        :return:                None
        """
        self.handlers['join'].append(func)

    def on_leave(self, func):
        """ Decorator for registering a handler function for users leaving a channel.

        :param func:            the function being decorated
        :return:                None
        """
        self.handlers['part'].append(func)

    def invoke_handler(self, name, *args):
        """ Executes all of the handler functions for a specific handler.

        :param name:            the name of the handler
        :param args:            a list of arguments to pass to the handler function
        :return:                None
        """
        for handler in self.handlers[name]:
            handler(*args)

    def connect(self, channel):
        """ Connects to a Twitch channel's chat.

        :param channel:         the name of the Twitch channel
        :return:                None
        """
        try:
            sock = self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((TWITCH_SERVER_ADDR, TWITCH_SERVER_PORT))
        except socket.error as e:
            print("Could not connect to the Twitch chat server.")
            return

        # for some weird reason Twitch requires channel names to be lowercase
        channel = self.channel = channel.lower()

        # send credentials to the Twitch servers
        self.write("PASS %s" % self.password)
        self.write("NICK %s" % self.username)
        self.write("JOIN #%s" % channel)
        self.write("CAP REQ :twitch.tv/membership")

        while True:
            try:
                buffer = sock.recv(1024).decode()
            except socket.error:
                break

            # since IRC messages are terminated by the a carriage return we will split the received
            # data and process each one
            for data in buffer.split("\r\n"):
                # if this is a PING message then we must respond with a PONG to prevent from being
                # timed out and disconnected
                if data == "PING :tmi.twitch.tv":
                    self.write("PONG tmi.twitch.tv")
                    continue

                # if this is a PRIVMSG then execute all registered 'message' handler functions
                privmsg_match = re.match(PRIV_PATTERN, data)

                if privmsg_match:
                    user, channel, message = privmsg_match.groups()
                    self.invoke_handler('message', user, message)
                    continue

                # if this is a JOIN message then execute all registered 'join' handler functions
                join_match = re.match(JOIN_PATTERN, data)

                if join_match:
                    user, channel = join_match.groups()

                    # if the client user has joined the channel then we will call the ``joined`` handler
                    if user == self.username:
                        self.invoke_handler('connected')
                    else:
                        self.invoke_handler('join', user)

                        if user not in self.users:
                            self.users.append(user)
                    continue

                # if this is a PART message then execute all registered 'part' handler functions
                part_match = re.match(PART_PATTERN, data)

                if part_match:
                    user, channel = part_match.groups()
                    self.invoke_handler('part', user)

                    if user in self.users:
                        self.users.remove(user)
                    continue
        self.invoke_handler('disconnected')

    def disconnect(self):
        """ Disconnects from the channel's chat. """
        self.send("/disconnect")
        self.sock.close()

    def clear_chat(self):
        """ Clears the current chat messages. """
        self.send("/clear")

    def set_color(self, color):
        """ Sets the color of the TwitchChat user's username.

        :param color:               the color name or value (for Turbo users)
        :return:
        """
        self.send("/color %s" % color)

    def ban_user(self, user):
        """ Bans a user from chat.

        :param user:                the name of the user
        :return:                    None
        """
        self.send("/ban %s" % user)

    def unban_user(self, user):
        """ Unbans a banned user from chat.

        :param user:                the name of the user
        :return:                    None
        """
        self.send("/unban %s" % user)

    def timeout_user(self, user, duration=600):
        """ Times out a chat user for a number of seconds.

        :param user:                the name of the user
        :param duration:            the number of seconds of the timeout
        :return:                    None
        """
        self.send("/timeout %s %i" % (user, duration))

    def slowmode_on(self, seconds):
        """ Enables slow mode in chat, limiting the number of messages sent in a
        period of time.

        :param seconds:             the minimum number of seconds between messages
        :return:                    None
        """
        self.send("/slow %i" % seconds)

    def slowmode_off(self):
        """ Disables slow mode in chat. """
        self.send("/slowoff")

    def subscribers_on(self):
        """ Enables subscriber only mode in chat. """
        self.send("/subscribers")

    def subscribers_off(self):
        """ Enables subscriber only mode in chat. """
        self.send("/subscribersoff")

    def write(self, data):
        """ Sends data to the server.

        :param data:                the data string
        :return:                    None
        """
        try:
            self.sock.send((data+"\r\n").encode())
        except socket.error:
            return

    def send(self, message):
        """ Sends a PRIVMSG to the channel's chat.

        :param message:             the message string
        :return:                    None
        """
        self.write("PRIVMSG #%s :%s" % (self.channel, message))
