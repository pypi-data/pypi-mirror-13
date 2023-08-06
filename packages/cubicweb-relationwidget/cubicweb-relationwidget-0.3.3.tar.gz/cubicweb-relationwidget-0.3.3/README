Summary
-------

This cube provides a generic but ergonomic widget to link an edited
entity to several others for a given relation. It provides:

* a list of checkbox-(de-)selectable related entities

* a mecanism to trigger the display of a pop-up window for each possible
  target entity type of the relation

* in the pop-up window, the end-user can:

  - search (using facets) entities to be linked to the edited entity,
  - display (in a paginated table) and select them (using a checkbox on
    each table line)
  - create a new entity to be linked (can be desactivated)


Usage
-----

Select the relation widget for your relation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the two following mecanisms to configure the user interface:

- either `cubicweb.web.uihelper.FormConfig`::

    from cubicweb.web import uihelper
    from cubes.relationwidget.views import RelationFacetWidget

    class MyEntityConfig(uihelper.FormConfig):
          etype = 'MyEntity'
          # Move `my_relation` into the attribute section:
          rels_as_attrs = ('my_relation', )
          # Edit `my_relation` using RelationFacetWidget:
          widgets = dict(
              my_relation=RelationFacetWidget,
          )

- or directly via `uicfg.autoform_field_kwarg`::

    from cubicweb.web.views import uicfg
    from cubes.relationwidget.views import RelationFacetWidget

    # edit the relation as attribute.
    uicfg.autoform_section.tag_subject_of(
        ('MyEntity', 'my_relation', '*'),
        formtype=('main', 'muledit'), section='attributes')

    # add the RelationFacetWidget for `my_relation`
    uicfg.autoform_field_kwargs.tag_subject_of(
        ('MyEntity', 'my_relation', '*'), {'widget': RelationFacetWidget})


Configure it (optional)
~~~~~~~~~~~~~~~~~~~~~~~

If you want to desactivate the ability to create a new entity to be
linked to the edited one, you can do it:

* for a single relation using uicfg again::

      uicfg.autoform_field_kwargs.tag_subject_of(
      ('MyEntity', 'my_relation', '*'),
      {'widget': RelationFacetWidget(no_creation_form=True)})

* application-wide by overriding `SearchForRelatedEntitiesView.has_creation_form`
  to always return False::

      from cubes.relationwidget.view import SearchForRelatedEntitiesView

      class MySearchForRelatedEntitiesView(SearchForRelatedEntitiesView):

          @property
          def has_creation_from(self):
              return False

      def registration_callback(vreg):
          vreg.register_and_register(MySearchForRelatedEntitiesView,
                                     SearchForRelatedEntitiesView)

There is also a `dialog_options` dictionary that can be used to
configure the bootstrap modal window (see
http://getbootstrap.com/javascript/#modals-options)::

      uicfg.autoform_field_kwargs.tag_subject_of(
      ('MyEntity', 'my_relation', '*'),
      {'widget': RelationFacetWidget(dialog_options={'keyboard': False})})
