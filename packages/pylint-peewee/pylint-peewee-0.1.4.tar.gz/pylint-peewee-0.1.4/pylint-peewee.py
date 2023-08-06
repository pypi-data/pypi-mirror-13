from astroid import MANAGER
from astroid import scoped_nodes

def register(linter):
    pass


class DummyQuery(object):
    """Mock for pylint"""
    require_commit = None

    methods = (
        '_add_query_clauses',
        '_clone_joins',
        '_clone_attributes',
        'clone',
        '__repr__',
        'scalar',
        'execute',
        '_execute',
        'sql',
        'compiler',
        'filter',
        'convert_dict_to_node',
        'ensure_join',
        'switch',
        'join',
        'orwhere',
        'where',
        '_model_shorthand'
    )

    def passer(self, *args, **kwargs):
        pass

    def __init__(self):
        self.register(self.methods)

    def register(self, methods):
        for m in methods:
            setattr(self, m, self.passer)


class DummySelect(DummyQuery):
    _node_type = None

    def __init__(self):
        super(DummySelect, self).__init__()

        new_methods = (
            'compound_op',
            '_compound_op_static',
            '__or__',
            '__and__',
            '__sub__',
            '__xor__',
            'union_all',
            '__select',
            'select',
            'from_',
            'group_by',
            'having',
            'order_by',
            'window',
            'limit',
            'offset',
            'paginate',
            'distinct',
            'for_update',
            'naive',
            'tuples',
            'dicts',
            'aggregate_rows',
            'alias',
            'annotate',
            'aggregate',
            '_aggregate',
            'count',
            'wrapped_count',
            'exists',
            'get',
            'first',
            'verify_naive',
            'get_query_meta',
            '_get_result_wrapper',
            'execute',
            '__iter__',
            'iterator',
            '__getitem__',
            '__len__',
            '__hash__',
        )

        self.register(new_methods)


class DummyWriteQuery(DummyQuery):
    def __init__(self):
        super(DummyWriteQuery, self).__init__()

        new_methods = (
            'requires_returning',
            'returning',
            'tuples',
            'dicts',
            'get_result_wrapper',
            '_execute_with_result_wrapper',
        )

        self.register(new_methods)


class DummyUpdate(DummyWriteQuery):
    def __init__(self):
        super(DummyUpdate, self).__init__()

        new_methods = (
            'on_conflict',
            '__iter__',
            'iterator',
        )

        self.register(new_methods)


class DummyInsert(DummyWriteQuery):
    def __init__(self):
        super(DummyInsert, self).__init__()

        new_methods = (
            '_iter_rows',
            'upsert',
            'on_conflict',
            'return_id_list',
            'is_insert_returning',
            '_insert_with_loop'
        )

        self.register(new_methods)


class DummyDelete(DummyWriteQuery):
    pass



def transform(cls):
    if 'db.Model' in cls.basenames:
        overrides = {
            'select': DummySelect,
            'get': DummySelect,
            'insert': DummyInsert,
            'update': DummyUpdate,
            'delete': DummyDelete,
        }
        for key in overrides:
            cls.locals[key] = [overrides[key]()]

MANAGER.register_transform(scoped_nodes.Class, transform)
