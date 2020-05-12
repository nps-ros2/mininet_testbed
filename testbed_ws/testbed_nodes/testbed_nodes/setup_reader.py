#!/usr/bin/env python3
from sys import version_info
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os.path import expanduser
import csv
from collections import defaultdict
from json import dumps

if version_info[0] == 2:
    # Python2 is for mininet
    from mn_wifi.link import wmediumd, adhoc, mesh # for class
    MININET_WIFI_CLASSES = {"adhoc":adhoc, "mesh":mesh}

elif version_info[0] == 3:
    # Python3 is for ROS2
    from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, \
         QoSReliabilityPolicy, QoSProfile
    MININET_WIFI_CLASSES = {"adhoc":"adhoc", "mesh":"mesh"}

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
    "Stations":["Name", "param=value"],

    # Links
    "Links":["Name", "param=value"],

    # Propagation Model
    "Propagation Model":["param=value"],

    # Mobility Model
    "Mobility Model":["param=value"],

    # Graph
    "Plot Graph":["param=value"],

    # Log Level
    "Log Level":["Level"],
}

def _json_serialize(_class):
    if _class in MININET_WIFI_CLASSES.values():
        # serialize mininet-WiFi class object as its class name
        return _class.__name__
    else:
        # use basic JSON types
        return _class.__dict__

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

# returned dict values are: float, int, str, or predefined mininet-WiFi class
def _typed_params(param_list):
    params = dict()
    for pair in param_list:
        key,value=pair.split("=")
        key,value=key.strip(),value.strip()

        try:
            # float or int
            if "." in value:
                params[key]=float(value)
            else:
                params[key]=int(value)
        except ValueError:
            # class or string
            if key == "cls":
                params[key] = MININET_WIFI_CLASSES[value]
            else:
                params[key]=value.replace(";",",")
    return params

def _named_typed_params(row):
    name = row[0]
    return name, _typed_params(row[1:])

def _publish_record(row):
    d=dict()
    d["role"]=row[0]
    d["subscription"] = row[1]
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
    d["subscription"] = row[1]

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
    plot_graph = dict()
    log_level = ""

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
                elif mode == "Mobility Model":
                    mobility_model = _typed_params(row)
                elif mode == "Plot Graph":
                    plot_graph = _typed_params(row)
                elif mode == "Log Level":
                    log_level = row[0]
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
    setup["plot_graph"] = plot_graph
    setup["log_level"] = log_level
    setup["all_recipients"] = _recipients(subscribers, robots)
    return setup

def show_setup(filename, setup):
    print("Scenario file: %s"%filename)
    print(dumps(setup, indent=4, sort_keys=True, default=_json_serialize))

if __name__ == '__main__':
    parser = ArgumentParser(description="Check your setup file.",
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("setup_file", type=str, help="The scenario setup file.")
    args = parser.parse_args()

    # show setup
    setup_file = expanduser(args.setup_file)
    setup = read_setup(setup_file)
    show_setup(setup_file, setup)

