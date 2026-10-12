"""The rule (which size an operator gets) and how it is applied."""


def test_main_size_applies_to_every_family(t):
    t.set_main(150, 100)
    t.guard.FixTree(t.root)
    for o in (t.root, t.top, t.chop, t.dat, t.comp, t.inner):
        t.eq(t.size(o), (150, 100), o.path)


def test_override_gives_a_family_its_own_size(t):
    t.set_main(150, 100)
    t.set_family('TOP', 200, 120)
    t.guard.FixTree(t.root)
    t.eq(t.size(t.top), (200, 120), 'TOP')
    t.eq(t.size(t.chop), (150, 100), 'CHOP')
    t.eq(t.size(t.comp), (150, 100), 'COMP')


def test_family_size_is_ignored_while_its_override_is_off(t):
    t.set_main(150, 100)
    t.set_family('DAT', 300, 300, on=False)
    t.guard.FixTree(t.root)
    t.eq(t.size(t.dat), (150, 100))


def test_sizes_are_rounded_and_kept_above_the_minimum(t):
    t.set_main(140.4, 99.6)
    t.eq(t.guard.sizes['CHOP'], (140, 100))
    t.tool.par.Sizew.val = 3            # the parameter clamps, so does the code
    t.guard.ReadSizes()
    t.eq(t.guard.sizes['CHOP'][0], t.mod.MIN_SIZE)


def test_annotate_is_left_alone(t):
    t.set_main(150, 100)
    t.eq(t.guard.SizeFor(t.note), None)
    t.guard.FixTree(t.root)
    t.eq(t.size(t.note), (77, 55))


def test_inside_of_an_annotate_is_left_alone(t):
    t.set_main(150, 100)
    inside = t.note.findChildren()
    assert inside, 'an Annotate COMP has operators inside'
    before = [t.size(o) for o in inside]
    t.guard.FixTree(t.root)
    t.guard.FixTree(t.note)
    t.eq([t.size(o) for o in inside], before)


def test_system_networks_are_left_alone(t):
    for path in ('/ui', '/sys', '/local', '/local/time'):
        t.eq(t.guard.SizeFor(op(path)), None, path)


def test_fix_keeps_the_bottom_left_corner(t):
    t.set_main(150, 100)
    x, y = t.top.nodeX, t.top.nodeY
    assert t.guard.Fix(t.top)
    t.eq((t.top.nodeX, t.top.nodeY), (x, y))


def test_fix_reports_whether_it_changed_anything(t):
    t.set_main(150, 100)
    t.eq(t.guard.Fix(t.top), True)
    t.eq(t.guard.Fix(t.top), False)


def test_fix_children_stays_in_one_network(t):
    t.set_main(150, 100)
    changed = t.guard.FixChildren(t.root)
    t.eq(changed, 4, 'top, chop, dat, comp')
    t.eq(t.size(t.inner), (77, 55), 'operator one level down')
    t.eq(t.size(t.root), t.size(t.root))


def test_fix_tree_reaches_nested_networks_and_is_idempotent(t):
    t.set_main(150, 100)
    t.eq(t.guard.FixTree(t.root), 6, 'root, top, chop, dat, comp, inner')
    t.eq(t.guard.FixTree(t.root), 0, 'second pass')
