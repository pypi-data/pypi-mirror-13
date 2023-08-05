#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           fujian
# Program Description:    An HTTP server that executes Python code.
#
# Filename:               test/test_fujian.py
# Purpose:                It's got all the tests.
#
# Copyright (C) 2015 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
'''
Automated unit tests for Fujian.
'''


from fujian import __main__ as fujian
import fujian as fujian_init
import sys


def test_stdout_handler():
    "It's a test for the StdoutHandler class."

    handler = fujian.StdoutHandler()
    assert '' == handler.get()
    handler.write('what what')
    assert 'what what' == handler.get()
    handler.write(' in the (censored)')
    assert 'what what in the (censored)' == handler.get()


def test_make_new_stdout():
    "It's a test for make_new_stdout()."

    try:
        assert 'sys' not in fujian.exec_globals
        assert not isinstance(sys.stdout, fujian.StdoutHandler)
        assert not isinstance(sys.stderr, fujian.StdoutHandler)
        fujian.make_new_stdout()
        assert 'sys' not in fujian.exec_globals
        assert isinstance(sys.stdout, fujian.StdoutHandler)
        assert isinstance(sys.stderr, fujian.StdoutHandler)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def test_get_from_stdout():
    "It's a test for get_from_stdout()."

    try:
        fujian.make_new_stdout()
        sys.stdout.write('lolz')
        assert 'lolz' == fujian.get_from_stdout()
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def test_get_from_stderr():
    "It's a test for get_from_stderr()."

    try:
        fujian.make_new_stdout()
        sys.stderr.write('errlolz')
        assert 'errlolz' == fujian.get_from_stderr()
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def test_myprint():
    "It's a test for myprint(). Note that myprint() appends a newline to its input!"

    really_keep_stdout = sys.__stdout__
    try:
        sys.__stdout__ = fujian.StdoutHandler()
        fujian.myprint('check it out')
        assert 'check it out\n' == sys.__stdout__.get()
    finally:
        sys.__stdout__ = really_keep_stdout


def test_get_traceback():
    "It's a test for get_traceback()."

    ran_the_check = False
    try:
        raise RuntimeError('I am not a tow truck.')
    except RuntimeError:
        ran_the_check = True
        assert fujian.get_traceback().endswith('RuntimeError: I am not a tow truck.\n')


def test_execute_works():
    "Test for execute_some_python() when the code-to-evaluate runs fine."

    code = ('fujian_return = 5\n' +
            'print("6")\n' +
            'import sys\n'
            'sys.stderr.write("7")'
           )

    # pre- and post-condition: "fujian_return" isn't defined
    assert 'fujian_return' not in fujian.exec_globals
    try:
        returns = fujian.execute_some_python(code)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    assert 'fujian_return' not in fujian.exec_globals

    assert {'return': '5', 'stdout': '6\n', 'stderr': '7'} == returns


def test_execute_broken():
    "Test for execute_some_python() when the code-to-evaluate messes up."

    code = ('fujian_return = 5\n' +
            'print("6")\n' +
            'import sys\n'
            'sys.stderr.write("7")\n' +
            'raise RuntimeError("A")'
           )

    # pre- and post-condition: "fujian_return" isn't defined
    assert 'fujian_return' not in fujian.exec_globals
    try:
        returns = fujian.execute_some_python(code)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    assert 'fujian_return' not in fujian.exec_globals

    assert '5' == returns['return']
    assert '6\n' == returns['stdout']
    assert '7' == returns['stderr']
    assert returns['traceback'].endswith('RuntimeError: A\n')


def test_default_headers():
    "Test for FujianHandler.set_default_headers()."

    class MockHandler(object):
        __class__ = fujian.FujianHandler
        def __init__(self):
            self.calls = []
        def set_header(self, header, value):
            self.calls.append((header, value))
    handler = MockHandler()

    fujian.FujianHandler.set_default_headers(handler)

    assert 'Server' == handler.calls[0][0]
    assert 'Fujian/{}'.format(fujian_init.__version__) == handler.calls[0][1]
    assert 'Access-Control-Allow-Origin' == handler.calls[1][0]
    assert fujian._ACCESS_CONTROL_ALLOW_ORIGIN == handler.calls[1][1]


def test_get_request():
    "It's a test for FujianHandler.get()."

    class MockHandler(object):
        __class__ = fujian.FujianHandler
        def write(self, write_this):
            self.wrote = write_this
    handler = MockHandler()

    fujian.FujianHandler.get(handler)

    assert '' == handler.wrote


def test_post_works():
    "It's a test for FujianHandler.post() when the code-to-evaluate runs fine."

    class MockRequest(object):
        body = ('fujian_return = 5\n' +
                'print("6")\n' +
                'import sys\n'
                'sys.stderr.write("7")'
               )

    class MockHandler(object):
        __class__ = fujian.FujianHandler
        request = MockRequest()
        def write(self, write_this):
            self.wrote = write_this
    handler = MockHandler()

    # pre- and post-condition: "fujian_return" isn't defined
    assert 'fujian_return' not in fujian.exec_globals
    try:
        fujian.FujianHandler.post(handler)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    assert 'fujian_return' not in fujian.exec_globals

    assert {'return': '5', 'stdout': '6\n', 'stderr': '7'} == handler.wrote


def test_post_broken():
    "It's a test for FujianHandler.post() when the code-to-evaluate messes up."

    class MockRequest(object):
        body = ('fujian_return = 5\n' +
                'print("6")\n' +
                'import sys\n'
                'sys.stderr.write("7")\n' +
                'raise RuntimeError("A")'
               )

    class MockHandler(object):
        __class__ = fujian.FujianHandler
        request = MockRequest()
        def write(self, write_this):
            self.wrote = write_this
        def set_status(self, status_code):
            self.status_code = status_code
    handler = MockHandler()

    # pre- and post-condition: "fujian_return" isn't defined
    assert 'fujian_return' not in fujian.exec_globals
    try:
        fujian.FujianHandler.post(handler)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    assert 'fujian_return' not in fujian.exec_globals

    assert 400 == handler.status_code
    assert '5' == handler.wrote['return']
    assert '6\n' == handler.wrote['stdout']
    assert '7' == handler.wrote['stderr']
    assert handler.wrote['traceback'].endswith('RuntimeError: A\n')


def test_open():
    "Test for FujianWebSocketHandler.open()."

    class MockHandler(object):
        __class__ = fujian.FujianWebSocketHandler
        def set_nodelay(self, arg):
            self.nodelay = arg
    handler = MockHandler()

    fujian.FujianWebSocketHandler.open(handler)

    assert True == handler.nodelay
    assert True == handler._is_open


def test_is_open():
    "Test for FujianWebSocketHandler.is_open()."

    class MockHandler(object):
        __class__ = fujian.FujianWebSocketHandler
        _is_open = 'four'
    handler = MockHandler()

    assert 'four' == fujian.FujianWebSocketHandler.is_open(handler)


def test_on_close():
    "Test for FujianWebSocketHandler.on_close()."

    class MockHandler(object):
        __class__ = fujian.FujianWebSocketHandler
    handler = MockHandler()

    fujian.FujianWebSocketHandler.on_close(handler)

    assert False == handler._is_open


def test_check_origin():
    "Tests for FujianWebSocketHandler.check_origin()."

    class MockHandler(object):
        __class__ = fujian.FujianWebSocketHandler
    handler = MockHandler()

    check_origin = fujian.FujianWebSocketHandler.check_origin

    assert True is check_origin(handler, 'https://localhost:77983')
    assert True is check_origin(handler, 'http://localhost:77983')
    assert False is check_origin(handler, 'https://bocalhost:77983')  # the bassoonist's computer


def test_on_message_1():
    "Test for FujianWebSocketHandler.on_message() when stdout has something."

    code = 'print("6")'

    class MockHandler(object):
        __class__ = fujian.FujianWebSocketHandler
        _message = None
        def write_message(self, message):
            self._message = message
    handler = MockHandler()

    # pre- and post-condition: "fujian_return" isn't defined
    assert 'fujian_return' not in fujian.exec_globals
    try:
        fujian.FujianWebSocketHandler.on_message(handler, code)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    assert 'fujian_return' not in fujian.exec_globals

    assert {'return': '', 'stdout': '6\n', 'stderr': ''} == handler._message


def test_on_message_2():
    "Test for FujianWebSocketHandler.on_message() when stderr has something."

    code = 'import sys\nsys.stderr.write("check")'

    class MockHandler(object):
        __class__ = fujian.FujianWebSocketHandler
        _message = None
        def write_message(self, message):
            self._message = message
    handler = MockHandler()

    # pre- and post-condition: "fujian_return" isn't defined
    assert 'fujian_return' not in fujian.exec_globals
    try:
        fujian.FujianWebSocketHandler.on_message(handler, code)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    assert 'fujian_return' not in fujian.exec_globals

    assert {'return': '', 'stdout': '', 'stderr': 'check'} == handler._message


def test_on_message_3():
    "Test for FujianWebSocketHandler.on_message() when fujian_return has something."

    code = 'fujian_return = "seven"'

    class MockHandler(object):
        __class__ = fujian.FujianWebSocketHandler
        _message = None
        def write_message(self, message):
            self._message = message
    handler = MockHandler()

    # pre- and post-condition: "fujian_return" isn't defined
    assert 'fujian_return' not in fujian.exec_globals
    try:
        fujian.FujianWebSocketHandler.on_message(handler, code)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    assert 'fujian_return' not in fujian.exec_globals

    assert {'return': 'seven', 'stdout': '', 'stderr': ''} == handler._message


def test_on_message_4():
    "Test for FujianWebSocketHandler.on_message() when traceback has something."

    code = 'raise RuntimeError("A")'

    class MockHandler(object):
        __class__ = fujian.FujianWebSocketHandler
        _message = None
        def write_message(self, message):
            self._message = message
    handler = MockHandler()

    # pre- and post-condition: "fujian_return" isn't defined
    assert 'fujian_return' not in fujian.exec_globals
    try:
        fujian.FujianWebSocketHandler.on_message(handler, code)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    assert 'fujian_return' not in fujian.exec_globals

    assert '' == handler._message['return']
    assert '' == handler._message['stdout']
    assert '' == handler._message['stderr']
    assert handler._message['traceback'].endswith('RuntimeError: A\n')


def test_on_message_5():
    "Test for FujianWebSocketHandler.on_message() when there's nothing to return."

    code = 'pass'

    class MockHandler(object):
        __class__ = fujian.FujianWebSocketHandler
        _message = None
        def write_message(self, message):
            self._message = message
    handler = MockHandler()

    # pre- and post-condition: "fujian_return" isn't defined
    assert 'fujian_return' not in fujian.exec_globals
    try:
        fujian.FujianWebSocketHandler.on_message(handler, code)
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    assert 'fujian_return' not in fujian.exec_globals

    assert None is handler._message
