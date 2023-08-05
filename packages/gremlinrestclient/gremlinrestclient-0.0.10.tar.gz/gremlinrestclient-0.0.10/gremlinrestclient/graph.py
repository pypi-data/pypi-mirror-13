import collections

from gremlinrestclient.client import GremlinRestClient


__all__ = ("TitanGraph", "TinkerGraph", "Graph", "Vertex", "Edge",
           "Collection")


Vertex = collections.namedtuple(
    "Vertex",
    ["id", "label", "properties"])


Edge = collections.namedtuple(
    "Edge",
    ["id", "source_id", "label", "target_id", "properties"])


Collection = collections.namedtuple(
    "Collection",
    ["vertices", "edges"]
)


class Graph:
    """
    A script factory for the Gremlin Server that defines the common interface
    for the Tinkerpop3 backends.
    """
    def __init__(self):
        self._vertex_alias = 0
        self._edge_alias = 0

    def create(self, *elements):
        """
        Create nodes and edges.

        :param elements: Args can either be
            :py:class:`Vertex<gremlinrestclient.client.Vertex>`,
            :py:class:`dict` that can be cast to a Vertex or a
            :py:class:`tuple` that can be cast to an Edge.
        """
        self._vertex_alias_list = []
        self._edge_alias_list = []
        self._param_id = 0

        vertices, edges = self._divide_elements(elements)
        vert_script, vert_bindings = self._parse_vertices(vertices)
        edge_script, edge_bindings = self._parse_edges(edges)
        if self._vertex_alias_list:
            vertex_alias = ",".join(self._vertex_alias_list)
        else:
            vertex_alias = ""
        vertex_alias = "[" + vertex_alias + "]"
        if self._edge_alias_list:
            edge_alias = ",".join(self._edge_alias_list)
        else:
            edge_alias = ""
        edge_alias = "[" + edge_alias + "]"
        # alias is used to return the newly created edges/vertices
        alias = "[%s, %s];" % (vertex_alias, edge_alias)
        script = "%s%s" % (vert_script, edge_script)
        vert_bindings.update(edge_bindings)
        return script, vert_bindings, alias

    def _divide_elements(self, elements):
        """
        A bit ugly, but this parses the mumbo jumbo the user can pass.
        """
        vertices = {}
        edges = []
        for arg in elements:
            if isinstance(arg, dict):
                vertices[id(arg)] = self._process_vertex(arg, vertices, elements)
            elif isinstance(arg, tuple):
                source, label, target = arg[:3]
                properties = arg[4:4] or {}
                source_vertex = self._process_vertex(source, vertices, elements)
                target_vertex = self._process_vertex(target, vertices, elements)
                alias = "e%s" % str(self._edge_alias)
                self._edge_alias += 1
                edge = source_vertex, label, target_vertex, properties, alias
                edges.append(edge)
            else:
                raise ValueError('%s not supported, use dict for vertices and tuple for edges')
        return vertices.values(), edges

    def _process_vertex(self, vertex, vertices, elements):
        if isinstance(vertex, int):
            vertex = elements[vertex]
        ptr = id(vertex)
        known_vertex = ptr in vertices
        if known_vertex:
            vertex = vertices[ptr]
        vertex_dict = self._build_vertex(vertex)
        if not known_vertex:
            vertices[ptr] = vertex_dict
        return vertex_dict

    def _build_vertex(self, vertex):
        if isinstance(vertex, Vertex):
            vertex_dict = vertex._asdict()
        elif isinstance(vertex, dict):
            if 'alias' in vertex:
                return vertex
            else:
                vertex_dict = {}
                vertex_dict["label"] = vertex.pop("label", "")
                vertex_dict["id"] = ""  # Clobbered
                vertex_dict["properties"] = vertex
        else:
            raise ValueError('%s can\'t be a vertex' % type(vertex))

        alias = "v%s" % str(self._vertex_alias)
        self._vertex_alias += 1
        vertex_dict["alias"] = alias
        return vertex_dict

    def _get_param(self):
        param = "p%s" % str(self._param_id)
        self._param_id += 1
        return param

    def _parse_vertices(self, vertices):
        script = ""
        bindings = {}
        for vertex in vertices:
            vid = vertex["id"]
            alias = vertex["alias"]
            if vid != "":
                param = self._get_param()
                script += "%s = g.V(%s).next();" % (alias, param)
                bindings[param] = vertex["id"]
            else:
                self._vertex_alias_list.append(alias)
                add_vertex = "%s = graph.addVertex(" % alias
                label = vertex["label"]
                props = vertex["properties"]
                if label:
                    param = self._get_param()
                    add_vertex += "label, %s, " % param
                    bindings[param] = label
                for k, v in props.items():
                    param = self._get_param()
                    add_vertex += "'%s', %s, " % (k, param)
                    bindings[param] = v
                add_vertex += ");"
                script += add_vertex
        return script, bindings

    def _parse_edges(self, edges):
        script = ""
        bindings = {}
        for edge in edges:
            source_alias = edge[0]["alias"]
            label = edge[1]
            target_alias = edge[2]["alias"]
            props = edge[3]
            alias = edge[4]
            add_edge = "%s = %s.addEdge('%s', %s, " % (alias, source_alias,
                                                       label, target_alias)
            for k, v in props.items():
                param = self._get_param()
                add_edge += "'%s', %s, " % (k, param)
                bindings[param] = v
            add_edge += ");"
            script += add_edge
            self._edge_alias_list.append(alias)
        return script, bindings


class TinkerGraph(GremlinRestClient, Graph):

    def __init__(self, url="http://localhost:8182"):
        GremlinRestClient.__init__(self, url=url)
        Graph.__init__(self)

    def create(self, *elements):
        script, bindings, alias = Graph.create(self, *elements)
        script = "%s%s" % (script, alias)
        return self._create(script, bindings)

    def _create(self, script, bindings):
        resp = self.execute(script, bindings=bindings)
        data = resp.data
        vertices = tuple(Vertex(v["id"],
                                v["label"],
                                v["properties"]) for v in data[0])
        edges = tuple(Edge(e["id"],
                           e["outV"],
                           e["label"],
                           e["inV"],
                           e.get("properties", {})) for e in data[1])
        collection = Collection(vertices, edges)
        return collection


class TitanGraph(TinkerGraph):

    def __init__(self, url="http://localhost:8182"):
        super(TitanGraph, self).__init__(url=url)

    def create(self, *elements):
        script, bindings, alias = Graph.create(self, *elements)
        script = "%s%s%s" % (script, "graph.tx().commit();", alias)
        return self._create(script, bindings)
