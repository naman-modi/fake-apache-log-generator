#!/usr/bin/python
import time
import datetime
import pytz
import numpy
import random
import gzip
import sys
import argparse
import os
from faker import Faker
from tzlocal import get_localzone

local = get_localzone()

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False

def print_checkpoint(file_size):
    """Print checkpoint to the console when a certain file size is reached."""
    print("Checkpoint: {} MB generated".format(file_size))
    sys.stdout.flush()  # Flush the standard output

parser = argparse.ArgumentParser(__file__, description="Fake Apache Log Generator")
parser.add_argument("--input", "-i", dest='input_file', help="Existing log file for appending logs", type=str, default="/app/output.log")
parser.add_argument("--num", "-n", dest='num_lines', help="Number of lines to generate (0 for infinite)", type=int, default=0)
parser.add_argument("--sleep", "-s", help="Sleep this long between lines (in seconds)", default=0.0, type=float)

args = parser.parse_args()

log_lines = args.num_lines
input_file = args.input_file

faker = Faker()

try:
    if input_file:
        f = open(input_file, 'a')  # Open the file in append mode
    else:
        print("Please provide an existing log file using the '--input' option.")
        sys.exit(1)

    response = ["200", "404", "500", "301"]
    verb = ["GET", "POST", "DELETE", "PUT"]
    resources = ["/list", "/wp-content", "/wp-admin", "/explore", "/search/tag/list", "/app/main/posts", "/posts/posts/explore", "/apps/cart.jsp?appID="]

    ualist = [faker.firefox, faker.chrome, faker.safari, faker.internet_explorer, faker.opera]
    log_entry_template = '%s - - [%s %s] "%s %s HTTP/1.0" %s %s "%s" "%s"\n'

    file_size_checkpoint = 50  # in MB
    total_file_size = os.path.getsize(input_file) / (1024.0 * 1024.0)  # Initial file size

    current_file_patch_size = 0

    flag = True
    while flag:
        if args.sleep:
            increment = datetime.timedelta(seconds=args.sleep)
        else:
            increment = datetime.timedelta(seconds=random.randint(30, 300))
        otime = datetime.datetime.now() + increment

        ip = faker.ipv4()
        dt = otime.strftime('%d/%b/%Y:%H:%M:%S')
        tz = datetime.datetime.now(local).strftime('%z')
        vrb = numpy.random.choice(verb, p=[0.6, 0.1, 0.1, 0.2])

        uri = random.choice(resources)
        if uri.find("apps") > 0:
            uri += str(random.randint(1000, 10000))

        resp = numpy.random.choice(response, p=[0.9, 0.04, 0.02, 0.04])
        byt = int(random.gauss(5000, 50))
        referer = faker.uri()
        useragent = numpy.random.choice(ualist, p=[0.5, 0.3, 0.1, 0.05, 0.05])()

        log_entry = log_entry_template % (ip, dt, tz, vrb, uri, resp, byt, referer,useragent)
        f.write(log_entry)
        f.flush()  # Flush the output to the file

        log_entry_size = len(log_entry.encode('utf-8'))

        # Checkpoint logic
        current_file_patch_size += log_entry_size / (1024.0 * 1024.0)  # Convert bytes to MB
        if current_file_patch_size >= file_size_checkpoint:
            total_file_size += current_file_patch_size
            print_checkpoint(total_file_size)
            current_file_patch_size = 0
            os.fsync(f.fileno())  # Ensure data is written to disk

    # Final checkpoint after generating all logs
    print_checkpoint(total_file_size)
    os.fsync(f.fileno())  # Ensure data is written to disk

finally:
    if input_file:
        f.close()
