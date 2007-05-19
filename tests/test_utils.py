# -*- coding: utf-8 -*-
"""
    werkzeug.utils test
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2007 by Georg Brandl.
    :license: BSD license.
"""

from py.test import raises

from werkzeug.utils import MultiDict, CombinedMultiDict, lazy_property

def test_multidict():
    md = MultiDict()
    assert isinstance(md, dict)

    mapping = [('a', 1), ('b', 2), ('a', 2), ('d', 3),
               ('a', 1), ('a', 3), ('d', 4), ('c', 3)]
    md = MultiDict(mapping)

    # simple getitem gives the first value
    assert md['a'] == 1
    assert md['c'] == 3
    raises(KeyError, "md['e']")
    assert md.get('a') == 1

    # list getitem
    assert md.getlist('a') == [1, 2, 1, 3]
    assert md.getlist('d') == [3, 4]
    # do not raise if key not found
    assert md.getlist('x') == []

    # simple setitem overwrites all values
    md['a'] = 42
    assert md.getlist('a') == [42]

    # list setitem
    md.setlist('a', [1, 2, 3])
    assert md['a'] == 1
    assert md.getlist('a') == [1, 2, 3]

    # verify that it does not change original lists
    l1 = [1, 2, 3]
    md.setlist('a', l1)
    del l1[:]
    assert md['a'] == 1

    # setdefault, setlistdefault
    assert md.setdefault('u', 23) == 23
    assert md.getlist('u') == [23]
    del md['u']

    assert md.setlistdefault('u', [-1, -2]) == [-1, -2]
    assert md.getlist('u') == [-1, -2]
    assert md['u'] == -1

    # delitem
    del md['u']
    raises(KeyError, "md['u']")
    del md['d']
    assert md.getlist('d') == []

    # keys, values, items, lists
    assert list(sorted(md.keys())) == ['a', 'b', 'c']
    assert list(sorted(md.iterkeys())) == ['a', 'b', 'c']

    assert list(sorted(md.values())) == [1, 2, 3]
    assert list(sorted(md.itervalues())) == [1, 2, 3]

    assert list(sorted(md.items())) == [('a', 1), ('b', 2), ('c', 3)]
    assert list(sorted(md.iteritems())) == [('a', 1), ('b', 2), ('c', 3)]

    assert list(sorted(md.lists())) == [('a', [1, 2, 3]), ('b', [2]), ('c', [3])]
    assert list(sorted(md.iterlists())) == [('a', [1, 2, 3]), ('b', [2]), ('c', [3])]

    # copy method
    copy = md.copy()
    assert copy['a'] == 1
    assert copy.getlist('a') == [1, 2, 3]

    # update with a multidict
    od = MultiDict([('a', 4), ('a', 5), ('y', 0)])
    md.update(od)
    assert md.getlist('a') == [1, 2, 3, 4, 5]
    assert md.getlist('y') == [0]

    # update with a regular dict
    md = copy
    od = {'a': 4, 'y': 0}
    md.update(od)
    assert md.getlist('a') == [1, 2, 3, 4]
    assert md.getlist('y') == [0]

    # pop, poplist, popitem, popitemlist
    assert md.pop('y') == 0
    assert 'y' not in md
    assert md.poplist('a') == [1, 2, 3, 4]
    assert 'a' not in md

    # remaining: b=2, c=3
    popped = md.popitem()
    assert popped in [('b', 2), ('c', 3)]
    popped = md.popitemlist()
    assert popped in [('b', [2]), ('c', [3])]


def test_combined_multidict():
    d1 = MultiDict([('foo', 1)])
    d2 = MultiDict([('bar', 2)])
    d = CombinedMultiDict([d1, d2])

    # lookup
    assert d['foo'] == 1
    assert d['bar'] == 2

    # get key errors for missing stuff
    try:
        d['missing']
    except KeyError:
        pass
    else:
        raise AssertionError('expected KeyError')

    # make sure that they are immutable
    try:
        d['foo'] = "blub"
    except TypeError:
        pass
    else:
        raise AssertionError('expected TypeError')


def test_lazy_property():
    foo = []
    class A(object):
        def prop(self):
            foo.append(42)
            return 42
        prop = lazy_property(prop)

    a = A()
    p = a.prop
    q = a.prop
    assert p == q == 42
    assert foo == [42]

    foo = []
    class A(object):
        def prop(self):
            foo.append(42)
            return 42
        prop = lazy_property(prop, name='propval')

    a = A()
    p = a.prop
    q = a.prop
    r = a.propval
    assert p == q == r == 42
    assert foo == [42, 42]