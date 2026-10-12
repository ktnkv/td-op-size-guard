# Parameter Execute DAT on the tool's size parameters: Size, every
# `<Family>override` toggle and every `<Family>size`.


def onValueChange(par, prev):
    # Read the sizes again and apply them to the open networks.
    parent().OnSizeParChange()
