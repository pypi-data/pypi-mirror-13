#!/usr/local/bin/python2.7

import sys
from numpy import array, loadtxt
import re
from matplotlib.pyplot import plot, show, legend, savefig, xlabel, ylabel, title
import argparse


datare = re.compile(r"[\w\.\+-]+")


def main():
    parser = argparse.ArgumentParser(description='Quick ploting from stdin')
    parser.add_argument('-save', type=str,
                        help='save figure')
    parser.add_argument('-style', help='figure style', type=str)
    parser.add_argument('-name', help='name the data line', type=str,
                        nargs="*")

    parser.add_argument('-xlabel', help='set x label', type=str)
    parser.add_argument('-ylabel', help='set y label', type=str)
    parser.add_argument('-title', help='set title', type=str)
    parser.add_argument('-f', help='load from file', type=str)

    args = parser.parse_args()

    if args.f:
        dataarr = loadtxt(args.f)
    else:
        totlist = []
        for i in sys.stdin:
            templist = []
            for j in datare.findall(i):
                templist.append(float(j))
            totlist.append(templist)
        dataarr = array(totlist)

    if args.xlabel:
        xlabel(args.xlabel)
    if args.ylabel:
        ylabel(args.ylabel)
    if args.title:
        title(args.title)

    if args.name and args.style:
        for i in range(1, len(dataarr[1, :])):
            plot(dataarr[:, 0], dataarr[:, i], args.style,
                 label=args.name[i-1])
        legend()
    elif args.name:
        for i in range(1, len(dataarr[1, :])):
            plot(dataarr[:, 0], dataarr[:, i], "--o", label=args.name[i-1])
        legend()
    elif args.style:
        for i in range(1, len(dataarr[1, :])):
            plot(dataarr[:, 0], dataarr[:, i], args.style)
    else:
        for i in range(1, len(dataarr[1, :])):
            plot(dataarr[:, 0], dataarr[:, i], "--o")

    if not args.save:
        show()
    else:
        savefig(args.save)

if __name__ == '__main__':
    main()
