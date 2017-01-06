def showarray(entities, columns):
    fields = [column[0] for column in columns]
    labels = [column[1] for column in columns]

    rows = []
    for entity in entities:
        rows.append([entity.get(field) for field in fields])

    return (labels, rows)


def showone(entity, columns):
    labels, rows = showarray([entity], columns)
    return (labels, rows[0])
