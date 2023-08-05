import gremlinpy.config
from gremlinpy.exception import GremlinError, StatementError


class Statement(object):

    def set_gremlin(self, gremlin):
        self.gremlin = gremlin

        return self

    def build(self):
        raise NotImplementedError('Gremlinpy statements need a build method')

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        self.build()

        return str(self.gremlin)


class Conditional(Statement):

    def __init__(self):
        self.if_condition = None
        self.if_body = None
        self.else_body = None
        self.elif_condition = []
        self.elif_body = []

    def set_if(self, condition, body):
        self.if_condition = condition
        self.if_body = body

        return self

    def set_elif(self, condition, body):
        self.elif_condition.append(condition)
        self.elif_body.append(body)

        return self

    def set_else(self, body):
        self.else_body = body

        return self

    def build(self):
        from gremlinpy.gremlin import UnboudFunctionRaw, Raw

        gremlin = self.gremlin

        if self.if_condition is None or self.if_body is None:
            error = 'Your statement needs at least both an if clause and body'
            raise StatmentError(error)

        #build the if statement
        if_condition = UnboudFunctionRaw(gremlin, 'if', [self.if_condition])

        gremlin.set_graph_variable('').add_token(if_condition)
        gremlin.close(self.if_body)

        #build all of the elif statements
        for i, condition in enumerate(self.elif_condition):
            body = self.elif_body[i]
            elif_condition = UnboudFunctionRaw(gremlin, 'elseif', [condition])

            gremlin.add_token(elif_condition).close(body)

        #build else statement
        if self.else_body is not None:
            else_condition = Raw(gremlin, 'else')

            gremlin.add_token(else_condition).close(self.else_body)

        return self


class GetEdge(Statement):
    directions = {
        'both': ('bothE', 'bothV'),
        'in': ('inE', 'outV'),
        'out': ('outE', 'inV'),
    }

    def __init__(self, out_v_id, in_v_id, label, direction='both', bind_ids=True):
        if direction not in self.directions:
            raise ValueError('The direction must be: ' + ', '.join(self.directions.keys()))

        self.out_v_id = out_v_id
        self.in_v_id = in_v_id
        self.label = label
        self.bind_ids = bind_ids
        self.direction = self.directions[direction]

    def build(self):
        from gremlinpy.gremlin import Function as GF
        
        gremlin = self.gremlin

        if self.bind_ids:
            out_id = gremlin.bind_param(self.out_v_id, 'V_OUT_ID')
            in_id = gremlin.bind_param(self.in_v_id, 'V_IN_ID')
        else:
            out_id = [self.out_v_id]
            in_id = [self.in_v_id]

        if self.direction[0] == 'outE':
            first = out_id
            second = in_id
        else:
            first = in_id
            second = out_id

        label = gremlin.bind_param(self.label, 'LABEL')
        back = gremlin.bind_param('vertex', 'VERTEX')
        
        gremlin.V(first[0])
        gremlin.unbound(self.direction[0], '"%s"' % self.label)
        gremlin.unbound('as', '"as_label"')
        
        v_func = GF(gremlin, self.direction[1])

        gremlin.add_token(v_func)
        gremlin.has('T.id', second[0]).unbound('select', '"as_label"')
