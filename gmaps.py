#!/usr/bin/env python2
# -*- coding: utf-8; -*-

import simplejson, urllib, sys, time
from time import sleep
import random
from difflib import SequenceMatcher as sm

GEOCODE_BASE_URL = 'http://maps.google.it/maps/api/directions/json'
THRESHOLD=0.6
SLEEP_T=1

def geocode(origin, destination, sensor):
    geo_args = {
        'origin': origin,
        'destination': destination,
        'sensor': sensor
    }

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    result = simplejson.load(urllib.urlopen(url))
    res = {}
    status = False

    if simplejson.dumps(result['status']) == "\"OK\"" :
        leg = result['routes'][0]['legs'][0]
        duration = simplejson.dumps(leg['duration']['value']).strip("\"")
        distance = simplejson.dumps(leg['distance']['value']).strip("\"")

        # conversions
        duration = float(duration) / 60
        distance = float(distance) / 1000

        # string comparison
        start_index = sm(None, origin, leg['start_address']).ratio()
        end_index = sm(None, destination, leg['end_address']).ratio()
        if (start_index < THRESHOLD) or (end_index < THRESHOLD):
            res['duration'] = "%.0f *" % duration
            res['distance'] = "%.1f *" % distance
            print >> sys.stderr, "ATTENZIONE! Forse alcune cittá non sono " \
                "state trovate\n. Partenza voluta: \"%s\", partenza suggerita" \
                ": \"%s\".\n Destinazione voluta: %s, " \
                " destinazione suggerita: \"%s\"" % (origin,
                                                     leg['start_address'],
                                                     destination,
                                                     leg['end_address'])
        else:
            res['duration'] = "%.0f" % (duration)
            res['distance'] = "%.1f" % (distance)
        status = True
    elif (simplejson.dumps(result['status']) == "\"ZERO_RESULTS\""):
        res['duration'] = "?"
        res['distance'] = "?"
        print >> sys.stderr, "Errore in %s -> %s" % (origin, destination)
        status = True
    else:
        res['duration'] = "?"
        res['distance'] = "?"
        print >> sys.stderr, "Errore in %s -> %s" % (origin, destination)
        print >> sys.stderr, simplejson.dumps(result['status'])

    return res, status, simplejson.dumps(result['status'])



if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "Usage: %s inputfile outputfile" % (sys.argv[0])
        exit(-1)

    try:
        fin = open(sys.argv[1])
    except Exception:
        print "Errore in apertura file"

    try:
        fout = open(sys.argv[2], "w")
    except Exception:
        print "Errore in apertura file"

    random.seed()

    status = True
    res_string = ""

    for i in fin:
        if i == "":
            continue
        res = {'distance': 0.0, 'duration': 0.0}
        fields = i.rstrip().split(";")
        from_city = fields[2]
        to_city = fields[3]

        print "Querying %s -> %s..." % (from_city, to_city)
        if (len(fields) <= 6) or (fields[6] == "" and from_city != to_city ):

            if status == True:
                res, status, res_string = geocode(origin=from_city,
                                                  destination=to_city,
                                                  sensor="false")

                print >> fout, "%s;%s;%s;%s;%s;%s;%s;%s" % (fields[0],
                                                            fields[1],
                                                            fields[2],
                                                            fields[3],
                                                            fields[4],
                                                            fields[5],
                                                            res['distance'],
                                                            res['duration'])

                print "Sleeping for " + str(SLEEP_T) + "s"
                sleep(SLEEP_T)
            else: # do nothing
                print >> fout, i.rstrip()
        else:
            print "Already present"
            print >> fout, i.rstrip()

    print "Result: %s" % (res_string)
