# Note: this is a subset of setup_reader.py.  It is compatible with Python 2
# so it can work with Mininet which is not compatible with Python3.

import csv
from collections import defaultdict
#from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, \
#     QoSReliabilityPolicy
#from rclpy.qos import QoSProfile

# modes: start, publishers, subscribers, robots
_START = []
_PUBLISH = ["Role", "Subscription", "Frequency", "Size",
            "History", "Depth", "Reliability", "Durability"]
_SUBSCRIBE = ["Role", "Subscription",
              "History", "Depth", "Reliability", "Durability"]
_ROBOT = ["Name", "Role", "param:value"]

# returned dict values are float else string
def _station_params(param_list):
    params = dict()
    for pair in param_list:
        key,value=pair.split(":")
        key,value=key.strip(),value.strip()
        # values are float if possible else string
        try:
            params[key]=float(value)
        except ValueError:
            params[key]=value.replace(";",",")
    return params

class RobotRecord():
    def __init__(self, row):
        self.robot_name = row[0]
        self.role = row[1]
        self.station_params = _station_params(row[2:])

    def __str__(self):
        text = "Robot: %s, %s"%(self.robot_name, self.role)
        for key, value in sorted(self.station_params.items()):
            if type(value) == str:
                # show with semicolons
                value = value.replace(",",";")
            text += ",%s:%s"%(key,value)
        return text

# throws
def read_robots(filename):
    robots = list()

    with open(filename) as f:
        mode="start"
        valid_header = _START
        reader = csv.reader(f)
        total_count = 0
        for row in reader:
            print(row)

            # blank first column
            if not row or not row[0]:
                continue

            # remove spaces
            row=[x.strip() for x in row]

            # mode publish
            if row[0]=="Publishers":
                mode = "publish"
                valid_header = _PUBLISH
                continue

            # mode subscribe
            if row[0]=="Subscribers":
                mode = "subscribe"
                valid_header = _SUBSCRIBE
                continue

            # mode robot
            if row[0]=="Robots":
                mode = "robot"
                valid_header = _ROBOT
                continue

            # allow valid header
            if row[:len(valid_header)] == valid_header:
                continue

            # parse by mode
            if mode == "publish":
                pass
            elif mode == "subscribe":
                pass
            elif mode == "robot":
                robots.append(RobotRecord(row))
            else:
                print("invalid mode '%s' for row '%s'"%(
                                            mode, ",".join(row)))
                raise RuntimeError("Invalid table.  Aborting")

        return robots

