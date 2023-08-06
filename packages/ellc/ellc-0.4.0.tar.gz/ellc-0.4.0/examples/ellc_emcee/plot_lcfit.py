#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function,
                            unicode_literals)
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--eps", help="genereate .eps file", action="store_true")
args = parser.parse_args()

if args.eps:
  import matplotlib
  matplotlib.use('Agg')
import numpy as np
import corner
import matplotlib.pyplot as plt
from astropy.table import Table, Column

#------------------------------------------------------------------------------

# Handy class for printing floats...
class prettyfloat(float):
  def __repr__(self):
    return "%0.6f" % self

#------------------------------------------------------------------------------
# Generate plots

model = Table.read('model.csv')
model = Table(model, masked=True)

mask = model['flag'] < 0 

fig=plt.figure(1,figsize=(12,8))

t_obs = np.extract(mask == False,model['time']) - 2456770
m_obs = np.extract(mask == False,model['mag'])
m_fit = np.extract(mask == False,model['fit'])
t_plt = np.array(model['time']) - 2456770
f_plt = np.array(model['fit'])
m_res = m_obs - m_fit
fontsize=12
plt.subplot(312)
plt.scatter(t_obs,m_obs,color='darkgreen',marker='x',s=3)
plt.plot(t_plt,f_plt,color='darkblue')
plt.ylabel("Kp [mag]",fontsize=fontsize)
plt.xlim([np.min(t_obs),np.max(t_obs)])
plt.ylim([0.7,-0.1])

plt.subplot(313)
plt.scatter(t_obs,m_obs,color='darkgreen',marker='x',s=2)
plt.xlabel("Time [BJD - 2456700]",fontsize=fontsize)
plt.ylabel("O-C [mag]",fontsize=fontsize)
plt.xlim([np.min(t_obs),np.max(t_obs)])
plt.ylim([0.005,-0.005])

plt.subplot(331)
plt.scatter(t_obs,m_obs,color='darkgreen',marker='x',s=3)
plt.plot(t_plt,f_plt,color='darkblue')
plt.ylabel("Kp [mag]",fontsize=fontsize)
plt.xlim([8.64,9.22])
plt.ylim([0.7,-0.1])

plt.subplot(332)
plt.scatter(t_obs,m_obs,color='darkgreen',marker='x',s=3)
plt.plot(t_plt,f_plt,color='darkblue')
plt.ylabel("Kp [mag]",fontsize=fontsize)
plt.xlim([21.09,21.52])
plt.ylim([0.7,-0.1])

plt.subplot(333)
plt.scatter(t_obs,m_obs,color='darkgreen',marker='x',s=3)
plt.plot(t_plt,f_plt,color='darkblue')
plt.ylabel("Kp [mag]",fontsize=fontsize)
plt.xlim([34.29,34.88])
plt.ylim([0.7,-0.1])

plt.tick_params(axis='both', labelsize=fontsize)
plt.tight_layout()

if args.eps:
  fig.savefig("lcfit.eps")
else:
  plt.show()



