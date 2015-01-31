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

import sis

def main():
  print
  print "synchronize join unique csv------[1]:"
  print "Join CSV ------------------------[2]:"
  print "Converte Date/time to senconds --[3]:"
  print "Delete row that has null values--[4]:"
  print "Sequence temporal----------------[5]:"
  print "Delete [n] extreme points--------[6]:"
  print "Find failures/size in time-------[7]:"
  print "synchronize final to after smooth[8]:"
  print "PLOT csv-------------------------[9]:"
  print "CSV smooth-----------------------[10]:"
  print "PLOT PERSONALIZADO---------------[11]:"

  print "EXIT-----------------------------[0]:\n"

  action = input()
  ax = None

  if action == 1:
    line = 0

    ID = sis.getInput("ID Raspberry")
    SENSE = sis.getInput("Sensor?")

    sense = ID + "/Deployment_"+ID+"_"+SENSE+"_week_[all].csv"
    humid = ID + "/Deployment_"+ID+"_humidity_week_[all].csv"
    temp  = ID + "/Deployment_"+ID+"_temperature_week_[all].csv"
    ref   = ID + "/42I-"+SENSE+"_week_[all].csv"


    booksense, b1 = sis.openfile(sense)
    bookhumid, b2 = sis.openfile(humid)
    booktemp, b3 = sis.openfile(temp)
    bookref, b4 = sis.openfile(ref)

    #sis.date_convert(bookref,ref, SENSE)

    colsense = sis.findfield(booksense, "seconds", b1, 1)
    colhumid = sis.findfield(bookhumid, "seconds", b2, 1)
    coltemp = sis.findfield(booktemp, "seconds", b3, 1)
    colref = sis.findfield(bookref, "seconds", b4, 1)

    d1,d4 = sis.synchronize(booksense, bookref, colsense, colref, 2)

    sis.closefile(b1)
    #booksense, b1 = sis.openfile(sense)
    #colsense = sis.findfield(booksense, "seconds", b1, 1)

    d1,d3 = sis.synchronize(d1,booktemp, colsense, coltemp, 2)

    sis.closefile(b1)
    #booksense, b1 = sis.openfile(sense)
    #colsense = sis.findfield(booksense, "seconds", b1, 1)

    d1,d2 = sis.synchronize(d1,bookhumid, colsense, colhumid, 2)

    name = ID + "/end_file/"+ SENSE + "_" + ID + "_all.csv"
    filewriter = (open(name,'wb'))
    writer = csv.writer(filewriter)
    print "PRINT"

    for bb1, bb2, bb3, bb4 in zip(d1, d2, d3, d4):
      if line < 1:
	writer.writerow(["seconds", "ref","Vs","temperature","humidity"])
      else:
	#print bb1[1] + "," + bb2 + "," + bb1[2] + "," + bb3[2] + "," + bb4[2]
	writer.writerow([bb1[0], bb4[1], bb1[1], bb3[1], bb2[1]])
      line += 1
    sis.closefile(b1)
    sis.closefile(b2)
    sis.closefile(b3)
    sis.closefile(b4)
    main()
  elif action == 2:
    ID = sis.getInput("ID Raspberry")
    WOORKBOOKNAME = sis.getInput("Book Location sense")
    sis.creacte_unique_file(WOORKBOOKNAME,None)
    #copiar para a pasta do respctivo ID
    os.system("mv " + WOORKBOOKNAME + "[all].csv "+ ID +"/" )

    WOORKBOOKNAME = sis.getInput("Book Location humidity")
    sis.creacte_unique_file(WOORKBOOKNAME,None)
    #copiar para a pasta do respctivo ID
    os.system("mv " + WOORKBOOKNAME + "[all].csv "+ ID +"/" )

    WOORKBOOKNAME = sis.getInput("Book Location temperature")
    sis.creacte_unique_file(WOORKBOOKNAME,None)
    #copiar para a pasta do respctivo ID
    os.system("mv " + WOORKBOOKNAME + "[all].csv "+ ID +"/" )

    WOORKBOOKNAME = sis.getInput("Book Location reference")
    sis.creacte_unique_file(WOORKBOOKNAME,None)
     #copiar para a pasta do respctivo ID
    os.system("mv " + WOORKBOOKNAME + "[all].csv "+ ID +"/" )
    main()
  elif action == 3:
    WOORKBOOKNAME = sis.getInput("Book Location")
    urbanbook, bb = sis.openfile(WOORKBOOKNAME)
    SENSE = sis.getInput("Field sense to save")
    sis.date_convert(urbanbook,WOORKBOOKNAME, SENSE)
    sis.closefile(bb)
    main()
  elif action == 4:
    WOORKBOOKNAME = sis.getInput("Book Location")
    urbanbook, bb = sis.openfile(WOORKBOOKNAME)
    row = sis.delete_empty(urbanbook)

    filewriter = (open(WOORKBOOKNAME+"_empty",'wb'))
    writer = csv.writer(filewriter)

    for r in row:
      writer.writerow(r)
    sis.closefile(bb)
    main()
  elif action == 5:
    WOORKBOOKNAME = sis.getInput("Book Location:")
    book, bb = sis.openfile(WOORKBOOKNAME)
    date = sis.getInput("Date\Time time is seconds[y/n]")
    if date == 'n':
      date = None
    erro, pos = sis.date_seq(book,date)
    if erro == True:
      print 'ERROR! File' + WOORKBOOKNAME + ' time is not continuous, vereficar time.'
    else:
      print 'Has no errors in the file '+ WOORKBOOKNAME +', the time is still'
    sis.closefile(bb)
    main()
  elif action == 6:
    WOORKBOOKNAME = sis.getInput("Book Location:")
    book, bb = sis.openfile(WOORKBOOKNAME)
    x = sis.getInput("Number points to cur:")

    header, row = sis.cut_point_limit(int(x)-2, book)

    filewriter = (open(WOORKBOOKNAME+"_extreme("+x+")",'wb'))
    writer = csv.writer(filewriter)
    for h in header:
      writer.writerow(h)
    for r in row:
      writer.writerow(r)
    sis.closefile(bb)
    main()
  elif action == 7:
    WOORKBOOKNAME = sis.getInput("Book Location:")
    book, bb = sis.openfile(WOORKBOOKNAME)
    TIME = sis.getInput("Fail bigger to time (seconds):")

    fail = sis.find_point_failures(book, TIME)

    sis.closefile(bb)
    book, bb = sis.openfile(WOORKBOOKNAME)

    MARGE = sis.getInput("Marge to delete (points):")
    data = sis.save_margim_failures(book,fail, MARGE)

    sis.closefile(bb)
    book, bb = sis.openfile(WOORKBOOKNAME)
    end_data = sis.delete_failures(book, data)

    filewriter = (open(WOORKBOOKNAME+"_fail_time|marge(" + TIME + "s|" + MARGE +"p)",'wb'))
    writer = csv.writer(filewriter)
    sis.closefile(bb)
    for r in end_data:
      writer.writerow(r)
    #save end_data in new file
    main()
  elif action == 8:
    line = 0

    orin = "ref/lux_ref.csv"#    SENSE = sis.getInput("Original File without error")
    end = "urban/basic_environment.csv"#    SENSE = sis.getInput("Final file with filtre")


    bookorig, b1 = sis.openfile(orin)
    bookend, b2 = sis.openfile(end)

    horig = sis.header(bookorig)
    hend = sis.header(bookend)

    h_book = sis.book_add(hend, horig)

    sis.closefile(b1)
    sis.closefile(b2)
    bookorig, b1 = sis.openfile(orin)
    bookend, b2 = sis.openfile(end)

    colorig = sis.findfield(bookorig, "seconds", b1, 1)
    colend = sis.findfield(bookend, "seconds", b2, 1)

    d1,d2 = sis.synchronize(bookend,bookorig, colend, colorig, 2)
    booka = sis.book_add(d1,d2)

    filewriter = (open(	"data_synchronize.csv",'wb'))
    writer = csv.writer(filewriter)
    print "PRINT"
    for a in booka:
      if line < 1:
	writer.writerow(list(h_book))
      else:
	writer.writerows(a)
      line += 1
    sis.closefile(b1)
    sis.closefile(b2)
  elif action == 0:
    print "Fechar Programa"
    sys.exit(0)
  elif action == 10:
    WOORKBOOKNAME = sis.getInput("Book Location")
    urbanbook, bb = sis.openfile(WOORKBOOKNAME)
    date = sis.getInput("Date\Time time is seconds[y/n]")
    if date == 'n':
      date = None
    sis.make_smooth(urbanbook, date, WOORKBOOKNAME)
    sis.closefile(bb)
  elif action == 9:
    NUMBER = sis.getInput("Number of plots")
    #fig,ax =plt.subplots()

    for x in range(0, int(NUMBER)):
      x_arr = []
      y_arr = []

      WOORKBOOKNAME = sis.getInput("Book Location")
      DATASETNAME = sis.getInput("Field to read in book [ ]:")

      urbanbook, bb = sis.openfile(WOORKBOOKNAME)
      col = sis.findfield(urbanbook, DATASETNAME, bb, 1)
      for book in urbanbook:
	x_arr.append(datetime.datetime.fromtimestamp(float(book[0])))
	y_arr.append(float(book[col]))
      if ax == None:
	ax = sis.make_plot(x_arr, y_arr, ax, DATASETNAME)
      else:
	ax = sis.make_plot(x_arr, y_arr, ax, DATASETNAME)
      bb.close()

    #plt.grid(True)
    plt.show
  # elif action == 11:

if __name__ == "__main__": main()
