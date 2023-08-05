from nose.tools import eq_

from ..functions import decode, encode


def test_encode():
    
    eq_(encode("foobar"), "foobar")
    eq_(encode(5), "5")
    eq_(encode(b"foobar"), "foobar")
    eq_(encode("foo\tbar"), "foo\\tbar")
    
def test_decode():
    
    eq_(decode("foobar"), "foobar")
    eq_(decode("5"), "5")
    eq_(decode("5", int), 5)
    eq_(decode(b"foobar"), "foobar")
    eq_(decode("foo\\tbar\\n"), "foo\tbar\n")

def test_encode_decode():
    
    input = "\t\nfoobar\t,derp"
    expected_encoded = "\\t\\nfoobar\\t,derp"
    
    eq_(encode(input), expected_encoded)
    
    eq_(decode(encode(input)), input)
