# Parameter Execute DAT on the tool's Active parameter.
#
# Switching Active off makes frameExec and opExec inactive, so nothing calls
# the extension any more. This DAT tells it to remove the watchers first.
#
# Switching Active on needs nothing here: the first Poll() after a pause
# starts the guard again with a full check of the project.


def onValueChange(par, prev):
    if not par.eval():
        parent().Stop()
