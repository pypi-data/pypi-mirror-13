import logging


class ConfigError(Exception):
    def __init__(self, message, errors=None):
        super(ConfigError, self).__init__(message)

        self.errors = errors
        logging.error(message)


class ConfigNotFoundError(Exception):
    def __init__(self, message, errors=None):
        super(ConfigNotFoundError, self).__init__(message)

        self.errors = errors
        logging.error(message)


class BrowseException(Exception):
    def __init__(self, message):
        super(BrowseException, self).__init__(message)

        self.message = message
        logging.error(message)


class SearchException(Exception):
    def __init__(self, message, errors=None):
        super(SearchException, self).__init__(message)
        logging.error(message)


class SearchEmptyException(Exception):
    def __init__(self, message):
        super(SearchEmptyException, self).__init__(message)
        logging.error(message)


class AmqpParseException(Exception):
    def __init__(self, message, errors=None):
        super(AmqpParseException, self).__init__(message)


class JsonParseException(Exception):
    def __init__(self, message, errors=None):
        super(JsonParseException, self).__init__(message)


class CrawlException(Exception):
    def __init__(self, message, errors=None):
        super(CrawlException, self).__init__(message)


class ThemeException(Exception):
    def __init__(self, message, errors=None):
        super(ThemeException, self).__init__(message)


class CrawlBotException(Exception):
    def __init__(self, message):
        super(CrawlBotException, self).__init__()
        logging.error(message)

        self.message = message