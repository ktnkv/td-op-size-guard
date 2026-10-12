# OP Execute DAT: the watchers on the networks open in network editors.
#
# SizeGuardExt.Watch writes its Monitor OPs parameter: for every open network
# the COMP itself and `<COMP>/*`. Its Active parameter is the expression
# `parent().par.Active`, and in perform mode its Monitor OPs list is empty.
#
# TouchDesigner calls these at the end of the frame in which the change
# happened, once per operator.


def onNumChildrenChange(changeOp):
    # An operator was created, pasted, loaded from a tox or deleted in an
    # open network. changeOp is that network's COMP.
    parent().OnChildrenChange(changeOp)


def onUIChange(changeOp):
    # A tile was moved or resized. changeOp is the operator.
    parent().OnTileChange(changeOp)
