import pytest

@pytest.fixture(params=[
    "{b.c.d: 2}",
    "{@@@@@@}",
    ])
def invalid_syntax(request):
    return request.param
