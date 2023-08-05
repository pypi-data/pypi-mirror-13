#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Wed 11 Nov 18:07:58 CET 2015

"""Plot EPSC animation
"""

import os
import sys
from matplotlib import rc
rc('text',usetex=1)
import matplotlib.pyplot as mpl
from matplotlib import animation
import bob.measure
import numpy as np
import argparse

import matplotlib.font_manager as fm

from matplotlib import gridspec

from ..utils import error_utils


def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('baseline_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, LICIT scenario (development set)')
  parser.add_argument('baseline_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, LICIT scenario (test set)')
  parser.add_argument('overlay_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, SPOOF scenario (spoofing attacks; development set)')
  parser.add_argument('overlay_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, SPOOF scenario (spoofing attacks; test set)')
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

  args = parser.parse_args()

  if args.criteria == 'eer':
    report_text = "EER"
  else:
    report_text = "Min.HTER"

  [base_neg, base_pos] = bob.measure.load.split_four_column(args.baseline_test)
  [over_neg, over_pos] = bob.measure.load.split_four_column(args.overlay_test)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(args.baseline_dev)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(args.overlay_dev)

  color_scheme = {'genuine':'#7bd425', 'impostors':'#257bd4', 'spoofs':'black', 'line':'#d4257b'} #7e25d4 #color_scheme = {'genuine':'blue', 'impostors':'red', 'spoofs':'black', 'line':'green'}
  linestyle_scheme = {'line1':'-', 'line2':'-'}
  linecolor_scheme = {'line1':'#257bd4', 'line2':'#7bd425'} #linecolor_scheme = {'line1':'blue', 'line2':'red'}
  alpha_scheme = {'genuine':0.9, 'impostors':0.8, 'spoofs':0.3} #alpha_scheme = {'genuine':0.6, 'impostors':0.8, 'spoofs':0.4}
  hatch_scheme = {'genuine':None, 'impostors':None, 'spoofs':None}  

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  mpl.rcParams.update({'font.size': 14})

  #fig = mpl.figure(figsize=(12, 6))
  fig = mpl.figure(figsize=(10, 6))
  gs = gridspec.GridSpec(2, 2, width_ratios=[3, 2]) 

  ax1 = fig.add_subplot(gs[:,0])
  ax2 = fig.add_subplot(gs[0,1])
  ax3 = fig.add_subplot(gs[1,1])
  '''
  ax1 = fig.add_subplot(1, 2, 1)
  ax2 = fig.add_subplot(2, 2, 2)
  ax3 = fig.add_subplot(2, 2, 4)
  '''
  points=100
  criteria=args.criteria
  omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
  errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list in the following order: frr, far, sfar, far_w, 

  thrs = thrs[0]
  err_wer = 100. * errors[4].flatten()
  err_sfar = 100. * errors[2].flatten()

  #import ipdb; ipdb.set_trace()
  #line, = ax1.axvline(x=[], ymin=0, ymax=1, linewidth=4, color=color_scheme['line'], linestyle='--', label="threshold")
  line1 = ax1.axvline(x=None, ymin=None, ymax=None, linewidth=4, color=color_scheme['line'], linestyle='--', label="threshold")
  line2, = ax2.plot([], [], color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label = r"WER$_{\omega,\beta}$",linewidth=4)
  line3, = ax3.plot([], [], color=linecolor_scheme['line2'], linestyle=linestyle_scheme['line2'], label = r"SFAR$",linewidth=4)


  def init():
    
    ax1.hist(base_pos, bins=10, color=color_scheme['genuine'], alpha=alpha_scheme['genuine'], hatch=hatch_scheme['genuine'],
      label="Genuine Users", normed=True)
    ax1.hist(base_neg, bins=10, color=color_scheme['impostors'], alpha=alpha_scheme['impostors'], hatch=hatch_scheme['impostors'],
      label="Impostors", normed=True)
    ax1.hist(over_neg, bins=10, color=color_scheme['spoofs'], alpha=alpha_scheme['spoofs'], hatch=hatch_scheme['spoofs'],
      label="Spoofing Attacks", normed=True)

    ax2.set_ylim([0, 35])
    ax2.set_xlim([0, 1])

    ax3.set_ylim([0, 80])
    ax3.set_xlim([0, 1])
    
    return line1,line2,line3

  #import ipdb; ipdb.set_trace()
  def animate(i):
    #import ipdb; ipdb.set_trace()
    line1.set_data([thrs[i], thrs[i]], [0, 1])
    line2.set_data(omega[:i], err_wer[:i])
    line3.set_data(omega[:i], err_sfar[:i])
    #ax2.plot(omega, 100. * errors[4].flatten(), color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label = r"WER$_{\omega,\beta}$",linewidth=4)
    return line1,line2, line3


  anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=points, interval=80, blit=True)
  

  fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
  #ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
  ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
  ax1.set_yticklabels(ax1.get_yticks(), fontProperties)

  ax2.set_xticklabels(ax2.get_xticks(), fontProperties)
  ax2.set_yticklabels(ax2.get_yticks(), fontProperties)

  ax3.set_xticklabels(ax3.get_xticks(), fontProperties)
  ax3.set_yticklabels(ax3.get_yticks(), fontProperties)

  ax1.set_xlabel('Scores')
  ax1.set_ylabel('Normalized count')

  #ax2.set_xlabel('Scores')
  ax2.set_ylabel(r"WER$_{\omega,\beta}$ (\%)")  
  ax3.set_xlabel(r"Weight $\omega$")  
  ax3.set_ylabel("SFAR (\%)")  


  
  newlabels_2 = [float(i.get_text()) for i in ax2.get_yticklabels()]
  newlabels_3 = [float(i.get_text()) for i in ax3.get_yticklabels()]

  ax2.set_yticklabels(["%.f" % i for i in newlabels_2])
  ax3.set_yticklabels(["%.f" % i for i in newlabels_3])

  anim.save('epsc_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

  mpl.show()
  """
  # Plot 10: EPSC - WER-w (in the past, this option was used to compute HTER_w)
  # -------------------------------------------------
  
  if 10 in args.demandedplot:
    points = 10
    criteria = args.criteria
    fig = mpl.figure()
   
    if args.var_param == 'omega':
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
    else:
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 

    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list in the following order: frr, far, sfar, far_w, wer_w
    
    mpl.rcParams.update({'font.size': 18})
     
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    
    if args.var_param == 'omega':
      mpl.plot(omega, 100. * errors[4].flatten(), color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label = r"WER$_{\omega,\beta}$",linewidth=4)
      mpl.xlabel(r"Weight $\omega$")
    else:  
      mpl.plot(beta, 100. * errors[4].flatten(), color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label = r"WER$_{\omega,\beta}$",linewidth=4)
      mpl.xlabel(r"Weight $\beta$")  
    
    mpl.ylabel(r"WER$_{\omega,\beta}$ (\%)")

    if args.var_param == 'omega':
      mpl.title(r"EPSC with %s, $\beta$ = %.2f" % (criteria, args.fixed_param) if args.title == "" else args.title)
    else:  
      mpl.title(r"EPSC with %s, $\omega$ = %.2f" % (criteria, args.fixed_param) if args.title == "" else args.title)

    mpl.legend(prop=fm.FontProperties(size=16))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()  
   
  # Plot 11: EPSC - SFAR
  # -------------------------------------------------
  
  if 11 in args.demandedplot:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    if args.var_param == 'omega':
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
    else:
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
      
    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list in the following order: frr, far, sfar, far_w, wer_w
    mpl.rcParams.update({'font.size': 18})
     
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    
    if args.var_param == 'omega':
      mpl.plot(omega, 100. * errors[2].flatten(), color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label = "SFAR",linewidth=4)
      mpl.xlabel(r"Weight $\omega$")
    else:  
      mpl.plot(beta, 100. * errors[2].flatten(), color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label = "SFAR",linewidth=4)
      mpl.xlabel(r"Weight $\beta$")  
         
    mpl.ylabel("SFAR (\%)")

    if args.var_param == 'omega':
      mpl.title(r"EPSC with %s, $\beta$ = %.2f" % (criteria, args.fixed_param) if args.title == "" else args.title)
    else:  
      mpl.title(r"EPSC with %s, $\omega$ = %.2f" % (criteria, args.fixed_param) if args.title == "" else args.title)

    mpl.legend(prop=fm.FontProperties(size=16))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()    
  
  
 
  pp.close() # close multi-page PDF writer
  """

if __name__ == '__main__':
  main()
