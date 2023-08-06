brocket
=======

A command line tool for building `Amazon Associates`_ links with as few actions as possible.

If you have a link in the clipboard, run this script, then the link on the clipboard becomes an `Amazon Associates`_ link.

OS X Only
---------

This is only for Mac OS X 10.8 or higher but it could easily be enhanced to support other operating systems.

Setup
-----

After you ``pip install brocket`` just run ``brocket``. It will prompt you for your tracking-id. Enter it.

Optional: Make sure it's correct by running ``brocket --show-tracking-id``.

How to Make Links
-----------------

Once it's setup, the easiest thing to do is

 1. Browse to an Amazon URL you want an affiliate link for.
 2. Copy the URL
 3. Run the ``brocket`` command. This will tag the URL with your tracking-id and put the new URL on the clipboard.
 4. Paste the URL where ever you want it to go.

Upping Your Game
----------------

I know what you're thinking "4 steps?!? You mean I have to go to my browser and copy a URL, then run a terminal command, then go back...". Yeah yeah I hear you.

There are probably lots of ways to skin this cat but here's what I did.

Make an AppleScript called ``Brocket`` and save it in ``~/Library/Scripts``. It just needs to be 1 line::

   do shell script "/usr/local/bin/brocket"

Then, if you haven't already install the wonderful `FastScripts`_. Your ``Brocket`` script should show up in the menu.

Finally assign ``Brocket`` a keyboard shortcut and you can skip switching to the Terminal to run the Brocket command.

Brocket Deer
------------

This little utility is named for the `Brocket Deer`_ which lives around the Amazon river. It also sounds like Rocket, but with a 'B' and I was looking for something with a fast sounding name.

.. _Amazon Associates: https://affiliate-program.amazon.com
.. _Brocket Deer: https://en.wikipedia.org/wiki/Brocket_deer
.. _FastScripts: https://red-sweater.com/fastscripts/
