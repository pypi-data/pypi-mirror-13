###############################################################################
#
#   Agora Portfolio & Risk Management System
#
#   Copyright 2015 Carlo Sbraccia
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

from onyx.database.objdb import ObjDbBase

import onyx.core
import contextlib
import getpass
import configparser
import logging
import os

__all__ = ["OnyxInit", "OnyxStartup"]

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
def init_environment(filenames=None):
    """
    Description:
        Load configuration options from one or more INI files.
    Inputs:
        filenames - a list of possible config file paths. By default, looks for
                    a onyx_config.ini in the HOME or USERPROFILE directories.
    """
    if filenames is None:
        home = os.getenv("HOME", os.getenv("USERPROFILE", "./"))
        filenames = [os.path.join(home, "onyx_config.ini")]

    config = configparser.ConfigParser()
    files = config.read(filenames)

    if not len(files):
        logger.warning("couldn't find any of the specified "
                       "config files: {0!s}".format(filenames))

    # --- database section
    os.environ["OBJDB"] = config.get("daabase", "objdb", fallback="ProdDb")
    os.environ["TSDB"] = config.get("database", "tsdb", fallback="TsDb")
    os.environ["DB_USER"] = config.get("database", "user",
                                       fallback=getpass.getuser())
    os.environ["DB_HOST"] = config.get("database", "host", fallback="")

    # --- datafeed section
    os.environ["BBG_DATAQUEUE"] = config.get("datafeed", "queue_address",
                                             fallback="127.0.0.1")
    os.environ["MC_SERVER"] = config.get("datafeed", "memcache_url",
                                         fallback="127.0.0.1:11211")


# -----------------------------------------------------------------------------
def OnyxInit(objdb=None, tsdb=None, user=None, host=None):
    """
    Description:
        Activate onyx databases and graph using the respective context
        managers.
    Inputs:
        objdb - an instance of an ObjDb client or the name of a valid ObjDb
        tsdb  - an instance of an TsDb client or the name of a valid TsDb
        user  - the database user
        host  - the database host
    Returns:
        A stack of context managers.
    """
    init_environment()

    objdb = objdb or os.getenv("OBJDB_PROD")
    tsdb = tsdb or os.getenv("TSDB_PROD")
    user = user or os.getenv("POSTGRESQL_USER")
    host = host or os.getenv("POSTGRESQL_HOST")

    if isinstance(objdb, ObjDbBase):
        objdb_clt = objdb
    else:
        objdb_clt = onyx.core.ObjDbClient(objdb, user, host)

    if isinstance(tsdb, onyx.core.TsDbClient):
        tsdb_clt = tsdb
    else:
        tsdb_clt = onyx.core.TsDbClient(tsdb, user, host)

    stack = contextlib.ExitStack()
    stack.enter_context(onyx.core.UseDatabase(objdb_clt))
    stack.enter_context(onyx.core.TsDbUseDatabase(tsdb_clt))
    stack.enter_context(onyx.core.UseGraph())

    return stack


# -----------------------------------------------------------------------------
def OnyxStartup(objdb=None, tsdb=None, user=None, host=None):
    stack = OnyxInit(objdb, tsdb, user, host)
    stack.__enter__()
    print("""Onyx has been fired up... Good luck!!!""")
    return {key: value
            for key, value in onyx.core.__dict__.items()
            if not key.startswith("__")}
