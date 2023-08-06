"""Extract script.

Read an import script and a list of downloaded filenames or directories of
downloaded files, and for each of those files, extract transactions from it.
"""
__author__ = "Martin Blais <blais@furius.ca>"

import itertools
import sys
import textwrap

from beancount.core import data
from beancount.parser import printer
from beancount.ingest import similar
from beancount.ingest import identify
from beancount.ingest import scripts_utils
from beancount.ingest import cache
from beancount import loader


HEADER = '; -*- mode: org; mode: beancount; coding: utf-8; -*-\n'


DUPLICATE_META = '__duplicate__'


def extract_from_file(filename, importer, existing_entries=None, min_date=None):
    """Import entries from file 'filename' with the given matches,

    Also cross-check against a list of provided 'existing_entries' entries,
    de-duplicating and possibly auto-categorizing.

    Args:
      filename: The name of the file to import.
      importer: An importer object that matched the file.
      existing_entries: A list of existing entries parsed from a ledger, used to
        detect duplicates and automatically complete or categorize transactions.
      min_date: A date before which entries should be ignored. This is useful
        when an account has a valid check/assert; we could just ignore whatever
        comes before, if desired.
    Returns:
      A list of new imported entries and a subset of these which have been
      identified as possible duplicates.
    """
    # Extract the entries.
    file = cache.FileMemo(filename)
    new_entries = importer.extract(file)
    if not new_entries:
        return [], []

    # Make sure the newly imported entries are sorted; don't trust the importer.
    new_entries.sort(key=data.entry_sortkey)

    # Ensure that the entries are typed correctly.
    for entry in new_entries:
        data.sanity_check_types(entry)

    # Filter out entries with dates before 'min_date'.
    if min_date:
        new_entries = list(itertools.dropwhile(lambda x: x.date < min_date,
                                               new_entries))

    # Find potential matching entries.
    duplicate_entries = []
    if existing_entries is not None:
        duplicate_pairs = similar.find_similar_entries(new_entries, existing_entries)
        duplicate_set = set(id(entry) for entry, _ in duplicate_pairs)

        # Add a metadata marker to the extracted entries for duplicates.
        mod_entries = []
        for entry in new_entries:
            if id(entry) in duplicate_set:
                marked_meta = entry.meta.copy()
                marked_meta[DUPLICATE_META] = True
                entry = entry._replace(meta=marked_meta)
                duplicate_entries.append(entry)
            mod_entries.append(entry)
        new_entries = mod_entries

    return new_entries, duplicate_entries


def print_extracted_entries(importer, entries, output):
    """Print the entries for the given importer.

    Args:
      importer: An importer object that matched the file.
      entries: A list of extracted entries.
      output: A file object to write to.
    """
    # Print the filename and which modules matched.
    pr = lambda *args: print(*args, file=output)
    pr('')
    pr(';; {}'.format(importer.name()))
    pr('')

    # Print out the entries.
    for entry in entries:
        # Check if this entry is a dup, and if so, comment it out.
        if DUPLICATE_META in entry.meta:
            meta = entry.meta.copy()
            meta.pop(DUPLICATE_META)
            entry = entry._replace(meta=meta)
            entry_string = textwrap.indent(printer.format_entry(entry), '; ')
        else:
            entry_string = printer.format_entry(entry)
        pr(entry_string)


def extract(importer_config,
            files_or_directories,
            output,
            entries=None,
            mindate=None):
    """Given an importer configuration, search for files that can be imported in the
    list of files or directories, run the signature checks on them, and if it
    succeeds, run the importer on the file.

    A list of entries for an existing ledger can be provided in order to perform
    de-duplication and a minimum date can be provided to filter out old entries.

    Args:
      importer_config: A list of (regexps, importer) pairs, the configuration.
      files_or_directories: A list of strings, filenames or directories to be processed.
      output: A file object, to be written to.
      entries:
      mindate:
    """
    output.write(HEADER)
    for filename, importers in identify.find_imports(importer_config, files_or_directories,
                                                     output):
        for importer in importers:
            # Import and process the file.
            new_entries, duplicate_entries = extract_from_file(filename,
                                                               importer,
                                                               entries,
                                                               mindate)
            if not new_entries and not duplicate_entries:
                continue

            print_extracted_entries(importer, new_entries, output)


def main():
    parser = scripts_utils.create_arguments_parser("Extract transactions from downloads")

    parser.add_argument('-e', '--existing', '--previous', metavar='BEANCOUNT_FILE',
                        default=None,
                        help=('Beancount file or existing entries for de-duplication '
                              '(optional)'))

    args, config, downloads_directories = scripts_utils.parse_arguments(parser)

    # Load the ledger, if one is specified.
    if args.existing:
        entries, _, _ = loader.load_file(args.existing)
    else:
        entries = None

    extract(config, downloads_directories, sys.stdout,
            entries=entries,
            mindate=None)
