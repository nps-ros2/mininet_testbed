#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os.path import expanduser
import csv
from collections import defaultdict
from json import dumps
try:
    from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, \
         QoSReliabilityPolicy, QoSProfile
except SyntaxError:
    # Python2 or incompatible ROS2 version
    pass

MODES = \
{
    # start
    "start":[],

    # Publishers
    "Publishers":["Role", "Subscription", "Frequency", "Size",
                  "History", "Depth", "Reliability", "Durability"],

    # Subscribers
    "Subscribers":["Role", "Subscription",
                   "History", "Depth", "Reliability", "Durability"],

    # Robots
    "Robots":["Name", "Role"],

    # Stations
    "Stations":["Name", "param:value"],

    # Links
    "Links":["Name", "param:value"],

    # Propagation Model
    "Propagation Model":["param:value"],

    # Mobility Model
    "Mobility Model":["param:value"],
}

# ref. https://github.com/ros2/demos/blob/master/topic_monitor/topic_monitor/scripts/data_publisher.py
def qos_profile(qos):
    history = qos["history"]             # keep_last|keep_all
    depth = qos["depth"]                 # used if using keep_last
    reliability = qos["reliability"]     # reliable|best_effort
    durability = qos["durability"]       # transient_local|volatile

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

# returned dict values are float else string
def _typed_params(param_list):
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

def _named_typed_params(row):
    name = row[0]
    return name, _typed_params(row[1:])

def _publish_record(row):
    d=dict()
    d["role"]=row[0]
    d["subscription"] = row[1]
    d["frequency"] = row[2]
    d["size"] = row[3]

    d["history"] = row[4]
    d["depth"] = row[5]
    d["reliability"] = row[6]
    d["durability"] = row[7]
    return d

def _subscribe_record(row):
    d=dict()
    d["role"]=row[0]
    d["subscription"] = row[1]

    d["history"] = row[2]
    d["depth"] = row[3]
    d["reliability"] = row[4]
    d["durability"] = row[5]
    return d

def _robot_record(row):
    d=dict()
    d["robot_name"] = row[0]
    d["role"] = row[1]
    return d

# get lists of subscriber robot names by key=subscription, value=list(names)
def _recipients(subscribers, robots):

    # get subscribers: key=subscription, value=list(robot names)
    all_recipients = defaultdict(list)
    for robot in robots:
        print("robot: ", robot)
        for subscriber in subscribers:
            print("subscriber: ", subscriber)
            if subscriber["role"] == robot["role"]:
                all_recipients[subscriber["subscription"]].append(
                                                       robot["robot_name"])
    return all_recipients

# throws
def read_setup(filename):
    publishers = list()
    subscribers = list()
    robots = list()
    stations = defaultdict(dict)
    links = defaultdict(dict)
    propagation_model = dict()
    mobility_model = dict()

    with open(filename) as f:
        mode="start"
        reader = csv.reader(f)
        total_count = 0
        for row in reader:

            # remove spaces
            row=[x.strip() for x in row]
            print(row)

            # blank or comment in first column
            if not row or not row[0] or row[0][0]=="#":
                continue

            # model label sets parser mode
            if row[0] in MODES.keys():
                mode = row[0]
                header = MODES[mode]
                continue

            # accept mode-appropriate header
            if row[:len(header)] == header:
                continue

            try:
                # parse by mode
                if mode == "Publishers":
                    publishers.append(_publish_record(row))
                elif mode == "Subscribers":
                    subscribers.append(_subscribe_record(row))
                elif mode == "Robots":
                    robots.append(_robot_record(row))
                elif mode == "Stations":
                    robot_name, typed_params = _named_typed_params(row)
                    stations[robot_name] = typed_params
                elif mode == "Links":
                    robot_name, typed_params = _named_typed_params(row)
                    links[robot_name] = typed_params
                elif mode == "Propagation Model":
                    propagation_model = _typed_params(row)
                elif mode == "Mobility Model":
                    mobility_model = _typed_params(row)
                else:
                    print("invalid mode '%s' for row '%s'"%(
                                            mode, ",".join(row)))
                    raise RuntimeError("Invalid table.  Aborting")
            except Exception:
                raise RuntimeError("Invalid line: %s.  Aborting"%row)

    setup = dict()
    setup["publishers"] = publishers
    setup["subscribers"] = subscribers
    setup["robots"] = robots
    setup["stations"] = stations
    setup["links"] = links
    setup["propagation_model"] = propagation_model
    setup["mobility_model"] = mobility_model
    print("open.subscribers: ", subscribers)
    print("open.robots: ", robots)
    setup["recipients"] = _recipients(subscribers, robots)
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

