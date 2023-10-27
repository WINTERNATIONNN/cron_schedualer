import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--visualize_type', type=str,default = None)
parser.add_argument('--filename', type=str,default = None)
parser.add_argument('--date', type=str,default = None)

args = parser.parse_args()