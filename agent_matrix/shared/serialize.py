

def clean_up_unpickleble(kwargs):
    if 'downstream_options' in kwargs:
        for i, ds in enumerate(kwargs['downstream_options']):
            if isinstance(ds, str):
                ...
            else:
                kwargs['downstream_options'][i] = ds.agent_id
    return kwargs