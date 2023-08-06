from __future__ import unicode_literals
import io
import os
import tempfile
import json

import pytest

from .. import util


@pytest.fixture
def tmp_path():
    return tempfile.mkdtemp()


@pytest.fixture
def tmp_path2():
    return tmp_path()


@pytest.fixture(scope='module')
def sample_package_path(version='1.0.0', compat_version='==1.0.0'):
    path = tempfile.mkdtemp()

    with io.open(os.path.join(path, 'package.json'), 'wb') as f:
        f.write(util.json_dump({
            "name": "test",
            "description": "test package",
            "include": [("data", "*")],
            "version": version,
            "license": "public domain",
            "compatibility": {"test": compat_version}
        }))
    data_path = os.path.join(path, 'data')
    os.mkdir(data_path)
    with io.open(os.path.join(data_path, 'xyz.model'), 'w') as f:
        for i in range(1):
            f.write(('%s' % i) * 1024)
    with open(os.path.join(data_path, 'xyz.json'), 'w') as f:
        json.dump({'test': True}, f)
    return path


@pytest.fixture(scope='module')
def sample_package_path2():
    return sample_package_path('2.0.0', '==2.0.0')


@pytest.fixture(scope='module')
def multi_version_package_path():
    return sample_package_path('1.0.0', '>=0.100.0,<0.101.0')


def pytest_addoption(parser):
    parser.addoption("--remote", action="store_true",
        help="include tests that require internet connectivity")


def pytest_runtest_setup(item):
    for opt in ['remote']:
        if opt in item.keywords and not item.config.getoption("--%s" % opt):
            pytest.skip("need --%s option to run" % opt)
