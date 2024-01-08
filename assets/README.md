# RacksDB assets

All assets are generated based on the content of `branding.svg` by running this
command:

```sh
$ ./update-branding
```

This automatically generates the SVG files in `scalables/` folder, PNG files (in
various sizes) and favicon in `bitmaps/` folder.

The script has some requirements:

* Python3
* [Ninja build system](https://ninja-build.org/). On Debian/Ubuntu, this can be
  installed with:

  ```sh
  $ sudo apt install ninja-build
  ```
* [Inkscape](https://inkscape.org/)
* [RFL build package](https://github.com/rackslab/RFL/tree/main/src/build)
* [Scour Python package](https://github.com/scour-project/scour/tree/master)

All the generated files are commited and pushed in Git repository to allow
direct usage by documentation site, main `README.md` file, etc…
