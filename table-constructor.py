#!/usr/bin/env python

import base64
import json
import optparse
import sys
import urllib.request, urllib.error, urllib.parse

mappings = {
  'topologies': 'topology/summary',
  'topology': 'topology/%(id)s'
}

def getUrl(base, action, protocol, window):
  wind = "" if window is None else ("?window="+str(window))
  #print ('%(protocol)s://%(base)s/api/v1/%(action)s%(window)s' % { 'protocol': protocol, 'base': base, 'action': mappings[action], 'window': wind})
  return ('%(protocol)s://%(base)s/api/v1/%(action)s%(window)s' % { 'protocol': protocol, 'base': base, 'action': mappings[action], 'window': wind})

def make_request(url, options):
  #print (url)
  req = urllib.request.Request(url)

  if options.passwd and options.user :
    req.add_header('Authorization', 'Basic ' + base64.b64encode('%(user)s:%(passwd)s' % { 'user': options.user, 'passwd': options.passwd }));

  return json.loads(urllib.request.urlopen(req).read())

def get_topologies(options):
  url = getUrl(options.host, 'topologies', options.protocol, None)
  res = make_request(url, options)
  return res['topologies']

def get_topology(options, topologyId):
  url = getUrl(options.host, 'topology', options.protocol, options.window) % {'id': topologyId}
  res = make_request(url, options)
  return res

def get_bolts(topologies, options, window):
  bolts = []
  for t in topologies:
    top = make_request(getUrl(options.host, 'topology', options.protocol, window) % { 'id': t['id'] }, options)
    bolts.extend(top['bolts'])
  return bolts

def get_topology_bolts(topology, options, window):
  bolts = []
  top = make_request(getUrl(options.host, 'topology', options.protocol, window) % { 'id': topology }, options)
  bolts.extend(top['bolts'])
  return bolts 

def get_spouts(topologies, options, window):
  spouts = []
  for t in topologies:
    top = make_request(getUrl(options.host, 'topology', options.protocol, window) % { 'id': t['id'] }, options)
    spouts.extend(top['spouts'])
  return spouts

def get_topology_spouts(topology, options, window):
  spouts = []
  top = make_request(getUrl(options.host, 'topology', options.protocol, window) % { 'id': topology }, options)
  spouts.extend(top['spouts'])
  return spouts

def main(argv):
  p = optparse.OptionParser(conflict_handler="resolve", description="This Zabbix plugin checks the health of a storm cluster.")

  p.add_option('-h', '--host', action='store', type='string', dest='host', default=None, help='The hostname you want to connect to')
  p.add_option('-u', '--user', action='store', type='string', dest='user', default=None, help='The username you want to login as')
  p.add_option('-p', '--pass', action='store', type='string', dest='passwd', default=None, help='The password you want to use for that user')
  p.add_option('-s', '--https', action='store_true', dest='https', help='use https to connect to the storm cluster')
  p.add_option('-e', '--include-emitted', action='store_true', dest='include_emitted', help='Include bolt & spout emit statistics')
  p.add_option('-a', '--action', action='store', dest='action', help='Action to perform')
  p.add_option('-w', '--window', type="int", dest='window', help='Time window for metrics')
  p.add_option('-m', '--metrics', action='store', type='string', dest='metrics', default=None, help='Metrics you want to get')
  p.add_option('-t', '--topology', action='store', type='string', dest='topology', default=None, help='Certain topology you want to get info about')
  p.add_option('-n', '--bsname', action='store', type='string', dest='bsname', default=None, help='Certain bolt or spout name you want to get info about')

  options, arguments = p.parse_args()
  options.protocol = 'https' if options.https else 'http'

  arr = []
  arr.append(Td("123"))
  arr.append(Td("123","red"))
  arr.append(Td("123", "red", 2))

  topologies = get_topologies(options)

  #times = [600, 10800, 86400, None]
  #timesStr = ['10m 0s', '3h 0m 0s', '1d 0h 0m 0s', 'All Time']

  times = [600, None]
  timesStr = ['10m 0s','All Time']

  backgrUsual1 = "#e5e5e5"
  backgrUsual2 = "#c9c9c9"

  backgrBolts1 = "#dbf8ff"
  backgrBolts2 = "#b1dae3"

  backgrSpouts1 = "#fff4ad"
  backgrSpouts2 = "#f7f2d0"


  result = "<html><font color=\"#0f0f0f\"><table border=1 color=\"black\">"
  for top in topologies:
    result += Tr(Td(top['id'], "#ff9baa" if top['status'] == 'INACTIVE' else "#ade87d" , 999))
    result += Tr(Td(top['uptime'], "#fff3bd", 999))
    topology = get_topology(options, top['id'])
    
    headers = ['assignedMemOnHeap', 'assignedTotalMem', 'assignedMemOffHeap', 'replicationCount']
    result += Tr(Tds(headers,backgrUsual1,backgrUsual2))
    data = [topology[stat] for stat in headers]
    result += Tr(Tds(data,backgrUsual1,backgrUsual2))
    
    if top['status'] == 'INACTIVE':
      continue

    headers = ['windowPretty', 'emitted', 'acked', 'transferred', 'failed']
    result += Tr(Tds(headers,backgrBolts1,backgrBolts2))
    for topStat in topology['topologyStats']:
      data = [topStat[stat] for stat in headers]
      result += Tr(Tds(data,backgrBolts1,backgrBolts2))

    result += Tr(Td("Bolts", "#2d89cf", 999))

    allBoltsWithTime = list(map(lambda time: get_topology_bolts(top['id'], options, time), times))
    #rotated = zip(*original[::-1]) # Python 2
    #rotated = tuple(zip(*original[::-1])) # Python 3
    allBoltsWithTime =  tuple(zip(*allBoltsWithTime[::-1]))

    for timedBolts in allBoltsWithTime:
        result += Tr(Td(timedBolts[0]['boltId'], "#90e9fc", 999))
        headers = ['emitted', 'acked', 'transferred', 'failed']
        result += Tr(Td('window',backgrBolts1) + Tds(headers,backgrBolts2, backgrBolts1)) 
        for timedBolt in zip(timesStr, reversed(timedBolts)):
          data = [timedBolt[1][header] for header in headers]
          result += Tr(Td(timedBolt[0],backgrBolts1) + Tds(data,backgrBolts2,backgrBolts1))
        headers = ['executed', 'executeLatency', 'executors', 'processLatency','requestedCpu', 'requestedMemOnHeap', 'requestedMemOffHeap']
        data = [timedBolts[0][header] for header in headers]
        result += Tr(Tds(headers,backgrUsual1,backgrUsual2)) 
        result += Tr(Tds(data,backgrUsual1,backgrUsual2))
      
    result += Tr(Td("Spouts", "#f0ce54", 999))  
    allSpoutsWithTime = list(map(lambda time: get_topology_spouts(top['id'], options, time), times))
    #rotated = zip(*original[::-1]) # Python 2
    #rotated = tuple(zip(*original[::-1])) # Python 3
    allSpoutsWithTime =  tuple(zip(*allSpoutsWithTime[::-1]))

    for timedSpouts in allSpoutsWithTime:
        result += Tr(Td(timedSpouts[0]['spoutId'], "#fce590", 999))
        headers = ['emitted', 'acked', 'transferred', 'failed']
        result += Tr(Td('window',backgrSpouts1) + Tds(headers,backgrSpouts2,backgrSpouts1)) 
        for timedSpout in zip(timesStr, reversed(timedSpouts)):
          data = [timedSpout[1][header] for header in headers]
          result += Tr(Td(timedSpout[0],backgrSpouts1) + Tds(data,backgrSpouts2,backgrSpouts1))

  #with open('somefile.html', 'w') as the_file:
    #the_file.write(result)

  print(result + "</table></font></html>")

def Tds(tds, color1 = None, color2 = None):
  result = ""
  color = color1
  for td in tds:
    result += Td(td, color)
    color = color2 if color == color1 and color2 is not None else color1
  return result

def Td(contains, color = None, span = 0):
  tdOpenTag = "<td align=center"
  tdOpenTag = tdOpenTag if color is None else (tdOpenTag + " bgcolor=" + color)
  tdOpenTag = tdOpenTag if span <= 0 else (tdOpenTag + " colspan=" + str(span))
  tdOpenTag = tdOpenTag + ">"
  return tdOpenTag + str(contains) + "</td>"

def Tr(contains):
  tr = "<tr>"
  for td in contains:
    tr += td
  return tr + "</tr>"

#
# main app
#
if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
