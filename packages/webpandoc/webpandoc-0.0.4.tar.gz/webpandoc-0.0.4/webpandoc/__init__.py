#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Florent Peterschmitt
# BSD New License

import os
import tempfile
import base64
import argparse
import subprocess
import zipfile
import shutil

import werkzeug

from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
from flask import request
from flask import send_file


class APIDocToPandoc(Resource):

    TMP_UP_DIR = './webpandoc_tmp/'

    PANDOC_FORMATS = {
        'pdf': 'latex',
    }

    PANDOC_ALLOWED_INPUT_FORMATS = [
        'markdown',
        'rts',
        'html',
    ]
    PANDOC_ALLOWED_OUTPUT_FORMATS = [
        'pdf',
        'odt',
        'html',
    ]

    def __init__(self, *args, **kwargs):
        super(APIDocToPandoc, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'sourceFile', type=werkzeug.datastructures.FileStorage, location='files')
        self.parser.add_argument(
            'sourceArchive', type=werkzeug.datastructures.FileStorage, location='files')
        self.parser.add_argument(
            'archiveIndex', type=str, default='webpandoc_index')
        self.parser.add_argument('raw', type=bool)
        self.parser.add_argument(
            'format_from', type=str, default='markdown', choices=self.PANDOC_ALLOWED_INPUT_FORMATS)
        self.parser.add_argument(
            'format_to', type=str, default='pdf', choices=self.PANDOC_ALLOWED_OUTPUT_FORMATS)
        self.parser.add_argument(
            'pandoc_writer', type=str, choices=['latex', 'odt'])

        self.TMP_UP_DIR = os.path.abspath(self.TMP_UP_DIR)

        if not os.path.isdir(self.TMP_UP_DIR):
            os.makedirs(self.TMP_UP_DIR)

    def file_cleanup(self):
        if os.path.isfile(self.upfile_path):
            os.remove(self.upfile_path)
        if os.path.isfile(self.converted_file_path):
            os.remove(self.converted_file_path)

    def save_workdir(self):
        self.old_workdir = os.getcwd()

    def restore_workdir(self):
        os.chdir(self.old_workdir)

    def cleanup_workdir(self):
        if os.getcwd() != self.TMP_UP_DIR:
            shutil.rmtree(os.getcwd())

    def pandoc_convert(self, mode='raw'):
        self.save_workdir()
        args = self.parser.parse_args()
        tmpdir = tempfile.mkdtemp(dir=self.TMP_UP_DIR)
        os.chdir(tmpdir)

        sourceArchive = request.files.get('sourceArchive', None)
        if sourceArchive:
            tmparchfile = tempfile.NamedTemporaryFile(
                dir=tmpdir, suffix='.zip')
            tmparchfilepath = os.path.join(tmpdir, tmparchfile.name)
            sourceArchive.save(tmparchfilepath)
            with zipfile.ZipFile(tmparchfilepath, 'r') as a:
                a.extractall(tmpdir)

            orig_name = args.archiveIndex
            orig_mimetype = ''

            self.upfile_path = os.path.join(tmpdir, args.archiveIndex)
        else:
            sourceFile = request.files['sourceFile']
            orig_name = sourceFile.filename
            orig_mimetype = sourceFile.mimetype

            tmpfile = tempfile.NamedTemporaryFile(dir=tmpdir)
            self.upfile_path = os.path.join(tmpdir, tmpfile.name)
            sourceFile.save(self.upfile_path)

        self.converted_file_path = self.upfile_path + '.' + args.format_to

        pandoc_writer = None
        if args.pandoc_writer:
            pandoc_writer = args.pandoc_writer
        elif args.format_to in self.PANDOC_FORMATS.keys():
            pandoc_writer = self.PANDOC_FORMATS[args.format_to]
        else:
            pandoc_writer = args.format_to

        pandoc_cmdline = 'cat {0} | pandoc -f {2} -t {3} -o {1}'.format(
            self.upfile_path, self.converted_file_path, args.format_from, pandoc_writer)
        p = subprocess.Popen(
            pandoc_cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        pandoc_stdout, pandoc_stderr = p.communicate()
        pandoc_retcode = p.returncode

        if not os.path.isfile(self.converted_file_path):
            if mode in ['raw', 'api_raw']:
                return None
            return {
                'convert_status': 0,
                'stdout': pandoc_stdout,
                'stderr': pandoc_stderr,
                'retcode': pandoc_retcode
            }

        if mode in ['raw', 'api_raw']:
            response = send_file(self.converted_file_path,
                                 attachment_filename=orig_name,
                                 mimetype=orig_mimetype,
                                 as_attachment=True)
        elif mode == 'api':
            with open(self.converted_file_path, 'r') as file_content:
                response = {
                    'convert_status': 1,
                    'file_content': base64.b64encode(file_content.read()),
                    'file_name': orig_name + '.' + args.format_to,
                }

        return response

    def post(self):
        args = self.parser.parse_args()

        mode = 'api'
        if args.raw:
            mode = 'api_raw'
        try:
            response = self.pandoc_convert(mode)
        except Exception, e:
            self.cleanup_workdir()
            self.restore_workdir()
            self.file_cleanup()
            raise
        finally:
            self.cleanup_workdir()
            self.restore_workdir()
            self.file_cleanup()

        return response


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bind', help='bind listen to address', type=str, default='0.0.0.0')
    parser.add_argument(
        '--port', help='listen on this port', type=int, default='5000')
    args = parser.parse_args()

    return args, parser


def get_converted(server, fname, ffrom, fto, is_archive=False):
    import requests
    s = requests.Session()

    fkey = 'sourceFile'
    if is_archive:
        fkey = 'sourceArchive'

    files = {
        fkey: (os.path.basename(fname), open(fname, 'rb')),
    }

    payload = {
        'format_from': ffrom,
        'format_to': fto
    }

    r = s.post(server, files=files, data=payload)
    jr = r.json()

    if jr['convert_status'] != 0:
        return base64.b64decode(jr['file_content'])
    else:
        None


def main_client():
    import argparse
    import base64
    import os.path
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', default='http://localhost:5000/api')
    parser.add_argument('--archive', type=str)
    parser.add_argument('--sourcefile', type=str)
    parser.add_argument('--destfile', type=str, required=False)
    parser.add_argument('--from', dest='ffrom', default='markdown')
    parser.add_argument('--to', dest='fto', default='pdf')

    args = parser.parse_args()

    if not args.archive and not args.sourcefile:
        parser.error('at least one of --archive or --sourcefile is required')

    if not args.archive:
        converted = get_converted(
            args.server, args.sourcefile, args.ffrom, args.fto)
    else:
        converted = get_converted(
            args.server, args.archive, args.ffrom, args.fto, True)

    if converted == None:
        sys.stderr.write('Failure while converting document.\n')
        sys.stderr.flush()
        sys.exit(1)

    if args.destfile:
        with open(args.destfile, 'wb') as fwrite:
            fwrite.write(converted)
    else:
        sys.stdout.write(converted)
        sys.stdout.flush()


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.debug = False
api = Api(app)
api.add_resource(APIDocToPandoc, '/api')


def main_server():
    args, parser = argparser()
    app.run(host=args.bind, port=args.port)

if __name__ == '__main__':
    pass
