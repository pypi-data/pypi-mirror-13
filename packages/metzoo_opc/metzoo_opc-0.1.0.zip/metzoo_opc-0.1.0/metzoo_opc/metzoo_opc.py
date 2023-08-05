import OpenOPC
import yaml
import pyodbc

class MetzooOPC:
  def __init__(self, config_file, debug = False):
    self.config= yaml.load(file(config_file))
    self.debug = debug
    self.init_database()
    self.init_mapping()
    self.init_opc()
  #
  def init_database(self):
    self.db= None
    if self.config.has_key("database"):
      conf= self.config["database"]
      if conf.has_key("connection"):
        db_connection= conf["connection"]
      else:
        db_connection= "DRIVER={%s};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s" % (conf["driver"], conf["host_name"], conf["db_name"], conf["login_name"], conf["login_pass"])
      if self.debug:
        print "DBConnection:", db_connection
      self.db= pyodbc.connect(db_connection)
  #
  def init_mapping(self):
    if self.config.has_key("mapping"):
      self.mapping= config["mapping"]
    elif self.db:
      self.mapping= {}
      cursor= self.db.cursor()
      cursor.execute("select * from metzoo.ifix_metzoo_relation")
      rows = cursor.fetchall()
      for row in rows:
        self.mapping[row.ifix_name]= [row.host_name, row.metric_name]
  #
  def init_opc(self):
    conf= self.config["opc"]
    self.opc = OpenOPC.open_client(conf["gateway"]) if conf.has_key("gateway") else OpenOPC.client()
    if conf.has_key("host_name"):
      self.opc.connect(conf["server_name"], conf["host_name"])
    else:
      self.opc.connect(conf["server_name"])
  #
