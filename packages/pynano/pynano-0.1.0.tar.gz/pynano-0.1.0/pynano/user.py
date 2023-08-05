from .base import NanoBase


class User(NanoBase):
    """
    A NanoBase object for representing NaNoWriMo participants.
    """
    # Endpoint URLs for user objects
    _primary_url = 'http://nanowrimo.org/wordcount_api/wc/{name}'
    _history_url = 'http://nanowrimo.org/wordcount_api/wchistory/{name}'

    @property
    def id(self):
        """The User's id.

        This property corresponds to `uid` in the API.

        :rtype: string
        """
        return self._fetch_element('uid')

    @property
    def name(self):
        """The User's username.

        This property corresponds to `uname` in the API.

        :rtype: string
        """
        return self._fetch_element('uname')

    @property
    def wordcount(self):
        """The User's current word count.

        This property corresponds to `user_wordcount` in the API.

        :rtype: int
        """
        return int(self._fetch_element('user_wordcount'))

    @property
    def winner(self):
        """The User's "winner" status.

        This property corresponds to `winner` in the API.

        :rtype: bool
        """
        return self._fetch_element('winner') == 'true'

