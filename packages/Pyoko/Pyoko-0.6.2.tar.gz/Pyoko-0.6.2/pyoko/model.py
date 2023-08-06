# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import six
from .node import Node, FakeContext
from . import fields as field
from .db.queryset import QuerySet
from .lib.utils import un_camel, lazy_property, pprnt, un_camel_id
import weakref

super_context = FakeContext()

# kept for backwards-compatibility
from .modelmeta import model_registry

class Model(Node):
    """
    This is base class for any model object.

    Field instances are used as model attributes to represent values.

    .. code-block:: python

        class Permission(Model):
            name = field.String("Name")
            code = field.String("Code Name")

            def __unicode__(self):
                return "%s %s" % (self.name, self.code)

    Models may have inner classes to represent ManyToMany relations, inner data nodes or lists.

    """
    objects = QuerySet
    _TYPE = 'Model'

    _DEFAULT_BASE_FIELDS = {
        'timestamp': field.TimeStamp(),
        'deleted': field.Boolean(default=False, index=True)}
    _SEARCH_INDEX = ''

    def __init__(self, context=None, **kwargs):
        self.key = None
        # holds list of banned fields for current context
        self._unpermitted_fields = []
        # this indicates cell filters applied and we can filter on them
        self._is_unpermitted_fields_set = False
        self._context = context
        self.verbose_name = kwargs.get('verbose_name')
        self.reverse_name = kwargs.get('reverse_name')
        self._pass_perm_checks = kwargs.pop('_pass_perm_checks', False)
        self.objects._pass_perm_checks = self._pass_perm_checks
        self._is_one_to_one = kwargs.pop('one_to_one', False)
        self.title = kwargs.pop('title', self.__class__.__name__)
        self._root_node = self
        self.new_back_links = {}
        kwargs['context'] = context
        super(Model, self).__init__(**kwargs)

        self.objects._set_model(model=self)
        self._instance_registry.add(weakref.ref(self))
        self.saved_models = []


    def __str__(self):
        try:
            return self.__unicode__()
        except AttributeError:
            return "%s object" % self.__class__.__name__


    def get_verbose_name(self):
        """
        Returns:
            Verbose name of the model instance
        """
        return self.verbose_name or self.Meta.verbose_name

    def prnt(self):
        """
        Prints DB data representation of the object.
        """
        print("= = = =\n\n%s object key: \033[32m%s\033[0m" % (self.__class__.__name__, self.key))
        pprnt(self._data or self.clean_value())

    def __eq__(self, other):
        """
        Equivalence of two model instance depends on uniformity of their
        self._data and self.key.
        """
        return self._data == other._data and self.key == other.key

    def __hash__(self):
        # hash is based on self.key if exists or serialization of object's data.
        if self.key:
            return hash(self.key)
        else:
            clean_value = self.clean_value()
            clean_value['timestamp'] = ''
            return hash(str(clean_value))


    def is_in_db(self):
        """
        Deprecated:
            Use "exist" property instead.
        """
        return self.exist

    @property
    def exist(self):
        """
        Used to check if a relation is exist or a model instance is saved to DB or not.

        Returns:
            True if this model instance stored in DB and has a key and False otherwise.

        Examples:
            >>> class Student(Model):
            >>>    #...
            >>>    adviser = Person()
            >>>
            >>> if student.adviser.exist:
            >>>    # do something
        """
        return bool(self.key)

    def get_choices_for(self, field):
        """
        Get the choices for the given fields.

        Args:
            field (str): Name of field.

        Returns:
            List of tuples. [(name, value),...]
        """
        choices = self._fields[field].choices
        if isinstance(choices, six.string_types):
            return [(d['value'], d['name']) for d in self._choices_manager.get_all(choices)]
        else:
            return choices

    def set_data(self, data, from_db=False):
        """
        Fills the object's fields with given data dict.
        Internally calls the self._load_data() method.

        Args:
            data (dict): Data to fill object's fields.
            from_db (bool): if data coming from db then we will
            use related field type's _load_data method

        Returns:
            Self. Returns objects itself for chainability.
        """
        self._load_data(data, from_db)
        return self

    def __repr__(self):
        if not self.is_in_db():
            return six.text_type(self.__class__)
        else:
            return self.__str__()

    def _apply_cell_filters(self, context):
        """
        Applies the field restrictions based on the
         return value of the context's "has_permission()" method.
         Stores them on self._unpermitted_fields.

        Returns:
            List of unpermitted fields names.
        """
        self._is_unpermitted_fields_set = True
        for perm, fields in self.Meta.field_permissions.items():
            if not context.has_permission(perm):
                self._unpermitted_fields.extend(fields)
        return self._unpermitted_fields

    def get_unpermitted_fields(self):
        """
        Gives unpermitted fields for current context/user.

        Returns:
            List of unpermitted field names.
        """
        return (self._unpermitted_fields if self._is_unpermitted_fields_set else
                self._apply_cell_filters(self._context))

    @staticmethod
    def row_level_access(context, objects):
        """
        If defined, will be called just before query
        compiling step and it's output summed up to existing query filter.

        Can be used to implement context-aware implicit filtering.
        You can define your query filters in here to enforce row level access control.

        Args:
            context: An object that contain required user attributes and permissions.
            objects (Queryset): QuerySet object.

        Examples:
            >>> return objects.filter(user=context.user)
        """
        pass

    @lazy_property
    def _name(self):
        return un_camel(self.__class__.__name)

    @lazy_property
    def _name_id(self):
        return "%s_id" % self._name

    def _update_new_linked_model(self, linked_mdl_ins, link):
        """
        Iterates through linked_models of given model instance to match it's
        "reverse" with given link's "field" values.
        """
        for lnk in linked_mdl_ins.get_links():
            mdl = lnk['mdl']
            if not isinstance(self, mdl) or lnk['reverse'] != link['field']:
                continue
            local_field_name = lnk['field']
            # remote_name = lnk['reverse']
            remote_field_name = un_camel(mdl.__name__)
            if not link['o2o']:
                remote_set = getattr(linked_mdl_ins, local_field_name)
                if remote_set._TYPE == 'ListNode' and self not in remote_set:
                    remote_set(**{remote_field_name: self._root_node})
                    linked_mdl_ins.save(internal=True)
            else:
                setattr(linked_mdl_ins, remote_field_name, self._root_node)
                linked_mdl_ins.save(internal=True)

    def _add_back_link(self, linked_mdl, link):
        # creates a new back_link reference
        self.new_back_links["%s_%s_%s" % (linked_mdl.key,
                                          link['field'],
                                          link['o2o'])] = (linked_mdl, link.copy())

    def _handle_changed_fields(self, old_data):
        """
        Looks for changed relation fields between new and old data (before/after save).
        Creates back_link references for updated fields.

        Args:
            old_data: Object's data before save.
        """
        for link in self.get_links(is_set=False):
            fld_id = un_camel_id(link['field'])
            if not old_data or old_data.get(fld_id) != self._data[fld_id]:
                # self is new or linked model changed
                if self._data[fld_id]:  # exists
                    linked_mdl = getattr(self, link['field'])
                    self._add_back_link(linked_mdl, link)

    def _process_relations(self):
        for k, v in self.new_back_links.copy().items():
            del self.new_back_links[k]
            self._update_new_linked_model(*v)

    def pre_save(self):
        """
        Called before object save.
        Can be overriden to do things that should be done just before
        object saved to DB.
        """
        pass

    def post_save(self):
        """
        Called after object save.
        Can be overriden to do things that should be done after object
        saved to DB.
        """
        pass

    def save(self, internal=False):
        """
        Save's object to DB.

        Do not override this method, use pre_save and post_save methods.

        Args:
            internal (bool): True if called within model.
                Used to prevent unneccessary calls to pre_save and
                post_save methods.

        Returns:
             Saved model instance.
        """
        if not internal:
            self.pre_save()
        old_data = self._data.copy()
        self.objects._save_model(self)
        self._handle_changed_fields(old_data)
        self._process_relations()
        if not internal:
            self.post_save()
        return self

    def delete(self):
        """
        This method just flags the object as "deleted" and saves it to DB.
        """
        self.deleted = True
        self.save()


class LinkProxy(object):
    """
    Proxy object for "self" referencing model relations
    Example:

        .. code-block:: python

            class Unit(Model):
                name = field.String("Name")
                parent = LinkProxy('Unit', verbose_name='Upper unit', reverse_name='sub_units')

    """
    _TYPE = 'Link'

    def __init__(self, link_to, one_to_one=False, verbose_name=None, reverse_name=None):
        self.link_to = link_to
        self.one_to_one = one_to_one
        self.verbose_name = verbose_name
        self.reverse_name = reverse_name
