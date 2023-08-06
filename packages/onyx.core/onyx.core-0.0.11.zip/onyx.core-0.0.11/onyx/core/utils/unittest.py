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

from ..database.objdb import ObjNotFound
from ..database.objdb_api import GetObj, AddObj, UseDatabase
from ..database.tsdb_api import TsDbUseDatabase
from ..depgraph.graph_api import CreateInMemory
from .startup import OnyxInit, load_system_configuration

from ..database.objdb import ObjDbClient
from ..database.tsdb import TsDbClient

import unittest
import getpass

__all__ = [
    "AddIfMissing",
    "ObjDbTestCase",
    "TsDbTestCase",
    "OnyxTestCase",
    "TestRunner"
]


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
class ObjDbTestCase(unittest.TestCase):
    # -------------------------------------------------------------------------
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        config = load_system_configuration()
        objdb = config.get("test", "objdb")
        user = config.get("test", "user", fallback=getpass.getuser())

        if objdb == config.get("database", "objdb"):
            raise RuntimeError("Trying to run unittests on "
                               "production database ObjDb={0:s}".format(objdb))

        self.objdb = objdb
        self.user = user
        self.clt = ObjDbClient(objdb, user, check=False)

    # -------------------------------------------------------------------------
    def setUp(self):
        # --- create tables and functions
        try:
            self.clt.initialize()
        except:
            self.clt.cleanup()
            self.clt.initialize()
        self.context = UseDatabase(database=self.objdb, user=self.user)
        self.context.__enter__()

    # -------------------------------------------------------------------------
    def tearDown(self):
        self.context.__exit__(None, None, None)
        # --- cleanup tables and functions
        self.clt.cleanup()


###############################################################################
class TsDbTestCase(unittest.TestCase):
    # -------------------------------------------------------------------------
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        config = load_system_configuration()
        tsdb = config.get("test", "tsdb")
        user = config.get("test", "user", fallback=getpass.getuser())

        if tsdb == config.get("database", "tsdb"):
            raise RuntimeError("Trying to run unittests on "
                               "production database TsDb={0:s}".format(tsdb))

        self.tsdb = tsdb
        self.user = user
        self.clt = TsDbClient(tsdb, user, check=False)

    # -------------------------------------------------------------------------
    def setUp(self):
        # --- create tables and functions
        try:
            self.clt.initialize()
        except:
            self.clt.cleanup()
            self.clt.initialize()
        self.context = TsDbUseDatabase(database=self.tsdb, user=self.user)
        self.context.__enter__()

    # -------------------------------------------------------------------------
    def tearDown(self):
        self.context.__exit__(None, None, None)
        # --- cleanup tables and functions
        self.clt.cleanup()


###############################################################################
class OnyxTestCase(unittest.TestCase):
    # -------------------------------------------------------------------------
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        config = load_system_configuration()
        objdb = config.get("test", "objdb")
        tsdb = config.get("test", "tsdb")
        user = config.get("test", "user", fallback=getpass.getuser())
        host = config.get("test", "host", fallback=None)

        if objdb == config.get("database", "objdb"):
            raise RuntimeError("Trying to run unittests on "
                               "production database ObjDb={0:s}".format(objdb))
        if tsdb == config.get("database", "tsdb"):
            raise RuntimeError("Trying to run unittests on "
                               "production database TsDb={0:s}".format(tsdb))

        self.obj_clt = ObjDbClient(objdb, user, host, check=False)
        self.ts_clt = TsDbClient(tsdb, user, host, check=False)

        self.objdb = objdb
        self.tsdb = tsdb
        self.user = user
        self.host = host

    # -------------------------------------------------------------------------
    def setUp(self):
        # --- create tables and functions
        try:
            self.obj_clt.initialize()
        except:
            self.obj_clt.cleanup()
            self.obj_clt.initialize()
        try:
            self.ts_clt.initialize()
        except:
            self.ts_clt.cleanup()
            self.ts_clt.initialize()
        self.context = OnyxInit(objdb=self.objdb, tsdb=self.tsdb,
                                user=self.user, host=self.host)
        self.context.__enter__()

    # -------------------------------------------------------------------------
    def tearDown(self):
        self.context.__exit__(None, None, None)
        # --- cleanup tables and functions
        self.obj_clt.cleanup()
        self.ts_clt.cleanup()


###############################################################################
class TestRunner(unittest.TextTestRunner):
    # -------------------------------------------------------------------------
    def run(self, test):
        config = load_system_configuration()
        objdb = config.get("test", "objdb")
        tsdb = config.get("test", "tsdb")
        user = config.get("test", "user", fallback=getpass.getuser())
        host = config.get("test", "host", fallback=None)

        if objdb == config.get("database", "objdb"):
            raise RuntimeError("Trying to run unittests on "
                               "production database ObjDb={0:s}".format(objdb))
        if tsdb == config.get("database", "tsdb"):
            raise RuntimeError("Trying to run unittests on "
                               "production database TsDb={0:s}".format(tsdb))

        obj_clt = ObjDbClient(objdb, user, host, check=False)
        ts_clt = TsDbClient(tsdb, user, host, check=False)

        try:
            # --- create tables and functions
            obj_clt.initialize()
            ts_clt.initialize()

            with OnyxInit(objdb=objdb, tsdb=tsdb, user=user, host=host):
                return super().run(test)
        finally:
            # --- cleanup tables and functions
            obj_clt.cleanup()
            ts_clt.cleanup()
