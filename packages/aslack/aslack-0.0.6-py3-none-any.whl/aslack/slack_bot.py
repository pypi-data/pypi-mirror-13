"""A Slack bot using the real-time messaging API."""

from itertools import count
import json
import logging
from random import randint
from textwrap import dedent

from aiohttp import MsgType, ws_connect

from .slack_api import SlackApiError, SlackBotApi

logger = logging.getLogger(__name__)


class SlackBot:
    """Base class Slack bot.

        Arguments:
          id_ (:py:class:`str`): The bot's Slack ID.
          user (:py:class:`str`): The bot's friendly name.
          api (SlackApi): The Slack API wrapper.

        Attributes:
          address_as (:py:class:`str`): The text that appears at the
            start of messages address to this bot (e.g.
            ``'<@user>: '``).
          full_name (:py:class:`str`): The name of the bot as it
            appears in messages about the bot (e.g. ``'<@user>'``).

        """

    API_AUTH_ENDPOINT = 'auth.test'
    """Test endpoint for API authorisation."""

    INSTRUCTIONS = dedent("""
    These are the default instructions for an aSlack bot.

    Override these as appropriate for your specific needs.
    """)

    MESSAGE_FILTERS = {}
    """Default filters for incoming messages."""

    RTM_HANDSHAKE = {'type': 'hello'}
    """Expected handshake message from RTM API."""

    RTM_START_ENDPOINT = 'rtm.start'
    """Start endpoint for real-time messaging."""

    def __init__(self, id_, user, api):
        self.id_ = id_
        self.user = user
        self.api = api
        self.full_name = '<@{}>'.format(id_)
        self.address_as = '{}: '.format(self.full_name)
        self._msg_ids = count(randint(1, 1000))

    async def get_socket_url(self):
        """Get the WebSocket URL for the RTM session.

        Warning:
          The URL expires if the session is not joined within 30
          seconds of the API call to the start endpoint.

        Returns:
          :py:class:`str`: The socket URL.

        """
        data = await self.api.execute_method(self.RTM_START_ENDPOINT)
        return data['url']

    def handle_message(self, message, filters):
        """Handle an incoming message appropriately.

        Arguments:
          message (:py:class:`aiohttp.websocket.Message`): The incoming
            message to handle.
          filters (:py:class:`dict`): The filters to apply to incoming
            messages.

        Returns:
          :py:class:`str`: The response to send as a result.

        """
        data = self._unpack_message(message)
        logger.debug(data)
        if data.get('type') == 'error':
            raise SlackApiError(
                data.get('error', {}).get('msg', str(data))
            )
        elif (self.message_is_to_me(data) and
              data['text'][len(self.address_as):].strip() == '?'):
            return self._format_message(
                channel=data['channel'],
                text=self._instruction_list(filters),
            )
        for filter_, dispatch in filters.items():
            if filter_(data):
                logger.debug('Response triggered')
                return self._format_message(**dispatch(data))

    async def join_rtm(self, filters=None):
        """Join the real-time messaging service.

        Arguments:
          filters (:py:class:`dict`, optional): Dictionary mapping
            message filters to the functions they should dispatch to.
            Use a :py:class:`collections.OrderedDict` if precedence is
            important; only one filter, the first match, will be
            applied to each message.

        """
        if filters is None:
            filters = self.MESSAGE_FILTERS
        url = await self.get_socket_url()
        logger.debug('Connecting to {!r}'.format(url))
        async with ws_connect(url) as socket:
            first_msg = await socket.receive()
            self._validate_first_message(first_msg)
            async for message in socket:
                if message.tp == MsgType.text:
                    result = self.handle_message(message, filters)
                    if result is not None:
                        socket.send_str(result)
                elif message.tp in (MsgType.closed, MsgType.error):
                    if not socket.closed:
                        await socket.close()
                    break
        logger.info('Left real-time messaging.')

    def message_mentions_me(self, data):
        """If you send a message that mentions the bot's name"""
        return (data.get('type') == 'message' and
                self.full_name in data.get('text', ''))

    def message_is_to_me(self, data):
        """If you send a message starting '@username: ' to the bot"""
        return (data.get('type') == 'message' and
                data.get('text', '').startswith(self.address_as))

    @classmethod
    async def from_api_token(cls, token):
        """Create a new instance from the API token.

        Arguments:
          token (:py:class:`str`): The bot's API token.

        Returns:
          SlackBot: The new instance.

        """
        api = SlackBotApi(token)
        data = await api.execute_method(cls.API_AUTH_ENDPOINT)
        return cls(data['user_id'], data['user'], api)

    def _format_message(self, channel, text):
        """Format an outoging message for transmission.

        Note:
          Adds the message type (``'message'``) and incremental ID.

        Arguments:
          channel (:py:class:`str`): The channel to send to.
          text (:py:class:`str`): The message text to send.

        Returns:
          str: The JSON string of the message.

        """
        payload = {'type': 'message', 'id': next(self._msg_ids)}
        payload.update(channel=channel, text=text)
        return json.dumps(payload)

    @classmethod
    def _instruction_list(cls, filters):
        """Generates the instructions for a bot and its filters.

        Note:
          The guidance for each filter is generated by combining the
          docstrings of the predicate filter and resulting dispatch
          function with a single space between. The class's
          :py:attr:`INSTRUCTIONS` and the default help command are
          added.

        Arguments:
          filters (:py:class:`dict`): The filters to apply to incoming
            messages.

        Returns:
          :py:class:`str`: The bot's instructions.

        """
        return '\n\n'.join([
            cls.INSTRUCTIONS.strip(),
            '*Supported methods:*',
            'If you send "@username: ?" to the bot it replies with these '
            'instructions.',
        ] + [
            ' '.join((filter_.__doc__, dispatch.__doc__))
            for filter_, dispatch in filters.items()
        ])

    @classmethod
    def _validate_first_message(cls, msg):
        """Check the first message matches the expected handshake.

        Arguments:
          msg (:py:class:`aiohttp.Message`): The message to validate.

        Raises:
          SlackApiError: If the data doesn't match the handshake.

        """
        data = cls._unpack_message(msg)
        logger.debug(data)
        if data != cls.RTM_HANDSHAKE:
            raise SlackApiError('Unexpected response: {!r}'.format(data))
        logger.info('Joined real-time messaging.')

    @staticmethod
    def _unpack_message(msg):
        """Unpack the data from the message.

        Arguments:
          msg (:py:class:`aiohttp.Message`): The message to unpack.

        Returns:
          :py:class:`dict`: The loaded data.

        Raises:
          :py:class:`AttributeError`: If there is no data attribute.
          :py:class:`json.JSONDecodeError`: If the data isn't valid
            JSON.

        """
        return json.loads(msg.data)
