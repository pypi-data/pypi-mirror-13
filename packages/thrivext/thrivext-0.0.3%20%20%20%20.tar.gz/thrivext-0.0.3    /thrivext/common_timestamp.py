import arrow


class Timestamp(type):
    """
    Metaclass for CommonTimestamp class. Defines a Timestamp class and way to perform
    instance-checks for this class.
    """
    TS_FORMAT_EASY = ["MM/DD/YYYY", "MM/DD/YY", "MM-DD-YYYY", "MM-DD-YY",
                      "MM/D/YYYY", "MM/D/YY", "MM-D-YYYY", "MM-D-YY",
                      "YYYY/MM/DD", "YYYY/MM/D", "YYYY-MM-DD", "YYYY-MM-D",
                      "YYYY-MM-DD HH:mm:ss", "YYYY-MM-DD HH:mm:ss ZZ",
                      "YYYY-MM-DD HH:mm:ss Z"]

    TS_FORMAT_STRICT = ["YYYY-MM-DD HH:mm:ss",
                        "YYYY-MM-DD HH:mm:ss ZZ",
                        "YYYY-MM-DD HH:mm:ss Z"]

    def __instancecheck__(self, timestamp_str):
        """
        Checks if 'timestamp_str' is of allowed formats. Currently configured to perform
        strict checking. That is only ISO8601-like formats are allowed.

        @type timestamp_str: str
        @param timestamp_str: String to be checked for timestamp-ness

        @rtype: None
        @return: None
        """
        try:
            if arrow.get(timestamp_str, Timestamp.TS_FORMAT_STRICT):
                return True
        except Exception as ex:
            return False


class CommonTimestamp(str):
    """
    Instance of Timestamp metaclass. *This* is the actual type that will be passed to the
    instancecheck method.
    """
    __metaclass__ = Timestamp

if __name__ == "__main__":
    """
    Sample usage
    """
    ts = "2015-11-20 17:a3:13"
    print isinstance(ts, CommonTimestamp)