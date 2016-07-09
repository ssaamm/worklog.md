==========
worklog.md
==========

A plain text system for keeping track of how long you work.

The format looks like this:

.. code::

    # Week 1

    ## 13 Jun 2016
    - Start @ 10:00
    - Lunch 12:00-13:00
    - Stop @ 18:00

    - Begin new job
    - Set up computer

    ## 14 Jun 2016
    - Start @ 8:30
    - Lunch 12:00-12:30
    - Stop @ 17:00

    - Fix calendar display error

    # Week 2

    ## 20 Jun 2016
    - Start @ 7:30
    - Lunch 11:00-11:30
    - Stop @ 16:00

    - Respond to code review

Installation
------------

.. code:: bash

    pip3 install worklogmd

You'll probably also want the `wl` bash command, which you can get by running
`printWorklogFunction` and appending the output to your Bash configuration
(`.bashrc` or `.bash_profile`, depending on OS).

Usage
-----

When you want to interact with your Worklog, type `wl` and modify the file.

A simple tool which will report on the number of hours you've worked each day
(`processWorklog worklog.md`) or each week (`processWorklog worklog.md -w`).
