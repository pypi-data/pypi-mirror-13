from pyrefactor.assertions import toggle_assert_style


def test_assert_equals():
    for assert_form, method_form in [
            ("assert x == y", "self.assertEquals(x, y)"),
            ("assert x == y, msg", "self.assertEquals(x, y, msg)"),
            ]:
        assert toggle_assert_style(assert_form) == method_form
        assert toggle_assert_style(method_form) == assert_form

def test_assert_true_false():
    for assert_form, method_form in [
    ("self.assertTrue(x)", "assert x"),
    ("self.assertFalse(x)", "assert (not x)"),
    ("self.assertFalse(x, 'msg')", "assert (not x), 'msg'"),
    ("self.assertTrue(x, 'msg')", "assert x, 'msg'"),
    ("self.assertTrue(x, 'msg')", "assert x, 'msg'"),
    ("self.assertIsNone(x, 'msg')", "assert x is None, 'msg'"),
    ("self.assertIsNotNone(x, 'msg')", "assert x is not None, 'msg'"),
    ]:
        assert toggle_assert_style(method_form) == assert_form
        assert toggle_assert_style(assert_form) == method_form

def test_assert_underscore():
    assert toggle_assert_style('self.assert_(x)') == 'assert x'


def test_errors(invalid_syntax):
    assert toggle_assert_style(invalid_syntax) == invalid_syntax
