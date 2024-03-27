# RacksDB assets

All assets are generated based on the content of `branding.svg` and
`screenshots/raw/` by running this command:

```sh
$ ./update-assets
```

This automatically generates:

- Scalable SVG files of the logo in `scalables/` folder,
- Bitmaps PNG files (in various sizes) of the logo in `bitmaps/` folder,
- Favicon in `bitmaps/` folder,
- Shadowed and Webp compressed versions of raw PNG screenshots.

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
* [ImageMagick](https://imagemagick.org/index.php)

All the generated files are commited and pushed in Git repository to allow
direct usage by documentation site, main `README.md` file, etc…
