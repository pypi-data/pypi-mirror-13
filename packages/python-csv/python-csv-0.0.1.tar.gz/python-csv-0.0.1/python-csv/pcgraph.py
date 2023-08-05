#!/usr/bin/env python
from matplotlib import pyplot as plt
import optparse
import sys
import utils
import csv

def readCL():
    parser = optparse.OptionParser()
    parser.add_option("-f","--infile",default="/dev/stdin")
    parser.add_option("-n","--no_header",action="store_true")
    parser.add_option("-b","--do_bin_plot",action="store_true")
    parser.add_option("-o","--outfile")
    options, args = parser.parse_args()
    return options.infile, options.no_header, options.do_bin_plot, options.outfile


#also can try context="fivethirtyeight"
def graph(pts, context="ggplot", title=None, line=False, outfile=None):
    with plt.style.context(context):
        x,y = zip(*pts)
        if line:
            plt.plot(x, y)
        else:
            plt.plot(x, y, '.')
        xmin = min([p[0] for p in pts])
        xmax = max([p[0] for p in pts])
        ymin = min([p[1] for p in pts])
        ymax = max([p[1] for p in pts])
        x_range = xmax - xmin; y_range = ymax - ymin
        eps = 0.05
        #don't reset if the ranges are empty, which happens
        #when plotting one point
        if x_range != 0 and y_range != 0:
            plt.xlim(xmin - eps * x_range, xmax + eps * x_range)
            plt.ylim(ymin - eps * y_range, ymax + eps * y_range)
    if title:
        plt.suptitle(title)
    if outfile:
        plt.savefig(filename)
    plt.show()


def bin_plot(pts, num_bins = 10, outfile=None):
    #sort pts by x value:
    pts.sort(key = lambda x: x[0])
    l = len(pts)
    outpts = []
    for i in range(int(num_bins)):
        break_pt1 = int(i*l/float(num_bins))
        break_pt2 = int((i+1)*l/float(num_bins))
        x_vals, y_vals = zip(*pts[break_pt1:break_pt2])
        x_val = sum(x_vals) / float(len(x_vals))
        y_val = sum(y_vals) / float(len(y_vals))
        outpts.append((x_val,y_val))
    # print outpts
    graph(outpts, title="Bin plot", outfile=outfile)

def curve_fit(xy_pts, fn, plot_points=True):
    #xy_pts = [(x,y)]
    #function of the form f(x, p_1, p_2,.. p_k)
    #for parameters p_i
    import scipy.optimize
    import matplotlib.pyplot as plt
    import numpy
    x, y = zip(*xy_pts)
    popt, pcov = scipy.optimize.curve_fit(fn, x, y, [1.0,1.0])
    
    # Plot data
    if plot_points:
        plt.plot(x, y, 'or')

    # Plot fit curve
    fit_x = numpy.linspace(min(x), max(x), 200)
    plt.plot(fit_x, fn(fit_x, *popt), "--r")
    plt.show()


def ls_dist_curve_fit(pts, fn, cnt=25):
    #least square curve fitting
    import matplotlib.pyplot as plt
    from utils import pairwise
    n, bins, patches = plt.hist(pts, cnt, normed=1, histtype='stepfilled', rwidth=0.8)
    bin_mids = [(b1 + b2) / 2.0 for b1,b2 in pairwise(bins) if b2]
    print len(bins)
    xy_pts = zip(bin_mids,n)
    curve_fit(xy_pts,fn,plot_points=False)
    

def mle_dist_curve_fit(pts, fn, cnt=25):
    #maximum likelihood curve fitting
    #http://glowingpython.blogspot.com/2012/07/distribution-fitting-with-scipy.html
    import scipy.stats
    import numpy
    import matplotlib.pyplot as plt

    #choices for fn:
    #scipy.stats.norm
    #scipy.stats.expon
    #scipy.stats.powerlaw

    fn_dict = {"normal":scipy.stats.norm,
               "exponential":scipy.stats.expon,
               "power":scipy.stats.pareto}
    if fn in fn_dict:
        fn = fn_dict[fn]

    param = fn.fit(pts) # distribution fitting
    print "Parameters: ",param
    xmin = min(pts)
    xmax = max(pts)
    x = numpy.linspace(xmin,xmax,100)
    # fitted distribution
    pdf_fitted = fn.pdf(x,*param)
    nll = fn.nnlf(param,x)
    print "Negative log likelihood: ", nll
    # original distribution
    # pdf = scipy.stats.norm.pdf(x)

    plt.title('Histogram + fit')
    plt.plot(x,pdf_fitted,'r-') #,x,pdf,'b-')
    plt.hist(pts,cnt,normed=1,alpha=.3)
    plt.show()


def mle_fit_normal_curve(pts):
    #maximum likelihood curve fitting for pts = [x]
    import scipy
    import scipy.optimize
    import scipy.stats
    def neg_llh(params, *args):
        pts = args
        loc, scale = params
        llh = sum([scipy.stats.norm.logpdf(x,loc,scale) for x in pts])
        return -1 * llh
    res = scipy.optimize.minimize(neg_llh, (0.0,1.0), args=tuple(pts), method='TNC', bounds=[(None,None),(1e-10,None)])
    return res


def mle_fit_pareto_curve(pts):
    #maximum likelihood curve fitting for pts = [x]
    #pareto.pdf(x, b, loc, scale) = (b/scale) / ((x-loc)/scale)**(b+1)
    #for (x-loc)/scale >= 1, b > 0
    import scipy
    import scipy.optimize
    import scipy.stats
    import math
    import numpy
    def neg_llh(params, *args):
        min_x, pts = args
        b, scale = params
        # scale + loc <= min(x)
        # loc = min_x - scale
        loc = min_x - scale
        # print b,loc,scale
        # print [scipy.stats.pareto.logpdf(x,b,loc,scale) for x in pts]
        llh = sum([scipy.stats.pareto.logpdf(x,b,loc,scale) for x in pts])
        return -1 * llh
    def grad(params, *args):
        min_x, pts = args
        b, scale = params
        grad_b = -1 * sum([1/float(b) - math.log((x-min_x)/float(scale) + 1) for x in pts])
        grad_scale = -1 * sum([-1/float(scale) + (b+1)* ((x-min_x)/float(scale)**2) / ((x-min_x)/float(scale) + 1) for x in pts])
        return numpy.array([grad_b, grad_scale])

    min_x = min(pts)
    print "Fitting pareto..."
    res = scipy.optimize.minimize(neg_llh, [1.0,1.0], jac=grad, args=(min_x,pts), method='L-BFGS-B', bounds=[(0.01,None),(0.01,None)], options={"disp":True})
    # res = scipy.optimize.minimize(neg_llh, [1.0,1.0], jac=grad, args=(min_x,pts), method='nelder-mead', bounds=[(0.01,None),(0.01,None)], options={"disp":True})
    print res
    return res
    



def plot_hist(pts,cnt=25,context="ggplot",outfile=None):
    pts = [x[0] for x in pts]
    x_cnt = len(set(pts))
    x_min = min(pts)
    x_max = max(pts)
    cnt = min(x_cnt,cnt) #don't have more buckets than x values

    #default x_range of the hist is [x_min, x_max]
    #increase this size a bit to make space in case some
    #bins are *centered* at x_min or x_max 
    #(this happens in dice roll histogram with 6 bins)
    bin_width = (x_max - x_min) / (cnt - 1)
    x_range = [x_min - 0.5 * bin_width, x_max + 0.5 * bin_width]

    with plt.style.context(context):
        n, bins, patches = plt.hist(pts, cnt, range=x_range, normed=1) #, histtype='stepfilled', rwidth=0.8)
        plt.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
    if outfile:
        plt.savefig(outfile)
    plt.show()


def plot_images(*image_list):
    import math
    n = len(image_list)
    d = math.ceil(n**0.5)
    for i,ix in enumerate(image_list):
        plt.subplot(d,d,1 + i)
        plt.imshow(ix, cmap=plt.cm.gray)
        plt.axis("off")
    plt.show()


def readcsv(f):
    if isinstance(f, file):
        f_in = f
        for r in _readcsv(f_in):
            yield r
    elif isinstance(f, str):
        with open(f) as f_in:
            for r in _readcsv(f_in):
                yield r
    else:
        raise

def _readcsv(f_in):
    header = None
    for line in csv.reader(f_in):
        if not header:
            header = line
        else:
            yield OrderedDict(zip(header,line))
        
if __name__ == "__main__":
    infile, no_header, do_bin_plot, outfile = readCL()

    #jtrigg avoid pandas for quicker loadtimes
    # import pandas as pd
    # import numpy

    # if no_header:
    #     dat = pd.read_csv(infile, dtype=str, header = None)
    # else:
    #     dat = pd.read_csv(infile, dtype=str)

    # print "imported"

    with open(infile) as f_in:
        if not no_header:
            hdr = f_in.next().strip()
            sys.stdout.write("WARNING: using first line of input, \"{hdr}\", as header. If file doesn't have a header use -n option.".format(**vars()) + '\n')
        df = [l.split(',') for l in f_in]
        l1 = len(df)
        #drop rows with non-floats
        df = [r for r in df if all(utils.str_is_float(x) for x in r)]
        l2 = len(df)
        dropped = l1 - l2
        #convert fields to float
        df = [[float(x) for x in r] for r in df]

    # print "loaded"

    if dropped != 0:
        sys.stderr.write("WARNING: dropped {} non float values".format(l1-l2) + '\n')

    if len(df[0]) == 1:
        plot_hist(df, outfile=outfile)
    elif len(df[0]) == 2:
        if len(df) > 1000 or do_bin_plot:
            bin_plot(df, outfile=outfile)
        else:
            graph(df, outfile=outfile)
    else:
        raise Exception("ERROR: >2 columns")
