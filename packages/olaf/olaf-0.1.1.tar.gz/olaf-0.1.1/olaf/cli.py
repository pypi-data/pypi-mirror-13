# -*- coding: utf-8 -*-

"""
    pipack
    ~~~~~~~~~~~~~
    command line tool to help you manage multiple requirements files.
"""

import glob
import click
import subprocess
import collections


@click.command()
@click.option('--prefix', '-p', default='requirements', help='Match files on {prefix}*.txt')
@click.option('--write', '-w', is_flag=True, help='Use if you want to commit the changes to your files.')
@click.argument('cmd', default='freeze', required=True)
def main(cmd, prefix, write):
    if cmd == 'freeze':
        freeze(prefix, write)


def freeze(prefix, write):
    frozen = pipfreeze()
    files = []
    unreqed = []

    for name in get_reqs_files(prefix):
        files.append({
            'name': name,
            'packages': jam(name),
            'updated': []
        })

    match_versions(frozen, files, unreqed)
    add_installed(files, unreqed)

    if write is True:
        write_updates(files)
    else:
        print_updates(files)

    uninstalled = check_uninstalled(frozen, files)


def get_reqs_files(prefix):
    return glob.glob('{}*.txt'.format(prefix))


def write_updates(files):
    # write the requirements files.
    for req in files:
        if len(req['updated']) > 0:
            rewrite(req)
        else:
            click.echo('No updates in {}'.format(req['name']))


def print_updates(files):
    # print the requirements files.
    for req in files:
        output(req)


def match_versions(frozen, files, unreqed):
    for package, version in frozen:
        found = False
        for req in files:
            if package in req['packages']:
                if req['packages'][package] != version:
                    click.echo(
                        '{} specifies version {} of {}, the installed version is {}'.format(
                            req['name'], req['packages'][package], package, version))
                    value = click.prompt(
                        """[1] Update {}\n[2] Keep existing value\n""".format(req['name']),
                        type=int
                    )
                    if value == 1:
                        req['packages'][package] = version
                        req['updated'].append(package)
                    elif value == 2:
                        pass
                found = True

        if found is False:
            unreqed.append({
                package: version
            })


def check_uninstalled(frozen, files):
    installed = []
    reqed = []
    for k, v in frozen:
        installed.append(k)
    for reqs in files:
        for k, v in reqs['packages'].items():
            reqed.append(k)

    uninstalled = list(set(reqed) - set(installed))
    click.echo(
        click.style(
            "The following packages are in your requirements but not installed.", fg='red'))
    click.echo(click.style('\n'.join(uninstalled), fg='red'))
    return uninstalled


def add_installed(files, unreqed):
    unique = [dict(y) for y in set(tuple(x.items()) for x in unreqed)]
    for package_d in unique:
        for package, version in package_d.items():
            click.echo(
                '{} is installed but not in any requirements file'.format(
                    package))
            pstr = '[0] Ignore\n'
            for index, rf in enumerate(files):
                pstr += '[{}] Add to {}\n'.format(index + 1, rf['name'])
            value = click.prompt(pstr, type=int)
            try:
                req_file = files[value - 1]
            except IndexError:
                click.echo('Not a valid selection soz.')
            else:
                req_file['packages'][package] = version
                req_file['updated'].append(package)


def pipfreeze():
    frozen = []
    try:
        packages = subprocess.check_output(["pip", "freeze"])
    except subprocess.CalledProcessError as e:
        click.echo('Error with pip freeze: {}'.format(e))
    else:
        for line in packages.splitlines():
            if line.startswith('-e '):
                package, version = (line.strip(), '')
                frozen.append((package, version))
            elif not line.startswith('## FIXME:'):
                package, version = line.strip().split('==')
                frozen.append((package, version))

        return frozen


def jam(filename):
    packages = {}
    try:
        with open(filename, 'r') as infile:
            infile.seek(0)
            for line in infile.readlines():
                if line.startswith('-e '):
                    package, version = (line.strip(), '')
                    packages[package] = version
                elif '==' in line:
                    package, version = line.strip().split('==')
                    packages[package] = version
                else:
                    packages[line.strip()] = 'latest'

    except IOError:
        click.echo('File {} not found.'.format(filename))

    infile.close()
    return packages


def rewrite(req):
    try:
        with open(req['name'], 'w') as outfile:
            outfile.seek(0)
            outfile.truncate()
            packages = collections.OrderedDict(sorted(req['packages'].items()))
            for k, v in packages.items():
                outfile.write('{}\n'.format(lineout(k, v)))
    except IOError:
        click.echo('File {} not found.'.format(req['name']))

    outfile.close()
    click.echo('Updated {} with packages \n\t{}'.format(
        req['name'], '\n\t'.join(req['updated'])))


def output(req):
    click.echo('\n')
    click.echo('#' * 80)
    click.echo('# {}'.format(req['name']))
    click.echo('#' * 80)
    packages = collections.OrderedDict(sorted(req['packages'].items()))
    for k, v in packages.items():
        if k not in req['updated']:
            click.echo(lineout(k, v))
        else:
            click.echo(click.style(lineout(k, v), fg='green'))
    click.echo('\n')


def lineout(package, version):
    if package.startswith('-e ') or version == 'latest':
        return package
    else:
        return '{}=={}'.format(package, version)
