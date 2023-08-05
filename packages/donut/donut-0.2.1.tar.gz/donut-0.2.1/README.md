# donut

The purpose of this script is to update dot files somewhere.  It works in the
following way.  Two locations are set:

- `dothome`, absolute path to the set the dotfiles
- `dotarchive`, absolute path to the dot files (usually some git archive)

Then symlinks are made from dothome to dotarchive.  Simple as that.

## Installation

```
pip install donut
```

## Usage

```
donut ~ ~/repos/dotfiles
```

## Notes

- `setup.cfg` should be a flat list of files in `dotarchive`
- otherwise all files in `dotarchive` will be symlinked
