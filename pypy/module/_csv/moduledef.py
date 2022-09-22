from pypy.interpreter.mixedmodule import MixedModule


class Module(MixedModule):
    """CSV parsing and writing.

This module provides classes that assist in the reading and writing
of Comma Separated Value (CSV) files, and implements the interface
described by PEP 305.  Although many CSV files are simple to parse,
the format is not formally defined by a stable specification and
is subtle enough that parsing lines of a CSV file with something
like line.split(\",\") is bound to fail.  The module supports three
basic APIs: reading, writing, and registration of dialects.


DIALECT REGISTRATION:

Readers and writers support a dialect argument, which is a convenient
handle on a group of settings.  When the dialect argument is a string,
it identifies one of the dialects previously registered with the module.
If it is a class or instance, the attributes of the argument are used as
the settings for the reader or writer:

    class excel:
        delimiter = ','
        quotechar = '\"'
        escapechar = None
        doublequote = True
        skipinitialspace = False
        lineterminator = '\\r\\n'
        quoting = QUOTE_MINIMAL

SETTINGS:

    * quotechar - specifies a one-character string to use as the 
        quoting character.  It defaults to '\"'.
    * delimiter - specifies a one-character string to use as the 
        field separator.  It defaults to ','.
    * skipinitialspace - specifies how to interpret whitespace which
        immediately follows a delimiter.  It defaults to False, which
        means that whitespace immediately following a delimiter is part
        of the following field.
    * lineterminator -  specifies the character sequence which should 
        terminate rows.
    * quoting - controls when quotes should be generated by the writer.
        It can take on any of the following module constants:

        csv.QUOTE_MINIMAL means only when required, for example, when a
            field contains either the quotechar or the delimiter
        csv.QUOTE_ALL means that quotes are always placed around fields.
        csv.QUOTE_NONNUMERIC means that quotes are always placed around
            fields which do not parse as integers or floating point
            numbers.
        csv.QUOTE_NONE means that quotes are never placed around fields.
    * escapechar - specifies a one-character string used to escape 
        the delimiter when quoting is set to QUOTE_NONE.
    * doublequote - controls the handling of quotes inside fields.  When
        True, two consecutive quotes are interpreted as one during read,
        and when writing, each quote character embedded in the data is
        written as two quotes.
"""

    appleveldefs = {
        'register_dialect':   'app_csv.register_dialect',
        'unregister_dialect': 'app_csv.unregister_dialect',
        'get_dialect':        'app_csv.get_dialect',
        'list_dialects':      'app_csv.list_dialects',
        '_dialects':          'app_csv._dialects',

        'Error':              'app_csv.Error',
        }

    interpleveldefs = {
        '__version__':      'space.wrap("1.0")',

        'QUOTE_MINIMAL':    'space.wrap(interp_csv.QUOTE_MINIMAL)',
        'QUOTE_ALL':        'space.wrap(interp_csv.QUOTE_ALL)',
        'QUOTE_NONNUMERIC': 'space.wrap(interp_csv.QUOTE_NONNUMERIC)',
        'QUOTE_NONE':       'space.wrap(interp_csv.QUOTE_NONE)',

        'Dialect': 'interp_csv.W_Dialect',

        'reader': 'interp_reader.csv_reader',
        'field_size_limit': 'interp_reader.csv_field_size_limit',

        'writer': 'interp_writer.csv_writer',
        }