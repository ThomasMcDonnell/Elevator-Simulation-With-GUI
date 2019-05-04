import os
import sys
import subprocess


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def init_virtualenv():
    p = os.path.dirname(os.path.realpath(__file__))
    # initialize virtualenv for project
    output, error = subprocess.Popen(
        [
            'virtualenv',
            os.path.join(p, 'venv')
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE).communicate()
    if error:
        print(bcolors.FAIL +
              f'An error occurred: \n{error}' +
              bcolors.ENDC)
        sys.exit(2)

    venv_bin = os.path.join(p, 'venv/bin')
    # install requirements
    output, error = subprocess.Popen(
        [
            os.path.join(venv_bin, 'pip'),
            'install',
            '-r',
            os.path.join(p, 'requirements.txt')
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE).communicate()
    if error:
        print(bcolors.FAIL +
              f'An error occurred during requiremets installation: \n{error}' +
              bcolors.ENDC)
        sys.exit(2)


def run():
    p = os.path.dirname(os.path.realpath(__file__))
    # initialize virtualenv for project
    output, error = subprocess.Popen(
        [
            'source',
            os.path.join(p, 'venv/bin/activate')
        ],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE).communicate()
    if error:
        print(bcolors.FAIL +
              f'An error occurred: \n{error}' +
              bcolors.ENDC)
        sys.exit(2)
    # run the view.py file
    output, error = subprocess.Popen(
        [
            'python',
            os.path.join(p, 'src/view.py')
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE).communicate()
    if error:
        print(bcolors.FAIL +
              f'An error occurred: \n{error}' +
              bcolors.ENDC)
        sys.exit(2)


if __name__ == "__main__":
    init_virtualenv()
    run()