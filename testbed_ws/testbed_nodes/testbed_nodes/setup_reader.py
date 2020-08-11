#!/usr/bin/env python3
from sys import version_info
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os.path import expanduser
import csv
from collections import defaultdict
from json import dumps
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, \
     QoSReliabilityPolicy, QoSProfile

# ref. https://github.com/ros2/demos/blob/master/topic_monitor/topic_monitor/scripts/data_publisher.py
def qos_profile(d):
    history = d["history"]             # keep_last|keep_all
    depth = d["depth"]                 # used if using keep_last
    reliability = d["reliability"]     # reliable|best_effort
    durability = d["durability"]       # transient_local|volatile

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

def _publish_record(row):
    d=dict()
    d["role"]=row[0]
    d["topic"] = row[1]
    d["frequency"] = int(row[2])
    d["size"] = int(row[3])

    d["history"] = row[4]
    d["depth"] = int(row[5])
    d["reliability"] = row[6]
    d["durability"] = row[7]
    return d

def _subscribe_record(row):
    d=dict()
    d["role"]=row[0]
    d["topic"] = row[1]

    d["history"] = row[2]
    d["depth"] = int(row[3])
    d["reliability"] = row[4]
    d["durability"] = row[5]
    return d

def _robot_record(row):
    d=dict()
    d["robot_name"] = row[0]
    d["role"] = row[1]
    return d

# get lists of subscriber robot names by key=topic, value=list(names)
def _recipients(subscribers, robots):

    # get subscribers: key=topic, value=list(robot names)
    all_recipients = defaultdict(list)
    for robot in robots:
        print("robot: ", robot)
        for subscriber in subscribers:
            print("subscriber: ", subscriber)
            if subscriber["role"] == robot["role"]:
                all_recipients[subscriber["topic"]].append(
                                                       robot["robot_name"])
    return all_recipients

# throws
def read_setup(filename):
    publishers = list()
    subscribers = list()
    robots = list()
    stations = list()
    links = list()
    propagation_model = dict()
    mobility_model = dict()
    start_mobility = dict()
    mobilities = list()
    stop_mobility = dict()
    plot_graph = None # else dict()

    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:

            # remove spaces
            row=[x.strip() for x in row]
            print(row)

            # blank or comment in first column
            if not row or not row[0] or row[0][0]=="#":
                continue

            # parse by mode
            mode = row[0]
            try:
                if mode == "Publisher":
                    publishers.append(_publish_record(row[1:]))
                elif mode == "Subscriber":
                    subscribers.append(_subscribe_record(row[1:]))
                elif mode == "Robot":
                    robots.append(_robot_record(row[1:]))
                else:
                    print("invalid directive '%s' for row '%s'"%(
                                            mode, ",".join(row)))
                    raise RuntimeError("Invalid table.  Aborting")
            except Exception:
                raise RuntimeError("Invalid line: %s.  Aborting"%row)

    setup = dict()
    setup["publishers"] = publishers
    setup["subscribers"] = subscribers
    setup["robots"] = robots
    setup["all_recipients"] = _recipients(subscribers, robots)
    return setup

def show_setup(filename, setup):
    print("Scenario file: %s"%filename)
    print(dumps(setup, indent=4, sort_keys=True))

if __name__ == '__main__':
    parser = ArgumentParser(description="Check your setup file.",
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("setup_file", type=str, help="The scenario setup file.")
    args = parser.parse_args()

    # show setup
    setup_file = expanduser(args.setup_file)
    setup = read_setup(setup_file)
    show_setup(setup_file, setup)

