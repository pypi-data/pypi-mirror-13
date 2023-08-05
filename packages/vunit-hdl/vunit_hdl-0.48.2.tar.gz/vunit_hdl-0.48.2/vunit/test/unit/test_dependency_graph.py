# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2014-2015, Lars Asplund lars.anders.asplund@gmail.com

"""
Test the DependencyGraph
"""

from vunit.dependency_graph import DependencyGraph
import unittest


class TestDependencyGraph(unittest.TestCase):
    """
    Test the DependencyGraph
    """

    def test_should_return_empty_compile_order_for_no_nodes(self):
        graph = DependencyGraph()
        self.assertEqual(graph.toposort(), [], 'Should return empty list')

    def test_should_return_list_of_nodes_when_there_are_no_dependencies(self):
        nodes = ['a', 'b', 'c', 'd']
        graph = DependencyGraph()
        self._add_nodes_and_dependencies(graph, nodes, [])
        result = graph.toposort()
        self.assertEqual(result.sort(), nodes.sort(), 'Should return the node list in any order')

    def test_should_sort_in_topological_order_when_there_are_dependencies(self):
        nodes = ['a', 'b', 'c', 'd', 'e', 'f']
        dependencies = [('a', 'b'), ('a', 'c'), ('b', 'd'), ('e', 'f')]
        graph = DependencyGraph()
        self._add_nodes_and_dependencies(graph, nodes, dependencies)
        result = graph.toposort()
        self._check_result(result, dependencies)

    def test_should_raise_runtime_error_exception_on_self_dependency(self):
        nodes = ['a', 'b', 'c', 'd']
        dependencies = [('a', 'b'), ('a', 'c'), ('b', 'd'), ('d', 'd')]
        graph = DependencyGraph()
        self._add_nodes_and_dependencies(graph, nodes, dependencies)
        self.assertRaises(RuntimeError, graph.toposort)

    def test_should_raise_runtime_error_exception_on_long_circular_dependency(self):
        nodes = ['a', 'b', 'c', 'd']
        dependencies = [('a', 'b'), ('a', 'c'), ('b', 'd'), ('d', 'a')]
        graph = DependencyGraph()
        self._add_nodes_and_dependencies(graph, nodes, dependencies)
        self.assertRaises(RuntimeError, graph.toposort)

    def test_should_resort_after_additions(self):
        nodes = ['a', 'b', 'c', 'd', 'e', 'f']
        dependencies = [('a', 'b'), ('a', 'c'), ('b', 'd'), ('e', 'f')]
        graph = DependencyGraph()
        self._add_nodes_and_dependencies(graph, nodes, dependencies)
        graph.toposort()
        dependencies = [('a', 'b'), ('a', 'c'), ('b', 'd'), ('e', 'f'), ('b', 'g')]
        graph.add_node('g')
        graph.add_dependency('b', 'g')
        result = graph.toposort()
        self._check_result(result, dependencies)

    def test_get_direct_dependencies_should_return_empty_set_when_no_dependendencies(self):
        nodes = ['a', 'b', 'c']
        dependencies = []
        graph = DependencyGraph()
        self._add_nodes_and_dependencies(graph, nodes, dependencies)
        result = graph.get_direct_dependencies('b')
        self.assertTrue(isinstance(result, (set)))
        self.assertFalse(result)

    def test_get_direct_dependencies_should_return_dependendencies_set(self):
        nodes = ['a', 'b', 'c', 'd']
        dependencies = [('a', 'b'), ('a', 'c')]
        graph = DependencyGraph()
        self._add_nodes_and_dependencies(graph, nodes, dependencies)
        result = graph.get_direct_dependencies('c')
        self.assertFalse('b' in result)
        self.assertTrue('a' in result)

    def _check_result(self, result, dependencies):
        """
        Check that the resulting has an order such that
        dependent files are located after their dependencies
        """
        for dep1, dep2 in dependencies:
            self.assertTrue(result.index(dep1) < result.index(dep2), "%s is not before %s" % (dep1, dep2))

    @staticmethod
    def _add_nodes_and_dependencies(graph, nodes, dependencies):
        """
        Add nodes and dependencies to the graph
        """
        for node in nodes:
            graph.add_node(node)
        for dep in dependencies:
            graph.add_dependency(dep[0], dep[1])

if __name__ == '__main__':
    unittest.main()
