import csv
from collections import defaultdict
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, \
     QoSReliabilityPolicy
from rclpy.qos import QoSProfile

# modes: start, publishers, subscribers, robots
_PUBLISH = ["role", "subscription", "frequency,size",
            "history", "depth", "reliability", "durability"]
_SUBSCRIBE = ["role", "subscription",
              "history", "depth", "reliability", "durability"]
_ROBOT = ["role", "x", "y", "z", "walks"]
HEADERS={"publishers":_PUBLISH, "subscribers":_SUBSCRIBE,
         "robots":_ROBOT}

# ref. https://github.com/ros2/demos/blob/master/topic_monitor/topic_monitor/scripts/data_publisher.py
def _qos_profile(history, depth, reliability, durability):
    # depth
    profile = QoSProfile(depth = depth)

    # history
    if history == "keep_all":
        profile.history = QoSHistoryPolicy.RMW_QOS_POLICY_HISTORY_KEEP_ALL
    elif history == "keep_last":
        profile.history = QoSHistoryPolicy.RMW_QOS_POLICY_HISTORY_KEEP_LAST
    else:
        raise RuntimeError("Invalid history policy: %s"%history)

    # reliability
    if reliability == "reliable":
        profile.reliability = \
                   QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_RELIABLE
    elif reliability == "best_effort":
        profile.reliability = \
                   QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT
    else:
        raise RuntimeError("Invalid reliability policy: %s"%reliability)

    # durability
    if durability == "transient_local":
        profile.durability = \
                   QoSDurabilityPolicy.RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL
    elif durability == "volatile":
        profile.durability = \
                   QoSDurabilityPolicy.RMW_QOS_POLICY_DURABILITY_VOLATILE
    else:
        raise RuntimeError("Invalid durability policy: %s"%durability)

    return profile

class PublishRecord():
    def __init__(self, row):
        self.role = row[0]
        self.subscription = row[1]
        self.frequency = int(row[2])
        self.size = int(row[3])

        history = row[4]             # keep_last|keep_all
        depth = int(row[5])          # used if using keep_last
        reliability = row[6]         # reliable|best_effort
        durability = row[7]          # transient_local|volatile
        self.qos_profile = _qos_profile(history, depth, reliability, durability)

class SubscribeRecord():
    def __init__(self, row):
        self.role = row[0]
        self.subscription = row[1]
        history = row[2]             # keep_last|keep_all
        depth = int(row[3])          # used if using keep_last
        reliability = row[4]         # reliable|best_effort
        durability = row[5]          # transient_local|volatile
        self.qos_profile = _qos_profile(history, depth, reliability, durability)

class RobotRecord():
    def __init__(self, row):
        self.role = row[0]
        self.x = float(row[1])
        self.y = float(row[2])
        self.z = float(row[3])
        if row[4] == "true":
            moves = True
        elif row[4] == "false":
            moves = False
        else:
            raise RuntimeError("Invalid field.  Aborting.")
    def position_string():
        return "%f,%f,%f"%(x,y,z)

# get lists of subscriber robot names by key=subscription, value=list(names)
def _recipients(subscribers, robots):

    # get subscribers: key=subscription, value=list(robot names)
    all_recipients = defaultdict(list)
    for i, robot in enumerate(robots):
        role = robot.role
        for subscriber in subscribers:
             if subscriber.role == role:
                 robot_name = "r%d"%i
                 all_recipients[subscriber.subscription].append(robot_name)
    return all_recipients

# throws
def read_setup(filename):
    publishers = list()
    subscribers = list()
    robots = list()

    with open(filename) as f:
        mode="start"
        reader = csv.reader(f)
        total_count = 0
        for row in reader:
            print("Row: %s"%",".join(row))

            # blank first column
            if not row or not row[0]:
                continue

            # lowercase the row
            row=[x.lower() for x in row]

            # mode publish
            if row[0]=="publishers":
                mode = "publish"
                continue

            # mode subscribe
            if row[0]=="subscribers":
                mode = "subscribe"
                continue

            # mode robot
            if row[0]=="robots":
                mode = "robot"
                continue

            # allow valid header
            if row[0] in HEADERS:
                header = headers[row[0]]
                if header == row[:len(header)]:
                    continue
                else:
                    raise RuntimeError("Invalid header.  Aborting.")

            # parse by mode
            if mode == "publish":
                publishers.append(PublishRecord(row))
            elif mode == "subscribe":
                subscribers.append(SubscribeRecord(row))
            elif mode == "robot":
                robots.append(RobotRecord(row))
            else:
                print("invalid mode '%s' for row '%s'"%(
                                            mode, ",".join(row)))
                raise RuntimeError("Invalid table.  Aborting")

        recipients = _recipients(subscribers, robots)
        return publishers, subscribers, robots, recipients

