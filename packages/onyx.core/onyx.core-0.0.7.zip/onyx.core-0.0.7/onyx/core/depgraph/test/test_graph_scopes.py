###############################################################################
#
#   Copyright: (c) 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from ..graph_api import GetVal, SetVal
from ..graph_api import UseGraph, CreateInMemory, InvalidateNode
from ..graph_scopes import EvalBlock, GraphScope
from ...database.objdb_api import UseDatabase
from . import ufo_testcls

from ... import database as onyx_db

import unittest
import os


class RegTest(unittest.TestCase):
    def setUp(self):
        self.use_db = UseDatabase(os.getenv("OBJDB_TEST", default="TestDb"))
        self.use_graph = UseGraph()
        self.use_db.__enter__()
        self.use_graph.__enter__()

        self.obj = CreateInMemory(ufo_testcls.TestCls3(Name="obj"))

    def tearDown(self):
        del self.obj
        self.use_db.__exit__()
        self.use_graph.__exit__()
        onyx_db.obj_instances.clear()

    def node_assertEqual(self, obj, vt, value):
        self.assertEqual(GetVal(self.obj.Name, vt), value)
        self.assertEqual(GetVal(self.obj, vt), value)

    def test_evalblock(self):
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        # --- create an eval block
        with EvalBlock() as ev_block:
            self.node_assertEqual(self.obj, "Number", 666.0)
            self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

            # --- now change Number to 0
            ev_block.change_value("obj", "Number", 0)
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

            # --- test multiple changes within nested eval blocks
            with EvalBlock() as new_ev_block:
                new_ev_block.change_value("obj", "Number", 333)
                self.node_assertEqual(self.obj, "CalcProperty", 667.0)

                new_ev_block.change_value("obj", "Number", -333)
                self.node_assertEqual(self.obj, "CalcProperty", -665.0)

            # --- outside nested eval block
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

            # --- now change the calc VT itself
            ev_block.change_value("obj", "CalcProperty", 1976)
            self.node_assertEqual(self.obj, "CalcProperty", 1976)

            with EvalBlock() as new_ev_block:
                new_ev_block.change_value("obj", "CalcProperty", 333)
                self.node_assertEqual(self.obj, "CalcProperty", 333)

            # --- outside nested eval block
            self.node_assertEqual(self.obj, "CalcProperty", 1976)

            # --- invalidating a changed node should take it back to the
            #     original state
            InvalidateNode(self.obj, "CalcProperty")
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

        # --- outside all eval blocks
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

    def test_graphscope_basic_usage(self):
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        # --- create a graph scope and set a first change
        scope = GraphScope()
        scope.change_value(self.obj, "Number", 0.0)

        # --- the value is changed, but not yet used
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        # --- use the graph scope to enforce existing changes and to add more
        with scope:
            self.node_assertEqual(self.obj, "Number", 0.0)
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

            scope.change_value(self.obj, "CalcProperty", "ABC")

            self.node_assertEqual(self.obj, "Number", 0.0)
            self.node_assertEqual(self.obj, "CalcProperty", "ABC")

        # --- outside graph scope
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        # --- a graph scope can be reused and all changes are live again
        with scope:
            self.node_assertEqual(self.obj, "Number", 0.0)
            self.node_assertEqual(self.obj, "CalcProperty", "ABC")

            # --- invalidating a changed node should take it back to the
            #     original state
            InvalidateNode(self.obj, "CalcProperty")
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

        # --- outside graph scope
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        with scope:
            # --- create another graph scope and test nested scopes.
            #     NB: the inner scope MUST be created inside the outer scope.
            #         This is a limitation, not a desired feature...
            inner = GraphScope()

            self.node_assertEqual(self.obj, "Number", 0.0)
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

            with inner:
                self.node_assertEqual(self.obj, "Number", 0.0)
                self.node_assertEqual(self.obj, "CalcProperty", 1.0)

                inner.change_value(self.obj, "Number", 5)
                self.node_assertEqual(self.obj, "CalcProperty", 11.0)

                inner.change_value(self.obj, "Number", -5)
                self.node_assertEqual(self.obj, "CalcProperty", -9.0)

            self.node_assertEqual(self.obj, "Number", 0.0)
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        # --- make sure the scope continues to work as expected even if we
        #     switch graph
        scope.change_value(self.obj, "Number", 0.0)

        self.node_assertEqual(self.obj, "Number", 666.0)

        with UseGraph():
            SetVal(self.obj, "Number", 5.0)

            self.node_assertEqual(self.obj, "Number", 5.0)

            with scope:
                self.node_assertEqual(self.obj, "Number", 0.0)
                self.node_assertEqual(self.obj, "CalcProperty", 1.0)

            self.node_assertEqual(self.obj, "Number", 5.0)
            self.node_assertEqual(self.obj, "CalcProperty", 11.0)

        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)


if __name__ == "__main__":
    unittest.main()
