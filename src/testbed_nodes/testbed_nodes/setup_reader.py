#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os.path import expanduser
import csv
from collections import defaultdict
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, \
     QoSReliabilityPolicy, QoSProfile

# modes: start, publishers, subscribers, robots
_START = []
_PUBLISH = ["Role", "Subscription", "Frequency", "Size",
            "History", "Depth", "Reliability", "Durability"]
_SUBSCRIBE = ["Role", "Subscription",
              "History", "Depth", "Reliability", "Durability"]
_ROBOT = ["Name", "Role", "param:value"]

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

def _qos_profile_string(profile):
    return "QoS: %s, %s, %s, %s"%(profile.history,
                                  profile.depth,
                                  profile.reliability,
                                  profile.durability)

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

    def __str__(self):
        return "Publisher: %s, %s, %d, %d, %s"%(
               self.role, self.subscription, self.frequency, self.size,
               _qos_profile_string(self.qos_profile))

class SubscribeRecord():
    def __init__(self, row):
        self.role = row[0]
        self.subscription = row[1]
        history = row[2]             # keep_last|keep_all
        depth = int(row[3])          # used if using keep_last
        reliability = row[4]         # reliable|best_effort
        durability = row[5]          # transient_local|volatile
        self.qos_profile = _qos_profile(history, depth, reliability, durability)

    def __str__(self):
        return "Subscriber: %s, %s, %s"%(
               self.role, self.subscription,
               _qos_profile_string(self.qos_profile))

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

# get lists of subscriber robot names by key=subscription, value=list(names)
def _recipients(subscribers, robots):

    # get subscribers: key=subscription, value=list(robot names)
    all_recipients = defaultdict(list)
    for robot in robots:
        for subscriber in subscribers:
            if subscriber.role == robot.role:
                all_recipients[subscriber.subscription].append(
                                                       robot.robot_name)
    return all_recipients

# throws
def read_setup(filename):
    publishers = list()
    subscribers = list()
    robots = list()

    with open(filename) as f:
        mode="start"
        valid_header = _START
        reader = csv.reader(f)
        total_count = 0
        for row in reader:

            # blank first column
            if not row or not row[0]:
                continue

            # remove spaces
            row=[x.strip() for x in row]
            print(row)

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

def show_setup(filename, publishers, subscribers, robots, recipients):
    print("Scenario file: %s"%filename)
    print("publishers: %d"%len(publishers))
    for publisher in publishers:
        print(publisher)
    print("subscribers: %d"%len(subscribers))
    for subscriber in subscribers:
        print(subscriber)
        print("recipients for subscription %s: "%subscriber.subscription,
                                       recipients[subscriber.subscription])
    print("robots: %d"%len(robots))
    for robot in robots:
        print(robot)


if __name__ == '__main__':
    parser = ArgumentParser(description="Check your setup file.",
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("setup_file", type=str, help="The scenario setup file.")
    args = parser.parse_args()

    # show setup
    setup_file = expanduser(args.setup_file)
    publishers, subscribers, robots, recipients = read_setup(setup_file)
    show_setup(setup_file, publishers, subscribers, robots, recipients)

