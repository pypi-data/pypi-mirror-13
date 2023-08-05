from pyrefactor.dict_styles import toggle_dict_style


def test_dict_to_curly():
    assert toggle_dict_style("{'a': 2}") == "dict(a=2)"

def test_curly_to_dict():
    assert toggle_dict_style("dict(a=2)") == "{'a': 2}"

def test_complex_dict():
    for dict_form, curly_form in [
            ("{'f': some_function(2), 'g': a.b.c.d}", "dict(f=some_function(2), g=a.b.c.d)"),
            ]:
        assert toggle_dict_style(dict_form) == curly_form
        assert toggle_dict_style(curly_form) == dict_form

def test_errors(invalid_syntax):
    assert toggle_dict_style(invalid_syntax) == invalid_syntax
