#!/usr/local/bin/python2.7

import sys
from numpy import array, loadtxt
import re
from matplotlib.pyplot import plot, show, legend, savefig, xlabel, ylabel,\
    title, errorbar
import argparse
import Interpolation.Interpolation as In

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
    parser.add_argument('-e', help='with error bar', action='store_true')
    parser.add_argument('-Inter', help='Interpolation', type=str,
                        nargs="*",
                        choices=['Neivlle', 'Lagrange', 'Newton', 'Linear'])

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

    if args.Inter:
        if args.e is not True:
            N = 2
        else:
            N = 3
        for Method in args.Inter:
            for i in range(len(dataarr[1, :])/N):
                data = dataarr[:, i*N:i*N+2]
                m = min(data[:, 0])
                M = max(data[:, 0])
                A = In.Interpolator(
                    data, getattr(In, Method), 100, [m, M]
                )
                plot(A.X, A.Y, "--", label=Method+"\'s Method "+args.name[i-1])

    if args.e is not True:
        if args.name and args.style:
            for i in range(len(dataarr[1, :])/2):
                plot(dataarr[:, i*2], dataarr[:, i*2+1], args.style,
                     label=args.name[i-1])
            legend()
        elif args.name:
            for i in range(len(dataarr[1, :])/2):
                plot(dataarr[:, i*2], dataarr[:, i*2+1],
                     "--o", label=args.name[i-1])
            legend()
        elif args.style:
            for i in range(len(dataarr[1, :])/2):
                plot(dataarr[:, i*2], dataarr[:, i*2+1], args.style)
        else:
            for i in range(len(dataarr[1, :])/2):
                plot(dataarr[:, i*2], dataarr[:, i*2+1], "--o")

        if not args.save:
            show()
        else:
            savefig(args.save)
    else:
        if args.name and args.style:
            for i in range(len(dataarr[1, :])/3):
                errorbar(dataarr[:, i*3], dataarr[:, i*3+1], fmt=args.style,
                         label=args.name[i-1], yerr=dataarr[:, i*3+2])
            legend()
        elif args.name:
            for i in range(len(dataarr[1, :])/3):
                errorbar(dataarr[:, i*3], dataarr[:, i*3+1],
                         "--o", label=args.name[i-1], yerr=dataarr[:, i*3+2])
            legend()
        elif args.style:
            for i in range(len(dataarr[1, :])/3):
                errorbar(dataarr[:, i*3], dataarr[:, i*3+1], fmt=args.style,
                         yerr=dataarr[:, i*3+2])
        else:
            for i in range(len(dataarr[1, :])/3):
                errorbar(dataarr[:, i*3], dataarr[:, i*3+1], "--o",
                         yerr=dataarr[:, i*3+2])

        if not args.save:
            show()
        else:
            savefig(args.save)

if __name__ == '__main__':
    main()
