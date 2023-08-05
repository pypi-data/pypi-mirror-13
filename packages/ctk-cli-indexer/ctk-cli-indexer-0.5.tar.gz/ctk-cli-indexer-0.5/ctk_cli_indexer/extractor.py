import os, re, sys

INDEX_ATTRIBUTES = 'name title version category description contributor acknowledgements documentation_url license'.split()

def extract_cli_properties(exe_filename):
    import ctk_cli

    cli = ctk_cli.CLIModule(exe_filename)

    timestamp = os.path.getmtime(exe_filename)
    doc = dict((attr, getattr(cli, attr))
               for attr in INDEX_ATTRIBUTES)

    authors = re.sub(r'\([^)]*\)', '', cli.contributor) if cli.contributor else ""
    doc['authors'] = [author.strip() for author in re.split(r' *, *(?:and *)?| +and +', authors)
                      if not author.startswith('http://') or re.search('@| -at- ', author)]
    
    doc['group_count'] = len(cli)
    doc['group_labels'] = '\n'.join(group.label for group in cli if group.label)
    doc['advanced_group_count'] = sum(group.advanced for group in cli)
    doc['parameter_count'] = sum(len(group) for group in cli)
    doc['parameter_names'] = '\n'.join(p.name for p in cli.parameters() if p.name)
    doc['parameter_labels'] = '\n'.join(p.label for p in cli.parameters() if p.label)

    return timestamp, doc


def listCLIExecutables(paths):
    import ctk_cli

    for path in paths:
        if os.path.isdir(path):
            for exe_filename in ctk_cli.listCLIExecutables(path):
                yield exe_filename
        elif ctk_cli.isCLIExecutable(path):
            yield path


def _scan_directories_helper(base_directories, verbose, skip_errors):
    errors = []
    documents = []

    for exe_filename in listCLIExecutables(base_directories):
        if verbose:
            sys.stderr.write('processing %s...\n' % (os.path.basename(exe_filename), ))
        try:
            timestamp, doc = extract_cli_properties(exe_filename)
        except Exception, e:
            sys.stderr.write('ERROR (skipping %s): %s\n' % (os.path.basename(exe_filename), e))
            errors.append(exe_filename)
            continue
        documents.append((timestamp, doc))

    return errors, documents


def scan_directories(base_directories, verbose = True):
    errors, documents = _scan_directories_helper(base_directories, verbose, skip_errors = False)
    return documents


def try_scan_directories(base_directories, verbose = True):
    """Like scan_directories(), but will skip errors.  Returns a tuple (errors, documents)
    where errors is a list of cli executables whose XML could not be parsed."""
    errors, documents = _scan_directories_helper(base_directories, verbose, skip_errors = True)
    return errors, documents
