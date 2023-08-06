cfgtool
=======

A configuration management tool that provides for self-documenting hosts
and coherently versioned configurations.

What does ``cfgtool`` do?
-------------------------

``cfgtool`` allows applications to separate their configuration files
from the host specific values that go into those files. These values,
called *beliefs*, can be deployed either by hand or by common
infrastructure orchistration tools `SaltStack <http://saltstack.com/>`__
or `Ansible <http://www.ansible.com/>`__.

Disclaimer
----------

While ``cfgtool`` shouldn't have any issue running on most Linux
distributions, it has only been tested on Debian based Linux systems.

How do I get it?
----------------

``cfgtool`` can be installed via ``pip``. It should be included as a
dependency for each application you install that is expected to have its
configuration managed by it.

::

    pip install cfgtool

How does it work?
-----------------

Upon installation (assuming with root permissions), ``cfgtool`` creates
the following configuration file and directories.

::

    /etc/cfgtool/cfgtool.conf
    /etc/cfgtool/module.d/
    /etc/cfgtool/belief.d/

``module.d`` contains a file for each installed application using
``cfgtool``. This file contains a list of configuration files we expect
``cfgtool`` to generate for that application. Each of these
configuration files is expected to have a corresponding ``.templ`` file
at the same directory as it is going to be installed.

Example:

::

    /etc/my_application/application.conf
    /etc/my_application/application.conf.templ

The ``.templ`` file is the template configuration file it will seed with
beliefs to generate the actual configuration file.

``belief.d`` contains JSON files, which hold our *beliefs* used in
generating application configurations.

We can change the locations of our ``module.d`` and ``belief.d``
directory in our ``cfgtool.conf`` file if we wish.

::

    belief_dir = "/my/new/belief/dir/..."
    module_dir = "/my/new/module/dir/..."

An example
----------

Let's say we have a Python application called ``reporter``. ``reporter``
is a program that generates a report every hour about the statistics for
the machine it runs on and sends them to a reporting server. Reporter
has two configuration files:

``/etc/reporter/reporter.conf`` defines what we want the report of our
machine to include.

::

    temperature=<boolean>
    system_load=<boolean>
    disk_space=<boolean>
    ...

``/etc/reporter/report_send_init.sh`` defines where we want the report
to go.

.. code:: bash

    export REPORTER_USER=<string>
    export REPORTER_PASS=<string>
    export FTP_SERVER=<string>
    export REPORT_PREFIX=<string>

This is used in a ``/etc/cron.hourly/reporter`` cron script that runs
every hour to generate a report and upload it to an FTP server.

.. code:: bash

    #! /bin/bash

    . /etc/reporter/report_send_init.sh

    filename="${REPORT_PREFIX}_$(date +%Y-%m-%d-%H-%M)"
    reporter -c /etc/reporter/reporter.conf > /tmp/${filename}.txt

    ftp -n <<EOF
    open ${FTP_SERVER}
    user ${REPORTER_USER} ${REPORTER_PASS}
    put /tmp/${filename}.txt
    EOF

    rm -f /tmp/${filename}.txt

Now let's say we are given the following scenario; we have to deploy our
``reporter`` tool over two server clusters at a company creatively named
*company*.

.. figure:: diagrams/company.png
   :alt: company\_overview

   company\_overview

After careful analysis, *company* has determined that the temperature of
each machine in their *letters* cluster needs to be carefully monitored.
They have another cluster called *numbers* that has a state of the art
cooling system with its own reporting, but has frequent disk space and
system load issues that need to be monitored.

The machines of each cluster periodically send their reports to their
master.

How are we going to configure all of these machines?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fortunately for us, *company* was diligent enough to implement some
orchistration software last month to deploy config files on each of
their machines. Their head of operations would like to have as few
configuration files as possible deployed across all installed
applications. Let's try and minimize the number of managed
configurations using ``cfgtool``!

Modifying the configurations of ``reporter``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Seeing as ``reporter`` is an in-house tool, we can modify it to use
``cfgtool`` as a dependency.

The head of operations has agreed to start using ``cfgtool`` to simplify
configuration across all servers. A unique 'environment' beliefs file
will be created and deployed for each of the machines in each cluster
under ``/etc/cfgtool/belief.d/env.json``. This will contain beliefs that
may be useful to many applications using ``cfgtool``.

Here is what that file would look like for server A in our diagram:

.. code:: json

    {
        "master": {
            "domain": "letters.company.com",
            "username": "machine_a",
            "password": "very_secret_password"
        },
        "host": {
            "name": "letters-a",
            "address": "lettersa.company.com"
        }
    }

Our head of operations has also deployed ``reporter`` specific
configurations to each cluster onto each machine under the file name
``/etc/reporter/belief.d/reporter.json``. Here is what that would look
like for machines in the ``numbers.company.com`` cluster.

.. code:: json

    {
        "reporter": {
            "temperature": false,
            "system_load": true,
            "disk": true
        }
    }

Let's create ``templ`` files for each of our configuration files. In
each of our ``templ`` files, we can reference these beliefs under
``belief.d/`` using ``${...}`` syntax. ``cfgtool`` merges all of our
belief files together (traversing them alphabetically) into one big
dictionary.

    **Warning:** If a belief is specified twice, the later one (the one
    in a file whose name is alphabetically greater) will be what
    ``cfgtool`` uses.

Let's change our configuration files into ``templ`` files.

``/etc/reporter/reporter.conf.templ``

.. code:: bash

    temperature=${reporter.temperature}
    system_load=${reporter.system_load}
    disk_space=${reporter.disk}
    ...

``/etc/reporter/report_send_init.sh.templ``

.. code:: bash

    export REPORTER_USER=${master.username}
    export REPORTER_PASS=${master.password}
    export FTP_SERVER=${master.domain}
    export REPORT_PREFIX=${host.name}

Now let's assume our directory structure for ``reporter`` looks like
this:

::

    ├── LICENSE
    ├── README.md
    ├── setup.py
    ├── requirements.txt
    ├── reporter
    │   ├── __init__.py
    │   ├── reporter.py
    │   ├── ...
    ├── config
    │   ├── reporter
    │   ├── reporter.conf.templ
    │   ├── report_send_init.sh.templ
    │   ├── reporter.sh
    ├── install.sh

Our new ``install.sh`` script will look like this:

.. code:: bash

    #! /bin/sh

    install -D -g root -o root -m 0644 -p config/reporter /etc/cfgtool/module.d/reporter
    install -D -g root -o root -m 0644 -p config/reporter.conf.templ /etc/reporter/reporter.conf.templ
    install -D -g root -o root -m 0644 -p config/report_send_init.sh.templ /etc/reporter/report_send_init.sh.templ
    install -D -g root -o root -m 0644 -p config/reporter.sh /etc/cron.hourly/reporter

The ``reporter`` file contains the names of the configuration files that
``reporter`` should generate:

.. code:: bash

    /etc/reporter/reporter.conf
    /etc/reporter/report_send_init.sh

Creating the *real* config files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At this point we have fully integrated ``cfgtool`` into ``reporter``,
deployed our beliefs and have our software installed, but **not** yet
usable because our config files do not exist yet. We still have to tell
``cfgtool`` to generate our configurations.

To generate the configurations, we run the following in the terminal:

.. code:: bash

    $ cfgtool write <module> [--force]

We replace ``<module>`` with the application we would like to create
configuration files for. ``--force`` means we would *actually* like to
write (to keep it differentiated from non-destructive commands).

Let's create the configuration files for ``reporter``. This command
needs to be run on each machine ``reporter`` is installed on and should
be part of your deployment process.

.. code:: bash

    $ cfgtool write reporter --force
    Module: reporter
      Generate...
        File: /etc/reporter/reporter.conf
        File: /reporter/report_send_init.sh

Let's look at what was produced on machine A:

``/etc/reporter/reporter.conf``

.. code:: bash

    temperature=true
    system_load=false
    disk_space=false
    ...

``/etc/reporter/report_send_init.sh``

.. code:: bash

    export REPORTER_USER="machine_a"
    export REPORTER_PASS="very_secret_password"
    export FTP_SERVER="letters.company.com"
    export REPORT_PREFIX="letters-a"

Wow, each machine is configured and ready to report just like that!

What if our configuration changes?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now it is a safe assumption that our setup will not necessarily stay the
same forever. Let's say two years after starting to use ``cfgtool``, a
new cooling system is introduced into our letters cluster and more
machines are added. We no longer have temperature issues we need to
monitor, but system load is now something we need to watch for some
reason.

A new ``reporter`` beliefs file has been deployed onto this cluster.

``/etc/reporter/belief.d/reporter.json``

.. code:: json

    {
        "reporter": {
            "temperature": false,
            "system_load": true,
            "disk": false
        }
    }

To update our configurations, we simply run our ``cfgtool write``
command on the cluster, as we did with the initial installation.

.. code:: bash

    $ cfgtool write reporter --force

And once again, our configurations are up to date!

Wait, what if I made a mistake and want my old configuration back?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``cfgtool`` is careful in that it always leaves a time stamped copy of
whatever it overwrites behind. Here's what our directory on machine A
looks like after running ``cfgtool write`` again.

::

    ├── etc
    │   ├── reporter
    │   │   ├── reporter.conf.templ
    │   │   ├── report_send_init.sh.templ
    │   │   ├── reporter.conf
    │   │   ├── reporter.conf-backup.2016-01-20_0019.23
    │   │   ├── report_send_init.sh
    │   │   ├── report_send_init.sh-backup.2016-01-20_0019.23
    │   │   ├── ...

Eventually this may really start to pile up after many consecutive
redeployments:

::

    reporter.conf
    reporter.conf-backup.2016-01-10_0019.23
    reporter.conf-backup.2016-01-11_0112.01
    reporter.conf-backup.2016-01-12_1202.26
    reporter.conf-backup.2016-01-13_0311.04
    reporter.conf-backup.2016-01-14_1049.45
    reporter.conf-backup.2016-01-15_0059.15
    reporter.conf-backup.2016-01-16_5001.02
    reporter.conf-backup.2016-01-17_0019.21
    ...

We can have ``cfgtool`` toss all of our backups with the ``clean``
command.

::

    $ cfgtool clean reporter

And now all the backups are gone.

::

    reporter.conf
    ...

Hmm, I can't recall if I (re)generated my configurations already
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can check if our existing configurations files match our beliefs (or
even exist) by running the ``check`` command.

.. code:: bash

    $ cfgtool check reporter
    Module: reporter
      Generate...
        File: /etc/reporter/reporter.conf-check
        File: /reporter/report_send_init.sh-check
      Check...
        File: /etc/reporter/reporter.conf-check
        File: /reporter/report_send_init.sh-check

If anything is inconsistent, the checks will not pass. Leave out the
module name to do a check for *all* installed applications.

What if I want to generate configurations to see what they look like but *not* immediately use them?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run ``cfgtool`` with the ``sample`` command to generate config files
with a ``.sample`` extension.

.. code:: bash

    $ cfgtool sample reporter
    Module: reporter
      Generate...
        File: /etc/reporter/reporter.conf.sample
        File: /reporter/report_send_init.sh.sample

If everything looks good, just run ``cfgtool`` with ``write``.

Wait a minute, going back to this thing about all the beliefs being combined by ``cfgtool``, doesn't that expose secrets?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now say for example we install another application called ``uploader``
which takes files that our vast client base uploads and puts them in
Amazon S3. Among its beliefs is an AWS key:

``/etc/cfgtool/belief.d/uploader.json``

.. code:: json

    {
        "uploader": {
            "aws_secret_key": "..."
        }
    }

We don't want tools like ``reporter`` getting access to that information
by simply putting ``${uploader.aws_secret_key}`` somewhere in their
configuration ``templ`` files. What do we do?

Fortunately, ``cfgtool`` is smart enough to realize who should know
what. As long as there is a top level belief called ``uploader``,
``cfgtool`` will realize it should only be seen by the ``uploader``
application and hide it.

We can confirm this by checking the beliefs that are exposed to
``reporter`` after installing ``uploader`` with the ``belief``
``cfgtool`` command in machine A.

.. code:: bash

    $ cfgtool belief db_reports
    Module: db_reports
    {
        "master": {
            "domain": "letters.company.com",
            "username": "machine_a",
            "password": "very_secret_password"
        },
        "host": {
            "name": "letters-a",
            "address": "lettersa.company.com"
        },
        "reporter": {
            "temperature": false,
            "system_load": true,
            "disk": true
        }
    }

The beliefs of ``uploader`` have not been exposed. You can be assured
your ``cfgtool`` utilizing apps only know what they are supposed to
know!

What's next?
------------

This page summarizes the major functionality of ``cfgtool``. To learn
more about other features of ``cfgtool``, check out the help section via
your terminal.

.. code:: bash

    $ cfgtool -help
