import collections


def showarray(entities, columns):
    fields = [column[0] for column in columns]
    labels = [column[1] for column in columns]

    rows = []
    for entity in entities:
        if isinstance(entity, collections.Mapping):
            rows.append([entity.get(field) for field in fields])
        else:
            rows.append([entity])

    return (labels, rows)


def showone(entity, columns):
    labels, rows = showarray([entity], columns)
    return (labels, rows[0])


def parse_kv(pairs):
    def _to_kv(pair):
        if '=' not in pair:
            return (pair, True)
        return pair.split('=', 1)
    return dict([_to_kv(param) for param in pairs])
