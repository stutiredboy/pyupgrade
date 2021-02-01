import pytest

from pyupgrade._data import Settings
from pyupgrade._main import _fix_plugins


@pytest.mark.parametrize(
    ('s', 'version'),
    (
        pytest.param(
            'from typing import Union\n'
            'x: Union[int, str]\n',
            (3, 9),
            id='<3.10 Union',
        ),
        pytest.param(
            'from typing import Optional\n'
            'x: Optional[str]\n',
            (3, 9),
            id='<3.10 Optional',
        ),
        pytest.param(
            'from __future__ import annotations\n'
            'from typing import Union\n'
            'SomeAlias = Union[int, str]\n',
            (3, 9),
            id='<3.9 not in a type annotation context',
        ),
        # https://github.com/python/mypy/issues/9945
        pytest.param(
            'from __future__ import annotations\n'
            'from typing import Union\n'
            'SomeAlias = Union[int, str]\n',
            (3, 10),
            id='3.10+ not in a type annotation context',
        ),
        # https://github.com/python/mypy/issues/9998
        pytest.param(
            'from typing import Union\n'
            'def f() -> Union[()]: ...\n',
            (3, 10),
            id='3.10+ empty Union',
        ),
    ),
)
def test_fix_pep604_types_noop(s, version):
    assert _fix_plugins(s, settings=Settings(min_version=version)) == s


@pytest.mark.parametrize(
    ('s', 'expected'),
    (
        pytest.param(
            'from typing import Union\n'
            'x: Union[int, str]\n',

            'from typing import Union\n'
            'x: int | str\n',

            id='Union rewrite',
        ),
        pytest.param(
            'x: typing.Union[int]\n',

            'x: int\n',

            id='Union of only one value',
        ),
        pytest.param(
            'x: typing.Union[Foo[str, int], str]\n',

            'x: Foo[str, int] | str\n',

            id='Union containing a value with brackets',
        ),
        pytest.param(
            'x: typing.Union[typing.List[str], str]\n',

            'x: list[str] | str\n',

            id='Union containing pep585 rewritten type',
        ),
        pytest.param(
            'x: typing.Union[int, str,]\n',

            'x: int | str\n',

            id='Union trailing comma',
        ),
        pytest.param(
            'x: typing.Union[(int, str)]\n',

            'x: int | str\n',

            id='Union, parenthesized tuple',
        ),
        pytest.param(
            'x: typing.Union[\n'
            '    int,\n'
            '    str\n'
            ']\n',

            'x: (\n'
            '    int |\n'
            '    str\n'
            ')\n',

            id='Union multiple lines',
        ),
        pytest.param(
            'x: typing.Union[\n'
            '    int,\n'
            '    str,\n'
            ']\n',

            'x: (\n'
            '    int |\n'
            '    str\n'
            ')\n',

            id='Union multiple lines with trailing commas',
        ),
        pytest.param(
            'from typing import Optional\n'
            'x: Optional[str]\n',

            'from typing import Optional\n'
            'x: str | None\n',

            id='Optional rewrite',
        ),
        pytest.param(
            'x: typing.Optional[\n'
            '    ComplicatedLongType[int]\n'
            ']\n',

            'x: None | (\n'
            '    ComplicatedLongType[int]\n'
            ')\n',

            id='Optional rewrite multi-line',
        ),
    ),
)
def test_fix_pep604_types(s, expected):
    assert _fix_plugins(s, settings=Settings(min_version=(3, 10))) == expected


@pytest.mark.parametrize(
    ('s', 'expected'),
    (
        pytest.param(
            'from __future__ import annotations\n'
            'from typing import Union\n'
            'x: Union[int, str]\n',

            'from __future__ import annotations\n'
            'from typing import Union\n'
            'x: int | str\n',

            id='variable annotations',
        ),
        pytest.param(
            'from __future__ import annotations\n'
            'from typing import Union\n'
            'def f(x: Union[int, str]) -> None: ...\n',

            'from __future__ import annotations\n'
            'from typing import Union\n'
            'def f(x: int | str) -> None: ...\n',

            id='argument annotations',
        ),
        pytest.param(
            'from __future__ import annotations\n'
            'from typing import Union\n'
            'def f() -> Union[int, str]: ...\n',

            'from __future__ import annotations\n'
            'from typing import Union\n'
            'def f() -> int | str: ...\n',

            id='return annotations',
        ),
    ),
)
def test_fix_generic_types_future_annotations(s, expected):
    assert _fix_plugins(s, settings=Settings(min_version=(3,))) == expected


# TODO: test multi-line as well