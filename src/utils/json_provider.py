from datetime import date, datetime
from flask.json.provider import DefaultJSONProvider


class CustomJsonProvider(DefaultJSONProvider):
    """
    Make Flask to not sort the keys when returning JSON,
    and provide a custom datetime format.
    """

    sort_keys = False

    def default(self, o):
        """Provides interface for datetime/date."""
        if isinstance(o, (datetime, date)):
            return o.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return DefaultJSONProvider.default(o)
