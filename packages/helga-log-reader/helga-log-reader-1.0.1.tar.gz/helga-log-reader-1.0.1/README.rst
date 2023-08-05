helga-log-reader
================

Read logs when enabled in helga settings. Has a large set of arguments, defaults
to the day.

Usage
-----

``!log`` - shows logs for current date

Can filter on start_date, end_date, start_time, end_time, nick, channel, and
text by adding the corresponding arguments.

``!log --nick narfman0`` - returns only messages posted by user/nick "narfman0"

``!log --start_date 2016-01-02`` - shows messages sent since Jan2 2016

License
-------

Copyright (c) 2016 Jon Robison

See included LICENSE for licensing information
