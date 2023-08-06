#!/usr/bin/env python
from pathlib import Path
import os
import subprocess
from string import Template
from .command import Command
from matador.session import Session


def _connection_string(dbms, connection, user, password):
    if dbms.lower() == 'oracle':
        return user + '/' + password + '@' + connection


def _sql_script(file_path):
    with file_path.open('r') as f:
        script = f.read()
        f.close()
    return script


def run_sql_script(logger, file_path):
    file = Path(file_path)
    message = Template(
        'Matador: Executing ${file} against ${connection} \n')
    substitutions = {
        'file': file.name,
        'connection': Session.environment['connection']
    }
    logger.info(message.substitute(substitutions))

    script = _sql_script(file)
    connection_string = _connection_string(
        Session.environment['dbms'],
        Session.environment['connection'],
        Session.credentials['user'],
        Session.credentials['password'])

    os.chdir(str(file.parent))

    if Session.environment['dbms'].lower() == 'oracle':
        script += '\nshow error'
        process = subprocess.Popen(
            ['sqlplus', '-S', '-L', connection_string],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE)
        process.stdin.write(script.encode('utf-8'))
        process.stdin.close()
        process.wait()


class RunSqlScript(Command):

    def _add_arguments(self, parser):

        parser.add_argument(
            '-d', '--directory',
            type=str,
            required=True,
            help='Directory containing script')

        parser.add_argument(
            '-f', '--file',
            type=str,
            required=True,
            help='Script file name')

        parser.add_argument(
            '-e', '--environment',
            type=str,
            required=True,
            help='Agresso environment')

    def _execute(self):
        Session.set_environment(self.args.environment)

        file_path = os.path.join(self.args.directory, self.args.file)

        run_sql_script(
            self._logger,
            file_path)
