class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


def dict_to_object(dictObj):
    if not isinstance(dictObj, dict):
        return dictObj
    inst = Dict()
    for k, v in dictObj.items():
        inst[k] = dict_to_object(v)
    return inst

if __name__ == '__main__':
    sum_result_obj ={}
    sum_result_obj['pre_sum'] = 0
    sum_result_obj['sum'] = 0
    sum_result_obj['pre_day'] = 4
    sum_result_obj['cur_day'] = None
    sum_obj = dict_to_object(sum_result_obj)
    print(sum_obj.cur_day)