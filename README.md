# Size Guard

Size Guard is a TouchDesigner tool that keeps every operator tile in the network editor at one size.

TouchDesigner has no project setting for the tile size. New operators come in the stock size, COMPs in another one, a pasted or imported network brings whatever its author had, and a tile can be stretched by accident. Size Guard sets the size once for the whole project and holds it.

## How to use

1. Download `SizeGuard.*.tox` from the [latest release](https://github.com/ktnkv/td-op-size-guard/releases/latest) and drop it into your project. The convention is `/tools/sizeguard`.
2. Set **Size**: the tile width and height for every operator.
3. To give one family a size of its own, turn on its **Override … Size** toggle and set the pair under it. COMPs come with their override already on.
4. Leave **Active** on. Turn it off to stop the tool; the tiles keep the size they have.

The first time the tool runs in a project it resizes every operator in it.

## How it works

When the tool starts running (the project opens, the tool is dropped in, **Active** is turned on, perform mode is left) it walks the whole project once and sets the size of every tile. It does the same before the project is saved.

Between those moments it watches only the networks that are open in network editors, because that is the only place where a tile can be created or stretched by hand. A new operator there gets its size within a frame, and a stretched tile goes back. A network nobody is looking at is checked when somebody opens it.

Only the width and the height of a tile change. Its bottom-left corner stays where it was.

In perform mode the tool changes nothing and watches nothing. With **Active** off it is not called at all. The sizes are ordinary tile sizes stored in the project, so a saved project does not need the tool.

## Limitations

- **No per-operator exceptions.** Every operator gets the size of its family, including panel COMPs, TOPs and tiles that were enlarged on purpose.
- **Never touched:** Annotate COMPs (comments, annotations and network boxes), TouchDesigner's own `/ui`, `/sys` and `/local`, and the contents of a locked private COMP.
- **Operators created by a script in a closed network** keep their size until that network is opened or the project is saved. Saving a `.tox` does not trigger a check.
- **A change of Size** reaches the open networks at once and the rest of the project when its networks are opened or the project is saved.
- **Neighbours are not moved.** After a size change tiles may overlap or leave gaps.
- **One small check per frame** while the network editor is in use, about 50 microseconds. In perform mode it is one call that returns at once.
