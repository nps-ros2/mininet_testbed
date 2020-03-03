#!/usr/bin/env python3
from sys import stdout
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os.path import join, expanduser
from collections import defaultdict
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from testbed_nodes.testbed_codec import testbed_encode, testbed_decode
from testbed_nodes.setup_reader import read_setup

class TestbedRobot(Node):

    def _make_publisher_timer_callback_function(self, subscription_name, size):
        def fn():
            if self.verbose:
                self.get_logger().info("publisher callback for %s"%subscription_name)
            self.counters[subscription_name] += 1
            count = self.counters[subscription_name]
            msg = String()
            msg.data = testbed_encode(self.robot_name,
                                      subscription_name,
                                      count,
                                      size)
#            self.get_logger().info("_make_publish: '%s'"%msg.data[:60])
            self.publisher_managers[subscription_name].publish(msg)
        return fn

    def _subscription_callback_function(self, msg):
#        self.get_logger().info("_make_subscribe: '%s'"%msg.data[:60])
        if self.verbose:
            self.get_logger().info("subscription callback")
        source, name, number, size, dt = testbed_decode(msg.data)
        response = "%s,%s,%d,%d,%f"%(source, name, number, size, dt)

        self.get_logger().info(response)

    def __init__(self, robot_name, robot_role, publishers,
                                             subscribers, verbose):
        super().__init__(robot_name)
        self.robot_name = robot_name
        self.robot_role = robot_role
        self.verbose = verbose

        # start publishers
        self.counters = defaultdict(int)
        self.publisher_managers = dict()
        self.timers = list()
        for publisher in publishers:
            # only publish to subscriptions intended for this robot
            if publisher.role != robot_role:
                continue

            # the publisher manager
            publisher_manager = self.create_publisher(
                                  String,
                                  publisher.subscription,
                                  qos_profile=publisher.qos_profile)
            self.publisher_managers[publisher.subscription] = publisher_manager

            # the counter
            counter = self.counters[publisher.subscription]

            # the callback function that is dynamically created using closure
            publisher_timer_callback_function = \
                            self._make_publisher_timer_callback_function(
                                           publisher.subscription, publisher.size)
            period = 1/publisher.frequency
            timer = self.create_timer(period, publisher_timer_callback_function)
            self.timers.append(timer)

        # start subscribers
        subscriptions = list()
        for subscriber in subscribers:

            # only subscribe to subscriptions intended for this robot
            if subscriber.role != robot_role:
                continue

            subscription = self.create_subscription(
                                  String,
                                  subscriber.subscription,
                                  self._subscription_callback_function,
                                  qos_profile=subscriber.qos_profile)
            subscriptions.append(subscription)

def main():
    default_setup_file = join(expanduser("~"),
                         "gits/mininet_testbed/testbed/csv_roles/example1.csv")
    parser = ArgumentParser(description="Generic testbed robot.",
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("robot_name", type=str,
                        help="The name of this robot node.")
    parser.add_argument("robot_role", type=str, help="This robot's role")
    parser.add_argument("-s","--setup_file", type=str,
                        help="The CSV setup file.",
                        default = default_setup_file)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose diagnostics.")
    args = parser.parse_args()
    print("Starting testbed_robot %s"%args.robot_name)
    stdout.flush()

    # get setup parameters
    publishers, subscribers = read_setup(args.setup_file, args.verbose)
    stdout.flush()

    rclpy.init()
    robot_node = TestbedRobot(args.robot_name, args.robot_role, publishers,
                              subscribers, args.verbose)
    rclpy.spin(robot_node)
    robot_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

