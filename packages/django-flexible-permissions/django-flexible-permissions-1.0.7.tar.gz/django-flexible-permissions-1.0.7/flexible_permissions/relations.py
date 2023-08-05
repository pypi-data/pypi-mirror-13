from collections import defaultdict

from flexible_permissions._utils import ensure_plural


_relation_registry = {}


def register_relation(cls, paths):
    _relation_registry[cls] = paths


def get_relation_paths(cls):
    """
    Return paths registered for the given class or any of its subclasses
    """

    results = defaultdict(list)
    for registered_cls, paths_registered in _relation_registry.iteritems():
        # Filter out irrelevant classes
        if cls != registered_cls and not issubclass(cls, registered_cls):
            continue

        # Merge multiple registries into a list
        for key, paths in paths_registered.iteritems():
            results[key].extend(ensure_plural(paths))

    return dict(results)


def get_related_target_prefixes(queryset, perms_name, *roles):
    paths = get_relation_paths(queryset.model)
    prefixes = []

    if perms_name in queryset.model._meta.get_all_field_names():
        prefixes.append(perms_name)

    for role in roles:
        role_prefix = role.split(".")[0]

        # Add in the path to the related object, plus perm
        for path in paths.get(role_prefix, []):
            prefixes.append(path + '__' + perms_name)

    return set(prefixes)


def get_related_agent_prefixes(queryset, perms_name, *roles):
    prefixes = []

    if perms_name in queryset.model._meta.get_all_field_names():
        prefixes.append(perms_name)

    return set(prefixes)
