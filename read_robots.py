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
_ROBOT = ["Name", "Role", "X", "Y", "Z", "Moves"]

class RobotRecord():
    def __init__(self, row):
        self.robot_name = row[0]
        self.role = row[1]
        self.x = float(row[2])
        self.y = float(row[3])
        self.z = float(row[4])
        if row[5] == "true":
            moves = True
        elif row[5] == "false":
            moves = False
        else:
            raise RuntimeError("Invalid field.  Aborting.")
    def position_string(self):
        return "%f,%f,%f"%(self.x,self.y,self.z)

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

