# -*- coding: utf-8 -*-
import os
import io
import json
import argparse

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


class DictObject:
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, DictObject(value))
            else:
                setattr(self, key, value)


def update_database(config):
    output = io.StringIO()

    for import_path in config.hosts.import_files:
        read_import_file(output, os.path.abspath(import_path))

    for import_url in config.base:
        print('reading data from %s' % import_url)
        output.write('\n# %s \n\n' % import_url)
        try:
            with urlopen(import_url) as fd:
                for chunk in iter(lambda: fd.read(8192), b''):
                    output.write(chunk.decode())
        except IOError:
            print('Can\'t load data of %s' % import_url)

    output.seek(0)
    with open(os.path.abspath(config.hosts.dest), 'wt') as fd:
        for chunk in iter(lambda: output.read(8192), ''):
            fd.write(chunk)


def read_import_file(output, import_file):
    with open(import_file, 'rt') as fd:
        for chunk in iter(lambda: fd.read(8192), ''):
            output.write(chunk)


def boot(config, force_upadte):
    try:
        with open(config, 'rt') as fdconfig:
            config = DictObject(json.loads(fdconfig.read()))
            dest_path = os.path.abspath(config.hosts.dest)
            if not force_upadte and os.path.exists(config.hosts.dest):
                print('system updated')
            else:
                update_database(config)
    except IOError as e:
        print('Can\'t load configuration file.')
        raise e
    except Exception as e:
        print(e.message)


def main():
    parse = argparse.ArgumentParser('adblockd')

    parse.add_argument(
        '-c',
        '--config',
        help='configuration file',
        required=True
    )

    parse.add_argument(
        '-u',
        '--update',
        help='sign for update block list.',
        action="store_true"
    )

    opts = parse.parse_args()
    config_path = os.path.abspath(opts.config)
    if os.path.exists(config_path):
        boot(config_path, force_upadte=opts.update)
    else:
        print('err')


if __name__ == '__main__':
    main()
