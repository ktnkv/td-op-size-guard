"""Size Guard: one tile size for every operator in the network editor.

The idea in three sentences:

1. When the guard starts running it walks the whole project once and gives
   every operator the size from the tool's parameters.
2. After that it only has to keep that state. An operator can be created or
   resized by hand only in a network that is open in a network editor, so the
   guard watches just those networks: an OP Execute DAT reports a new
   operator or a resized tile there, and the guard fixes it.
3. Networks nobody looks at are not watched. They are checked at the moment
   somebody opens them, and once more before the project is saved.

The guard "runs" while Active is on and TouchDesigner is not in perform mode.
With Active off the Execute DATs of the tool are inactive and nothing here is
called. In perform mode Poll() is still called once a frame and returns on
its first line: TouchDesigner has no event for entering perform mode.

Who calls what:

    frameExec  (Execute DAT)            every frame          -> Poll()
                                        before project save  -> FixProject()
    opExec     (OP Execute DAT)         operator added       -> OnChildrenChange()
                                        tile moved/resized   -> OnTileChange()
    sizeExec   (Parameter Execute DAT)  a size was edited    -> OnSizeParChange()
    runExec    (Parameter Execute DAT)  Active switched off  -> Stop()
"""

# Operator families, as OP.family names them. Each has an "Override" toggle
# and a size of its own on the tool's page: Topoverride, Topsize, ...
FAMILIES = ('TOP', 'CHOP', 'SOP', 'POP', 'MAT', 'DAT', 'COMP')

# TouchDesigner's own networks. They are not part of the project.
SYSTEM_ROOTS = ('/ui', '/sys', '/local')

# Operators whose tile size is their content, not a matter of taste.
# An Annotate COMP is a comment, an annotation or a network box: its tile is
# the box the user drew.
EXEMPT_TYPES = ('annotateCOMP',)

# A tile smaller than this is hard to grab. The parameters are clamped to the
# same value; this is the guard for a value set from a script.
MIN_SIZE = 20


class SizeGuardExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        # False until the first Poll() after the project opened, the tool was
        # dropped in, Active was switched on or perform mode was left.
        self.started = False
        # ids of the networks shown in network editors at the last Poll().
        self.shownIds = ()
        # {'TOP': (width, height), ...}, read from the parameters.
        self.sizes = {}

    # ======================================================================
    # The rule: which size an operator must have
    # ======================================================================
    def ReadSizes(self):
        """Read the size of every family from the tool's parameters.

        A family with its Override toggle on uses its own size, every other
        family uses the main Size. The result is kept in self.sizes so that
        checking an operator does not evaluate parameters again.
        """
        par = self.ownerComp.par
        main = (self._whole(par.Sizew), self._whole(par.Sizeh))
        self.sizes = {}
        for family in FAMILIES:
            name = family.capitalize()                  # 'TOP' -> 'Top'
            if par[name + 'override'].eval():
                self.sizes[family] = (self._whole(par[name + 'sizew']),
                                      self._whole(par[name + 'sizeh']))
            else:
                self.sizes[family] = main
        return self.sizes

    @staticmethod
    def _whole(par):
        """A size parameter as a whole number of network units."""
        return max(MIN_SIZE, int(round(par.eval())))

    def SizeFor(self, o):
        """(width, height) the operator must have, or None to leave it alone."""
        if o.OPType in EXEMPT_TYPES:
            return None
        if self._is_system(o):
            return None
        return self.sizes.get(o.family)

    @staticmethod
    def _is_system(o):
        path = o.path
        return any(path == root or path.startswith(root + '/')
                   for root in SYSTEM_ROOTS)

    # ======================================================================
    # Applying the rule
    # ======================================================================
    def Fix(self, o):
        """Give one operator its size. Returns True if it was changed.

        Only the width and the height are written, so the bottom-left corner
        of the tile (nodeX, nodeY) stays where it was.
        """
        size = self.SizeFor(o)
        if size is None:
            return False
        width, height = size
        if o.nodeWidth == width and o.nodeHeight == height:
            return False
        o.nodeWidth = width
        o.nodeHeight = height
        return True

    def FixChildren(self, comp):
        """Fix the operators of one network. Returns how many were changed."""
        return sum(self.Fix(o) for o in comp.children)

    def FixTree(self, comp):
        """Fix an operator and everything inside it, at any depth.

        An exempt COMP is skipped together with its contents: an Annotate
        COMP is built from operators of its own, and they are not ours.
        """
        if not comp.isCOMP:
            return int(self.Fix(comp))
        if comp.OPType in EXEMPT_TYPES:
            return 0
        inside = comp.findChildren()
        exempt = tuple(o.path + '/' for o in inside
                       if o.OPType in EXEMPT_TYPES)
        changed = int(self.Fix(comp))
        for o in inside:
            if exempt and o.path.startswith(exempt):
                continue
            changed += self.Fix(o)
        return changed

    def FixProject(self):
        """Fix every operator of the project. Returns how many were changed.

        About 3 microseconds per operator, so this is for rare moments only:
        the start of the guard and the save of the project.
        """
        self.ReadSizes()
        return sum(self.FixTree(top) for top in op('/').children)

    # ======================================================================
    # Running: start, the per-frame poll, stop
    # ======================================================================
    def Start(self):
        """The guard begins to run: bring the whole project to the rule."""
        self.FixProject()
        self.started = True
        # Forget the networks seen before the pause, so that the Poll() that
        # called us sets the watchers again.
        self.shownIds = ()

    def Poll(self):
        """Called every frame while the guard runs.

        Looks at which networks are open in network editors. Nothing happens
        while they stay the same. When the user goes into another network,
        the watchers move there and that network is checked: it may hold
        operators a script created while nobody was looking.
        """
        if ui.performMode:
            # The show is on: touch nothing. Leaving perform mode will look
            # like a fresh start, with a full check of the project.
            if self.started:
                self.Stop()
            return
        if not self.started:
            self.Start()
        shown = self.ShownNetworks()
        ids = tuple(sorted(comp.id for comp in shown))
        if ids == self.shownIds:
            return
        self.shownIds = ids
        self.Watch(shown)
        for comp in shown:
            self.FixChildren(comp)

    def ShownNetworks(self):
        """The COMPs whose networks are open in network editor panes."""
        shown = []
        for pane in ui.panes:
            if pane.type != PaneType.NETWORKEDITOR:
                continue
            comp = pane.owner
            if comp is None or comp in shown or self._is_system(comp):
                continue
            if comp.OPType in EXEMPT_TYPES:
                continue
            shown.append(comp)
        return shown

    def Watch(self, networks):
        """Point the OP Execute DAT at the given networks.

        For each network two entries go into its Monitor OPs parameter:
        the COMP itself (reports an added or removed operator) and
        `<COMP>/*` (every operator in it reports a moved or resized tile).

        The list is kept this short on purpose. TouchDesigner registers the
        whole list again on every operator created anywhere in the project,
        so watching the whole project would make each creation slow.
        """
        patterns = []
        for comp in networks:
            patterns.append(comp.path)
            patterns.append(comp.path.rstrip('/') + '/*')   # '/' -> '/*'
        self.ownerComp.op('opExec').par.op = ' '.join(patterns)

    def Stop(self):
        """The guard is paused: Active was switched off or perform mode began.

        The watchers are removed. The next Poll(), whenever it comes, starts
        with a full check of the project.
        """
        self.started = False
        self.shownIds = ()
        self.ownerComp.op('opExec').par.op = ''

    # ======================================================================
    # Reactions to events
    # ======================================================================
    def OnChildrenChange(self, comp):
        """An operator appeared in or left a watched network."""
        if comp.id in self.shownIds:
            self.FixChildren(comp)

    def OnTileChange(self, o):
        """A tile in a watched network was moved or resized.

        Moving is reported too and costs one comparison here. After a fix the
        event comes once more, finds the right size and changes nothing.
        """
        network = o.parent()
        if network is not None and network.id in self.shownIds:
            self.Fix(o)

    def OnSizeParChange(self):
        """A size or an Override toggle on the tool was edited.

        The open networks follow at once. The rest of the project follows
        when its networks are opened or the project is saved.
        """
        if not self.started:
            return
        self.ReadSizes()
        for comp in self.ShownNetworks():
            self.FixChildren(comp)
