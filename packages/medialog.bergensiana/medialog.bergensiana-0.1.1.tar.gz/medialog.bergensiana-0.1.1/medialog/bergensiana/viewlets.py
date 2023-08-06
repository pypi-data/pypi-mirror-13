from plone.memoize.view import memoize
from zope.i18n import translate
from zope.viewlet.interfaces import IViewlet
from AccessControl import getSecurityManager
from Acquisition import aq_base, aq_inner
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import IViewView
from plone.protect.utils import addTokenToUrl
from plone.app.layout.viewlets.common import ViewletBase


class TopperViewlet(ViewletBase):
    index = ViewPageTemplateFile('topper.pt')

    def update(self):
        super(TopperViewlet, self).update()
        self.year = date.today().year

    def render_topper_portlets(self):
        """
        You might ask, why is this necessary. Well, let me tell you a story...

        plone.app.portlets, in order to provide @@manage-portlets on a context,
        overrides the IPortletRenderer for the IManageContextualPortletsView view.
        See plone.portlets and plone.app.portlets

        Seems fine right? Well, most of the time it is. Except, here. Previously,
        we were just using the syntax like `provider:plone.footerportlets` to
        render the footer portlets. Since this tal expression was inside
        a viewlet, the view is no longer IManageContextualPortletsView when
        visiting @@manage-portlets. Instead, it was IViewlet.
        See zope.contentprovider

        In to fix this short coming, we render the portlet column by
        manually doing the multi adapter lookup and then manually
        doing the rendering for the content provider.
        See zope.contentprovider
        """
        portlet_manager = getMultiAdapter(
            (self.context, self.request, self.__parent__), name='plone.topperportlets')
        portlet_manager.update()
        return portlet_manager.render()