# -*- coding: utf-8 -*-
import sys
import argparse
import json
from pymongo import MongoClient
from pymongo import DESCENDING, ASCENDING

'''Allow insertion only for the following valid benchmarks'''
VALID_BENCHMARKS = ['benchmark%d' % i for i in range(10)]
'''Name of the database'''
DBNAME = 'lboard'
"""MongoDB should run at the following URI"""
URI = 'mongodb://localhost:27017/'
"""JSON record should have the following keys"""
FIELDS = ['benchmarkName', 'user', 'type', 'metric', 'metricValue']
""" Flag to clear the db; set to False in production mode """
CLEARDB = False

class LeaderBoard:
    """The main class for the leaderboard."""

    def __init__(self):
        """Initialize required vars for the leaderboard class."""
        self.db = None
        self.mgDbClient = None

    def openMongoDB(self, uri):
        """Initialize mongodb for the given uri."""
        if uri is None:
            print "uri name %s not found", uri
            sys.exit(2)
        try:
            self.mgDbClient = MongoClient(uri)
            self.db = self.mgDbClient[DBNAME]
        except:
            print "error in initializing MongoDB: %s", sys.exc_info()[0]

    def closeMongoDB(self):
        """Close mongodb."""
        try:
            self.mgDbClient.close()
        except:
            print "error in closing MongoDB: %s", sys.exc_info()[0]

    def clearDataBase(self, uri):
        """Clear the DBNAME database."""
        mgDbClient = MongoClient(uri)
        mgDbClient.drop_database(DBNAME)

    def clearTable(self, table_name):
        """Clear the table_name database."""
        self.db.drop_collection(table_name)

    def validateRecord(self, record):
        """validate the json record."""
        keys = record.keys()
        for key in keys:
            print key
            if key not in FIELDS:
                print "key %s is missing in JSON file"
                sys.exit(2)

    def readJasonFile(self, jsonFileName):
        """Read the json file."""
        with open(jsonFileName) as json_data:
            data = json.load(json_data)
            for record in data:
                if 'benchmarkName' in record.keys():
                    benchmarkName = record['benchmarkName']
                    if benchmarkName in VALID_BENCHMARKS:
                        self.db[benchmarkName].insert(record)
                    else:
                        print "benchmark name %s not found", benchmarkName
                else:
                    print "benchmarkName key is missing in JSON file"
                    sys.exit(2)

    def queryBenchmarkResults(self, benchmarkName, ascending):
        """Query the benchmark table for the given benchmark name."""
        if benchmarkName is not None:
            benchmarkData = self.db[benchmarkName]
            if ascending:
                result = list(benchmarkData.find().sort("score", ASCENDING))
            else:
                result = list(benchmarkData.find().sort("score", DESCENDING))
        return result

    def printResult(self, result):
        """print the result; the result should iterator data type (list)."""
        for i, record in enumerate(result):
            print i, '==>', record


if __name__ == '__main__':
    jsonFileName = None
    benchmarkName = None
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--jsonFileName', action='store', dest='jsonFileName',
                        help='json file name')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('--benchmarkName', action='store',
                               dest='benchmarkName', help='benchmark name',
                               required=True)
    cmdLineArgs = parser.parse_args()
    print 'benchmarkName      =', cmdLineArgs.benchmarkName
    print 'jsonFileName       =', cmdLineArgs.jsonFileName

    # sys.exit(0)

    jsonFileName = cmdLineArgs.jsonFileName
    benchmarkName = cmdLineArgs.benchmarkName

    """ Initialize LeaderBoard class """
    lb = LeaderBoard()
    """ Open database connection """
    lb.openMongoDB(URI)

    """ Clear the db based on CLEARDB flag """
    if CLEARDB and jsonFileName is not None:
        lb.clearDataBase(URI)
        lb.clearTable('benchmark1')

    """ Upload the data in the json file """
    if jsonFileName is not None:
        lb.readJasonFile(jsonFileName)

    """ Return the results for benchmarkName """
    if benchmarkName is not None:
        result = lb.queryBenchmarkResults(benchmarkName, 1)
        lb.printResult(result)

    """ Close database connection """
    lb.closeMongoDB()
