import click
import datetime
import glob
import json
import os
import requests
import sys
import yaml

from termcolor import cprint, colored
from subprocess import call
from zipfile import ZipFile


##############################################################################
# Constants
CONFIG_FILE = "brains.yaml"
HISTORY_DIR = "brains_history"
#URL_BASE = "http://localhost:8000"
URL_BASE = "http://dev-coop-brains.herokuapp.com"
URL_SUBMIT = "%s/submissions/create" % URL_BASE


##############################################################################
# Helpers
def _print(str):
    sys.stdout.write(str)
    sys.stdout.flush()


def _get_config():
    return yaml.load(open(CONFIG_FILE).read(), Loader=yaml.loader.BaseLoader)


##############################################################################
# CLI
@click.group()
def cli():
    # This is the entry point (wrapper?) for all of our command line options
    if sys.argv[1] == 'init':
        # first check, does CONFIG_FILE already exist?
        if os.path.exists(CONFIG_FILE):
            if not click.confirm("Are you sure you want to overwrite existing brains?"):
                exit(0)
    else:
        if not os.path.exists(CONFIG_FILE):
            print "`CONFIG_FILE` not found, do `brains init` first"
            exit(-1)


INIT_RUN_MESSAGE_1 = colored("How do you run your script? eg, ", "cyan")
INIT_RUN_MESSAGE_2 = colored("python run.py $INPUT ", "magenta")
INIT_RUN_MESSAGE_3 = colored("($INPUT replaced with dataset path)\n", "cyan")

@cli.command()
@click.option("--name", prompt=colored("Give me your brains, I mean name", "cyan"))
@click.option("--languages", prompt=colored("Languages (python, ruby, etc.)", "cyan"))
@click.option("--run", prompt=INIT_RUN_MESSAGE_1 + INIT_RUN_MESSAGE_2 + INIT_RUN_MESSAGE_3)
def init(name, languages, run):
    """Initializes your CONFIG_FILE for the current submission"""
    contents = [file_name for file_name in glob.glob("*.*") if file_name != "brains.yaml"]

    with open(CONFIG_FILE, "w") as output:
        output.write(yaml.safe_dump({
            "run": run,
            "name": name,
            "languages": languages,
            # automatically insert all root files into contents
            "contents": contents,
        }, default_flow_style=False))

    print ""
    cprint("Automatically including the follow files in brain contents:", "cyan")
    for file_name in contents:
        print "\t", file_name
    print ""
    cprint("done! brains.yaml created", 'green')


@cli.command()
@click.option('--description', default=None, help='description')
@click.option('--datasets', default=None, help='comma separated name of datasets to use (overrides brains.yaml)')
@click.option('--wait/--dont-wait', default=True, help="wait for results or return immediately")
@click.option('--verbose', default=False, is_flag=True, help="print extra output")
def push(description, datasets, wait, verbose):
    """Publish your submission to brains"""
    # Loading config
    config = _get_config()
    file_patterns = config["contents"]
    if not isinstance(file_patterns, type([])):
        # put it into an array so we can iterate it, if it isn't already an array
        file_patterns = [file_patterns]
    if datasets:
        datasets_string = datasets.split(',')
    else:
        datasets_string = config.get("datasets", '')


    # Getting all file names/globs -- making sure we get CONFIG_FILE
    files = {CONFIG_FILE}  # use a set so we don't get duplicates
    for pattern in file_patterns:
        files.update(glob.glob(pattern))
    if not files:
        print "No files could be found? Check your contents section in `CONFIG_FILE`!"
        exit(-1)

    if verbose:
        print ""
        print "gatherered files:"
        for path in files:
            print "\t", path
        print ""

    # Zipping
    _print("zipping...")

    if not os.path.exists("brains_history"):
        os.mkdir("brains_history")

    zip_path = 'brains_history/%s.zip' % str(datetime.datetime.now())
    with ZipFile(zip_path, 'w') as zip_file:
        for path in files:
            zip_file.write(path)
    cprint("done", 'green')

    # Sending to server
    with open(zip_path, 'rb') as zip_file:
        _print("sending to server...")
        try:
            response = requests.post(
                URL_SUBMIT,
                files={
                    "zip_file": zip_file,
                },
                data={
                    "name": config["name"],
                    "description": description or '',
                    "languages": config["languages"],
                    "datasets": datasets_string,
                    "wait": wait,
                },
                stream=wait  # if we're waiting for response then stream
            )

            if response.status_code == 200:
                cprint("done", 'green')

                if wait:
                    _print("\nOutput: ")
                    cprint(" " * 70, 'green', attrs=('underline',))

                    chunk_buffer = ""
                    # read in 1 chunk at a time for carriage return detection
                    for chunk in response.iter_content(chunk_size=1):
                        chunk_buffer += chunk

                        if chunk == '\r':
                            # We hit the end of a message!
                            try:
                                data = json.loads(chunk_buffer)
                                if "stdout" not in data or "stderr" not in data:
                                    print "dis one"
                                    continue
                            except (ValueError,):
                                continue

                            if data["stdout"]:
                                # Get rid of termination string, if it's there
                                data["stdout"] = data["stdout"].replace("-%-%-%-%-END BRAIN SEQUENCE-%-%-%-%-", "")
                                _print(data["stdout"])
                            if data["stderr"]:
                                _print(colored(data["stderr"], 'red'))

                            # Clear buffer after reading message
                            chunk_buffer = ""
            else:
                cprint(response.json()["error"], 'red')
        except requests.exceptions.ConnectionError:
            cprint("failed to connect to server!", 'red')
            exit(-2)


@cli.command()
@click.option('--dataset', default=None, help='name of dataset to use')
def run(dataset):
    """Run brain locally"""
    config = _get_config()

    if dataset:
        _print("getting dataset from brains...")
        cprint("done", 'green')

        # check dataset cache for dataset
        # if not exists
        # r = requests.get('https://api.github.com/events', stream=True)
        # with open(filename, 'wb') as fd:
        #     for chunk in r.iter_content(chunk_size):
        #         fd.write(chunk)

    cprint('Running "%s"' % config["run"], 'green', attrs=("underline",))
    call(config["run"].split())


@cli.command()
def get(submission_id):
    # TODO: Download some submission to work with
    pass
