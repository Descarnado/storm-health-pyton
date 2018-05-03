#!/usr/bin/env python

import base64
import json
import optparse
import sys
import urllib.request, urllib.error, urllib.parse

def main(argv):
  #print (CreateTd("123"))
  #print (CreateTd("123", "red"))
  #print (CreateTd("123", "red", 2))
  arr = []
  arr.append(CreateTd("123"))
  arr.append(CreateTd("123","red"))
  arr.append(CreateTd("123", "red", 2))

  print(CreateTr(CreateTd("SomeHeader",None, 999)))
  print(CreateTr(arr))

def CreateTd(contains, color = None, span = 0):
  tdOpenTag = "<td"
  tdOpenTag = tdOpenTag if color is None else (tdOpenTag + " color=" + color)
  tdOpenTag = tdOpenTag if span <= 0 else (tdOpenTag + " colspan=" + str(span))
  tdOpenTag = tdOpenTag + ">"
  return tdOpenTag + contains + "</td>"

def CreateTr(contains):
  tr = "<tr>"
  for td in contains:
    tr += td
  return tr + "</tr>"

#
# main app
#
if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
