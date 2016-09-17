#!/usr/bin/env python
"""
PyPLE (say "pipple") -- the Python Persistent Logic Engine

pyple.py: Main PyPLE class and simple test script

Copyright (C) 2006-2007 Ansel Halliburton.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the PyPLE Project nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

NOTES
*   PyPLE is lean and mean.  Just say no to complexity!
*   You can run this file to do some simple testing: python pyple.py
*   The tests depend on PyYAML, and expect a YAML file called 'pyple-db.yaml'
    with database connection parameters.  (try 'easy_install pyyaml')  You
    do NOT need PyYAML to import PyPLE.
*   Special thanks to Stanford Law School for allowing me to continue work on
    PyPLE in 2007!

HISTORY
v0.0.1  PyPLE was born in a flash of inspiration at L & L Hawaiian Barbecue in
        Palo Alto, California on April 7, 2006.  Version 0.0.1 was thrown together
        more or less that night.
v0.1.0  Port to SQLObject for database persistence begun - 1/22/07
v0.2.0  Complete rewrite of SQLObject version
v0.3.0  Another major rewrite -- simplifying Operator, parameters, etc. 3/15/07.  It works! :)
v0.3.1  Renamed Regex -> RegexOp for IPLC compatibility; other people might have that problem too.
        Added regex cache.
"""

#   Interesting tokens to look for in this source code:
#   #TODO:  Items that need doing
#   #BUG:   Identified bug
#   #NOTE:  Note by author

__revision__ = "$Id$"
__author__ = 'Ansel Halliburton (github at anseljh dot com)'
__release__ = (0,3,1,'alpha',0)

PYPLE_TAGLINE = "PyPLE (say \"pipple\") -- the Python Persistent Logic Engine"
PYPLE_COPYRIGHT = "Copyright (c) 2006-2007 Ansel Halliburton"
ASTERISKS = 40 # number of asterisks to use as separator in debug/test output
DEBUG = 0

DUMP_INDENT_SPACING = 2
DUMP_INDENT_CHAR = ' '

import re
from sqlobject import * # SQLObject ORM
from sqlobject.inheritance import InheritableSQLObject

class Operator(InheritableSQLObject):

  parameters = RelatedJoin('Operator', joinColumn='parameter_id')
  name = StringCol(length=255, notNone=False, default=None)

  class sqlmeta:
    table = 'pyple_operator'

  def eval(self, data=None):
    pass # to be overloaded

  def addParameter(self, param):
    if param is self:
      raise ValueError("A rule cannot contain itself as a sub-rule!")
    else:
      self.addOperator(param)

  def dump(self, indent=0):
    details = []
    if self.name is not None:
      details.append("name=\"%s\"" % self.name)
    if isinstance(self, RegexOp):
      details.append("pattern=\"%s\"" % self.pattern)
    print("%s+ %s (%s) #%d" % (DUMP_INDENT_CHAR * DUMP_INDENT_SPACING * indent, self.sqlmeta.table, ', '.join(details), self.id))
    for p in self.parameters:
      p.dump(indent+1)

class AlwaysTrueOp(Operator):
  def eval(self, data=None):
    return True
  class sqlmeta:
    table = 'pyple_op_always_true'

class AlwaysFalseOp(Operator):
  def eval(self, data=None):
    return False
  class sqlmeta:
    table = 'pyple_op_always_false'

class RegexOp(Operator):

  pattern = StringCol(length=255)
  case_sensitive = BoolCol(default=False)

  class sqlmeta:
    table = 'pyple_op_regex'

  def compile(self, engine=None):
    if self.case_sensitive:
      r = re.compile(self.pattern)
    else:
      r = re.compile(self.pattern, re.IGNORECASE)
    if engine is not None:
      engine.re_cache[self.pattern] = r
    return r

  def eval(self, data, engine=None):
    tmp_re = None
    if engine is None:
      tmp_re = self.compile()
    elif self.pattern in engine.re_cache:
      tmp_re = engine.re_cache[self.pattern]
    else:
      tmp_re = self.compile(engine)

    result = tmp_re.search(data)
    if result:
      return True
    else:
      return False

class AND(Operator):
  class sqlmeta:
    table = 'pyple_op_and'
  def eval(self, data=None):
    for param in self.parameters:
      if not param.eval(data):
        return False
    return True # implicit else after for loop

class OR(Operator):
  class sqlmeta:
    table = 'pyple_op_or'
  def eval(self, data=None):
    for param in self.parameters:
      if param.eval(data):
        return True
    return False # implicit else after for loop

class NOT(Operator):
  class sqlmeta:
    table = 'pyple_op_not'
  def eval(self, data=None):
    assert len(self.parameters) < 2, "NOT only works with one or zero Operator parameters"
    if len(self.parameters) > 0:
      for param in self.parameters:
        if param.eval(data):
          return False
    return True # implicit else after for loop

class XOR(Operator):
  class sqlmeta:
    table = 'pyple_op_xor'
  def eval(self, data=None):
    assert len(self.parameters) == 2, "XOR only works with two Operator parameters"
    if self.parameters[0].eval(data) and not self.parameters[1].eval(data):
      return True
    elif self.parameters[1].eval(data) and not self.parameters[0].eval(data):
      return True
    else:
      return False

class NAND(Operator):
  class sqlmeta:
    table = 'pyple_op_nand'
  def eval(self, data=None):
    assert len(self.parameters) == 2, "NAND only works with two Operator parameters"
    if self.parameters[0].eval(data) and self.parameters[1].eval(data):
      return False
    else:
      return True

class NOR(Operator):
  """
  Not strictly a correct implementation of the binary NOR operator, because
  this one accepts more than two operands.  Returns True only if all the
  parameters (operands) evaluate to False.  (If any parameter returns True, NOR
  returns False.)
  """
  class sqlmeta:
    table = 'pyple_op_nor'
  def eval(self, data=None):
    assert len(self.parameters) >= 2, "NOR only works with two or more Operator parameters"
    for param in self.parameters:
      if param.eval(data):
        return False
    return True # implicit else after for loop

PYPLE_TABLES = [Operator, AlwaysTrueOp, AlwaysFalseOp, RegexOp, AND, OR, NOT, XOR, NAND, NOR]

class Engine:

  def __init__(self, debug=DEBUG):
    self.debuglevel = debug
    self.dbconnection = None
    self.re_cache = {}          # Cache of compiled regular expressions; keyed by pattern

  @staticmethod
  def build_db_uri(d):
      """
      Build database connection URI from dictionary of connection parameters
      """
      uri = "%s://%s:%s@%s:%d/%s" % (d['dbtype'], d['username'], d['password'], d['host'], d['port'], d['database'])
      if DEBUG:
        uri = uri + "?debug=1"
      return uri

  def set_db_connection(self, conn):
      self.dbconnection = conn
      sqlhub.processConnection = self.dbconnection
      self.hub = sqlhub
      #__connection__ = self.dbconnection
      if self.debuglevel > 0:
          print("pyple.Engine.set_db_connection(): Connected to DB: %s" % self.dbconnection)

  def connect_to_db(self, uri):
      if self.debuglevel > 0:
          print("Connecting to DB with: %s" % uri)
      conn = connectionForURI(uri)
      self.set_db_connection(conn)

  def connect_with_tg_hub(self, hub):
    """
    Use a DB connection from TurboGears.  Pass it the hub object from a TG model.
    Example:
      import pyple
      PYPLE_ENGINE = pyple.Engine()
      PYPLE_ENGINE.connect_with_tg_hub(hub)
    Note: I have no idea why, but this won't work if it's at the top of this model file.  Ugh.
    """
    self.set_db_connection(hub.hub.getConnection())

  def create_tables(self):
    for table in PYPLE_TABLES:
      table._connection = self.dbconnection
      table.createTable()

  def drop_tables(self):
    for table in PYPLE_TABLES:
      table._connection = self.dbconnection
      table.dropTable(ifExists=True)

  def new_op(self, optype=None, *args, **kw):
    if optype is None:
      raise ValueError("Engine.new_op(): optype can't be None.")
    op = optype(*args, **kw)
    op._connection = self.dbconnection
    if optype is RegexOp and 'pattern' in kw:
      self.cache_regex(kw['pattern'])
    return op

  def get_op(self, name):
    rs = Operator.selectBy(name=name)
    assert rs.count() == 1, "Operator.selectBy(name=name) should return only one result."
    return rs[0]

  def cache_regex(self, pattern, obj=None):
    if obj is not None:
      self.re_cache[pattern] = obj
    else:
      self.re_cache[pattern] = re.compile(pattern) #NOTE: doesn't include case-sensitivity etc. flags!

  def compound_regex_rule(self, ruletype=None, patterns=None, name=None):
    root = self.new_op(ruletype, name=name)
    for pattern in patterns:
      rule = self.new_op(RegexOp, pattern=pattern)
      root.addParameter(rule)
    return root

if __name__ == "__main__":

  import yaml #PyYAML: YAML parser/emitter - because its easy_install isn't b0rked like PySyck's: see http://pyyaml.org/ticket/44

  E = Engine() # instantiate the engine
  E.connect_to_db(Engine.build_db_uri(yaml.load(open('pyple-db.yaml').read()))) # Connect to the DB
  E.drop_tables() # drop all the tables
  E.create_tables() # rebuild all the tables

  # Run tests

  test_true = AlwaysTrueOp()
  assert test_true.eval() == True, "AlwaysTrueOp.eval() should always return True"

  test_false = AlwaysFalseOp()
  assert test_false.eval() == False, "AlwaysFalseOp.eval() should always return False"

  test_and = AND()
  test_and.addParameter(test_true)
  test_and.addParameter(test_false)
  assert test_and.eval() == False, "AND.eval() of True and False should return False"

  test_or = OR()
  test_or.addParameter(test_true)
  test_or.addParameter(test_false)
  assert test_or.eval() == True, "OR.eval() of True and False should return True"

  test_and_2 = AND()
  test_and_2.addParameter(test_and)
  test_and_2.addParameter(test_or)
  assert test_and_2.eval() == False, "Complex AND should return False"

  txt = "ORDER, for the reasons set forth in the related Memoranda Opinions issued in this matter on 06/30/06 and 10/10/06, and for good cause, the final Markman definitions applicable to the disputed claim terms and phrases are as follows: (see Order for details). Signed by Judge T. S. Ellis III on 10/10/06. Copies mailed: yes (pmil) (Entered: 10/12/2006)"

  starts_with_order = RegexOp(pattern="^ORDER")
  assert starts_with_order.eval(txt) == True, "starts_with_order.eval(txt) should be True"

  contains_markman = RegexOp(pattern="markman")
  assert contains_markman.eval(txt) == True, "contains_markman.eval(txt) should be True"

  both = AND()
  both.addParameter(starts_with_order)
  both.addParameter(contains_markman)
  assert both.eval(txt) == True, "both.eval(txt) should be True"

  not_matching = RegexOp(pattern="foobar")
  assert not_matching.eval(txt) == False, "not_matching.eval(txt) should be False"

  false_and = AND()
  false_and.addParameter(starts_with_order)
  false_and.addParameter(not_matching)
  assert false_and.eval(txt) == False, "false_and.eval(txt) should be False"

  alt_data = "ORDER re: foobar and stuff"

  assert false_and.eval(alt_data) == True, "false_and.eval(alt_data) should be True"

  test_not = NOT()
  test_not.addParameter(test_true)
  assert test_not.eval() == False, "NOT.eval() of False should be True"

  test_xor = XOR()
  test_xor.addParameter(test_false)
  test_xor.addParameter(test_true)
  assert test_xor.eval() == True, "XOR.eval() of False, True should be True"

  test_xor2 = XOR()
  test_xor2.addParameter(test_true)
  test_xor2.addParameter(test_true)
  assert test_xor2.eval() == False, "XOR.eval() of True, True should be False"

  test_nand1 = NAND()
  test_nand1.addParameter(test_true)
  test_nand1.addParameter(test_true)
  assert test_nand1.eval() == False, "NAND.eval() of True, True should be False"

  test_nand2 = NAND()
  test_nand2.addParameter(test_true)
  test_nand2.addParameter(test_false)
  assert test_nand2.eval() == True, "NAND.eval() of True, False should be True"

  at2 = E.new_op(AlwaysTrueOp)
  assert at2.eval() == True, "AlwaysTrueOp.eval() should be True. [generated by Engine.new_op()]"

  print("The end!")
