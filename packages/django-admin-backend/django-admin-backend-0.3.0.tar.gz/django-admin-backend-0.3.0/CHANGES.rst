0.2.0 (not released yet)
------------------------

* Adjusted multiple imports:

  - Forms, formfields and widgets should be now always imported from
    ``django_backend.forms``. Example::

    # OLD import, will no longer work
    from django_backend.backend.base.formfields import SelectRelatedField

    # NEW import
    from django_backend.forms import SelectRelatedField

* Add ``ManageRelatedField`` that can inline a list page of a related model
  in the change view.

* Add ``GenericRelationListField`` that can show a reorderable list related
  by a intermediary model with a generic foreign key.

0.1.0
-----

* Initial release.
