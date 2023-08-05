import unittest
from gremlinrestclient import (GremlinRestClient, GremlinServerError,
                               TinkerGraph, TitanGraph)


class GremlinRestClientTestCase(unittest.TestCase):

    def setUp(self):
        self.client = GremlinRestClient()

    def test_request(self):
        resp = self.client.execute("1 + 1")
        self.assertEqual(resp.data[0], 2)

    def test_bindings(self):
        resp = self.client.execute("x + x", bindings={"x": 1})
        self.assertEqual(resp.data[0], 2)

    def test_error(self):
        try:
            self.client.execute("x + x.fasdfewq", bindings={"x": 1})
            error = False
        except GremlinServerError:
            error = True
        self.assertTrue(error)


class GraphTestCase(unittest.TestCase):

    def setUp(self):
        self.graph = TinkerGraph()

    def test_create(self):
        node1 = {"label": "person", "name": "dave", "age": 34}
        resp = self.graph.create(
            (node1, "KNOWS", 1), {"label": "lang", "name": "python"})
        self.assertEqual(len(resp.vertices), 2)
        self.assertEqual(len(resp.edges), 1)
        edge, = resp.edges
        out_v = resp.vertices[0]
        in_v = resp.vertices[1]
        self.assertEqual(edge.source_id, out_v.id)
        self.assertEqual(edge.target_id, in_v.id)

    def test_create_vertex(self):
        resp = self.graph.create(
            {"label": "person", "name": "dave", "age": 34})
        node1, = resp.vertices
        resp = self.graph.create(
            (node1, "KNOWS", 1), {"label": "lang", "name": "python"})
        self.assertEqual(len(resp.vertices), 1)
        self.assertEqual(len(resp.edges), 1)
        edge, = resp.edges
        in_v, = resp.vertices
        self.assertEqual(edge.target_id, in_v.id)

    def test_create_multiple(self):
        p = {"label": "lang", "name": "python"}
        d = {"label": "person", "name": "dave", "age": 34}
        f = {"label": "person", "name": "frens", "age": 34}
        resp = self.graph.create(
            p,
            (d, 'KNOWNS', 0),
            (f, 'KNOWNS', p),
        )
        self.assertEqual(len(resp.vertices), 3)
        self.assertEqual(len(resp.edges), 2)
        e1, e2 = resp.edges
        v1, v2, v3 = resp.vertices
        self.assertEqual(e1.source_id, v2.id)
        self.assertEqual(e1.target_id, v1.id)
        self.assertEqual(e2.source_id, v3.id)
        self.assertEqual(e2.target_id, v1.id)


class TitanGraphTestCase(unittest.TestCase):

    def setUp(self):
        self.graph = TitanGraph()

    def test_create(self):
        node1 = {"label": "person", "name": "dave", "age": 34}
        resp = self.graph.create(
            (node1, "KNOWS", 1), {"label": "lang", "name": "python"})
        self.assertEqual(len(resp.vertices), 2)
        self.assertEqual(len(resp.edges), 1)
        edge, = resp.edges
        out_v = resp.vertices[0]
        in_v = resp.vertices[1]
        self.assertEqual(edge.source_id, out_v.id)
        self.assertEqual(edge.target_id, in_v.id)

    def test_create_vertex(self):
        resp = self.graph.create(
            {"label": "person", "name": "dave", "age": 34})
        node1, = resp.vertices
        resp = self.graph.create(
            (node1, "KNOWS", 1), {"label": "lang", "name": "python"})
        self.assertEqual(len(resp.vertices), 1)
        self.assertEqual(len(resp.edges), 1)
        edge, = resp.edges
        in_v, = resp.vertices
        self.assertEqual(edge.target_id, in_v.id)


if __name__ == "__main__":
    unittest.main()
