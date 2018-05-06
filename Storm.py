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

  if options.host is None:
    p.print_help()
    return

  window = options.window
  metrics = options.metrics
  topology = options.topology
  bsname = options.bsname

  if window is not None and not (window == 600 or window == 10800 or window == 86400):
    print ("Window parameter is not correctly setted!")
    return
  #topologies = get_topologies(options)
  #bolts = get_bolts(topologies, options)
  #spouts = get_spouts(topologies, options)

  #print_topology_count(topologies, options.host)
  if options.action is None:
    print_topologies_summary(options)
  elif options.action == "bolts":
    print_bos_info(options,"bolts", topology, bsname, metrics, window)
  elif options.action == "spouts":
    print_bos_info(options,"spouts", topology, bsname, metrics, window)
  elif options.action == "topology":
    print_topology_info(options, topology, metrics, window)
  elif options.action == "topologyStats":
    print_topology_stats(options, topology, metrics, window)
  else:
    print_topologies_summary(options)
  #print_capacity(bolts, options.host)
  #print_execute_latency(bolts, options.host)
  #print_process_latency(bolts, options.host)
  #if options.include_emitted:
  #  print_emitted(bolts, spouts, options.host)

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

def parse_float(object, fieldname):
  return float(object[fieldname])

def capacity(b):
  return b['capacity']
  #return parse_float(b, 'capacity')

def execute_latency(b):
	return b['executeLatency']
  #return parse_float(b, 'executeLatency')

def process_latency(b):
	return b['processLatency']
  #return parse_float(b, 'processLatency')

#def print_topology_count(topologies, host):
  #print('%s storm.topologies %i' % (host, len(topologies)))

#def print_capacity(bolts, host):
  #print('%s storm.capacity %' % (host, sorted(list(map(capacity, bolts)))[-1]))

#def print_execute_latency(bolts, host):
 # print('%s storm.executeLatency %s' % (host, sorted(list(map(execute_latency, bolts)))[-1]))

#def print_process_latency(bolts, host):
  #print('%s storm.processLatency %s' % (host, sorted(list(map(process_latency, bolts)))[-1]))

#def print_emitted(bolts, spouts, host):
#  for b in bolts:
#    print('%(host)s storm.bolts.%(boltName)s.emitted %(emitted)i' % { 'host': host, 'boltName': b['boltId'].lower(), 'emitted': int(b['emitted']) })
#
#  for s in spouts:
#    print('%(host)s storm.spouts.%(spoutName)s.emitted %(emitted)i' % { 'host': host, 'spoutName': s['spoutId'].lower(), 'emitted': int(s['emitted']) })

def print_topologies_summary(options):
  tops = get_topologies(options)
  
  resultStr = ""

  for top in tops:
    resultStr += top['name'] + ":\r\n"
    resultStr += "\tstatus: " + top['status'] + "\r\n"
    if top['status'] == "ACTIVE":
      
      bolts = get_topology_bolts(top['id'], options)
      resultStr += "\tbolts:\r\n"
      for bolt in bolts:
        resultStr += "\t\t" + bolt['boltId'] +":" + "\r\n"
        resultStr += "\t\t\t" + "emitted:"  + str(bolt['emitted']) + "\r\n"
      
      spouts = get_topology_spouts(top['id'], options)
      resultStr += "\tspouts:\r\n"
      for spout in spouts:
        resultStr += "\t\t" + spout['spoutId'] +":" + "\r\n"
        resultStr += "\t\t\t" + "emitted:"  + str(spout['emitted']) + "\r\n"

  print(resultStr);

def print_topology_info(options, topology, metrics, window):
  tops = get_topologies(options)

  if topology is not None:
    tops = filter(lambda t: t['name'] == topology, tops)

  arr = map(lambda tplg: get_topology(options, tplg['id']), tops)

  print(sum(map(lambda a: a[metrics], arr)));

def print_topology_stats(options, topology, metrics, window):
  tops = get_topologies(options)

  if topology is not None:
    tops = filter(lambda t: t['name'] == topology, tops)

  arr = map(lambda tplg: get_topology(options, tplg['id']), tops)
  arr = map(lambda t: t['topologyStats'], arr)
  
  statsByTime = []
  for x in arr:
    statsByTime += x

  statsByTime = filter(lambda x: x['window'] == str(window) if window is not None else x['window'] == ':all-time', statsByTime)

  print(sum(map(lambda a: int(a[metrics]) if a[metrics] is not None else 0, statsByTime)));

def print_bos_info(options, boltsOrSpouts, topology, bsname, metrics, window):
  #Получаем список всех доступных топологий
  tops = get_topologies(options)
  #Если указанно имя конкретной топологии, то отсекаем все остальные топологии по имени.
  if topology is not None:
    tops = filter(lambda t: t['name'] == topology, tops)
  #В зависимости от параметра boltsOrSpouts получаем все спауты или болты у топологий из массива tops
  arr = get_bolts(tops, options, window) if boltsOrSpouts == "bolts"  else get_spouts (tops, options, window)
  #Если указано имя конкретного болта или спаута, то откидываем остальные, у которых не совпадает имя
  if bsname is not None:
    arr = filter(lambda a: a['boltId'] == bsname if boltsOrSpouts == "bolts" else a['spoutId'] == bsname, arr)
  #Если не указано название желаемой метрики, то показываем соответствующее сообщение
  if metrics is None:
    print ('Metrics is not specified! Read help.')
    return
  #Выводим сумму метрики
  print(sum(map(lambda a: a[metrics], arr)));

#
# main app
#
if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
