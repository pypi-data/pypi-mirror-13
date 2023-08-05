#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
import re
import subprocess
import sys
import yaml

import click


__author__ = 'Kentaro Wada <www.kentaro.wada@gmail.com>'
__version__ = '2.0.2'


this_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
CONFIG_FILE = os.path.expanduser('~/.gshell')
if platform.uname()[0] == 'Linux':
    DRIVE_EXE = '_gshell_drive-linux-x64'
elif platform.uname()[0] == 'Darwin':
    DRIVE_EXE = '_gshell_drive-osx-x64'
else:
    sys.stderr.write('Not supported os\n')
    sys.exit(1)



@click.group()
def cli():
    pass


def init():
    if not os.path.exists(os.path.expanduser('~/.gdrive')):
        subprocess.call(DRIVE_EXE, shell=True)


def get_name_by_id(id):
    cmd = '{exe} info --id {id}'.format(exe=DRIVE_EXE, id=id)
    stdout = subprocess.check_output(cmd, shell=True)
    for l in stdout.splitlines():
        if l.startswith('Title: '):
            return l.split()[-1]


def getcwd():
    if os.path.exists(CONFIG_FILE):
        return yaml.load(open(CONFIG_FILE))
    home_id = raw_input('Please specify home directory id: ')
    name = get_name_by_id(home_id)
    config = {'home_id': home_id, 'home_name': name,
              'id': home_id, 'name': name}
    yaml.dump(config, open(CONFIG_FILE, 'w'))
    return config


@cli.command(name='upload', help='upload file')
@click.argument('filename', required=True, type=click.Path(exists=True))
def cmd_upload(filename):
    init()
    cwd = getcwd()
    cmd = '{exe} upload --file {file} --parent {pid}'.format(
        exe=DRIVE_EXE, file=filename, pid=cwd['id'])
    subprocess.call(cmd, shell=True)


@cli.command(name='download', help='download file')
@click.argument('filename', required=True)
def cmd_download(filename):
    init()
    id = get_id_by_name(filename)
    cmd = '{exe} download --id {id}'.format(exe=DRIVE_EXE, id=id)
    subprocess.call(cmd, shell=True)


@cli.command(name='rm', help='remove file')
@click.argument('filename', required=True)
def cmd_rm(filename):
    init()
    id = get_id_by_name(filename)
    cmd = '{exe} delete --id {id}'.format(exe=DRIVE_EXE, id=id)
    subprocess.call(cmd, shell=True)


@cli.command(name='ll', help='list files in detail')
def cmd_ll():
    init()
    cwd = getcwd()
    cmd = '''{exe} list --query " '{pid}' in parents" --noheader'''.format(
        exe=DRIVE_EXE, pid=cwd['id'])
    subprocess.call(cmd, shell=True)


@cli.command(name='ls', help='list files')
def cmd_ls():
    init()
    cwd = getcwd()
    cmd = '''{exe} list --query " '{pid}' in parents"'''.format(
        exe=DRIVE_EXE, pid=cwd['id'])
    stdout = subprocess.check_output(cmd, shell=True)
    lines = stdout.splitlines()
    header = lines[0]
    start = re.search('Title', header).start()
    end = re.search('Size', header).start()
    print('\n'.join([l[start:end].strip() for l in stdout.splitlines()[1:]]))


@cli.command(name='mkdir', help='make directory')
@click.argument('dirname', required=True)
def cmd_mkdir(dirname):
    init()
    cwd = getcwd()
    cmd = '{exe} folder --title {name} --parent {pid}'.format(
        exe=DRIVE_EXE, name=dirname, pid=cwd['id'])
    subprocess.call(cmd, shell=True)


@cli.command(name='pwd', help='print current working directory')
def cmd_pwd():
    init()
    print(getcwd()['name'])


def get_id_by_name(name):
    init()
    cwd = getcwd()
    cmd = '''{exe} list --query " '{pid}' in parents"'''.format(
        exe=DRIVE_EXE, pid=cwd['id'])
    stdout = subprocess.check_output(cmd, shell=True)
    lines = stdout.splitlines()
    header = lines[0]
    start = re.search('Title', header).start()
    end = re.search('Size', header).start()
    for l in stdout.splitlines()[1:]:
        id, title = l[:start].strip(), l[start:end].strip()
        if len(name) > 40:
            name = name[:19] + '...' + name[-18:]
        if name == title:
            return id


def get_parent_id(id):
    init()
    cmd = '{exe} info --id {id}'.format(exe=DRIVE_EXE, id=id)
    stdout = subprocess.check_output(cmd, shell=True)
    for l in stdout.splitlines():
        if l.startswith('Parents: '):
            return l.split()[-1]


@cli.command(name='cd', help='change directory')
@click.argument('dirname', required=False)
def cmd_cd(dirname):
    init()
    cwd = getcwd()
    if dirname is None:
        cwd['id'] = cwd['home_id']
        cwd['name'] = cwd['home_name']
    elif dirname == '..':
        id = get_parent_id(cwd['id'])
        cwd['id'] = id
        cwd['name'] = get_name_by_id(id=id)
    else:
        id = get_id_by_name(dirname)
        if id is None:
            sys.stderr.write('directory {name} does not exist\n'
                             .format(name=dirname))
            sys.exit(1)
        cwd['id'] = id
        cwd['name'] = get_name_by_id(id=id)
    yaml.dump(cwd, open(CONFIG_FILE, 'w'))


@cli.command(name='open', help='open current site on browser')
def cmd_open():
    init()
    cwd = getcwd()
    if platform.uname()[0] == 'Linux':
        open_exe = 'gnome-open'
    elif platform.uname()[0] == 'Darwin':
        open_exe = 'open'
    else:
        sys.stderr.write('Not supported os\n')
        sys.exit(1)
    cmd = "{exe} 'https://drive.google.com/drive/u/1/folders/{id}'"\
        .format(exe=open_exe, id=cwd['id'])
    subprocess.call(cmd, shell=True)


@cli.command(name='share', help='share file')
@click.argument('filename', required=True)
def cmd_share(filename):
    init()
    id = get_id_by_name(name=filename)
    cmd = '{exe} share --id {id}'.format(exe=DRIVE_EXE, id=id)
    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    cli()
