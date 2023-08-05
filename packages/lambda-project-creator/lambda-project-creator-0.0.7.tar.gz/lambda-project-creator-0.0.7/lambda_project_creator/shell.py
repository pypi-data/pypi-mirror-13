#!/usr/bin/python
# coding:utf-8

import sys,traceback
import os
import subprocess
import time
from os import path
import logging
import traceback

LOG = logging.getLogger(__name__)

version = 0.01
INTERROBANG = '\xe2\x81\x89\xef\xb8\x8f'
here = path.abspath(path.dirname(__file__))

def generate_file_from_template(template_file,output_file,replace_word_list={}):

    f_output = open(output_file, "a")
    f_template = open(path.join(here,template_file), 'r')

    for line in f_template:
        if not line.startswith('#'):
           for key,value in replace_word_list.items():
              line = line.replace(str(key), str(value))

        f_output.write(line)

    f_template.close()
    f_output.close()

# lambda.json
def create_lambda_json(args):

    file_name_without_ext, ext = os.path.splitext(args.file_name)

    word_list ={
        "${name}"   :args.project_name,
        "${region}" : args.region,
        "${file_name}" : file_name_without_ext,
        "${handler}"   : args.lambda_handler,
        "${timeout}"   : args.timeout,
        "${memory}"    : args.memory,
    }

    generate_file_from_template('template.json','lambda.json',word_list)

    print('==> generated lambda.json')

# python
def create_python_file(args):
    word_list ={
        "${handler}"   : args.lambda_handler
    }

    file_name_without_ext, ext = os.path.splitext(args.file_name)

    generate_file_from_template('template.py',file_name_without_ext + '.py' ,word_list)

    print('==> generated python file ' + file_name_without_ext + '.py')

# requirement.txt
def create_requirement_txt():
    generate_file_from_template('template.txt','requirement.txt')

    print('==> generated requirement.txt')

#mkdir project_dir && cd project_dir
def create_project_root_dir(args):
    if not os.path.exists(args.project_name):
       os.makedirs(args.project_name)
    os.chdir(args.project_name)
    print('==> created project root directory ' + args.project_name)

#virtualenv .venv_args.project_name
def execute_virtualenv(args):
    ret = subprocess.Popen(['virtualenv','.venv_'+args.project_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=os.environ.copy())
    ret.wait()
    stdout_data, stderr_data = ret.communicate()
    LOG.debug(stdout_data)
    print('==> created virtualenv ' + '.venv_' + args.project_name)

#source .venv_args.project_name/bin/activate
def activate_virtualenv(args):
    script = '.venv_'+args.project_name+'/bin/activate'
    ret = subprocess.Popen(". %s; env" % script, stdout=subprocess.PIPE, shell=True)
    ret.wait()
    stdout_data, stderr_data = ret.communicate()
    env = dict((line.split("=", 1) for line in stdout_data.splitlines()))
    os.environ.update(env)
    LOG.debug(stdout_data)

#pip install lambda-uploader
def pipinstall_lambda_uploader():
    ret = subprocess.Popen(['pip', 'install', 'lambda-uploader'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=os.environ.copy())
    ret.wait()
    stdout_data, stderr_data = ret.communicate()
    LOG.debug(stdout_data)
    print('==> installed lambda-uploader')

def _execute(args):

    create_project_root_dir(args)

    execute_virtualenv(args)

    activate_virtualenv(args)

    pipinstall_lambda_uploader()

    create_lambda_json(args)

    create_python_file(args)

    create_requirement_txt()

    print('Successfully created project')

# entry point
def main(arv=None):

    if not (sys.version_info[0] == 2 and sys.version_info[1] == 7):
        raise RuntimeError('lambda-project-creator requires Python 2.7')

    import argparse

    parser = argparse.ArgumentParser(
            version=('version %s' % version),
            description='Create AWS lambda project for lambda-uploader')

    parser.add_argument('-p',
                        action='store',
                        dest='project_name',
                        help='project name',
                        required=True,
                        default="lambda")

    parser.add_argument('-n',
                        action='store',
                        dest='function_name',
                        help='function name',
                        default="lambda")

    parser.add_argument('-f',
                        action='store',
                        dest='file_name',
                        help='file name',
                        default="lambda.py")

    parser.add_argument('-l',
                        action='store',
                        dest='lambda_handler',
                        help='lambda_handler',
                        default="lambda_handler")

    parser.add_argument('-r',
                        action='store',
                        dest='region',
                        help='region',
                        default="ap-northeast-1")

    parser.add_argument('-m',
                        action='store',
                        dest='memory',
                        help='memory',
                        default="128")

    parser.add_argument('-t',
                        action='store',
                        dest='timeout',
                        help='timeout',
                        default="300")

    verbose = parser.add_mutually_exclusive_group()
    verbose.add_argument('-V', dest='loglevel', action='store_const',
                         const=logging.INFO,
                         help="Set log-level to INFO.")
    verbose.add_argument('-VV', dest='loglevel', action='store_const',
                         const=logging.DEBUG,
                         help="Set log-level to DEBUG.")
    parser.set_defaults(loglevel=logging.WARNING)

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    LOG.debug(args)

    try:
        _execute(args)
    except Exception:
        print('%s Unexpected error. Please report this traceback.' % INTERROBANG )

        traceback.print_exc()
        sys.stderr.flush()
        sys.exit(1)

if __name__ == "__main__":
    main()

