def add_decorator(*targets, decorator=None):
    if decorator is None:
        raise ValueError('The decorator must be defined')
    for target in targets:
        yield decorator(target)