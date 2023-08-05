#!/usr/bin/env python
#  Copyright 2014 Hans Meine <hans_meine@gmx.net>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys, os, argparse, logging
import simplejson
from ctk_cli_indexer.extractor import try_scan_directories

class VerboseErrorParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help(sys.stderr)
        sys.exit(2)


def extract(args):
    errors, docs = try_scan_directories(args.base_directory)
    simplejson.dump(docs, args.json_filename, indent = '  ')
    args.json_filename.write('\n')
    if errors:
        sys.stderr.write('%d CLI executables had fatal errors and were excluded from the output.\n' % (len(errors), ))

def index(args):
    # local imports, so that we can extract without elasticsearch being available
    # (and index without ctk_cli being available)
    import elasticsearch
    from ctk_cli import isCLIExecutable
    from ctk_cli_indexer.indexer import create_elasticsearch_index, update_elasticsearch_index

    if len(args.path) == 1 and not (os.path.isdir(args.path[0]) or isCLIExecutable(args.path[0])):
        with file(args.path[0]) as f:
            docs = simplejson.load(f)
    else:
        docs = scan_directories(args.path)

    # TODO: at the moment, the commandline is limited to *one* host/port, and no SSL or URL prefix
    es = elasticsearch.Elasticsearch([dict(host = args.host, port = args.port)])

    create_elasticsearch_index(es)

    update_elasticsearch_index(es, docs, args.source_name)

def main():
    parser = VerboseErrorParser(description = 'index CLI modules in elasticsearch database')

    logging.basicConfig()
    
    commands = parser.add_subparsers()
    extractor_parser = commands.add_parser(
        'extract', help = 'only create JSON description from CLI modules (no DB access)')
    extractor_parser.add_argument(
        'base_directory', nargs = '+',
        help = 'directories (at least one) in which to search for CLI module executables, '
        'or direct paths to executables')
    extractor_parser.add_argument(
        '--json_filename', '-o', type = argparse.FileType('w'), default = sys.stdout)
    extractor_parser.set_defaults(action = extract)


    index_parser = commands.add_parser(
        'index', help = 'update elasticsearch index (given CLI modules or JSON description)')
    index_parser.add_argument('--host', default = 'localhost',
                              help = 'hostname elasticsearch is listening on (default: localhost)')
    index_parser.add_argument('--port', default = 9200,
                              help = 'port elasticsearch is listening on (default: 9200)')

    index_parser.add_argument(
        'source_name', help = "identifier for the source "
        "(e.g. 'slicer' or 'nifty-reg') of this set of CLI modules "
        "(will be used to remove old documents from this source "
        "from the Elasticsearch index if they are no longer present)")
    index_parser.add_argument(
        'path', nargs = '+',
        help = 'one or more directories in which to search for CLI module executables, '
        'paths to CLI executables, or (exactly one) JSON file as created by `extract` subcommand')

    index_parser.set_defaults(action = index)


    args = parser.parse_args()
    args.action(args)


if __name__ == '__main__':
    main()
