
import functools
import juice.utils as utils


def test_encrypted_string():
    pw = "hello world"
    e = utils.encrypt_string(pw)
    v = utils.verify_encrypted_string(pw, e)
    assert v is True

def test_is_valid_email():
    assert utils.is_valid_email("youder.com") is False
    assert utils.is_valid_email("yo@uder.com") is True
    assert utils.is_valid_email("yo-uder@pp.com") is True
    assert utils.is_valid_email("yo.uder@pp.com") is True
    assert utils.is_valid_email("yo-uder@pp.co.com") is True

def test_to_struct():
    s = utils.to_struct(n="Hello", b="Bye")
    assert s.n == "Hello"


def test_get_decorators_list():

    def deco1(func):
        @functools.wraps(func)
        def decorated_view(*args, **kwargs):
            return func(*args, **kwargs)
        return decorated_view

    def deco2(func):
        @functools.wraps(func)
        def decorated_view(*args, **kwargs):
            return func(*args, **kwargs)
        return decorated_view

    class Hi(object):

        @deco1
        @deco2
        def hello(self):
            return True

    k_hi = Hi()
    decos = utils.get_decorators_list(k_hi.hello)
    assert isinstance(decos, list)
    assert "deco1" in decos
    assert "deco2" in decos