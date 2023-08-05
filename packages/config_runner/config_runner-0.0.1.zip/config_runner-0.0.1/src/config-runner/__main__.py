import sys
from os import walk, getcwd, chdir
from os.path import abspath
from subprocess import Popen, PIPE
from argparse import ArgumentParser


def main(args):
    parser = ArgumentParser(description='Execute process on all directories'
                            ' containing matching file')
    parser.add_argument('--config_file',
                        type=str,
                        default='tox.ini',
                        action='store',
                        help='The config files to look for (default: '
                        '%(default)s)')
    parser.add_argument('command',
                        type=str,
                        action='store',
                        help='The command string to run in each directory')
    args = parser.parse_args()

    command = args.command.split()
    result = 0
    for root, dirs, files in walk('.'):
        for f in files:
            if f == args.config_file:
                current_dir = getcwd()
                chdir(abspath(root))
                process = Popen(command, stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                process.wait()
                if process.returncode == 0:
                    print root, '.'
                else:
                    result += 1
                    print root, 'F'
                    print ''.join(stdout)
                    print ''.join(stderr)
                chdir(current_dir)
    return result


if __name__ == '__main__':
    result = main(sys.argv)
    sys.exit(result)
