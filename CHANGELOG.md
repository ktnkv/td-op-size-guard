# Changelog

## 0.1.2

### Fixed

- A script that creates an operator in an open network and destroys it in the same frame no longer makes the tool print an error at the end of that frame. TouchDesigner reports the destroyed operator as `None`, and the tool now ignores it.

## 0.1.1

### Added

- A `readme` annotation and a `changelog` DAT inside the component. What the tool is, how to use it and its history now travel with the tox.

## 0.1.0

### Added

- Initial release. One tile size for every operator, with an optional size per operator family. The whole project is checked when the tool starts running and before the project is saved; the networks open in network editors are kept in line as operators are created or resized.
