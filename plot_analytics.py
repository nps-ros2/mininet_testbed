#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import defaultdict
from statistics import mean
import csv
import matplotlib.pyplot as plt


def plot_latency_points(args, dropped, total, outliers, plots_x, plots_y):
    plt.clf()
    if outliers == 1:
        plural = ""
    else:
        plural = "s"
    plt.title("Latency point graph for %s\n(%d of %d messages failed, %d outlier%s dropped)"%(args.dataset_name, dropped, total, outliers, plural))
    plt.ylabel("Latency in milliseconds")
    plt.xlabel("Time in seconds")
    for key in sorted(list(plots_x.keys())):
        plt.plot(plots_x[key], plots_y[key], '.', markersize=2,
                 label="%s, %d datapoints"%(key, len(plots_x[key])))
    plt.legend()
    if args.write_file:
        plt.savefig("%s_latency_points.png"%args.write_file)
    else:
        plt.show()

def plot_latency(args, dropped_latencies, total_latencies, plots_x, plots_y):
    plt.clf()
    plt.title("Latency graph for %s\n(%d of %d messages failed)"%(
                  args.dataset_name, dropped_latencies, total_latencies))
    plt.ylabel("Latency in milliseconds")
    plt.xlabel("Time in seconds")
    for key in sorted(list(plots_x.keys())):
        plt.plot(plots_x[key], plots_y[key], '-', markersize=2,
                 label=key)
    plt.legend()
    if args.write_file:
        plt.savefig("%s_latency.png"%args.write_file)
    else:
        plt.show()

def plot_throughput(args, plots_x, plots_y):
    plt.clf()
    plt.title("Throughput graph for %s"%args.dataset_name)
    plt.ylabel("Bytes per second")
    plt.xlabel("Time in seconds")
    for key in sorted(list(plots_x.keys())):
        plt.plot(plots_x[key], plots_y[key], '-', markersize=2,
                 label=key)
    plt.legend()
    if args.write_file:
        plt.savefig("%s_throughput.png"%args.write_file)
    else:
        plt.show()

def plot_loss(args, plots_x, plots_y):
    plt.clf()
    plt.title("Loss graph for %s"%args.dataset_name)
    plt.ylabel("%Packets lost")
    plt.xlabel("Time in seconds")
    for key in sorted(list(plots_x.keys())):
        plt.plot(plots_x[key], plots_y[key], '-', markersize=2,
                 label=key)
    plt.legend()
    if args.write_file:
        plt.savefig("%s_loss.png"%args.write_file)
    else:
        plt.show()

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
                help="The time, in seconds, for each histogram bar.",
                        default = 25)
    parser.add_argument("-w","--write_file", type=str,
                    help="Write to <filename>_<plot_type>.png.",
                        default = "")
    args = parser.parse_args()

    plots_x_latency=defaultdict(list)
    plots_y_latency=defaultdict(list)
    latency_outliers = 0

    with open(args.input_file) as f:
        row=csv.reader(f)
        max_y=args.max_ms_latency
        datapoints = dict()
        t0=None
        for c in row:
            # skip lines with less than 5 commas
            if len(c) < 5:
                continue

            # skip Row lines
            if c[0][:4] == "Row:":
                continue

            # remove ROS2 log headers
            header_index = c[0].find(": ")
            if header_index != -1:
                c[0] = c[0][header_index+2:]

            key = c[0],c[1],c[2], int(c[3]) # from, to, subscription, tx_count
            if len(c) == 5:
                if not t0:
                    t0 = float(c[4]) # start time in time.perf_counter seconds
                # tx: from, to, subscription, tx_count, timestamp
                datapoints[key] = float(c[4]), 0, 0 # time_ns, latency, size

            elif len(c) == 7:
                # from, to, subscription, tx_count, rx_count, size, timestamp
                time = (datapoints[key][0] - t0) # seconds from t0
                latency = (float(c[6]) - datapoints[key][0]) * 1000 # ms
                datapoints[key] = float(c[6]), latency, c[5] # t_sec, latency, size

                if latency > max_y:
                    latency_outliers += 1
                else:
                    latency_key = "%s, %s, %s, %d bytes"%(c[0],c[1],c[2],
                                                          float(c[5]))
                    plots_x_latency[latency_key].append(time)
                    plots_y_latency[latency_key].append(latency)

            else:
                print("disregarding row")
                print(c)

    # statistics by bar period
    latencies = defaultdict(list)
    throughputs = defaultdict(list)
    percent_losses = defaultdict(list)

    dropped_latencies = 0
    total_latencies = 0
    bar_period = args.bar_period
    for key, value in datapoints.items():
        # key = from, to, subscription, _tx_count
        # value = time_ns, latency, size
        t=((value[0]-t0)//bar_period) * bar_period
        stat_key = key[0],key[1],key[2],t

        # latency
        latency = float(value[1])
        if latency:
            latencies[stat_key].append(latency)
        else:
            dropped_latencies += 1
        total_latencies += 1

        # throughput
        throughput = int(value[2])
        throughputs[stat_key].append(throughput)

        # percent_loss
        if throughput == 0:
            percent_loss = 100
        else:
            percent_loss = 0
        percent_losses[stat_key].append(percent_loss)

    # latency
    latencies_x = defaultdict(list)
    latencies_y = defaultdict(list)
    for key, value in latencies.items():
        if not value:
            # we do not monitor values when messages are lost
            continue
        # key = from, to, subscription, int_second
        # value = int latencies
        key_string = "%s, %s, %s"%(key[0],key[1],key[2])
        latencies_x[key_string].append(key[3]) # second
        latencies_y[key_string].append(mean(value))

    # throughput
    throughputs_x = defaultdict(list)
    throughputs_y = defaultdict(list)
    for key, value in throughputs.items():
        # key = from, to, subscription, int_second
        # value = int throughputs
        key_string = "%s, %s, %s"%(key[0],key[1],key[2])
        throughputs_x[key_string].append(key[3]) # second
        throughputs_y[key_string].append(sum(value)/bar_period)

    # percent loss
    percent_losses_x = defaultdict(list)
    percent_losses_y = defaultdict(list)
    for key, value in percent_losses.items():
        # key = from, to, subscription, int_second
        # value = int percent_losses
        key_string = "%s, %s, %s"%(key[0],key[1],key[2])
        percent_losses_x[key_string].append(key[3]) # second
        percent_losses_y[key_string].append(mean(value))

    plot_latency_points(args, dropped_latencies, total_latencies,
                        latency_outliers, plots_x_latency, plots_y_latency)
    plot_latency(args, dropped_latencies, total_latencies,
                                    latencies_x, latencies_y)
    plot_throughput(args, throughputs_x, throughputs_y)
    plot_loss(args, percent_losses_x, percent_losses_y)

