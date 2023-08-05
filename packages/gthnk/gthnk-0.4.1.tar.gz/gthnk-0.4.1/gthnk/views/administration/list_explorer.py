# -*- coding: utf-8 -*-
# gthnk (c) 2014-2016 Ian Dennis Miller

from flask.ext.admin import expose
from flask.ext.security import current_user
from flask.ext.diamond.administration import AuthView
from gthnk.models.item_list import ItemList
import flask


class ListExplorer(AuthView):
    def is_accessible(self):
        return current_user.is_authenticated()

    def is_visible(self):
        return False

    @expose('/')
    def index_view(self):
        return flask.redirect(flask.url_for('admin.index'))

    @expose("/<list_name>/items")
    def items_view(self, list_name):
        item_list = ItemList.find(name=list_name)
        if item_list:
            return self.render('itemlist_explorer/itemlist_view.html', item_list=item_list)
        else:
            return flask.redirect(flask.url_for('admin.index'))
