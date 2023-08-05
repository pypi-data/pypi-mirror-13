# encoding: utf-8


def separete_into_groups(list_objs, size_group=100):
    groups = []
    group = []
    for org in list_objs:
        group.append(org)
        if len(group) >= size_group:
            groups.append(group)
            group = []
    if group:
        groups.append(group)
    return groups
