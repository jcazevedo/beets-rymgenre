# beets-rymgenre

`beets-rymgenre` is a [beets][beets] plugin to fetch genre information from
[rateyourmusic.com][rym] and assigning it to your albums and items.

## Installation

The plugin requires [lxml][lxml] and [requests][requests], which you can install
using [pip][pip] by typing:

```
$ pip install lxml requests
```

After having [lxml][lxml] and [requests][requests] installed, edit your config
file and add the path to the `beetsplug` folder of a clone of this repository to
your [pluginpath][beets-pluginpath] line. Also enable the plugin by adding the
`rymgenre` value to your `plugins` line.

## Configuration

[rateyourmusic.com][rym] attributes genres per album. Each album has a set of
primary genres and a set of secondary genres. There is also a [tree][rym-tree]
of genres. You can configure the plugin to set (1) only the primary genres of an
album, (2) both the primary and secondary genres or (3) the union of ancestor
genres for each primary and secondary genre. The default configuration is the
latter, but you can override it by using the `level` configuration value. The
`level` configuration value can have one of three possible values: `primary`,
`secondary` or `parent`:

```
rymgenre:
    level: parent
```

It is also possible to configure the separator to use for multiple genres. The
default value is `', '`, but it is customizable through the `separator`
configuration value:

```
rymgenre:
    separator: ' / '
```

## Running

`beets-rymgenre` doesn't run automatically on import. Instead, one should use
the command `beet rymgenre [QUERY]` to fetch genres for albums matching a
certain query. The genre import requires user confirmation and can be overriden
by selecting a different alternative or by specifying a [rateyourmusic.com][rym]
URL.

## Thanks

Thanks to [Rui Gonçalves][ruippeixotog], who created the original `genres-tree`
yaml, using his [scala-scraper][scala-scraper] library.

## Copyright

Copyright (c) 2014 Joao Azevedo. See LICENSE for details.

[beets]: http://beets.radbox.org/
[beets-pluginpath]: http://beets.readthedocs.org/en/latest/reference/config.html#pluginpath
[lxml]: http://lxml.de/
[pip]: http://www.pip-installer.org/
[requests]: http://docs.python-requests.org/
[ruippeixotog]: http://github.com/ruippeixotog/
[rym]: http://rateyourmusic.com/
[rym-tree]: http://rateyourmusic.com/rgenre
[scala-scraper]: http://github.com/ruippeixotog/scala-scraper
