__author__ = 'tflourenco'
#!/usr/bin/python
import re
from numpy import *
from pylab import *
from matplotlib import pyplot as plt
import scipy.interpolate as inter
from scipy.interpolate import interp1d
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import DateFormatter
import csv
import sys
import datetime
import numpy as np
import glob
import os.path
import os
import math
from scipy.signal import wiener, filtfilt, butter, gaussian, freqz
from scipy.ndimage import filters
import scipy.optimize as op
import scipy.ndimage as ndi
import itertools

#constantes
NUMBERS = re.compile(r'(\d+)')
TSL2591_LUX_DF		= 408
TSL2591_LUX_COEFB	= 1.64
TSL2591_LUX_COEFC	= 0.59
TSL2591_LUX_COEFD	= 0.86



#ORDER
def numericalSort(value):
    parts = NUMBERS.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

#GET IMPUT
def getInput(prompt, default=None):
    if default:
        prompt_line = "{:s} [{:s}]: ".format(prompt, default)
    else:
        prompt_line = "{:s}: ".format(prompt)
    ret = raw_input(prompt_line)
    if ret == '' and default:
        ret = default
    return ret

#IS FLOAT
def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

#OPEN CSV
def openfile(output_csv):
  bb = open(output_csv, "rb")
  book = csv.reader(bb, delimiter=',')
  print 'OPEN csv name ['+ output_csv+']'
  return book ,bb

#CLOSE CSV
def closefile(bb):
  bb.close()
  print "CLOSE CSV"

#FIND FIELD
def findfield(book, setname, bb, opt):
  num = 0
  coll = 0

  for row in book:
    for collunm in row:
      num = num + 1
      if setname in collunm:
	  coll = num -1
	  if opt == None:
	    closefile(bb)
	  print "Field "+setname+" is ["+str(coll)+"]"
	  return coll

#UNIQUE FILE
#NOTE abreviar o abrir documento
def creacte_unique_file(input_csv, matrix):
  file_counter = 0
  datafinal = []
  data = []
  x = 1

  for filename in sorted(glob.glob(input_csv + '*.csv'), key=numericalSort):
    with open(filename, "rb") as b:
      print filename
      book = csv.reader(b,delimiter=',')
      if file_counter < 1:
	for row in book:
	  data.append(row)
      else:
	header = next(book)
	for row in book:
	  data.append(row)


    file_counter += 1

  x = file_counter
  closefile(b)
  tittle = input_csv + "[all].csv"
  filewriter = (open(tittle,'wb'))
  writer = csv.writer(filewriter)
  for dat in data:
     writer.writerow(dat)
  print ('\nCREACTE UNIQUE FILE\nNumber of files ' + str(input_csv) + '(x).csv exist x:= ' + str(x) + "\n")

#DATA SEQUENCE IS TRUE OR NOT
def date_seq(book,typ):
  index = 0
  pos = []
  time = []
  erro = False

  for row in book:
    if typ == None:
      temp_time = datetime.datetime.strptime(" ".join((row[0], row[1])), "%m-%d-%Y %H:%M:%S")
      time.append(int(temp_time.strftime('%s') )) #function main
    else:
      time.append((row[0]))

  y1=0
  tim_p = 0
  for y,tim in enumerate(time):
    if y > 1 and y < (len(time)):
      if tim < tim_p:
	erro = True
	pos.append(y)
      elif erro != True:
	erro = False
    if y1 <= y:
      y1 = y
      tim_p = tim
  return erro, pos

#LUMINOSITY TSL2591
def luminosity_calib(ch0, ch1, again, atime):
  cpl = (atime*again)/ TSL2591_LUX_DF
  lux1 = (ch0 - (TSL2591_LUX_COEFB * ch1))/ float(cpl)
  lux2 = ( ( TSL2591_LUX_COEFC * float(ch0) ) - ( TSL2591_LUX_COEFD * float(ch1) ) ) / cpl
  lux = max(lux1,lux2)

  return lux, lux1, lux2

#SMOOTH
def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y

#SMOOTH DEMO
def smooth_demo(y_arr, x_arr, field,WOORKBOOKNAME):
    print(len(y_arr), len(x_arr))
    xn=asarray(y_arr)
    #yy=smooth(y_arr)

    #ws=31

    #subplot(211)
    #plot(ones(ws))

    #windows=['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    windows=[ 'blackman']


    hold(True)
    #for w in windows[1:]:
        #eval('plot('+w+'(ws) )')

    #axis([0,30,0,1.1])
    window_len=60
    legend(windows)
    title("The smoothing windows")
    #subplot(212)
    plot(x_arr,y_arr,'o-')
    #plot(xn)#, 'signal with noise'
    for w in windows:
        y_smooth = smooth(xn,window_len,w)[window_len/2-1: -window_len/2]
        print(len(x_arr), len(y_smooth),window_len )
        plot(x_arr,y_smooth,'o-')
    l=['original signal']#, 'signal with noise'
    l.extend(windows)

    legend(l)
    title("Smoothing a noisy signal = " + field)
    savefig(WOORKBOOKNAME+"_"+field + '_smooth_vs_original.png')
    show()
    return y_smooth

#CUT LIMITS
def cut_point_limit(num, book):
  data = []
  header = []
  row = []
  data = upload_csv(book)
  for n, dat in enumerate(data):
    if n < 1:
      header.append(dat)
    if (n > num) and (n < (len(data)-num)):
      row.append(dat)
  return header, row

#DATA CONVERT TO SECONDS
def date_convert(book, name,sense):
  time = []
  d2 = []
  d1 = []
  data = []
  line = 0
  col = findfield(book, sense, None, 1)

  for row in book:
    temp_time = datetime.datetime.strptime(" ".join((row[0], row[1])), "%H:%M:%S %m-%d-%y")
    time.append(int(temp_time.strftime('%s') ))
    #print str(datetime.datetime.strptime(" ".join((row[0], row[1])), "%H:%M:%S %m-%d-%y"))
    data.append(row)

  filewriter = (open(name,'wb'))
  writer = csv.writer(filewriter)

  for tt,dat in zip(time,data):
    if line < 1:
      writer.writerow(["seconds", "sense"])
    else:
      writer.writerow([tt, dat[col]])
    line = line + 1

#UPLOAD CSV
def upload_csv(book):
  data = []
  for b in book:
    data.append(b)
  print "UPLOAD CSV"
  return data

#synchronize
def synchronize(book1, book2, col1, col2, sense):
  print "synchronize"
  data1 = []
  data2 = []
  x_arr=[]
  y_arr=[]
  x1_arr=[]
  y1_arr=[]
  data1.sort()
  data2.sort()

  b1 = []
  b2 = []
  x = 0
  y = 0
  z = 0
  j = 0

  data1 = upload_csv(book1)

  data2 = upload_csv(book2)

  for d1 in data1:
    for y, d2 in enumerate(data2):
      if y>=x:
	z+=1
	if int(float(d2[col2])/60)  ==  int(float(d1[col1])/60):
	  b1.append(d1)
	  b2.append(d2)
	  j+=1
	  x = y
	  break
  print "synchronize " + str(j) + " Lines of "+ str(len(data2))

  return b1, b2

#DELETE EMPTY
def delete_empty(book):
  row = []
  x = 0
  data = upload_csv(book)

  for y, dat in enumerate(data):
    if dat[1] != "" and dat[2] != "" and dat[3] != "" and dat[4] != "":
      x += 1
      row.append(dat)

  print "DELETE " + str((x-1) - y) +" row"
  return row

#FIND FAILURES POINT IN TIME
def find_point_failures(book, time):
  data = []
  data = upload_csv(book)
  fail = []
  dele = []
  time_p = 0
  y = 0
  count = 0

  for x,dat in enumerate(data):
    if x > 1 and x < len(data):
      if ((float(dat[0]) - float(time_p)) >= float(time)):
	fail.append(x)
	#print str((int(dat[0]) - int(time_p))/60) +" minut"
	count += 1
    if y <= x:
      y = x
      time_p = dat[0]

  print str(count) + " failures"
  return fail

#SAVING MARGES FAILURE
def save_margim_failures(book, fail, marge):
  data = []
  del_data = []
  data = upload_csv(book)
  count = 0

  for f in fail:
    for x, datx in enumerate(data):
      if int(x) >= int(f-int(marge)) and int(x) <= int(f+(int(marge)-1)):
	del_data.append(datx)
	count += 1

  print str(count) + " row to delete"
  return del_data

#DELETE FAILURES
def delete_failures(book, data_delet):
  data = upload_csv(book)
  count = 0
  end_data = []

  for dat in data:
    x = 0
    for y, dl in enumerate(data_delet):
      if dat == dl:
	count += 1
	x = 1
    #print str(y) +" and len"+str(len(data_delet))
    if y == len(data_delet)-1 and x == 0:
      end_data.append(dat)

  print str(count) + " delete"
  return end_data

#SMOOTH CSV
def make_smooth(book, typ, WOORKBOOKNAME):
    y_arr = []
    j_arr = []
    z_arr = []
    k_arr = []
    y_smooth = []
    j_smooth = []
    z_smooth = []
    k_smooth = []
    x_arr = []
    data = []
    time = []
    line = 0
    count = 0
    if typ == None:
      i = 1
    else:
      i = 0

    for row in book:
      if (len(row[1]) == 0):
	continue
      data.append(row)

    for x,dat in enumerate(data):
      if x < 1:
	y = dat[1+i]
	j = dat[2+i]
	z = dat[3+i]
	k = dat[4+i]
      else:
	if float(dat[1]) >  0:
	  if typ == None:
	    temp_time = datetime.datetime.strptime(" ".join((dat[1], dat[0])), "%m-%d-%y %H:%M:%S")
	    time.append(int(temp_time.strftime('%s') )) #function main7
	    y_arr.append(float(dat[1+i]))
	    j_arr.append(float(dat[2+i]))
	    z_arr.append(float(dat[3+i]))
	    k_arr.append(float(dat[4+i]))
	  else:
	    if dat[3] != "":
	      x_arr.append((float(dat[0])))
	      y_arr.append(float(dat[1]))
	      j_arr.append(float(dat[2]))
	      z_arr.append(float(dat[3]))
	      k_arr.append(float(dat[4]))
	    #k_arr.append(float(dat[4]))
	else:
	  print "Oops Have a negative value in position " + dat[0] + " value " +dat[1]
	  count +=1

    if typ == None:
      for tim in time:
	x_arr.append(float(tim))

    y_smooth = smooth_demo(y_arr,x_arr,y,WOORKBOOKNAME)
    j_smooth = smooth_demo(j_arr,x_arr,j,WOORKBOOKNAME)
    z_smooth = smooth_demo(z_arr,x_arr,z,WOORKBOOKNAME)
    k_smooth = smooth_demo(k_arr,x_arr,k,WOORKBOOKNAME)


    tittle = WOORKBOOKNAME + "_smooth_negative["+str(count)+"]"
    filewriter = (open(tittle,'wb'))
    writer = csv.writer(filewriter)

    for time, yy, jj, zz, kk in zip(x_arr,  y_smooth, j_smooth, z_smooth,k_smooth):
      if line < 1 :
	writer.writerow(['time', y, j, z, k])
      else:
	writer.writerow([time, yy, jj, zz, kk])
      line += 1

#PLOT
def make_plot(x,y, ax1, rowname):
  if ax1 == None:
    print"NONE"
    fig,ax =plt.subplots()
    ax.set_xlabel('Time')
    ax.plot(x,y,"r-",label = " ".join((rowname)))
    ax.legend(loc='upper left')
    for tl in ax.get_yticklabels():
       tl.set_color('r')
  else:
    print "NOT NONE"
    ax = ax1.twinx()
    ax.set_xlabel('Time')
    ax.plot(x,y,"g-", label = " ".join((rowname)))
    ax.legend(loc='upper right')
    for tl in ax.get_yticklabels():
      tl.set_color('g')
  #plt.show()
  return ax

#Header
def header(book):
  header = []
  data = upload_csv(book)
  for n, dat in enumerate(data):
    if n < 1:
      header.append(dat)

  return header

#ADD BOOK PARALEL
def book_add(one,tow):
  for o in one:
    for t in tow:
      o += t

  return o

def plot_per(x1,x2,x3,x4,y1,y2,y3,y4):
  f, axarr = plt.subplots(2, sharex=True)
  axarr[0].plot(x1, y1)
  #axarr[0].plot(x2, y2)
  axarr[0].set_xlabel('Time')
  axarr[0].set_ylabel('lux')
  axarr[0].set_title('luminosity')
  axarr[1].scatter(x3, y3)
  #axarr[1].scatter(x4, y4)

  axarr[1].set_xlabel('Time')
  axarr[1].set_ylabel('AGAIN')