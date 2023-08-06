#
#    Copyright (C) 2015  Corporation of Balclutha. All rights Reserved.
#
#    For your open source solution, bureau service and consultancy requirements,
#    visit us at http://www.balclutha.org or http://www.last-bastion.net.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from Acquisition import aq_inner
from zope.interface import implements, Invalid
from zope import schema
from z3c.form import button
from plone.supermodel import model

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from plone.directives import form

from ..utils import parse_spec

def minuteConstraint(value):
    if not parse_spec(value, 0, 59):
        raise Invalid(_(u"Invalid minute range"))
    return True

def hourConstraint(value):
    if not parse_spec(value, 0, 23):
        raise Invalid(_(u"Invalid hour range"))
    return True

def monthConstraint(value):
    if not parse_spec(value, 1, 12):
        raise Invalid(_(u"Invalid month range"))
    return True

def dowConstraint(value):
    if not parse_spec(value, 0, 7):
        raise Invalid(_(u"Invalid day of week range"))
    return True

def domConstraint(value):
    if not parse_spec(value, 1, 31):
        raise Invalid(_(u"Invalid day of month range"))
    return True


class IPropertySchema(model.Schema):
    """
    Registration properties
    """

    minute = schema.ASCIILine(
        title=_(u'label_minute', default=u'Minute'),
         description=_(u'help_minute',
                      default=u"Which minute (0-59)."),
        required = True,
        constraint = minuteConstraint,
        default = '0',
        )

    hour = schema.ASCIILine(
        title=_(u'label_hour', default=u'Hour'),
         description=_(u'help_hour',
                       default=u"Which hour (0-23)."),
        required = True,
        constraint = hourConstraint,
        default = '0'
        )

    month = schema.ASCIILine(
        title=_(u'label_Month', default=u'Month'),
         description=_(u'help_month',
                       default=u"Which day (0-12)."),
        required = True,
        constraint = monthConstraint,
        default = '*'
        )

    day_of_month = schema.ASCIILine(
        title=_(u'label_day_of_month', default=u'Day of Month'),
         description=_(u'help_day_of_month',
                       default=u"Which day (1-31)."),
        required = True,
        constraint = domConstraint,
        default = '*'
        )

    day_of_week = schema.ASCIILine(
        title=_(u'label_day_of_week', default=u'Day of Week'),
         description=_(u'help_day_of_week',
                       default=u"Which day of week (0-7). 0 and 7 are Sunday"),
        required = True,
        constraint = dowConstraint,
        default = '*'
        )

    tz = schema.Choice(
        title=_(u'label_timezone', default=u'Timezone'),
        description=_(u'help_timezone',
                      default=u"Which timezone."),
        required = True,
        vocabulary='plone.app.vocabularies.Timezones'
        )

    active = schema.Bool(
        title=_(u'label_active', default=u'Active'),
         description=_(u'help_active',
                      default=u"Is this schedule currently active (invoked)."),
        required = True,
        default = False,
        )




class EditForm(form.SchemaForm):
    schema = IPropertySchema

    label = _(u"Event Schedule")
    description = _(u"Scheduling of background(s) on this item.")

    def update(self):
        # disable Plone's editable border
        #self.request.set('disable_border', True)

        # call the base class version - this is very important!
        super(EditForm, self).update()

    def updateActions(self):
        super(EditForm, self).updateActions()
        self.actions["edit"].addClass("context")
        self.actions["cancel"].addClass("standalone")

    @button.buttonAndHandler(_(u'Edit'))
    def handleEdit(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:
            self.context.manage_editSchedule(data['tz'], 
                                             data['minute'],
                                             data['hour'], 
                                             data['month'], 
                                             data['day_of_month'], 
                                             data['day_of_week'], 
                                             data['active'])
        except Exception, e:
            IStatusMessage(self.request).addStatusMessage(str(e),"error")
            self.status = self.formErrorsMessage
            return

        # Redirect back to the front page with a status message
        IStatusMessage(self.request).addStatusMessage(_(u"Scheduler Properties Edited"),"info")
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)


class ViewForm(EditForm):

    mode = 'display'
