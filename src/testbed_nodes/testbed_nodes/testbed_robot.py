#!/usr/bin/env python3
from sys import stdout
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os.path import join, expanduser
from collections import defaultdict
from time import perf_counter
from fcntl import flock, LOCK_EX, LOCK_UN
import rclpy
from rclpy.node import Node
from testbed_msg import TestbedMessage
from testbed_nodes.testbed_codec import testbed_encode, testbed_decode
from testbed_nodes.setup_reader import read_setup

class TestbedRobot(Node):

    def _make_publisher_timer_callback_function(self, subscription_name, size,
                                                recipients, f):
        def fn():
            self.counters[subscription_name] += 1
            transmit_count = self.counters[subscription_name]
            robot_name = self.robot_name

            # compose message
            msg = TestbedMessage()
            msg.publisher_name = robot_name
            msg.tx_count = transmit_count
            msg.message = subscription_name[0]*size

            # compose network metadata log
            s = ""
            for recipient_robot_name in recipients:
                s += "%s,%s,%s,%d,%f\n"%(
                           robot_name,
                           recipient_robot_name,
                           subscription_name,
                           transmit_count,
                           perf_counter())

            # publish the message
            self.publisher_managers[subscription_name].publish(msg)

            # log the publish metadata
            flock(f, LOCK_EX) # exclusive lock
            f.write(s)
            flock(f, LOCK_UN) # unlock
        return fn

    def _make_subscriber_callback_function(self, subscription_name, f):
        def fn(self, msg):
#            self.get_logger().info("_make_subscribe: '%s'"%msg.data[:60])
#            self.get_logger().info("subscription callback")
       
            # rx log: from, to, subscription, tx count, rx count, msg size, ts
            response = "%s,%s,%s,%d,%d,%d,%f"%(
                           msg.publisher_name,
                           self.robot_name,
                           subscriptioin_name,
                           msg.tx_count,
                           self.counters[subscription_name],
                           len(msg.message))

            # log the response metadata
            flock(f, LOCK_EX) # exclusive lock
            f.write(s)
            flock(f, LOCK_UN) # unlock
        return fn

    def __init__(self, robot_name, role, setup_file, f):
        super().__init__(robot_name)
        self.robot_name = robot_name
        self.role = role
        self.f = f

        # get setup parameters
        publishers, subscribers, robots, all_recipients = read_setup(
                                                               setup_file)

        # start publishers for this role
        self.counters = defaultdict(int)
        self.publisher_managers = dict()
        self.timers = list()
        for publisher in publishers:
            # only publish subscriptions assigned to this role
            if publisher.role != role:
                continue

            # the subscription for this publisher entry
            subscription = publisher.subscription

            # make and keep static references to publisher managers
            self.publisher_managers[subscription] = self.create_publisher(
                             TestbedMessage, subscription,
                             qos_profile=publisher.qos_profile)

#            # the counter
#            counter = self.counters[subscription]

            # recipients
            recipients = all_recipients[subscription]

            # the callback function that is dynamically created using closure
            publisher_timer_callback_function = \
                            self._make_publisher_timer_callback_function(
                                  subscription, publisher.size, recipients, f)
            period = 1/publisher.frequency
            timer = self.create_timer(period, publisher_timer_callback_function)
            self.timers.append(timer)

        # start subscribers
        subscriptions = list()
        for subscriber in subscribers:

            # only subscribe to subscriptions assigned to this role
            if subscriber.role != role:
                continue

            _subscriber_callback_function = _make_subscriber_callback_function(
                                  subscriber.subscription, f)

            subscription = self.create_subscription(
                                  TestbedMessage,
                                  subscriber.subscription,
                                  _subscriber_callback_function,
                                  qos_profile=subscriber.qos_profile)
            subscriptions.append(subscription)

def main():
    parser = ArgumentParser(description="Generic testbed robot.",
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("robot_name", type=str,
                        help="The name of this robot node.")
    parser.add_argument("role", type=str, help="This robot's role")
    parser.add_argument("setup_file", type=str, help="The scenario setup file.")
    parser.add_argument("out_file", type=str, help="The output file.")
    args = parser.parse_args()
    print("Starting testbed_robot %s"%args.robot_name)
    stdout.flush()

    # open out_file w+
    with open(args.out_file, "w+") as f:

        rclpy.init()
        robot_node = TestbedRobot(args.robot_name, args.role,
                                  args.setup_file, f)
        rclpy.spin(robot_node)
        robot_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

