#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import defaultdict
from statistics import mean
import csv
import matplotlib.pyplot as plt

"""
get datapoints: from, to, topic, time, bar_time, size, latency, %loss
"""
def read_datapoints(filename, bar_period):
    points = dict()
    t0=None
    with open(args.input_file) as f:
        row=csv.reader(f)

        # Reading points is a two-step process: 1) find tx and 2) resolve
        # in rx.  Unresolved rx will have latency and size values of 0.
        # Loop twice because items can be out of order: rx before tx.
        for c in row:
            try:
                # key = from, to, topic, tx_count
                # value = either: (tx_time) or (tx_time, size, latency)
                key = c[0],c[1],c[2], int(c[3])

                if len(c) == 5:
                    # from, to, topic, tx_count, timestamp
                    if not t0:
                        t0 = float(c[4]) # start time in seconds

                    tx_time = float(c[4]) - t0
                    points[key] = (tx_time,)

                elif len(c) == 7:
                    pass

                else:
                    raise RuntimeError("unexpected length %d"%len(c))

            except Exception as e:
                print("disregarding row in first pass", c)
                print(repr(e))

    with open(args.input_file) as f:
        row=csv.reader(f)
        for c in row:
            try:
                # key = from, to, topic, tx_count
                # value = either: (tx_time) or (tx_time, size, latency)
                key = c[0],c[1],c[2], int(c[3])

                if len(c) == 5:
                    pass

                elif len(c) == 7:
                    # from, to, topic, tx_count, rx_count, size, timestamp
                    tx_time = points[key][0]
                    rx_time = float(c[6]) - t0
                    latency = (rx_time - tx_time) * 1000 # ms
                    size = int(c[5])
                    points[key] = (tx_time, size, latency)

                else:
                    raise RuntimeError("unexpected length %d"%len(c))

            except Exception as e:
                print("disregarding row in second pass", c)
                print(repr(e))

    # convert points into big list of tuple datapoints
    datapoints = list()
    for key, value in points.items():

        # bar time
        bar_time = (value[0] // bar_period) * bar_period
        
        # from, to, topic, time, bar_time, size, latency, %loss
        if len(value) == 3:
            # resolved
            datapoints.append((*key[:3], value[0], bar_time, *value[1:], 0))
        else:
            datapoints.append((*key[:3], value[0], bar_time, 0, 0, 100))

    return datapoints

def latency_points(datapoints, max_ms_latency):
    # datapoints are:
    # from, to, topic, time, bar_time, size, latency, %loss
    count_total = 0
    count_dropped = 0
    count_outliers = 0
    time_points_x = defaultdict(list)
    latency_points_y = defaultdict(list)

    for point in datapoints:
        count_total += 1
        latency = point[6]
        size = point[5]
        time = point[3]

        if latency == 0:
            count_dropped += 1
        elif latency > max_ms_latency:
            count_outliers += 1
        else:
            time_latency_key = "%s, %s, %s, %d bytes"%(*point[:3], size)
            time_points_x[time_latency_key].append(time)
            latency_points_y[time_latency_key].append(latency)

    return time_points_x, latency_points_y, \
           count_total, count_dropped, count_outliers

def latency_averages(datapoints, max_ms_latency):
    # datapoints are:
    # from, to, topic, time, bar_time, size, latency, %loss
    count_total = 0
    count_dropped = 0
    count_outliers = 0
    bar_latencies = defaultdict(list)

    # get bar latencies as dict of list of latencies
    for point in datapoints:
        count_total += 1
        if point[6] == 0:
            count_dropped += 1
        elif point[6] > max_ms_latency:
            count_outliers += 1
        else:
            bar_time = point[4]
            latency = point[6]
            key = ("%s, %s, %s"%(point[:3]), bar_time)
            bar_latencies[key].append(latency)


    # get plottable latencies
    latencies_x = defaultdict(list)
    latencies_y = defaultdict(list)

    for key, value in bar_latencies.items():
        key_string, bar_time = key
        latencies_x[key_string].append(bar_time)
        latencies_y[key_string].append(mean(value))

    return latencies_x, latencies_y, count_total, count_dropped, count_outliers

def throughput_averages(datapoints, bar_period):
    # datapoints are:
    # from, to, topic, time, bar_time, size, latency, %loss
    bar_throughputs = defaultdict(list)

    # get bar latencies as dict of list of size
    for point in datapoints:
            bar_time = point[4]
            size = point[5]
            throughput = size / bar_period
            key = ("%s, %s, %s"%(point[:3]), bar_time)
            bar_throughputs[key].append(throughput)

    # get plottable latencies
    throughputs_x = defaultdict(list)
    throughputs_y = defaultdict(list)

    for key, value in bar_throughputs.items():
        key_string, bar_time = key
        throughputs_x[key_string].append(bar_time)
        throughputs_y[key_string].append(sum(value))

    return throughputs_x, throughputs_y

def loss_averages(datapoints):
    # datapoints are:
    # from, to, topic, time, bar_time, size, latency, %loss
    bar_losses = defaultdict(list)

    # get bar losses as dict of list of %loss values
    for point in datapoints:
            bar_time = point[4]
            loss = point[7]
            key = ("%s, %s, %s"%(point[:3]), bar_time)
            bar_losses[key].append(loss)

    # get plottable latencies
    losses_x = defaultdict(list)
    losses_y = defaultdict(list)

    for key, value in bar_losses.items():
        key_string, bar_time = key
        losses_x[key_string].append(bar_time)
        losses_y[key_string].append(mean(value))

    return losses_x, losses_y

def plot_latency_points(plots_x, plots_y, args,
                        total, dropped, outliers):
    if outliers == 1:
        plural = ""
    else:
        plural = "s"
    plt.title("Latency points\n(%d of %d messages failed, %d "
              "outlier%s dropped)"%(dropped, total, outliers, plural))
    plt.ylabel("Latency in milliseconds")
    plt.xlabel("Time in seconds")
    for key in sorted(list(plots_x.keys())):
        plt.plot(plots_x[key], plots_y[key], '.', markersize=2,
                 label="%s, %d datapoints"%(key, len(plots_x[key])))
    plt.legend()

def plot_latency_trend(plots_x, plots_y, args, total, dropped, outliers):
    if outliers == 1:
        plural = ""
    else:
        plural = "s"
    plt.title("Averaged latency\n(%d of %d messages failed, %d "
              "outlier%s dropped)"%(dropped, total, outliers, plural))
    plt.ylabel("Latency in milliseconds")
    plt.xlabel("Time in seconds")
    for key in sorted(list(plots_x.keys())):
        plt.plot(plots_x[key], plots_y[key], '-', markersize=2, label=key)
    plt.legend()

def plot_throughput_trend(plots_x, plots_y, args):
    plt.title("Averaged byte throughput")
    plt.ylabel("Bytes per second")
    plt.xlabel("Time in seconds")
    for key in sorted(list(plots_x.keys())):
        plt.plot(plots_x[key], plots_y[key], '-', markersize=2, label=key)
    plt.legend()

def plot_loss_trend(plots_x, plots_y, args):
    plt.title("Packet loss")
    plt.ylabel("%Packets lost")
    plt.xlabel("Time in seconds")
    for key in sorted(list(plots_x.keys())):
        plt.plot(plots_x[key], plots_y[key], '-', markersize=2, label=key)
    plt.legend()

if __name__=="__main__":

    parser = ArgumentParser(description="Plot latency graph for network flows.",
                        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("input_file", type=str,
                        help="The CSV data input file.")
    parser.add_argument("dataset_name", type=str,
                    help="The name of this dataset.")
    parser.add_argument("-m","--max_ms_latency", type=float,
                help="The maximum ms latency allowed without being dropped.",
                        default = 20)
    parser.add_argument("-b","--bar_period", type=int,
                help="The time, in seconds, for each averaged period.",
                        default = 5)
    parser.add_argument("-w","--write_file", type=str,
                    help="Write to <filename>_<plot_type>.png.",
                        default = "")
    args = parser.parse_args()

    datapoints = read_datapoints(args.input_file, args.bar_period)

    # plots
    plt.figure(figsize=(12,10), dpi=90)
    plt.suptitle("QoS for %s"%args.dataset_name)

    # latency points
    plt.subplot(2,2,1)
    time_points_x, latency_points_y, \
                      count_total, count_dropped, count_outliers = \
                      latency_points(datapoints, args.max_ms_latency)
    plot_latency_points(time_points_x, latency_points_y, args,
                        count_total, count_dropped, count_outliers)

    # latency bar averages
    plt.subplot(2,2,2)
    latencies_x, latencies_y, count_total, count_dropped, count_outliers = \
                 latency_averages(datapoints, args.max_ms_latency)
    plot_latency_trend(latencies_x, latencies_y, args,
                       count_total, count_dropped, count_outliers)

    # bytes throughput
    plt.subplot(2,2,3)
    throughputs_x, throughputs_y = throughput_averages(datapoints,
                                                       args.bar_period)
    plot_throughput_trend(throughputs_x, throughputs_y, args)

    # % loss
    plt.subplot(2,2,4)
    throughputs_x, throughputs_y = loss_averages(datapoints)
    plot_loss_trend(throughputs_x, throughputs_y, args)

    # to screen or file
    if args.write_file:
        plt.savefig("%s.png"%args.write_file)
    else:
        plt.show()

