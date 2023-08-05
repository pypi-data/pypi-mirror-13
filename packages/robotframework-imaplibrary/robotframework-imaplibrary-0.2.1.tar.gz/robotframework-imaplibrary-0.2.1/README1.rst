IMAP email testing library for Robot Framework
==============================================

|Docs| |Version| |Status| |Python| |Download| |License|

Introduction
------------

ImapLibrary is a IMAP email testing library for `Robot Framework`_.

More information about this library can be found in the `Keyword Documentation`_.


These keyword actions are available::

    Open Mailbox:
        Open the mailbox on a mail server with a valid authentication:
        Arguments:
            - server:   the server name (e.g. imap.googlemail.com)
            - user:     the user name (e.g. me@googlemail.com)
            - password: the user's password

    Wait for Mail:
        Wait for an incoming mail. Check the mailbox every 10 seconds
        for incoming mails until a matching email is received or the
        timeout is exceeded. Returns the mail number of the latest matching
        email.
        Arguments:
            - fromEmail: the email address of the sender (not required)
            - toEmail:   the email address of the receiver (not required)
            - status:    the status of the email (not required)
            - timeout:   the timeout how long the mailbox shall check emails
                         in seconds (defaults to 60 seconds)

    Get Links From Email:
        Finds all links in an email body and returns them

        Arguments:
            - mailNumber: is the index number of the mail to open

    Get Matches From Email:
        Finds all occurrences of a regular expression

        Arguments:
            - mailNumber: is the index number of the mail to open
            - regexp: a regular expression to find

    Open Link from Mail:
        Find a link in an email body and open the link. Returns the links' html.
        Arguments:
            mailNumber: the number of the email to check for a link
            linkNumber: the index of the link to open
                        (defaults to 0, which is the first link)

    Get Email body:
        Returns an email body
        Arguments:
            mailNumber: the number of the email to check for a link

    Walk Multipart Email
        Returns the number of parts of a multipart email. Content is stored internally
        to be used by other multipart keywords. Subsequent calls iterate over the
        elements, and the various Get Multipart keywords retrieve their contents.

        Arguments:
            mailNumber: the index number of the mail to open

    Get Multipart Content Type
        Return the content-type for the current part of a multipart email

    Get Multipart Payload
        Return the payload for the current part of a multipart email

        Arguments:
            decode: an optional flag that indicates whether to decoding

    Get Multipart Field Names
        Return the list of header field names for the current multipart email

    Get Multipart Field
        Returns the content of a header field 

        Arguments:
            field: a string such as 'From', 'To', 'Subject', 'Date', etc.

    Mark as read:
        Mark all received mails as read

    Close Mailbox:
        Close the mailbox after finishing all mail activities of a user.

For more informaiton on `status` see: `Mailbox Status <http://pymotw.com/2/imaplib/#mailbox-status>`_.

Here is an example of how to use the library:

==============  ==========================  ===================================  ==================================  =============  ============
 Action         Argument                    Argument                             Argument                            Argument       Argument
==============  ==========================  ===================================  ==================================  =============  ============
Open Mailbox    server=imap.googlemail.com  user=mymail@googlemail.com           password=mysecretpassword
${LATEST}=      Wait for Mail               fromEmail=noreply@register.com       toEmail=mymailalias@googlemail.com  status=UNSEEN  timeout=150
${HTML}=        Open Link from Mail         ${LATEST}
Should Contain  ${HTML}                     Your email address has been updated
Close Mailbox
==============  ==========================  ===================================  ==================================  =============  ============

Here is an example of how to work with multipart emails, ignoring all non content-type='test/html' parts:

==============  ==========================  ===================================  ===================================  ============
 Action         Argument                    Argument                             Argument                             Argument
==============  ==========================  ===================================  ===================================  ============
Open Mailbox    server=imap.googlemail.com  user=mymail@googlemail.com           password=mysecretpassword
${LATEST}=      Wait for Mail               fromEmail=noreply@register.com       toEmail=mymailalias@googlemail.com   timeout=150
${parts}=       Walk Multipart Email        ${LATEST}
@{fields}=      Get Multipart Field Names
${from}=        Get Multipart Field         From
${to}=          Get Multipart Field         To
${subject}=     Get Multipart Field         Subject
:FOR            ${i}                        IN RANGE                             ${parts}
\               Walk Multipart Email        ${LATEST}
\               ${content-type}=            Get Multipart Content Type
\               Continue For Loop If        '${content-type}' != 'text/html'
\               ${payload}=                 Get Multipart Payload                decode=True
\               Should Contain              ${payload}                           Update your email address
\               ${HTML}=                    Open Link from Mail                  ${LATEST}
\               Should Contain              ${HTML}                              Your email address has been updated
Close Mailbox
==============  ==========================  ===================================  ===================================  ============

Installation
------------

Using ``pip``
'''''''''''''

The recommended installation method is using pip_:

.. code:: bash

    pip install robotframework-imaplibrary

The main benefit of using ``pip`` is that it automatically installs all
dependencies needed by the library. Other nice features are easy upgrading
and support for un-installation:

.. code:: bash

    pip install --upgrade robotframework-imaplibrary
    pip uninstall robotframework-imaplibrary

Notice that using ``--upgrade`` above updates both the library and all
its dependencies to the latest version. If you want, you can also install
a specific version:

.. code:: bash

    pip install robotframework-imaplibrary==x.x.x

Proxy configuration
'''''''''''''''''''

If you are behind a proxy, you can use ``--proxy`` command line option
or set ``http_proxy`` and/or ``https_proxy`` environment variables to
configure ``pip`` to use it. If you are behind an authenticating NTLM proxy,
you may want to consider installing CNTML_ to handle communicating with it.

For more information about ``--proxy`` option and using pip with proxies
in general see:

- http://pip-installer.org/en/latest/usage.html
- http://stackoverflow.com/questions/9698557/how-to-use-pip-on-windows-behind-an-authenticating-proxy
- http://stackoverflow.com/questions/14149422/using-pip-behind-a-proxy

Manual installation
'''''''''''''''''''

If you do not have network connection or cannot make proxy to work, you need
to resort to manual installation. This requires installing both the library
and its dependencies yourself.

- Make sure you have `Robot Framework installed`_.

- Download source distributions (``*.tar.gz``) for the library:

  - https://pypi.python.org/pypi/robotframework-imaplibrary

- Download PGP signatures (``*.tar.gz.asc``) for signed packages.

- Find each public key used to sign the package:

.. code:: bash

    gpg --keyserver pgp.mit.edu --search-keys D1406DE7

- Select the number from the list to import the public key

- Verify the package against its PGP signature:

.. code:: bash

    gpg --verify robotframework-imaplibrary-x.x.x.tar.gz.asc robotframework-imaplibrary-x.x.x.tar.gz

- Extract each source distribution to a temporary location.

- Go to each created directory from the command line and install each project using:

.. code:: bash

       python setup.py install

If you are on Windows, and there are Windows installers available for
certain projects, you can use them instead of source distributions.
Just download 32bit or 64bit installer depending on your system,
double-click it, and follow the instructions.

Directory Layout
----------------

doc/
    `Keyword documentation`_

src/
    Python source code

Usage
-----

To write tests with Robot Framework and ImapLibrary,
ImapLibrary must be imported into your Robot test suite.

+-----------------------+
| *** Settings ***      |
+---------+-------------+
| Library | ImapLibrary |
+---------+-------------+

See `Robot Framework User Guide`_ for more information.

More information about Robot Framework standard libraries and built-in tools
can be found in the `Robot Framework Documentation`_.

Building Keyword Documentation
------------------------------

The `Keyword Documentation`_ can be found online, if you need to generate the keyword documentation, run:

.. code:: bash

    make doc

Contributing
------------

If you would like to contribute code to Imap Library project you can do so through GitHub by forking the repository and sending a pull request.

When submitting code, please make every effort to follow existing conventions and style in order to keep the code as readable as possible. Please also include appropriate test cases.

Before your code can be accepted into the project you must also sign the `Imap Library CLA`_ (Individual Contributor License Agreement).

That's it! Thank you for your contribution!

License
-------

Copyright (c) 2015 Richard Huang.

This library is free software, licensed under: `Apache License, Version 2.0`_.

Documentation and other similar content are provided under `Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License`_.

.. _Apache License, Version 2.0: https://goo.gl/qpvnnB
.. _CNTML: http://goo.gl/ukiwSO
.. _Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License: http://goo.gl/SNw73V
.. _Imap Library CLA: https://goo.gl/forms/QMyqXJI2LM
.. _Keyword Documentation: https://goo.gl/ntRuxC
.. _pip: http://goo.gl/jlJCPE
.. _Robot Framework: http://goo.gl/lES6WM
.. _Robot Framework Documentation: http://goo.gl/zy53tf
.. _Robot Framework installed: https://goo.gl/PFbWqM
.. _Robot Framework User Guide: http://goo.gl/Q7dfPB
.. |Docs| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
    :target: https://goo.gl/ntRuxC
    :alt: Keyword Documentation
.. |Version| image:: https://img.shields.io/pypi/v/robotframework-imaplibrary.svg
    :target: https://goo.gl/q66LcA
    :alt: Package Version
.. |Status| image:: https://img.shields.io/pypi/status/robotframework-imaplibrary.svg
    :target: https://goo.gl/q66LcA
    :alt: Development Status
.. |Python| image:: https://img.shields.io/pypi/pyversions/robotframework-imaplibrary.svg
    :target: https://goo.gl/sXzgao
    :alt: Python Version
.. |Download| image:: https://img.shields.io/pypi/dm/robotframework-imaplibrary.svg
    :target: https://goo.gl/q66LcA
    :alt: Monthly Download
.. |License| image:: https://img.shields.io/pypi/l/robotframework-imaplibrary.svg
    :target: https://goo.gl/qpvnnB
    :alt: License
