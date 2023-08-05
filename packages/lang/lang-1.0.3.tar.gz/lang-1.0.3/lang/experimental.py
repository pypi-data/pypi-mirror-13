

def _get_class(func):
    func_name = func.func_name
    code = func.func_code
    for name, obj in func.func_globals.iteritems():
        if hasattr(obj, '__dict__') and func_name in obj.__dict__:
            comp_func = obj.__dict__[func_name]
            import ipdb; ipdb.set_trace()
            pass
            return obj
    return None

# Final function decorator
def final(func):

    import ipdb; ipdb.set_trace()
    def Wrapper(*args, **kwargs):
        cls = _get_class(func)
        return func(*args, **kwargs)

    return Wrapper
