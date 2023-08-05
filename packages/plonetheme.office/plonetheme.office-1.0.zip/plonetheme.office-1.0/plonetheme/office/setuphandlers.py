from collective.grok import gs
from plonetheme.office import MessageFactory as _

@gs.importstep(
    name=u'plonetheme.office', 
    title=_('plonetheme.office import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('plonetheme.office.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
