# -*- coding: utf-8 -*-
# copyright 2013-2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-relationwidget views/forms/actions/components for web ui"""

from cwtags.tag import div, p, a, span, h2, h3, input, ul, li, label, button

from logilab.common.decorators import cached, cachedproperty
from logilab.common.registry import Predicate
from logilab.mtconverter import xml_escape

from rql import nodes

from cubicweb.uilib import js
from cubicweb.predicates import empty_rset, match_view, match_form_params
from cubicweb.view import View, EntityStartupView
from cubicweb.web import formwidgets as fwdg, stdmsgs
from cubicweb.web.views import tableview, startup
from cubicweb.web.views.editforms import CreationFormView
from cubicweb.web.views.navigation import (SortedNavigation,
                                           PageNavigationSelect)


_ = unicode

_('required_error')
_('no selected entities')


def boostrap_dialog(w, _, domid, title):
    w('''
<div id="%(domid)s" class="modal fade rw-modal" tabindex="-1" role="dialog">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">%(title)s</h2>
      </div>
      <div class="modal-body">
        <p>%(loading)s</p>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">%(close)s</button>
        <button type="button" class="btn btn-primary save">%(validate)s</button>
      </div>
    </div><!-- /.modal-content -->
  </div><!-- /.modal-dialog -->
</div><!-- /.modal -->'''
% {'domid': xml_escape(domid), 'title': xml_escape(title),
   'loading': _('loading...'), 'validate': _('validate'), 'close': _('close')})


def _ensure_set(value):
    """Given None, a string or some kind of iterable of strings, ensure the
    value is a set of strings (empty in case of None).
    """
    if value is None:
        return frozenset()
    if isinstance(value, (set, frozenset)):
        return value
    if isinstance(value, basestring):
        return frozenset((value,))
    assert isinstance(value, (list, tuple)), 'unexpected type for %r' % value
    return frozenset(value)


class edited_relation(Predicate):
    """Predicate to be used to specialize 'search_related_entities' views
    (:cls:`SearchForRelatedEntitiesView` here) by specifying at least one of

    * `rtype`, the edited relation,
    * `tetype`, the target entity type,
    * `role`, the originating entity role in the relation.

    `rtype` or `tetype` may be given as a string value or as a (list/tuple/set)
    of string values.
    """
    def __init__(self, rtype=None, tetype=None, role=None):
        assert rtype or tetype or role
        self.rtypes = _ensure_set(rtype)
        self.tetypes = _ensure_set(tetype)
        assert role is None or role in ('subject', 'object'), role
        self.role = role

    def __call__(self, cls, _cw, **kwargs):
        if 'relation' not in _cw.form:
            return 0
        rtype, tetype, role = _cw.form['relation'].split(':')
        score = 0
        if rtype in self.rtypes:
            score += 1
        if tetype in self.tetypes:
            score += 1
        if role == self.role:
            score += 1
        return score


def _guess_multiple(form, field, targetetype):
    """guess cardinality of edited relation"""
    eschema = form._cw.vreg.schema[form.edited_entity.cw_etype]
    rschema = eschema.schema[field.name]
    rdef = eschema.rdef(rschema, role=field.role, targettype=targetetype)
    card = rdef.role_cardinality(field.role)
    return card in '*+'


def make_action(form, field, targetetype, widgetuid, dialog_options):
    multiple = _guess_multiple(form, field, targetetype)
    kwargs = {'vid': 'search_related_entities',
              '__modal': 1,
              'multiple': '1' if multiple else '',
              'relation': '%s:%s:%s' % (field.name, targetetype, field.role)}
    if field.widget.no_creation_form:
        kwargs['no_creation_form'] = 1
    entity = form.edited_entity
    if not entity.has_eid():
        # entity is not created yet
        url = form._cw.build_url('ajax', fname='view', etype=entity.__regid__,
                                 **kwargs)
    else:
        # entity is edited, use its absolute url as base url
        url = form._cw.build_url('ajax',
                                 fname='view', eid=entity.eid, **kwargs)
    options = {
        'dialogOptions': dialog_options,
        'editOptions': {
            'required': int(field.required),
            'multiple': multiple,
            'searchurl': url,
        },
    }
    return str(js.jQuery('#' + widgetuid).relationwidget(options))


class RelationFacetWidget(fwdg.Select):
    """ Relation widget with facet selection, providing:

    * a list of checkbox-(de-)selectable related entities

    * a mecanism to trigger the display of a pop-up window for each possible
      target entity type of the relation

    * a pop-up window to:

      - search (using facets) entities to be linked to the edited entity,
      - display (in a paginated table) and select them (using a checkbox on
        each table line)
      - create a new entity to be linked (can be desactivated)

    Partitioning by target entity type provides:

    * potentially lighter result sets
    * pertinent facets (mixing everything would shut down all
      but the most generic ones)
    """
    needs_js = ('cubicweb.ajax.js', 'cubicweb.widgets.js',
                'cubicweb.facets.js', 'cubes.relationwidget.js')
    needs_css = ('cubicweb.facets.css', 'cubes.relationwidget.css')
    related_vid = 'incontext'

    def __init__(self, *args, **kwargs):
        """ RelationFacetWidget creation has following optional config,
        to be passed as keyword arguments:

        - no_creation_form: a value that should be truthy if you want to
          hide the creation form
        - dialog_options: a dict of bootstrap modal options
          (see http://getbootstrap.com/javascript/#modals-options)

        """
        self._dialog_options = kwargs.pop('dialog_options', {})
        self.no_creation_form = kwargs.pop('no_creation_form', False)
        super(RelationFacetWidget, self).__init__(*args, **kwargs)

    def _render(self, form, field, renderer):
        _ = form._cw._
        form._cw.html_headers.define_var(
            'facetLoadingMsg', _('facet-loading-msg'))
        entity = form.edited_entity
        html = []
        w = html.append
        domid = ('widget-%s'
                 % field.input_name(form, self.suffix).replace(':', '-'))
        rtype = entity._cw.vreg.schema.rschema(field.name)
        # prepare to feed the edit controller
        related = self._compute_related(form, field)
        self._render_post(w, entity, rtype, field.role, related, domid)
        # compute the pop-up trigger action(s)
        self._render_triggers(w, domid, form, field, rtype)
        # this is an anchor for the modal dialog
        boostrap_dialog(w, _, domid, title=_(rtype))
        return u'\n'.join(unicode(node) for node in html)

    def _compute_related(self, form, field):
        """ For each already related entity, return a pair (html, unicode(eid))
        where html is the view of each entity with vid the value of
        `self.related_vid`.

        If no entity is already related, use the optional callable `value` of
        the field, from uicfg.
        """
        entity = form.edited_entity
        related = []
        linkedto = form.linked_to.get((field.name, field.role))
        if linkedto:
            related += [(form._cw.entity_from_eid(eid).view(self.related_vid),
                         unicode(eid)) for eid in linkedto]
        if entity.has_eid():
            seen = set(str_eid for html, str_eid in related)
            rset = entity.related(field.name, field.role)
            related += [(e.view(self.related_vid), unicode(e.eid))
                        for e in rset.entities() if unicode(e.eid) not in seen]
        if not related and callable(field.value):
            entity_from_eid = form._cw.entity_from_eid
            view = lambda eid: entity_from_eid(int(eid)).view(self.related_vid)
            related = [(view(eid), eid) for eid in field.value(form, field)]
        return related

    def _render_post(self, w, entity, rtype, role, related, domid):
        name = '%s-%s:%s' % (rtype, role, entity.eid)
        with div(w, id='inputs-for-' + domid,
                 Class='cw-relationwidget-list'):
            for html_label, eid in related:
                with div(w):
                    with label(w, **{'for-name': name}):
                        w(input(name=name, type='checkbox',
                                checked='checked',
                                value=eid,
                                **{'data-html-label': xml_escape(html_label)}))
                        w(html_label)

    def _render_triggers(self, w, domid, form, field, rtype):
        """ According to the number of target entity types for the edited entity
        and considered relation, write the html for:

        * a user message indicating there is no entity that can be linked
        * a button-like link if there is a single possible target etype
        * a drop-down list of possible target etypes if there are more than 1

        In both later cases, actionning them will trigger the dedicated search
        and select pop-up window.
        """
        _ = form._cw._
        dialog_title = _('search entities to be linked to %(targetetype)s')
        actions = []
        target_etypes = rtype.targets(form.edited_entity.e_schema, field.role)
        for target_etype in target_etypes:
            options = self._dialog_options.copy()
            if 'title' not in options:
                options['title'] = dialog_title % {
                    'targetetype': _(target_etype)}
            actions.append((target_etype, make_action(
                form, field, target_etype, domid, options)))
        if not actions:
            w(div(xml_escape(_('no available "%s" to relate to')
                             % ', '.join("%s" % _(e) for e in target_etypes)),
                  **{'class': 'alert alert-warning'}))
        elif len(actions) == 1:
            # Just one: a direct link.
            target_etype, action = actions[0]
            link_title = xml_escape(_('link to %(targetetype)s')
                                    % {'targetetype': _(target_etype)})
            w(p(a(link_title, onclick=xml_escape(action),
                  href=xml_escape('javascript:$.noop()'),
                  Class='btn btn-default cw-relationwidget-single-link'),
                ))
        else:
            # Several possible target types, provide a combobox
            with div(w, Class='btn-group'):
                with button(w, type="button",
                            Class="btn btn-default dropdown-toggle form-control",
                            **{'data-toggle': "dropdown"}):
                    w(_('link to ...') + ' ')
                    w(span(Class="caret"))
                with ul(w, Class='dropdown-menu'):
                    for target_etype, action in actions:
                        w(li(a(xml_escape(_(target_etype.type)),
                               Class="btn-link",
                               onclick=xml_escape(action))))


class SearchForRelatedEntitiesView(EntityStartupView):
    """view called by the edition view when the user asks to search
    for something to link to the edited eid
    """
    __regid__ = 'search_related_entities'
    __select__ = EntityStartupView.__select__ & match_form_params('relation')
    # do not add this modal view in the breadcrumbs history:
    add_to_breadcrumbs = False

    @property
    def rdef(self):
        return self._cw.form['relation'].split(':')

    @cachedproperty
    def has_creation_form(self):
        if self._cw.form.get('no_creation_form', False):
            return False
        rtype, tetype, role = self.rdef
        return self._cw.vreg.schema[tetype].has_perm(self._cw, 'add')

    def nav(self):
        _ = self._cw._
        w = self.w
        rtype, tetype, role = self.rdef
        eid = self.compute_entity().eid
        css_class = 'nav nav-tabs'
        if not self.has_creation_form:
            css_class += ' hidden'
        with ul(w, Class=css_class, role='tablist'):
            with li(w, role='presentation', Class='active'):
                w(a(xml_escape(_('Link/unlink entities')),
                    Class='toggle-cw-relationwidget-table',
                    href='#cw-relationwidget-table-%s' % eid,
                    data_toggle='tab', role='tab'))
            if self.has_creation_form:
                with li(w, role='presentation'):
                    w(a(xml_escape(self._cw._('Link to a new entity')),
                        href='#rw-creation-form-%s' % eid,
                        data_toggle='tab', role='tab'))

    def selection(self):
        _ = self._cw._
        w = self.w
        rtype, tetype, role = self.rdef
        eid = self.compute_entity().eid
        with div(w, id='cw-relationwidget-table-%s' % eid,
                 Class='tab-pane fade in active cw-relationwidget-table'):
            w(h2(u'%s (%s)' % (self._cw.__(tetype), _('selection'))))
            rset = self.linkable_rset()
            with div(w, Class='table-wrapper',
                     data_rql=xml_escape(rset.printable_rql())):
                self.wview('select_related_entities_table', rset=rset)
            # placeholder divs for deletions & additions
            w(div(Class='alert alert-danger hidden cw-relationwidget-alert'))
            # placeholder for linked entities summary
            with div(w, Class='cw-relationwidget-summary'):
                if self._cw.form.get('multiple'):
                    w(h3(_('Selected items')))
                else:
                    w(h3(_('Selected item')))
                w(ul(Class=('cw-relationwidget-linked-summary'
                            ' cw-relationwidget-list')))

    def creation(self):
        rtype, tetype, role = self.rdef
        eid = self.compute_entity().eid
        with div(self.w, id="rw-creation-form-%s" % eid,
                 Class='tab-pane fade rw-creation-form', data_etype=tetype):
            self.wview('rw-creation', etype=tetype)

    def content(self):
        with div(self.w, Class='panel tab-content'):
            self.selection()
            if self.has_creation_form:
                self.creation()

    def call(self):
        self.nav()
        self.content()

    def linkable_rset(self):
        """Return rset of entities to be displayed as possible values for the
        edited relation. You may want to override this.
        """
        entity = self.compute_entity()
        rtype, tetype, role = self.rdef
        rql, args = entity.cw_linkable_rql(rtype, tetype, role,
                                           ordermethod='fetch_order',
                                           vocabconstraints=False)
        return self._cw.execute(rql, args)

    @cached
    def compute_entity(self):
        if self.cw_rset:
            entity = self.cw_rset.get_entity(0, 0)
        else:
            etype = self._cw.form['etype']
            entity = self._cw.vreg['etypes'].etype_class(etype)(self._cw)
            entity.eid = next(self._cw.varmaker)
        return entity


startup.ManageView.skip_startup_views.add(SearchForRelatedEntitiesView.__regid__)  # noqa


class SelectEntitiesTableLayout(tableview.TableLayout):
    __regid__ = 'select_related_entities_table_layout'
    display_filter = 'top'
    hide_filter = False


class SelectMainEntityColRenderer(tableview.MainEntityColRenderer):
    """Custom renderer of the main entity in the table of selectable entities
    that includes a DOM attribute to be used for selection on JS side.
    """
    attributes = {'data-label-cell': 'true'}


class SelectEntitiesColRenderer(tableview.RsetTableColRenderer):

    def render_header(self, w):
        # do not add headers
        w(u'')

    def render_cell(self, w, rownum):
        entity = self.cw_rset.get_entity(rownum, 0)
        w(input(type='checkbox', value=entity.eid))

    def sortvalue(self, rownum):
        return None


class SelectEntitiesTableView(tableview.EntityTableView):
    """Table view of the selectable entities in the relation widget

    Selection of columns (and respective renderer) can be overridden by
    updating `columns` and `column_renderers` class attributes.
    """
    __regid__ = 'select_related_entities_table'
    layout_id = 'select_related_entities_table_layout'
    columns = ['select', 'entity']
    column_renderers = {
        'select': SelectEntitiesColRenderer('one', sortable=False),
        'entity': SelectMainEntityColRenderer(),
    }

    def page_navigation_url(self, navcomp, _path, params):
        params['divid'] = self.domid
        params['vid'] = self.__regid__
        return navcomp.ajax_page_url(**params)

_match_rw_view = match_view(SelectEntitiesTableView.__regid__)

class RelationWidgetNavigationMixin(object):

    page_size_property = 'relationwidget.table-page-size'

    def render_link_display_all(self, w):
        '''Do not render a "display all" link when the rset size is bigger than
        `display_all_limit`, but only the number of entities'''
        limit = self._cw.property_value('relationwidget.display-all-limit')
        if len(self.cw_rset) > limit:
            with ul(w, Class="pagination pull-right rw-total-size"):
                with li(w):
                    w(span(xml_escape(self._cw._('total: %s entities')
                                      % len(self.cw_rset))))
        else:
            super(RelationWidgetNavigationMixin,
                  self).render_link_display_all(w)


class RelationWidgetPageNavigationSelect(RelationWidgetNavigationMixin,
                                         PageNavigationSelect):
    __select__ = PageNavigationSelect.__select__ & _match_rw_view


class RelationWidgetSortedNavigation(RelationWidgetNavigationMixin,
                                     SortedNavigation):
    __select__ = SortedNavigation.__select__ & _match_rw_view


def rset_main_type(rset):
    """Try to get the type of the first variable of the result set.
    None if not found.
    """
    rqlst = rset.syntax_tree()
    if len(rqlst.children) > 1:
        return None
    select = rqlst.children[0]
    if not isinstance(select.selection[0], nodes.VariableRef):
        return None
    varname = select.selection[0].name
    etypes = set(sol[varname] for sol in select.solutions)
    if len(etypes) != 1:
        return None
    return etypes.pop()


class NoEntitiesToSelectView(View):
    """Fallback view to be used when there is no entity to relate
    """
    __regid__ = 'select_related_entities_table'
    __select__ = empty_rset()

    def call(self, **kwargs):
        self.w(u'<div class="alert alert-info">%s</div>\n'
               % xml_escape(self._cw._('No entity to put in relation')))


class RelationWidgetCreationFormView(CreationFormView):
    __regid__ = 'rw-creation'

    def form_title(self, entity):
        "override to replace the h1 by a h2"
        ptitle = self._cw._(self.title)
        self.w(u'<div class="formTitle"><h2>%s %s</h2></div>' % (
            entity.dc_type(), ptitle and '(%s)' % ptitle))

    def init_form(self, form, entity):
        # __domid hidden is set in form constructor, so we have to override it
        form.field_by_name('__domid').value = form.domid = 'rw-creation-form'
        form.cwtarget = 'rw-eformframe'
        form.add_hidden('__onsuccess',
                        'window.parent.cw.cubes.relationwidget.created')
        form.add_hidden('__onfailure',
                        'window.parent.cw.cubes.relationwidget.creationFailed')
        form.form_buttons = [
            fwdg.SubmitButton(),
            fwdg.Button(stdmsgs.BUTTON_CANCEL,
                attrs={'class': 'btn btn-default rw-creation-cancel'})]
