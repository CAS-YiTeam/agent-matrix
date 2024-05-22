from agent_matrix.msg.general_msg import GeneralMsg, SpecialDownstreamSet, SpecialDownstream

def clean_up_unpickleble(kwargs):
    if 'downstream_options' in kwargs:
        for i, ds in enumerate(kwargs['downstream_options']):
            if isinstance(ds, str):
                ...
            elif isinstance(ds, SpecialDownstream):
                kwargs['downstream_options'][i] = ds.downstream
            else:
                kwargs['downstream_options'][i] = ds.agent_id
    return kwargs