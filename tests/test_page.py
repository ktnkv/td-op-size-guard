"""The tool's interface and the wiring of its DATs. Read-only."""

FAMILIES = ('TOP', 'CHOP', 'SOP', 'POP', 'MAT', 'DAT', 'COMP')
RUNNING = 'parent().par.Active'


def test_pages_are_size_guard_then_about(t):
    t.eq([p.name for p in t.tool.customPages], ['Size Guard', 'About'])


def test_parameter_order(t):
    want = ['Active', 'Sizew', 'Sizeh']
    for fam in FAMILIES:
        n = fam.capitalize()
        want += [n + 'override', n + 'sizew', n + 'sizeh']
    got = [p.name for p in t.tool.customPars if p.page.name == 'Size Guard']
    t.eq(got, want)


def test_each_family_is_a_section_with_a_gated_size(t):
    for fam in FAMILIES:
        n = fam.capitalize()
        toggle = t.tool.par[n + 'override']
        t.eq(toggle.label, 'Override %s Size' % fam)
        t.eq(toggle.startSection, True, fam)
        # COMPs ship with a size of their own; the other families follow Size.
        t.eq(toggle.default, fam == 'COMP', fam)
        for axis in 'wh':
            size = t.tool.par[n + 'size' + axis]
            t.eq(size.label, '%s Size' % fam)
            t.eq(size.enableExpr, 'me.par.%soverride' % n)
            t.eq(size.enable, bool(toggle.eval()), fam)


def test_main_size_is_always_enabled(t):
    for p in (t.tool.par.Sizew, t.tool.par.Sizeh):
        t.eq(p.enable, True)
        t.eq(p.enableExpr, None)
        t.eq(p.clampMin, True)
        t.eq(p.min, t.mod.MIN_SIZE)


def test_every_parameter_has_help(t):
    for p in t.tool.customPars:
        if p.page.name == 'Size Guard':
            assert p.help, p.name


def test_about_page(t):
    t.eq([p.name for p in t.tool.customPars if p.page.name == 'About'],
         ['Version', 'Toxsavebuild'])
    for p in (t.tool.par.Version, t.tool.par.Toxsavebuild):
        t.eq(p.readOnly, True, p.name)
        t.eq(p.default, p.val, p.name)


def test_execute_dats_are_inactive_while_the_tool_is_off(t):
    for name in ('frameExec', 'opExec'):
        active = t.tool.op(name).par.active
        t.eq(active.mode, ParMode.EXPRESSION, name)
        t.eq(active.expr, RUNNING, name)


def test_dat_wiring(t):
    frame, ops = t.tool.op('frameExec'), t.tool.op('opExec')
    t.eq((frame.par.framestart.eval(), frame.par.projectpresave.eval()),
         (True, True))
    t.eq((ops.par.numchildrenchange.eval(), ops.par.uichange.eval()),
         (True, True))
    run_, size = t.tool.op('runExec'), t.tool.op('sizeExec')
    t.eq(run_.par.op.eval(), t.tool)
    t.eq(run_.par.pars.eval(), 'Active')
    t.eq(size.par.op.eval(), t.tool)


def test_dat_text_matches_src(t):
    for name in ('SizeGuardExt', 'frameExec', 'opExec', 'runExec', 'sizeExec'):
        src = open(project.folder + '/src/' + name + '.py').read()
        t.eq(t.tool.op(name).text.replace('\r\n', '\n'), src, name)
