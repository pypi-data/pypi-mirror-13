import sys
import os
import requests
import json
import subprocess
import getpass
import version

from time import gmtime, strftime
from websocket import create_connection

config_filename = 'deploy.json'
config = {}
secret = None


def echo(content):
    print "\033[92m[%s]-------> '%s'" % (strftime("%H:%M:%S", gmtime()), content)


def warning(content):
    print "\033[93m[%s]-------> '%s'" % (strftime("%H:%M:%S", gmtime()), content)


def is_init():
    global config_filename
    if not os.path.isfile(config_filename):
        warning("config file does not exists")
        sys.exit(0)


# Initializing
def init():
    global config_filename
    if os.path.isfile(config_filename):
        warning("deploy.json already exists")
        sys.exit(0)

    echo("initializing")
    subprocess.call("cp " + os.path.dirname(__file__) + '/../data/deploy.json .', shell=True)
    echo("Please edit deploy.json")
    sys.exit(0)


def read_config():
    global config_filename, config
    if os.path.isfile(config_filename):
        with open(config_filename) as data_file:
            config = json.load(data_file)


def read_secret():
    global secret
    secret = getpass.getpass("secret:")


def print_help():
    print "Try `sra deploy`?"
    sys.exit(0)


def process():
    import time
    global config_filename, config, secret
    if len(sys.argv) > 1:
        task = sys.argv[1]

        if task == 'init':
            init()

        if task == '-h' or task == '--help':
            print_help()

        if task == '-v' or task == '--version':
            print version.__VERSION__
            sys.exit(0)

        is_init()
        read_config()
        read_secret()
        package = {}

        try:
            stage = sys.argv[2]
        except IndexError:
            stage = config['default_stage']

        try:
            stage_setting = config['stages'][stage]
            __ENDPOINT__ = stage_setting['host'] + ':' + stage_setting['port']
            websocket = create_connection("ws://" + __ENDPOINT__ + "/_sockets")
        except KeyError:
            warning("invalid stage")
            sys.exit(0)

        echo("SRA client version: " + version.__VERSION__)

        if task == 'check':
            print 'check feature has not implement'
        elif task == 'rollback':

            echo("Rollback")
            package['task'] = 'rollback'
            package['deploy_to'] = config['deploy_to']
            package['shared_paths'] = config['shared_paths']
            package['secret_token'] = secret
            websocket.send(json.dumps(package))
            echo("Receiving...")
            while True:
                result = websocket.recv()
                result_json = json.loads(result)
                if result_json['close']:
                    echo("Done.")
                    break
                else:
                    echo(result_json['updates'])
        elif task == 'deploy':
            echo("=================================")
            echo("Deploy to " + stage)
            echo("=================================")
            echo("Deploying")
            start = time.time()

            # build
            subprocess.call(config['build_command'], shell=True)
            echo("Build finished")

            # make sure package exists
            if config['package_filename']:
                package_filename = config['package_filename']
            else:
                package_filename = 'latest.zip'

            if not os.path.isfile(package_filename):
                warning("package not exists")
                sys.exit(0)

            # upload
            url = 'http://' + __ENDPOINT__ + '/upload'
            files = {'package': (package_filename, open(package_filename, 'rb'))}
            headers = {'client_version': version.__VERSION__,
                       'X-Secret-Token': secret,
                       'deploy_to': config['deploy_to']}
            response = requests.post(url, files=files, headers=headers)
            response_object = json.loads(response.text)
            if not response_object['result']:
                warning(response_object['message'])
                websocket.close()
                sys.exit(0)

            echo("Upload success: " + response_object['deploy_id'])

            package['task'] = 'deploy'
            package['body'] = response_object['deploy_id']
            package['deploy_id'] = response_object['deploy_id']
            package['deploy_to'] = config['deploy_to']
            package['shared_paths'] = config['shared_paths']
            package['secret_token'] = secret

            websocket.send(json.dumps(package))

            echo("Receiving...")
            while True:
                result = websocket.recv()
                result_json = json.loads(result)
                if result_json['close']:
                    echo("Done.")
                    echo("Elapsed time: " + str(int(time.time() - start)) + " seconds")
                    sys.exit(0)
                else:
                    echo(result_json['updates'])

            websocket.close()
        else:
            warning("task '%s' not found" % task)
    else:
        print_help()


def main():
    try:
        process()
    except KeyboardInterrupt:
        warning("Aborted")
        sys.exit(0)
