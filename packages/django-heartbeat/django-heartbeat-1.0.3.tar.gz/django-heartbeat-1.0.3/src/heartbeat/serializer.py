from collections import OrderedDict


def heartbeat_format(request, checker_module):
    data = checker_module.check(request)
    if isinstance(data, list):
        print(data)
        data = sorted(data)
    if isinstance(data, dict):
        data = OrderedDict(sorted(data.items()))
    return {checker_module.__name__.split('.')[-1]: data}

#
# def sort_dict_in_depth(dic):
#     for i in range(len(dic)):
#         if isinstance(dic, str):
