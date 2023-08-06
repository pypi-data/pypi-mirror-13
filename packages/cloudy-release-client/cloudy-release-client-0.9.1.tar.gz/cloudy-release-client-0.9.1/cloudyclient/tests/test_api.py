import os.path as op
import subprocess

from nose.tools import assert_equal, assert_raises

from cloudyclient.api import find_deployment_variables, run, wait_process


DATA_DIR = op.join(op.dirname(__file__), 'data')


def test_find_deployment_variables():
    location = DATA_DIR
    assert_equal(find_deployment_variables(location), None)

    # Variables in YAML format
    location = op.join(DATA_DIR, 'checkout_sample', '.project.0')
    assert_equal(find_deployment_variables(location), {'a': 1, 'b': 3})
    location = op.join(DATA_DIR, 'checkout_sample', '.project.0', 'subdir')
    assert_equal(find_deployment_variables(location), {'a': 1, 'b': 3})

    # Variables in JSON format
    location = op.join(DATA_DIR, 'checkout_sample', '.project-json.0')
    assert_equal(find_deployment_variables(location), {'a': 1, 'b': 3})
    location = op.join(DATA_DIR, 'checkout_sample', '.project-json.0',
                       'subdir')
    assert_equal(find_deployment_variables(location), {'a': 1, 'b': 3})

    # Variables in Python format
    location = op.join(DATA_DIR, 'checkout_sample', '.project-python.0')
    assert_equal(find_deployment_variables(location), {'a': 1, 'b': 3})
    location = op.join(DATA_DIR, 'checkout_sample', '.project-python.0',
                       'subdir')
    assert_equal(find_deployment_variables(location), {'a': 1, 'b': 3})

    # Variables in Shell format
    location = op.join(DATA_DIR, 'checkout_sample', '.project-shell.0')
    variables = find_deployment_variables(location)
    assert_equal(unicode(variables), "\na=\"1\"\nb=\"2\"\n")

    # Variables in Shell format, with base variables
    location = op.join(DATA_DIR, 'checkout_sample',
                       '.project-shell-with-base-vars.0')
    variables = find_deployment_variables(location)
    assert_equal(unicode(variables), "a=\"0\"\na=\"1\"\nb=\"2\"\n")


def test_run():
    assert_equal(run('echo', 'foo'), 'foo')


def test_run_async():
    proc = run('echo', 'foo', block=False)
    assert_equal(wait_process(proc), 'foo')


def test_run_with_error():
    assert_raises(subprocess.CalledProcessError, run, 'false')
