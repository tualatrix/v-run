from argparse import ArgumentParser, REMAINDER
from glob import glob
import os.path
import sys
import signal
import pexpect
from shutil import get_terminal_size
from contextlib import contextmanager

@contextmanager
def temp_environ():
    """Allow the ability to set os.environ temporarily"""
    environ = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(environ)

def fork_compat(venv, args):
        # Grab current terminal dimensions to replace the hardcoded default
        # dimensions of pexpect.
        cmd = os.environ['SHELL']
        dims = get_terminal_size()
        with temp_environ():
            c = pexpect.spawn(cmd, ["-i"], dimensions=(dims.lines, dims.columns))
        c.sendline('. {}/bin/activate'.format(venv))
        if args:
            c.sendline(" ".join(args))

        # Handler for terminal resizing events
        # Must be defined here to have the shell process in its context, since
        # we can't pass it as an argument
        def sigwinch_passthrough(sig, data):
            dims = get_terminal_size()
            c.setwinsize(dims.lines, dims.columns)

        signal.signal(signal.SIGWINCH, sigwinch_passthrough)

        # Interact with the new shell.
        c.interact(escape_character=None)
        c.close()
        sys.exit(c.exitstatus)

def run():
    parser = ArgumentParser(
        usage='%(prog)s [OPTIONS] [--] [CMD]',
        description='''
            Run command from an existing python virtual environment (that is,
            with the environment's bin directory prepended to PATH). By default
            the location of the virtual environment directory is searched from
            your current working directory and used if only one match is found.
            This behavior can be overridden with the --venv option.

            CMD contains the command line to execute. You can prepend
            CMD with -- to avoid conflict with %(prog)s own options. If CMD is
            omitted then the environment's python interpreter is run without
            arguments.

            This tool tries to guess if you want to run the python interpreter
            so that you do not need to start CMD with 'python'. For that it
            first tries to run CMD. If that fails because the executable for
            CMD can not be found and the first word of CMD begins with '-' or
            ends with '.py', then 'python' is prepended to CMD and the
            execution is retried. If you do not desire such a behavior, pass
            the --no-guess option.
        ''',
    )

    parser.add_argument('--venv',
        help='''
            Use this virtual environment instead of searching for one.
        ''',
    )

    parser.add_argument('--no-guess',
        action='store_true',
        help='''
            Do not try to prepend 'python' when execution fails because the
            command is not found.
        ''',
    )

    args, cmd_args = parser.parse_known_args()

    if not cmd_args:
        cmd_args = ['python']

    if cmd_args and cmd_args[0] == '--':
        cmd_args.pop(0)

    if not args.venv:
        venvs = []

        for p in glob(os.path.join('.*', 'bin', 'python')) + glob(os.path.join('*', 'bin', 'python')):
            if os.access(p, os.X_OK):
                venvs.append(os.path.dirname(os.path.dirname(p)))

        if not venvs:
            print('No virtual environments found', file=sys.stderr)
            exit(1)

        if len(venvs) > 1:
            print('More than one virtual environment found:', file=sys.stderr)
            for p in venvs:
                print('  ' + p, file=sys.stderr)
            print('Please, use the --venv option.', file=sys.stderr)
            exit(1)

        args.venv = venvs[0]

    path = os.path.join(args.venv, 'bin')
    if 'PATH' in os.environ:
        os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
    else:
        os.environ['PATH'] = path

    try:
        if cmd_args[0] == "shell" and len(cmd_args) == 1:
            fork_compat(args.venv, None)
        else:
            os.execvp(cmd_args[0], cmd_args)
    except FileNotFoundError:
        if args.no_guess:
            raise

        if cmd_args[0].startswith('-') or cmd_args[0].endswith('.py'):
            cmd_args.insert(0, 'python')
            os.execvp(cmd_args[0], cmd_args)
        else:
            raise


if __name__ == '__main__':
    run()
