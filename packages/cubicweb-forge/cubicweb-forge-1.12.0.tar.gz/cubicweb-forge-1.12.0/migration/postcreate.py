"""forge post creation script, set application's workflows

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubes.localperms import xperm

# Project workflow
pwf = add_workflow(_('default project workflow'), 'Project')

active = pwf.add_state(_('active development'), initial=True)
asleep = pwf.add_state(_('asleep'))
dead   = pwf.add_state(_('no more maintained'))
moved  = pwf.add_state(_('moved'))

pwf.add_transition(_('temporarily stop development'), active, asleep,
                   ('managers', 'staff'), 'U has_update_permission X')
pwf.add_transition(_('stop maintainance'), (active, asleep), dead,
                   ('managers', 'staff'), 'U has_update_permission X')
pwf.add_transition(_('restart development'), (asleep, dead), active,
                   ('managers', 'staff'), 'U has_update_permission X')
pwf.add_transition(_('project moved'), (active, asleep), moved,
                   ('managers', 'staff'), 'U has_update_permission X')


# Ticket workflow
twf = add_workflow(_('forge ticket workflow'), 'Ticket')

open       = twf.add_state(_('open'), initial=True)
waiting    = twf.add_state(_('waiting feedback'))
rejected   = twf.add_state(_('rejected'))
inprogress = twf.add_state(_('in-progress'))
done       = twf.add_state(_('done'))
vp         = twf.add_state(_('validation pending'))
resolved   = twf.add_state(_('resolved'))
deprecated = twf.add_state(_('deprecated'))
notvalidated = twf.add_state(_('not validated'))

twf.add_transition(_('start'), open, inprogress,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('reject'), (open, inprogress), rejected,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('done'), (open, inprogress), done,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('ask validation'), done, vp,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('deprecate'), open, deprecated,
                   ('managers', 'staff'), xperm('client', 'developer'))
twf.add_transition(_('resolve'), vp, resolved,
                   ('managers', 'staff'), xperm('client'))
twf.add_transition(_('reopen'), (done, rejected), open,
                   ('managers', 'staff'), xperm('client'))
twf.add_transition(_('refuse validation'), (vp,), notvalidated,
                   ('managers', 'staff'), xperm('client'))
twf.add_transition(_('wait for feedback'), (open, inprogress), waiting,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('got feedback'), waiting, None, # go back transition
                   ('managers', 'staff'), xperm('client', 'developer'))
