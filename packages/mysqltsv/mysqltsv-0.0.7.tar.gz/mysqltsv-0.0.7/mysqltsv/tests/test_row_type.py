import pickle

from nose.tools import eq_

from ..row_type import RowGenerator


def test_row_type():
    MyRow = RowGenerator(["foo", "bar", "baz"])
    r = MyRow("15\t16\tNULL")
    eq_(r.foo, "15")
    eq_(r['foo'], "15")
    eq_(r[0], "15")
    eq_(r.bar, "16")
    eq_(r['bar'], "16")
    eq_(r[1], "16")
    eq_(r.baz, None)
    eq_(r['baz'], None)
    eq_(r[2], None)

    MyRow = RowGenerator(["foo", "bar", "baz"], types=[int, int, int])
    r = MyRow("15\t16\tNULL")
    eq_(r.foo, 15)
    eq_(r['foo'], 15)
    eq_(r[0], 15)
    eq_(r.bar, 16)
    eq_(r['bar'], 16)
    eq_(r[1], 16)
    eq_(r.baz, None)
    eq_(r['baz'], None)
    eq_(r[2], None)

    eq_(pickle.loads(pickle.dumps(r)).baz, None)
    eq_(pickle.loads(pickle.dumps(r))['baz'], None)
    eq_(pickle.loads(pickle.dumps(r))[2], None)
