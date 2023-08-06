import json
from collections import OrderedDict
from django.db import models
from django.core import paginator
from django.utils import six, encoding
from rest_framework import serializers, pagination, metadata, response, exceptions
from rest_framework.fields import SkipField
from jkspy.helpers import dprint
from jkspy.django.shortcuts import makeSearchCriterion

def view_name(cls, suffix=None):
    if hasattr(cls, 'view_name'):
        return cls.view_name()
    return cls.__name__

class DefaultPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100
     
    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        for key, val in request.query_params.items():
            print(key+': '+str(val))
        
        if 'searchword' in request.query_params:
            searchword = request.query_params['searchword']
            criterion = makeSearchCriterion(searchword, globals()[queryset.model.__name__+'Serializer'].Meta.fields)            
            queryset = queryset.filter(criterion)
             
        if 'filters' in request.query_params:
            filters = json.loads(request.query_params['filters'])
            pfil = {}
            for key, val in filters.items():
                if type(val) == list:
                    if len(val) > 0:
                        pfil[key+'__in'] = val
                else:
                    pfil[key] = val
                    
            queryset = queryset.filter(models.Q(**pfil))
         
        if 'sort' in request.query_params and request.query_params['sort']:
            try:
                sortlist = json.loads(request.query_params['sort'])
                queryset = queryset.order_by(*sortlist)
            except ValueError:
                queryset = queryset.order_by(request.query_params['sort'])
#         try:
#             sort = request.query_params['sort']
#             print(sort)
#             if sort:
#                 queryset = queryset.order_by(sort)                
#         except KeyError:
#             pass
         
        page_size = self.get_page_size(request)
        if not page_size:
            return None
 
        pgn = paginator.Paginator(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = pgn.num_pages
 
        try:
            self.page = pgn.page(page_number)
        except paginator.InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise exceptions.NotFound(msg)
 
        if pgn.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True
 
        self.request = request
        return list(self.page)
 
    def get_paginated_response(self, data):
        return response.Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

class DisplayField(serializers.ReadOnlyField):
    def __init__(self, *args, **kwargs):
        if 'display_func' in kwargs.keys():
            self.display_func = kwargs['display_func']
            del kwargs['display_func']
        kwargs['source'] = '*'
        super(DisplayField, self).__init__(*args, **kwargs)
        self.type = 'string'
    
    def to_representation(self, value):
#         dprint(value)
#         dprint(self.parent.instance, 0)
#         dprint(self.parent, 1)
#         dprint(self.parent.instance)
        if hasattr(self, 'display_func'):
            return self.display_func(value)
        return self.parent.instance.__str__()

class NestableSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields
        
        for field in fields:
            if isinstance(field, serializers.Serializer):
                attribute = field.get_attribute(instance)
                nested_fields = NestableSerializer.to_representation(field, attribute)
                for key, val in nested_fields.items():
                    ret[field.field_name+'__'+key] = val
            else:
                try:
                    attribute = field.get_attribute(instance)
                except SkipField:
                    continue
    
                if attribute is None:
                    # We skip `to_representation` for `None` values so that
                    # fields do not have to explicitly deal with that case.
                    ret[field.field_name] = None
                else:
                    ret[field.field_name] = field.to_representation(attribute)
        return ret
#         return super(NestableSerializer, self).to_representation(instance)
    
    def to_internal_value(self, data):
        return super(NestableSerializer, self).to_internal_value(data)
    
class DefaultMetadata(metadata.SimpleMetadata):
    def __init__(self, *args, **kwargs):
        super(DefaultMetadata, self).__init__(*args, **kwargs)
        self.label_lookup[ DisplayField ] = 'string'
    
    def determine_metadata(self, request, view):
        metadata = OrderedDict()
        metadata['name'] = view.get_view_name()
        metadata['description'] = view.get_view_description()
        metadata['renders'] = [renderer.media_type for renderer in view.renderer_classes]
        metadata['parses'] = [parser.media_type for parser in view.parser_classes]
        if hasattr(view, 'get_serializer'):
            actions = self.determine_actions(request, view)
            if actions:
                metadata['actions'] = actions
        return metadata
    
    def get_serializer_info(self, serializer):
        """
        Given an instance of a serializer, return a dictionary of metadata
        about its fields.
        """
        ret = OrderedDict()
        if hasattr(serializer, 'child'):
            # If this is a `ListSerializer` then we want to examine the
            # underlying child serializer instance instead.
            serializer = serializer.child
        
        for field_name, field in serializer.fields.items():
#             print(type(field))
            if isinstance(field, serializers.Serializer):
                nested_fields = DefaultMetadata.get_serializer_info(self, field)
                for key, val in nested_fields.items():
                    ret[field.field_name+'__'+key] = val
            else:
                ret[field_name] = self.get_field_info(field)
        return ret
        
    def get_field_info(self, field):
        """
        Given an instance of a serializer field, return a dictionary
        of metadata about it.
        """
        field_info = OrderedDict()
        field_info['type'] = self.label_lookup[field]
        field_info['required'] = getattr(field, 'required', False)

        attrs = [
            'read_only', 'label', 'help_text',
            'min_length', 'max_length',
            'min_value', 'max_value'
        ]

        for attr in attrs:
            value = getattr(field, attr, None)
            if value is not None and value != '':
                field_info[attr] = encoding.force_text(value, strings_only=True)

        if getattr(field, 'child', None):
            field_info['child'] = self.get_field_info(field.child)
        elif getattr(field, 'fields', None):
            field_info['children'] = self.get_serializer_info(field)

        if not field_info.get('read_only') and hasattr(field, 'choices'):
            field_info['choices'] = [
                {
                    'value': choice_value,
                    'display_name': encoding.force_text(choice_name, strings_only=True)
                }
                for choice_value, choice_name in field.choices.items()
            ]

        return field_info