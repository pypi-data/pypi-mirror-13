# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.uuid.interfaces import IUUID


class UUIDAwarePermalinkAdapter(object):

    def __init__(self, context):
        self.context = context

    def getPermalink(self):
        context = self.context
        portal_url = getToolByName(context, 'portal_url')
        s_props = getToolByName(context, 'portal_properties').site_properties
        use_view_action = s_props.typesUseViewActionInListings
        if self.context.portal_type in use_view_action:
            suffix = '/view'
        else:
            suffix = ''
        return '%s/resolveuid/%s%s' % (portal_url(), IUUID(context), suffix)
