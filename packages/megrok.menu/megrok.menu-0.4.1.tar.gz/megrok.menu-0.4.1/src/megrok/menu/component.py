# -*- coding: utf-8 -*-

import martian.util
import grokcore.component
from martian.error import GrokImportError
from zope.browsermenu.menu import BrowserMenu


class Menu(BrowserMenu):
    pass


class SubMenuItem(BrowserMenu):
    pass


class menuitem(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE

    def factory(self, menu, icon=None, filter=None, order=None, extra=None):
        if martian.util.check_subclass(menu, Menu):
            menu = grokcore.component.name.bind().get(menu)
        if martian.util.not_unicode_or_ascii(menu):
            raise GrokImportError(
                "You can only pass unicode, ASCII, or a subclass "
                "of megrok.menu.Menu to the '%s' directive." % self.name)
        return (menu, icon, filter, order, extra)
