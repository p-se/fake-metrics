from typing import Dict



def build_metric(metric: Dict[str, str]):
    """
    >>> build_metric({
    ...     '__name__': 'foobar',
    ...     'instance': 'localhost:888',
    ...     'job': 'ceph-mgr',
    ...     'pool_id': '9',
    ... })
    'foobar{instance="localhost:888",job="ceph-mgr",pool_id="9"}'
    """
    assert '__name__' in metric, '__name__ must be a key in metric'
    name = metric['__name__']
    metric_copy = metric.copy()
    del metric_copy['__name__']
    labels = '{' + ','.join(f'{k}="{v}"' for k, v in metric_copy.items()) + '}'
    return f'{name}{labels}'
