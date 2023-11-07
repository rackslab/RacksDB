# RacksDB Documentation

## Generate manpage

To generate the manpage, run this command:

```sh
$ make man
```

## Generate objects reference documentation

To generate the schema objects partial of database structure reference
documentation, run this command:

```sh
make ref
```

## Generate objects reference documentation

To generate the schema objects partial of drawing parameters reference
documentation, run this command:

```sh
make drawing-ref
```

## Update OpenAPI description

To update reference OpenAPI description of RacksDB REST API, run this command:

```sh
make openapi
```

## Optimize SVG images

To optimize the SVG images in documentation, run this command:

```sh
$ make optim
```

This will significantly reduce files size and load time in browser.

This requires Python 3 [scour](https://pypi.org/project/scour/) library. On
Ubuntu/Debian, install it with:

```sh
$ sudo apt install python3-scour
```
