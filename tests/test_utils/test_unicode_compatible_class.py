

from sumy import _compat as compat

BYTES_STRING = "ľščťžáýíééäúňô €đ€Ł¤".encode()
UNICODE_STRING = "ľščťžáýíééäúňô €đ€Ł¤"
NATIVE_STRING = compat.to_string(UNICODE_STRING)


@compat.unicode_compatible
class Clazz:
    def __unicode__(self):
        return UNICODE_STRING


def _assert_strings_equal(str1, str2):
    assert type(str1) is type(str2)
    assert str1 == str2


def test_native_bytes():
    returned = bytes(Clazz())
    _assert_strings_equal(BYTES_STRING, returned)


def test_to_bytes():
    returned = compat.to_bytes(Clazz())
    _assert_strings_equal(BYTES_STRING, returned)


def test_to_string():
    returned = compat.to_string(Clazz())
    _assert_strings_equal(NATIVE_STRING, returned)


def test_to_unicode():
    returned = compat.to_unicode(Clazz())
    _assert_strings_equal(UNICODE_STRING, returned)
