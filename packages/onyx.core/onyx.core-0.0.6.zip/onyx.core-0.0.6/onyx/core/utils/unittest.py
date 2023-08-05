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

from ..database.objdb import ObjDbDummyClient, ObjNotFound
from ..database.objdb_api import GetObj, AddObj
from ..depgraph.graph_api import CreateInMemory
from .startup import OnyxInit

import unittest

__all__ = ["AddIfMissing", "TestRunner"]


# -----------------------------------------------------------------------------
def AddIfMissing(obj, in_memory=False):
    try:
        return GetObj(obj.Name)
    except ObjNotFound:
        if in_memory:
            return CreateInMemory(obj)
        else:
            return AddObj(obj)


###############################################################################
class TestClient(ObjDbDummyClient):
    # -------------------------------------------------------------------------
    def get(self, name, refresh=False):
        return super().get(name)


###############################################################################
class TestRunner(unittest.TextTestRunner):
    # -------------------------------------------------------------------------
    def run(self, test):
        objdb = TestClient(database="test", user="testuser")
        with OnyxInit(objdb=objdb):
            return super().run(test)
