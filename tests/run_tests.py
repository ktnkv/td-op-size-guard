"""Size Guard test runner. Runs inside a live TouchDesigner.

    exec(open(project.folder + '/tests/run_tests.py').read())

Each tests/test_*.py defines test_* functions that take one argument, `t`
(see Harness). A test gets a fresh scratch COMP and the scratch is destroyed
after it, pass or fail. The tool's parameters and the state of its extension
are put back after every test. Nothing outside the scratch is created,
removed or resized by a test.
Set ONLY to a substring to run matching tests: ONLY = 'override'.
"""
import glob
import os
import traceback

TOOL_PATH = '/tools/sizeguard'
SCRATCH_NAME = 'sizeguard_test_scratch'


class Harness:
    """What a test sees: the tool, a scratch network, and a few asserts."""

    def __init__(self, tool):
        self.tool = tool
        self.guard = tool.ext.SizeGuardExt
        self.mod = tool.op('SizeGuardExt').module
        self.root = None
        self._saved = None

    # ---- scratch ------------------------------------------------------
    def fresh(self):
        """New scratch: one operator of several families, and a nested COMP.

        Every tile gets a size that no rule in the tests asks for.
        """
        self.drop()
        self._save_tool()
        # Every test starts from "one size for all": no family override.
        for p in self.tool.customPars:
            if p.name.endswith('override'):
                p.val = False
        self.guard.ReadSizes()
        self.root = op('/').create(baseCOMP, SCRATCH_NAME)
        self.top = self.root.create(constantTOP, 'top')
        self.chop = self.root.create(constantCHOP, 'chop')
        self.dat = self.root.create(textDAT, 'dat')
        self.comp = self.root.create(baseCOMP, 'comp')
        self.inner = self.comp.create(constantCHOP, 'inner')
        self.note = self.root.create(annotateCOMP, 'note')
        for i, o in enumerate(self.all()):
            o.nodeX, o.nodeY = i * 400, -300
            o.nodeWidth, o.nodeHeight = 77, 55
        return self

    def all(self):
        return [self.top, self.chop, self.dat, self.comp, self.inner, self.note]

    def drop(self):
        old = op('/' + SCRATCH_NAME)
        if old is not None:
            old.destroy()
        self.root = None
        self._restore_tool()

    # ---- the tool is left as it was found -----------------------------
    def _save_tool(self):
        g = self.guard
        self._saved = dict(
            pars={p.name: p.val for p in self.tool.customPars
                  if p.page.name == 'Size Guard'},
            started=g.started, shownIds=g.shownIds,
            watch=self.tool.op('opExec').par.op.val)

    def _restore_tool(self):
        if self._saved is None:
            return
        for name, val in self._saved['pars'].items():
            self.tool.par[name].val = val
        g = self.guard
        g.started = self._saved['started']
        g.shownIds = self._saved['shownIds']
        self.tool.op('opExec').par.op = self._saved['watch']
        g.ReadSizes()
        self._saved = None

    # ---- helpers ------------------------------------------------------
    def set_main(self, w, h):
        self.tool.par.Sizew, self.tool.par.Sizeh = w, h
        self.guard.ReadSizes()

    def set_family(self, family, w, h, on=True):
        n = family.capitalize()
        self.tool.par[n + 'override'] = on
        self.tool.par[n + 'sizew'], self.tool.par[n + 'sizeh'] = w, h
        self.guard.ReadSizes()

    def size(self, o):
        return (o.nodeWidth, o.nodeHeight)

    # ---- asserts ------------------------------------------------------
    def eq(self, got, want, what=''):
        assert got == want, '%s: got %r, want %r' % (what or 'value', got, want)


def _load(path):
    ns = dict(globals())
    exec(compile(open(path).read(), path, 'exec'), ns)
    return [(os.path.basename(path)[:-3] + '.' + k, v)
            for k, v in ns.items() if k.startswith('test_') and callable(v)]


def run():
    tool = op(TOOL_PATH)
    if tool is None:
        raise RuntimeError('%s not found' % TOOL_PATH)
    t = Harness(tool)
    only = globals().get('ONLY')
    tests = []
    for path in sorted(glob.glob(project.folder + '/tests/test_*.py')):
        tests += _load(path)
    if only:
        tests = [x for x in tests if only in x[0]]
    passed, failed = 0, []
    for name, fn in tests:
        t.fresh()
        try:
            fn(t)
            passed += 1
        except Exception:
            failed.append((name, traceback.format_exc(limit=4)))
        finally:
            t.drop()
    for name, tb in failed:
        print('FAIL', name)
        print(tb)
    print('%d passed, %d failed (%d tests)' % (passed, len(failed), len(tests)))
    return not failed


RESULT = run()
