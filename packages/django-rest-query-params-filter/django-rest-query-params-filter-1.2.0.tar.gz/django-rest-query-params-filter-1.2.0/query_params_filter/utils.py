from copy import copy


def mix_dicts_self_params(self: dict, params: dict, priority='params'):
    # Mix the "self" and the "params", with default priority to "params"
    self = copy(self) if self else {}  # Returning a copy because the update was making it default in all requests
    params = params if params else {}
    if priority == 'self':
        params.update(self)
        return params
    elif priority == 'params':
        self.update(params)
        return self


def filter_fields(objects: list, query_params):

    raw_fields = remove_empty(query_params['fields'].split(',')) if 'fields' in query_params else []

    result, exclude, fields = [], [], []

    for field in raw_fields:
        if field.startswith('-'):
            exclude.append(field.replace('-', ''))
        else:
            fields.append(field)

    for obj in objects:
        filtered_fields = {} if fields else obj.copy()
        for key, value in obj.items():
            if key in fields:
                filtered_fields[key] = obj[key]
            elif key in exclude and not fields:
                del filtered_fields[key]
        result.append(filtered_fields)

    return result


def can_be_str(string: str):
    try:
        int(string)  # Check if can be integer
    except ValueError:
        try:
            float(string)  # Check if can be float
        except ValueError:
            try:
                if string not in ['True', 'False']:
                    raise ValueError  # Check if can be boolean
            except ValueError:
                return True
    return False


def takeoff_list(dict: dict):
    # If use same "dict", it repeats items if there's a special character at 0 (don't have a clue)
    new_dict = {}
    for key, value in dict.items():
        new_dict.update({key: value[0]})
    return new_dict


def single_value(string: str):
    result = remove_empty(string.split(','))
    return result[0] if len(result) == 1 else False


def url_encoder(dict: dict):
    query_params = ''
    for i, (key, value) in enumerate(dict.items()):
        n = 1 if isinstance(value, str) else (2 if value else 0)
        if n and key != 'id':
            query_params += ('&' if i > 0 else '') + key + '=' + (','.join(value) if n > 1 else value)
    return query_params


def remove_empty(some_list: list):
    return [x for x in some_list if x]
