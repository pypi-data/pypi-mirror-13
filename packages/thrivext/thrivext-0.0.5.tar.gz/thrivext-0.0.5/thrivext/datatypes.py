import arrow


class TimestampMeta(type):
    """
    Metaclass for Timestamp class. Defines a Timestamp class and way to perform
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
        Checks if 'timestamp_str' is of allowed formats. Currently configured to
        perform strict checking. That is only ISO8601-like formats are allowed.

        :type timestamp_str: str
        :param timestamp_str: String to be checked for timestamp-ness

        :rtype: bool
        :return: True if timestamp_str respresents Timestamp in one of the
                 allowed formats.
        """
        try:
            if arrow.get(timestamp_str, TimestampMeta.TS_FORMAT_STRICT):
                return True
        except Exception as ex:
            return False


class Timestamp(str):
    """
    Instance of TimestampMeta metaclass. *This* is the actual type that will be
    passed to the instancecheck method.
    """
    __metaclass__ = TimestampMeta


class IntegerMeta(type):
    """
    Meta class for Integer, defines instance check for Integer.
    """

    def __instancecheck__(self, s):
        """
        Checks if 's' is an integer string.

        :type s: str
        :param s: String to be checked for Integer-ness

        :rtype: bool
        :return: True if 's' is an integer
        """
        try:
            return isinstance(s, str) and isinstance(int(s), int)
        except ValueError:
            return False


class Integer(str):
    """
    Instance of the IntegerMeta class. This is the actual class that will
    passed to the instancecheck method.
    """
    __metaclass__ = IntegerMeta


class FloatMeta(type):
    """
    Metaclass for float, defines instance check for float
    """

    def __instancecheck__(self, s):
        """
        Checks if 's' is a Float

        :type s: str
        :param s: String to be checked for float-ness

        :rtype: bool
        :return: True if string s is a float
        """

        try:
            return isinstance(s, str) and isinstance(float(s), float)
        except ValueError:
            return False


class Float(str):
    """
    Instance of the FloatMeta class. This is the actual class that will
    passed to the instancecheck method.
    """
    __metaclass__ = FloatMeta


class BooleanMeta(type):
    """
    Metaclass for Boolean types, defines instance check for Boolean values
    """

    TRUTHVALUES = ["TRUE", "true", "t", "1", "y", "yes",
                   "FALSE", "false", "f", "0", "n", "no"]

    def __instancecheck__(self, s):
        """
        Checks if 's' is a boolean. Boolean is defined as belonging to
        specific set of strings

        :type s: str
        :param s: String to be checked for bool-ness

        :rtype: bool
        :return: True if string s is a valid boolean
        """
        try:
            return s in BooleanMeta.TRUTHVALUES
        except ValueError:
            return False


class Boolean(str):
    """
    Boolean class that will be passed to the instancecheck method.
    """

    __metaclass__ = BooleanMeta


if __name__ == "__main__":
    """
    Sample usage
    """
    assert not isinstance("2015-11-20 17:a3:13", Timestamp)
    assert isinstance("2015-11-20 17:03:13", Timestamp)

    assert not isinstance("abc", Integer), "abc is not an integer"
    assert isinstance("0", Integer), "0 is an integer"
    assert isinstance("25", Integer), "25 is an integer"
    assert not isinstance("25.0", Integer), "25.0 is not an integer"

    assert not isinstance("abc", Float), "abc is not a float"
    assert isinstance("25", Float), "25 is a float"
    assert isinstance("25.2", Float), "25.2 is a float"

    assert not isinstance("abc", Boolean), "abs is not a Boolean"
    assert isinstance("TRUE", Boolean), "TRUE is a Vertica boolean"
    assert isinstance("true", Boolean), "true is a Vertica boolean"
    assert isinstance("t", Boolean), "t is a Vertica boolean"
    assert isinstance("1", Boolean), "1 is a Vertica boolean"
    assert isinstance("y", Boolean), "y is a Vertica boolean"
    assert isinstance("yes", Boolean), "yes is a Vertica boolean"
    assert isinstance("FALSE", Boolean), "TRUE is a Vertica boolean"
    assert isinstance("false", Boolean), "true is a Vertica boolean"
    assert isinstance("f", Boolean), "t is a Vertica boolean"
    assert isinstance("0", Boolean), "1 is a Vertica boolean"
    assert isinstance("n", Boolean), "y is a Vertica boolean"
    assert isinstance("no", Boolean), "yes is a Vertica boolean"
