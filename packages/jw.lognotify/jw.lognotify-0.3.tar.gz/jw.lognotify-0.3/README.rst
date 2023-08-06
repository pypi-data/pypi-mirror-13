Lognotify
=========

This is yet another real-time log scanner done for the ever reoccurring reason of failure to find an existing suitable
tool.

Features
--------

* simple, yet flexible configuration in the `YAML <http://yaml.org>`_ format
* actions programmable in Python, Tcl or Bash
* log rotation detection
* variable leading log context for every event
* burst mode: collect events within a certain time frame and report them together

Configuration
-------------

Lognotify reads a configuration file specified on the command line with the ``--config`` or ``-c`` option. The
configuration specifies what content to search for and what to do if some is found in the log.

Overview
........

Consider this example::

    when:
        - error
        - problem
        - critical
        - fatal
        - bad
        -
            - not
            - ^perl
            - ^/pascal/i
    do:
        python: |
            if logfile:
                print(logfile, messages[-1][-1])
        burst: 2
    ---
    when:
        - strange
    do: |
        echo $logfile: ${message[-1]}

A configuration can have one ore more sections, denoted by a ``---`` delimiting line. Each section specifies what to
look for and what to do if something interesting is found.

Sections
........

Each section consists of a `when` clause and a `do` clause. For every line from a logfile, all sections are checked for
matching search expressions in the `when` clause.  When a match is found for a section, the corresponding `do` clause
is executed.

`When` clause
.............

The `when` clause contains an itemized list of expressions to searche for in every incoming line from the log.
Variations in syntax specify how to search for the item. The expressions are tried in order. As soon as a match is
found, the `do` clause is executed and processing of this particular section is terminated.

The `when` list forms an `OR`-expression. Within the list, sublists may specify `AND`-expressions. Thus ::

    - expr1
    -
        - expr2a
        - expr2b

means ::

    expr1 OR (expr2a AND expr2b)

Groups can be infinitely nested. The general rule is that every group within an `OR` group is an `AND` group and vice
versa.

Search expressions
..................

A search expression can have one of the following forms:

**word**
    Search for `word` irrespective of case and match only at word boundaries. Thus ``error`` matches in the following
    lines:

        Error: invalid syntax

        An error occurred.

        No error-checking enabled.

    but *not* in:

        No errorchecking.

        maxerror

    If you want to match irrespective of word boundaries, you have to use regular expressions (see below).

**/word/[flags]**
    Search for a `regular expression <https://docs.python.org/2/library/re.html>`_. Some flags for altering the
    operation are available:

    *i*
        match case insensitive. See `IGNORECASE <https://docs.python.org/2/library/re.html#re.IGNORECASE>`_.

    *m*
        match in multi-line mode. Probably not very useful. See
        `MULTILINE <https://docs.python.org/2/library/re.html#re.MULTILINE>`_.

    *l*
        match according to the current locale. See
        `LOCALE <https://docs.python.org/2/library/re.html#re.LOCALE>`_.

    *s*
        make '.' match any character, including newline. See
        `DOTALL <https://docs.python.org/2/library/re.html#re.DOTALL>`_.

    *u*
        match according to the Unicode character properties table. See
        `UNICODE <https://docs.python.org/2/library/re.html#re.UNICODE>`_.

    *x*
        parse verbose regex with comments and white space. See
        `VERBOSE <https://docs.python.org/2/library/re.html#re.VERBOSE>`_.

All these expressions can be prefixed with a caret (``^``) to mean "do not match word":

**^word**

**^/word/**

.. note::

    Since the whole configuration is expressed in YAML, strings containing certain characters must be quoted in order
    not to interfere with the YAML syntax. These characters are: ``[ ] { } ! " ' : ? % @ , - # ~ | > * &``. Also,
    certain words have special meaning in YAML and must therefore also be quoted: ``yes``, ``no``, ``on``, ``off``,
    ``true``, ``false``, and ``null``.

Pitfalls
........

The search algorithm gives rise to surprises in certain constellations. One common error is to request something
like this::

    -
        - not
        - ^this
    -
        - not
        - ^that

where `^this` and `^that` cancel each other out. If a line contains 'not' it will always match, no matter whether `this`
or `that` occurs in the line. The proper way would be ::

    -
        - not
        - ^this
        - ^that

The most common pattern is to search for any line containing `word1`, `word2` or `word3` but not `except1` or `except2`.
You might be inclined to write this as ::

    - word1
    - word2
    - word3
    -
        - ^except1
        - ^except2

But this would not work. The way to do it goes along the follong lines: written as a logical expression, it would be ::

    (word1 OR word2 OR word3) AND (NOT except1 OR NOT except2)

which translates to ::

    (word1 OR word2 OR word3) AND NOT except1 AND NOT except2

which, expressed as list operations, translates to ::

    AND(OR(word1, word2, word3), NOT(except1), NOT(except2))

We have therefore an `AND` list on top. However, in lognotify we start out in an `OR` list. We therefore have to put our
`AND` list as the single element into the top `OR` list. The final result would be ::

    # OR list
    -
        # AND list
        -
            # OR list
            - word1
            - word2
            - word3
        - ^except1
        - ^except2

`Do` clause
...........

The `do` clause specifies what action to take when one of the expressions in the `when` clause matches. To run commands
on the selected logfile lines, `Python <http://python.org>`_, `bash` or `Tcl <http://tcl.tk>`_ can be used. Some
variables are injected, depending on the language used. Scripts receive one or more events at a time depending on
whether context and/or burst mode was requested. If neither context not burst mode is requested, one single line is
reported at a time.

.. note::

    Use the pipe character at the end of a line prior to the code block to cause YAML to process the following indented
    block without interpretation, leaving line endings intact (see the examples below).

Context
'''''''

Context is a number of lines running up to the actual log event line. It can be requested with the ``--config``/``-C``
flag. Context lines are marked with a ``True`` value in `Python` or `Tcl` or a value of 1 in `bash` or `sh` to
distinguish them from log lines. However, if a context line is also a regular log line (appearing because it is part of
a burst) it is not marked as such.

Burst mode
''''''''''

In burst mode, log lines arriving within a certain time frame are kept together and appear in the same call. Burst mode
can be requested either as a `burst` specifier in a `do` clause or with a ``--burst`` or ``--force-burst`` command line
flag. Good values for burst time frames are between 2 and 5 seconds. The ``--force-burst`` flag overrides values
specified in `do` clauses while ``--burst`` does not.

Python
''''''

`Python` code can be one block or be split into an initialization section and a runtime section. The former is executed
once at startup and is intended to contain stuff like ``import`` statements, function definitions and the like. The
latter is run for every event.

In `Python`, the following variables are available:

**logfile**
    A string containing the path of the logfile where the event was coming from
**messages**
    A list of tuples. For each event the tuple contains:
        - a bool which is True if the entry is a context line
        - the sequence number
        - a float with a timestamp
        - a string with the message text

Example (assuming Python3 syntax)::

    do:
        python: |
            for msg in messages:
                print('%s: %s' % (logfile, msg[3]))

Example with initialization (assuming Python3 syntax)::

    python:
        - |
            # Setup UDP socket
            import sys
            import socket
            sock = socket.socket(type=socket.SOCK_DGRAM)
            sock.connect(('127.0.0.1', 7777))
        - |
            # Write stuff to UDP socket
            for msg in messages:
                sock.send('json:{}\n'.format(msg[3].replace(r'\n', ' ')).encode('u8'))

Tcl
'''

`Tcl` code can be one block or be split into an initialization section and a runtime section. The former is executed
once at startup and is intended to contain stuff like ``proc`` statements. The latter is run for every
event.

In `Tcl`, the following variables are available:

**logfile**
    The path of the logfile where the event was coming from
**messages**
    A list of lists. For each event the inner list contains:
        - a bool which is True if the entry is a context line
        - the sequence number
        - an int with a timestamp
        - a string with the message text

Example::

    do:
        tcl: |
            foreach m $messages {
                puts "$logfile: [clock format [expr int([lindex $m 2])]] [lindex $m 3]"
            }

Example with initialization::

    do:
        tcl:
            - |
                proc output {m} {
                    puts $m
                }
            - |
                foreach m $messages {
                    output "$logfile: [clock format [expr int([lindex $m 2])]] [lindex $m 3]"
                }

Bash and sh
'''''''''''

In `bash` and `sh`, the following variables are available:

**logfile**
    The path of the logfile where the event was coming from
**iscontext**
    An array with an int for every line where 1 means it is a context line or 0 otherwise
**seqno**
    An array containing the sequence number for every line
**time**
    An array containing the timestamp in ISO format for every line
**message**
    An array containing the text for every line

Example::

    do:
        bash: |
            echo $logfile: ${time[-1]} ${message[-1]}

But since `bash` is the default language, it can be written as::

    do: |
        echo $logfile: ${message[-1]}

The `do` clause can be omitted altogether in which case a default of ::

    do:
        python: |
            for msg in messages:
                print('%s: %s' % (logfile, msg[3]))

is assumed.

Running
-------

Command synopsis:
    ``lognotify`` [-h] --config `CONFIG` [--full]
        [--burst `BURST` | --force-burst `FORCE_BURST`]
        [--context `CONTEXT`] [--debug] [--version]
        logfile [logfile ...]

Positional arguments:
    `logfile`
        A log file to scan

Optional arguments:
    -h, --help                  show this help message and exit
    --config CONFIG, -c CONFIG  specify config file
    --full, -f                  scan files from beginning
    --burst BURST, -b BURST     report bursts of BURST seconds together
    --force-burst FORCE_BURST, -B FORCE_BURST
                                force reporting bursts of BURST seconds together
    --context CONTEXT, -C CONTEXT
                                specify context size
    --debug, -d                 Print some debug information to stderr
    --version, -v               display version and exit

At least one path to an existing, readable log file is expected.

The ``--full`` or ``-f`` option requests reading files from the start. Without the flag, reading begins at the current
end of file. Sequence numbering always begins from the point where reading begins.

The ``--debug`` or ``-d`` option sends information to the standard error file. Repeating the flag increases the
amount of information.

Useful scripts
--------------

This section is a collection of useful scripts.

Send desktop notification
.........................

To be used as root (change ``'username'`` accordingly)::

    from subprocess import check_call

    check_call(
        [
            'su', 'username', '-c',
            'DISPLAY=:0 notify-send "%s" "%s"' % (logfile, '\n'.join('> '[m[0]] + m[3] for m in messages))
        ]
    )

Send desktop notification to remote machine
...........................................

To be used as root (change ``'hostname'`` and ``username`` accordingly)::

    from subprocess import check_call
    from platform import node

    check_call(
        [
            'ssh', 'hostname',
            r'su username -c "DISPLAY=:0 notify-send \"%s: %s\" \"%s\""' % (
                node(),
                logfile,
                '\n'.join('! '[m[0]] + m[3] for m in messages)
            )
        ]
    )

Send e-mail
...........

Change ``'mail-user'``, ``'mail-user-password'``, ``source-email`` and ``destination-email`` accordingly::

    do:
        python: |
            from smtplib import SMTP
            import sys

            client = SMTP('localhost')
            try:
                client.starttls()
            except:
                pass
            client.login('mail-user', 'mail-user-password')
            client.sendmail(
                'source-email',
                'destination-email',
                'From: source-email\n'
                'To: destination-email\n'
                'Subject: Message in %s\n\n'
                '%s\n' % (logfile, '\n'.join('> '[m[0]] + m[3] for m in messages))
            )

