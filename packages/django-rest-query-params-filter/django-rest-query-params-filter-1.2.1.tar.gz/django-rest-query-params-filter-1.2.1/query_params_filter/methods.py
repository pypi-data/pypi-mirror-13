from copy import copy

from rest_framework.serializers import HyperlinkedModelSerializer

from .utils import remove_empty, can_be_str


def get_key_value_filter(key_values, ns):
    # Receives {'field1': 'value1|value2', 'field2': 'value3,value4', 'field3': 'value5', 'field4': 'number',
    #           'pure-field5': any_weird_type_or_pure_value_you_want}
    # Returns this string:  "field1__range": ["value1", "value2"],
    #                       "field2__in": ["value3", "value4"],
    #                       "field3__icontains": "value5",
    #                       "field4": "number",
    #                       "field5": pure_value_XY  # A variable created in "ns" with the value
    to_query = ''
    final_i1 = len(key_values)
    # Iterate keys-values
    for i1, (key, values) in enumerate(key_values.items()):
        range_query = False

        pure_query = False
        if key.startswith('pure-'):
            pure_query = True
            key = key.replace('pure-', '')

        if not isinstance(values, bool) and not isinstance(values, int) and not pure_query:
            if '|' in values:
                # Range query case (separator: "|", or Pipe)
                # Makes "1|2" turn into ["1","2"], "1," into ["1"] and a "length" different of 2 aborts the loop
                values_list = remove_empty(values.split('|'))
                if len(values_list) != 2:
                    continue
                range_query = True
            else:
                # List of values case
                # Makes "1,2" turn into ["1","2"] and "1," into ["1"]
                values_list = remove_empty(values.split(','))
        else:
            values_list = values

        is_bool = isinstance(values_list, bool)
        is_int = isinstance(values_list, int)
        final_i2 = 1 if is_bool or pure_query or is_int else len(values_list)
        # Iterate list of values
        for i2, a_value in ([[0, values_list]] if is_bool or is_int or pure_query else enumerate(values_list)):
            if pure_query:
                key_a_value = 'pure_value_' + str(i1) + str(i2)
                ns.update({key_a_value: a_value})
            # Or "like query" or "range query", not both
            like_query = can_be_str(a_value) if not pure_query and not range_query and not is_bool else False
            # Handle single and multiple values mounting single query or "__in"/"__range" with a list
            to_query += (('"' + key +
                          ('__icontains": ' if like_query else
                           ('__range": ' if range_query else
                            ('__in": ' if final_i2 > 1 and not pure_query else '": '))) if i2 == 0 else '') +
                         ('[' if i2 == 0 and final_i2 > 1 else '') +
                         (str(a_value) if is_bool or is_int
                          else ('"' + a_value + '"' if not pure_query else key_a_value)) +
                         (']' if final_i2 == i2 + 1 and final_i2 > 1 else '') +
                         (', ' if i2 + 1 != final_i2 or i1 + 1 != final_i1 else ''))
    return to_query


def set_serializer(instance, request):
    if 'base' in instance.serializer_base or instance.serializer_class:
        fields, exclude, raw_fields = [], [], []
        if 'fields' in request.query_params:
            raw_fields = remove_empty(request.query_params['fields'].split(','))
        for raw_field in raw_fields:
            if raw_field.startswith('-'):
                exclude.append(raw_field.replace('-', ''))
            else:
                fields.append(raw_field)

        instance.serializer_class = serializer_factory(model=(None if 'model' not in instance.serializer_base
                                                              else instance.serializer_base['model']),
                                                       # "base" is priority here
                                                       base=(instance.serializer_class
                                                             if 'base' not in instance.serializer_base
                                                             else instance.serializer_base['base']),
                                                       fields=tuple(fields), exclude=tuple(exclude))
    # assign it to "self.serializer_class"
    return instance.serializer_class


def serializer_factory(model=None, base=HyperlinkedModelSerializer, fields=None, exclude=None, order_by=None):
    # Source for this f***ing solution: http://stackoverflow.com/a/27468982/4694834
    attrs = {}
    if model:
        attrs.update({'model': model})
    # "fields" take priority over "exclude"
    if fields:
        if hasattr(base.Meta, 'exclude'):
            del base.Meta.exclude
        attrs.update({'fields': fields})
    if exclude and not fields:
        if hasattr(base.Meta, 'fields'):
            fields = list(base.Meta.fields)
            for field in exclude:
                fields.remove(field)
            attrs.update({'fields': tuple(fields)})
        else:
            attrs.update({'exclude': exclude})

    parent = (object,)
    if hasattr(base, 'Meta'):
        parent = (base.Meta, object)
    Meta = type('Meta', parent, attrs)
    if model:
        class_name = model.__name__ + 'Serializer'
    else:
        class_name = 'CustomSerializer'
    return type(base)(class_name, (base,), {'Meta': Meta, })


def filter_selected_fields(query_params, selected_fields):
    if selected_fields:
        dont_filter, do_filter = [], []
        for selected_field in selected_fields:  # Mount both selected and not selected fields
            if selected_field.startswith('-'):
                dont_filter.append(selected_field.replace('-', ''))
            else:
                do_filter.append(selected_field)
        new_query_params = copy(query_params)
        if do_filter or dont_filter:
            condition = 'key not in do_filter' if do_filter else 'key in dont_filter'  # Mount the string to eval
            for key, value in new_query_params.items():
                if eval(condition):
                    del query_params[key]

    return query_params
