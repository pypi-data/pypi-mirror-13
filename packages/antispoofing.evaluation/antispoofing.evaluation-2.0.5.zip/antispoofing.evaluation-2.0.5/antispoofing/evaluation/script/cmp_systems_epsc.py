#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Sep  8 18:24:05 CEST 2014

"""Plots different types of EPSC plots (WER_wb or SFAR) as demanded by the user, parameterized by one of the parameters, for one or more systems which are given as input. The other parameter is fixed to one or more values given as command line argument. The systems are given with the base directory of their scores 
"""

import os
import sys
from matplotlib import rc
rc('text',usetex=1)
import matplotlib.pyplot as mpl
import bob.measure
import bob.io.base
import numpy as np
import argparse

import matplotlib.font_manager as fm

from ..utils import error_utils

def define_infiles(indir):
  if os.path.isdir(os.path.join(indir, 'licit', 'nonorm')) and os.path.isdir(os.path.join(indir, 'spoof', 'nonorm')):
    baseline_dev = os.path.join(indir, 'licit', 'nonorm', 'scores-dev')
    baseline_test = os.path.join(indir, 'licit', 'nonorm', 'scores-test') #eval
    overlay_dev = os.path.join(indir, 'spoof', 'nonorm', 'scores-dev')
    overlay_test = os.path.join(indir, 'spoof', 'nonorm', 'scores-test') #eval
  elif os.path.isdir(os.path.join(indir, 'licit', 'scores')) and os.path.isdir(os.path.join(indir, 'spoof', 'scores')):
    baseline_dev = os.path.join(indir, 'licit', 'scores', 'scores-dev')
    baseline_test = os.path.join(indir, 'licit', 'scores', 'scores-eval') #eval
    overlay_dev = os.path.join(indir, 'spoof', 'scores', 'scores-dev')
    overlay_test = os.path.join(indir, 'spoof', 'scores', 'scores-eval') #eval
  else:
    baseline_dev = os.path.join(indir, 'licit', 'scores-dev')
    if os.path.exists(os.path.join(indir, 'licit', 'scores-eval')):
      baseline_test = os.path.join(indir, 'licit', 'scores-eval') #eval
    else:
      baseline_test = os.path.join(indir, 'licit', 'scores-test')
    overlay_dev = os.path.join(indir, 'spoof', 'scores-dev')
    if os.path.exists(os.path.join(indir, 'spoof', 'scores-eval')):
      overlay_test = os.path.join(indir, 'spoof', 'scores-eval') #eval
    else:
      overlay_test = os.path.join(indir, 'spoof', 'scores-test') #eval
  return baseline_dev, baseline_test, overlay_dev, overlay_test


def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  
  parser.add_argument('-d', '--indirs', metavar='DIR', type=str,
      default=('.',), dest='indirs', nargs='+',
      help='The names of the input score directories of the systems to be compared (defaults to "%(default)s")')

  parser.add_argument('-l', '--labels', metavar='DIR', type=str,
      default=('method label',), dest='labels', nargs='+',
      help='The labels of the methods to be compared (defaults to "%(default)s")')

  parser.add_argument('-c', '--criteria', metavar='STR', type=str,
      dest='criteria', default="eer", help='Criteria for threshold selection', choices=('eer', 'hter', 'wer'))  
   
  parser.add_argument('--vp', '--var_param', metavar='STR', type=str,
      dest='var_param', default='omega', help='Name of the varying parameter', choices=('omega','beta'))    
  parser.add_argument('--fp', '--fixed_param', metavar='STR', type=float,
      dest='fixed_param', default=0.5 , help='Value of the fixed parameter')    
      
  parser.add_argument('--nocolor', action='store_true',help='If True, will generate all the plots in grayscale.')
  parser.add_argument('--norealdata', action='store_true',help='If True, will annotate the plots hypothetically, instead of with real data values of the calculated error rates.')
  parser.add_argument('-t', '--title', metavar='STR', type=str,
      dest='title', default="", help='Plot title')
  parser.add_argument('-o', '--output', metavar='FILE', type=str,
      default='plots.pdf', dest='output',
      help='Set the name of the output file (defaults to "%(default)s")')
  
  parser.add_argument('--inoepsc', '--input_noepsc', metavar='FILE', type=str, default=None, dest='input_noepsc', help=argparse.SUPPRESS) #The name of an input hdf5file containing values that need to be plotted, but which are precomputed and can not be computed with EPSC (eg. AND decision level fusion) 

  parser.add_argument('-i', '--demandedplot', metavar='STR', type=int, dest='demandedplot', default=1, help='The numbers of plot that needs to be plotted. Select: 1 - WER_wb curves; 2 - SFAR curves', nargs='+')

  args = parser.parse_args()

  from matplotlib.backends.backend_pdf import PdfPages

  if len(args.indirs) != len(args.labels):
    labels = args.indirs
  else:
    labels = args.labels  

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  if args.nocolor: # plot in grey-scale
    color_mapping = {0:'black', 1:'black', 2:'black', 3:'black', 4:'black', 5:'black', 6:'black'}
    line_mapping = {0:'--', 1:'-', 2:':', 3:'-.', 4:' ', 5:'-.', 6:' '}
  else:  
    #color_mapping = {0:'green', 1:'blue', 2:'red', 3:'magenta', 4:'cyan', 5:'black', 6:'yellow'}
    #color_mapping = {0:'#7bd425', 1:'#257bd4', 2:'#7e25d4', 3:'#d47e25', 4:'#d4257b', 5:'#d2d425'} # green, blue, violet, orange, pink, yellow
    color_mapping = {0:'#7e25d4', 1:'#d47e25', 2:'#7e25d4', 3:'#d47e25', 4:'#d4257b', 5:'#d2d425'} # green, blue, violet, orange, pink, yellow
    line_mapping = {0:'-', 1:'-', 2:'-', 3:'-', 4:'--', 5:'--', 6:'--', 7:'--'}


  fig = mpl.figure()

  
  # First, plot the systems which have a single score
  for index, indir in enumerate(args.indirs):
   
    sys.stdout.write("Plotting scores for %s system...\n" % indir)
    baseline_dev, baseline_test, overlay_dev, overlay_test = define_infiles(indir)

    [base_neg, base_pos] = bob.measure.load.split_four_column(baseline_test)
    [over_neg, over_pos] = bob.measure.load.split_four_column(overlay_test)
    [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(baseline_dev)
    [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(overlay_dev)

    # Plot 1: EPSC - WER-w (in the past, this option was used to compute HTER_w)
    # -------------------------------------------------
    
    if 1 in args.demandedplot:
      points = 100
      criteria = args.criteria
    
      if args.var_param == 'omega':
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
      else:
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param)  
      
      errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list as 2D numpy.ndarrays in the following order: frr, far, sfar, far_w, wer_wb, hter_wb
    
      #import ipdb; ipdb.set_trace()
      if args.var_param == 'omega':
        mpl.plot(omega, 100. * errors[4].flatten(), color=color_mapping[index], linestyle=line_mapping[index], label = args.labels[index],linewidth=4)
      else:  
        mpl.plot(beta, 100. * errors[4].flatten(), color=color_mapping[index], linestyle=line_mapping[index], label = args.labels[index],linewidth=4)


   
    # Plot 2: EPSC - SFAR
    # -------------------------------------------------
    elif 2 in args.demandedplot:
      points = 100
      criteria = args.criteria
    
      if args.var_param == 'omega':
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
      else:
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
       
      errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list as 2D numpy.ndarrays in the following order: frr, far, sfar, far_w, wer_wb, hter_wb
    
      
      if args.var_param == 'omega':
        mpl.plot(omega, 100. * errors[2].flatten(), color=color_mapping[index], linestyle=line_mapping[index], label = args.labels[index], linewidth=4)
      else:  
        mpl.plot(beta, 100. * errors[2].flatten(), color=color_mapping[index], linestyle=line_mapping[index], label = args.labels[index], linewidth=4)
      

  # Now plot additional data if available (some which have been precomputed and do not depend on EPSC)
  if args.input_noepsc is not None:
    f = bob.io.base.HDF5File(args.input_noepsc)  
    if 1 in args.demandedplot:
      error_to_plot = f.read('hter_w')
    elif 2 in args.demandedplot:
      error_to_plot = f.read('sfar')
    mpl.plot(omega, 100. * error_to_plot, color=color_mapping[2], linestyle=line_mapping[2], linewidth=4, label = 'decision-level fusion (AND)')

  mpl.rcParams.update({'font.size': 18})
  if 1 in args.demandedplot:
    mpl.ylabel(r"HTER$_{\omega}$ (\%)")
    
  elif 2 in args.demandedplot:
    mpl.ylabel("SFAR (\%)")

  if args.var_param == 'omega':
    mpl.xlabel(r"Weight $\omega$")
  else:  
    mpl.xlabel(r"Weight $\beta$") 
  
  mpl.legend(prop=fm.FontProperties(size=22), loc = 2)
  #mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=12)) #ncol=4
  fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
  ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
  ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
  ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
  mpl.grid()  
  
  pp.savefig()
  
  pp.close() # close multi-page PDF writer
 

if __name__ == '__main__':
  main()
