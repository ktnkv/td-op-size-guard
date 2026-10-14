"""Watchers and reactions. The extension methods are called directly: the
OP Execute callbacks themselves arrive at the end of a frame, after a test
has finished. No pane is moved."""


def watch(t):
    return t.tool.op('opExec').par.op.val


def test_watch_lists_the_comp_and_its_children(t):
    t.guard.Watch([t.root, t.comp])
    t.eq(watch(t), '%s %s/* %s %s/*' % (t.root.path, t.root.path,
                                         t.comp.path, t.comp.path))


def test_watch_on_the_project_root(t):
    t.guard.Watch([op('/')])
    t.eq(watch(t), '/ /*')


def test_stop_removes_the_watchers(t):
    t.guard.Watch([t.root])
    t.guard.Stop()
    t.eq(watch(t), '')
    t.eq(t.guard.started, False)
    t.eq(t.guard.shownIds, ())


def test_shown_networks_are_comps_outside_the_system(t):
    for comp in t.guard.ShownNetworks():
        assert comp.isCOMP, comp.path
        t.eq(t.guard.SizeFor(comp) is None and comp.path != '/', False, comp.path)


def test_new_operator_in_a_watched_network_is_fixed(t):
    t.set_main(150, 100)
    t.guard.shownIds = (t.root.id,)
    t.guard.OnChildrenChange(t.root)
    t.eq(t.size(t.top), (150, 100))
    t.eq(t.size(t.inner), (77, 55), 'nested network is not watched')


def test_change_in_an_unwatched_network_is_ignored(t):
    t.set_main(150, 100)
    t.guard.shownIds = ()
    t.guard.OnChildrenChange(t.root)
    t.guard.OnTileChange(t.top)
    t.eq(t.size(t.top), (77, 55))


def test_resized_tile_in_a_watched_network_is_put_back(t):
    t.set_main(150, 100)
    t.guard.shownIds = (t.root.id,)
    t.guard.OnTileChange(t.top)
    t.eq(t.size(t.top), (150, 100))
    t.top.nodeWidth = 300
    t.guard.OnTileChange(t.top)
    t.eq(t.size(t.top), (150, 100))


def test_size_edit_does_nothing_while_the_guard_is_stopped(t):
    t.guard.started = False
    t.tool.par.Sizew = 222
    t.guard.OnSizeParChange()
    assert t.guard.sizes['CHOP'][0] != 222


def test_operator_destroyed_in_the_same_frame_is_ignored(t):
    # A script creates a network, adds an operator and destroys the network
    # in one call. At the end of that frame TouchDesigner calls both OP
    # Execute callbacks with None in place of the operator that is gone.
    t.guard.shownIds = (t.root.id,)
    t.guard.Watch([t.root])
    gone = t.root.create(baseCOMP, 'gone')
    gone.create(constantCHOP, 'child')
    gone.destroy()
    callbacks = t.tool.op('opExec').module
    callbacks.onNumChildrenChange(None)
    callbacks.onUIChange(None)
    t.guard.OnChildrenChange(None)
    t.guard.OnTileChange(None)
