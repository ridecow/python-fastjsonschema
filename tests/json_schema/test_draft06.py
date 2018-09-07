import pytest

from .utils import template_test, resolve_param_values_and_ids


def pytest_generate_tests(metafunc):
    param_values, param_ids = resolve_param_values_and_ids(
        version=6,
        suite_dir='JSON-Schema-Test-Suite/tests/draft6',
        ignored_suite_files=[
            # Optional.
            'ecmascript-regex.json',
        ],
    )
    metafunc.parametrize(['version', 'schema', 'data', 'is_valid'], param_values, ids=param_ids)


# Real test function to be used with parametrization by previous hook function.
test = template_test
