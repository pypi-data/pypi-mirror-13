try:
    from cubicweb import _
except ImportError:
    _ = unicode

create_entity('CWGroup', name=_('staff'))
