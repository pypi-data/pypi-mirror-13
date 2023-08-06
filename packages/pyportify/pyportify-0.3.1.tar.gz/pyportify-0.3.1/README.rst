Pyportify
=========

`|Build Status| <https://travis-ci.org/rckclmbr/pyportify>`_

A port of `portify <https://github.com/mauimauer/portify>`_ to python.

But it actually works.

Transfers your Spotify Premium playlists to Google Music: All Access

By using Pyportify you may violate both Spotify's and Google's Terms of
Service. You agree that you are using Pyportify on your own risk. The
author does not accept liability (as far as permitted by law) for any
loss arising from any use of this tool. If you choose not to agree to
these terms, then you may not use this tool.

You can read about portify here:
`http://www.maui.at/2013/06/portify/ <http://www.maui.at/2013/06/portify/>`_

If you are unable to sign in to your Google account, turn on access for
less secure apps here:
https://www.google.com/settings/security/lesssecureapps/

Download
--------

Windows:

https://xr6.me/pyportify/pyportify-0.3.0-win32.zip

OSX:

https://xr6.me/pyportify/pyportify-0.3.0-osx.tar.gz

Install from pypi
-----------------

OS X:

::

    $ brew install python3
    $ pip3 install pyportify

Ubuntu:

::

    sudo apt-get update
    sudo apt-get install -y python-pip3
    sudo pip3 install pyportify

Fedora

::

    sudo yum check-update
    sudo pip install pyportify

Running
-------

::

    $ pyportify
    # Now open a browser to http://localhost:3132

EZ

Alternatively, you can copy all playlists easily using the
``pyportify-copyall`` command:

::

    $ pyportify-copyall
    Enter Google email address: example@gmail.com
    Enter Google password:
    Enter Spotify username: spotifyuser
    Enter Spotify password:
    (transfer music)
    ...

Or, use Docker:

::

    $ docker run -t -i --rm -p 3132:3132 rckclmbr/pyportify

    or

    $ docker run -t -i --rm rckclmbr/pyportify /ve/bin/pyportify-copyall

License
-------

Licensed under the terms of the Apache 2.0 License All Trademarks are
the property of their respective owners.

.. |Build
Status| image:: https://travis-ci.org/rckclmbr/pyportify.svg?branch=master
