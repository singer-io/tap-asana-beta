import asana
import singer

LOGGER = singer.get_logger()


""" Simple wrapper for Asana. """


class Asana():
    """Base class for tap-asana"""

    def __init__(
        self, client_id=None, client_secret=None, redirect_uri=None, refresh_token=None, access_token=None
    ):  # pylint: disable=too-many-arguments
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.access_token = access_token

        if all([self.refresh_token, self.client_id, self.client_secret, self.redirect_uri]):
            self._client = self._oauth_auth() or self._access_token_auth()
            self.refresh_access_token()
        elif self.access_token:
            self._client = self._access_token_auth()
        else:
            raise ValueError("Invalid configuration: Must provide either refresh_token with OAuth credentials or access_token.")

    def _oauth_auth(self):
        """Oauth authentication for tap"""
        if (
            self.client_id is None
            or self.client_secret is None
            or self.redirect_uri is None
            or self.refresh_token is None
        ):
            LOGGER.debug("OAuth authentication unavailable.")
            return None
        return asana.Client.oauth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
        )

    def _access_token_auth(self):
        """Check for access token"""
        if self.access_token is None:
            LOGGER.debug("OAuth authentication unavailable.")
            return None
        return asana.Client.access_token(self.access_token)

    def refresh_access_token(self):
        return self._client.session.refresh_token(
            self._client.session.token_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
        )

    @property
    def client(self):
        return self._client
