"""
This file contains functions to deal with Bibtex files and edit them.

TODO: Unittests + use bibtexparser writer
"""
import bibtexparser
import re

from codecs import open
from libbmc import tools


default_papers_filename_mask = "{first}_{last}-{journal}-{year}{arxiv_version}"
default_books_filename_mask = "{authors} - {title}"


def dict2BibTeX(data):
    """
    Convert a single BibTeX entry dict to a BibTeX string.

    :param data: A dict representing BibTeX entry, as the ones from \
            ``bibtexparser`` output.
    :return: A formatted BibTeX string.
    """
    bibtex = '@' + data['ENTRYTYPE'] + '{' + data['ID'] + ",\n"

    for field in [i for i in sorted(data) if i not in ['ENTRYTYPE', 'ID']]:
        bibtex += "\t" + field + "={" + data[field] + "},\n"
    bibtex += "}\n"
    return bibtex


def write(filename, data):
    """
    Create a new BibTeX file.

    :param filename: The name of the BibTeX file to write.
    :param data: A list of dict representing BibTeX entries, as the ones from \
            ``bibtexparser`` output.
    """
    bibtex = "\n".join([dict2BibTeX(i) for i in data])
    with open(filename, 'w', encoding='utf-8') as fh:
        fh.write(bibtex)


def append(filename, data):
    """
    Append some entries to a bibtex file.

    :param filename: The name of the BibTeX file to edit.
    :param data: A list of dict representing BibTeX entries, as the ones from \
            ``bibtexparser`` output.
    """
    with open(filename, 'a', encoding="utf-8") as fh:
        fh.write("\n".join([dict2BibTeX(i) for i in data]))


def edit(filename, identifier, data):
    """
    Update an entry in a BibTeX file.

    :param filename: The name of the BibTeX file to edit.
    :param identifier: The id of the entry to update, in the BibTeX file.
    :param data: A dict associating fields and updated values. Fields present \
            in the BibTeX file but not in this dict will be kept as is.
    """
    # Get current bibtex
    with open(filename, 'r', encoding="utf-8") as fh:
        bibtex = bibtexparser.load(fh)
    bibtex = bibtex.entries_dict

    # Update it
    for k in data:
        bibtex[identifier][k] = data[k]

    # Write the resulting BibTeX
    write(filename, bibtex)


def replace(filename, identifier, data):
    """
    Replace an entry in a BibTeX file.

    :param filename: The name of the BibTeX file to edit.
    :param identifier: The id of the entry to replace, in the BibTeX file.
    :param data: A dict representing a BibTeX entry, as the one from \
            ``bibtexparser`` output.
    """
    # Get current bibtex
    with open(filename, 'r', encoding="utf-8") as fh:
        bibtex = bibtexparser.load(fh)
    bibtex = bibtex.entries_dict

    # Update the bibtex
    bibtex[identifier] = data

    # Write the resulting BibTeX
    write(filename, bibtex)


def delete(filename, identifier):
    """
    Delete an entry in a BibTeX file.

    :param filename: The name of the BibTeX file to edit.
    :param identifier: The id of the entry to delete, in the BibTeX file.
    """
    # Get current bibtex
    with open(filename, 'r', encoding="utf-8") as fh:
        bibtex = bibtexparser.load(fh)
    bibtex = bibtex.entries_dict

    # Delete the bibtex entry
    try:
        del(bibtex[identifier])
    except KeyError:
        pass

    # Write the resulting BibTeX
    write(filename, bibtex)


def get(filename, ignore_fields=[]):
    """
    Get all entries from a BibTeX file.

    :param filename: The name of the BibTeX file.
    :param ignore_fields: An optional list of fields to strip from the BibTeX \
            file.

    :returns: A list of ``bibtexparser`` dicts representing the fetched \
            entries.
    """
    # Open bibtex file
    with open(filename, 'r', encoding="utf-8") as fh:
        bibtex = bibtexparser.load(fh)
    bibtex = bibtex.entries_dict

    # Clean the entry dict if necessary
    bibtex = [{k: entry[k] for k in entry if k not in ignore_fields}
              for entry in bibtex]

    return bibtex


def get_entry_by_filter(filename, filter, ignore_fields=[]):
    """
    Get an entry from a BibTeX file.

    :param filename: The name of the BibTeX file.
    :param filter: A function returning ``True`` or ``False`` whether the \
            entry should be included or not.
    :param ignore_fields: An optional list of fields to strip from the BibTeX \
            file.

    :returns: A ``bibtexparser.BibDatabase`` object representing the \
            first matching entry. ``None`` if entry was not found.
    """
    # Open bibtex file
    with open(filename, 'r', encoding="utf-8") as fh:
        bibtex = bibtexparser.load(fh)
    bibtex = bibtex.entries

    matching_entry = None
    try:
        # Try to fetch the matching entry dict
        for entry in bibtex.items:
            if filter(entry):
                matching_entry = entry
    except KeyError:
        # If none found, return None
        return None

    # Clean the entry dict if necessary
    matching_entry = {k: matching_entry[k]
                      for k in matching_entry if k not in ignore_fields}

    return matching_entry


def get_entry(filename, identifier, ignore_fields=[]):
    """
    Get an entry from a BibTeX file.

    :param filename: The name of the BibTeX file.
    :param identifier: An id of the entry to fetch, in the BibTeX file.
    :param ignore_fields: An optional list of fields to strip from the BibTeX \
            file.

    :returns: A ``bibtexparser.BibDatabase`` object representing the \
            fetched entry. ``None`` if entry was not found.
    """
    return get_entry_by_filter(filename,
                               lambda x: x["ID"] == identifier,
                               ignore_fields)


def to_filename(bibtex, mask=default_papers_filename_mask):
    """
    Convert a bibtex entry to a formatted filename according to a given mask.

    .. note ::

        Available masks out of the box are:
            - ``journal``
            - ``title``
            - ``year``
            - ``first`` for the first author
            - ``last`` for the last author
            - ``authors`` for the list of authors
            - ``arxiv_version`` (discarded if no arXiv version in the BibTeX)

        Filename is slugified after applying the masks.

    :param bibtex: A dict representing a BibTeX entry, as the one from \
            ``bibtexparser`` output.
    :param mask: A Python format string.

    :returns: A formatted filename.
    """
    authors = re.split(' and ', bibtex['author'])

    filename = mask
    filename = filename.format(journal=bibtex.get("journal", default=""))
    filename = filename.format(title=bibtex.get("title", default=""))
    filename = filename.format(year=bibtex.get("year", default=""))

    filename = filename.format(first=authors[0].split(',')[0].strip())
    filename = filename.format(last=authors[-1].split(',')[0].strip())
    filename = filename.format(authors=", ".join(
        [i.split(',')[0].strip() for i in authors]))

    arxiv_version = ""
    if "eprint" in bibtex:
        arxiv_version = '-' + bibtex['eprint'][bibtex['eprint'].rfind('v'):]
    filename = filename.format(arxiv_version=arxiv_version)

    return tools.slugify(filename)
