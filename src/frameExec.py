# Execute DAT: the clock of the guard.
#
# Its Active parameter is the expression `parent().par.Active`, so with the
# tool switched off TouchDesigner calls nothing here.


def onFrameStart(frame):
    # Which networks are open now? See SizeGuardExt.Poll.
    # In perform mode Poll() returns at once.
    parent().Poll()


def onProjectPreSave():
    # The saved file holds every operator at its size, including the ones in
    # networks nobody opened since a script created them.
    if not ui.performMode:
        parent().FixProject()
