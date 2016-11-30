import argparse
import pandas as pd
import time
import json
import pip

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import numpy as np
import sys

BENCHMARKNAME = 'benchmark1'
TYPE = 'autoencoder'
EPOCH = 2
BATCH = 50

P     = 60025    # 245 x 245
N1    = 2000
NE    = 600      # encoded dim
F_MAX = 33.3
DR    = 0.2


class AutoEncoder():
    def __init__(self, metaDataDict):
        self.train = None
        self.test = None
        self.x_train = None
        self.x_test = None
        self.diffs = None
        self.initTime = None
        self.trainTime = None
        self.testTime = None
        self.ae = None
        self.resultJson = None
        self.resultDict = {}

        self.metaDataDict = metaDataDict
        self.train = self.readFile(self.metaDataDict['trainFileName'])
        self.test = self.readFile(self.metaDataDict['testFileName'])
        self.initBackend()
        self.normalizeData()
        self.createEncoder()
        self.trainEncoder()
        self.testEncoder()
        self.collectResult()

    def initBackend(self):
        backend = metaDataDict['backend']
        if backend == 'tf':
            os.environ["KERAS_BACKEND"] = 'tensorflow'
        else:
            os.environ["KERAS_BACKEND"] = 'theano'

    def installedPackages(self):
        installedPackages = pip.get_installed_distributions()
        installedPackagesList = sorted(["%s==%s" % (i.key, i.version)
                                        for i in installedPackages])
        return installedPackagesList

    def readFile(self, fileName):
        df = (pd.read_csv(fileName).values).astype('float32')
        return df

    def normalizeData(self):
        self.x_train = self.train[:, 0:P] / F_MAX
        self.x_test = self.test[:, 0:P] / F_MAX

    def createEncoder(self):
        from keras.layers import Input, Dense
        from keras.models import Model
        start = time.time()
        input_vector = Input(shape=(P,))
        x = Dense(N1, activation='sigmoid')(input_vector)
        x = Dense(NE, activation='sigmoid')(x)
        encoded = x
        x = Dense(N1, activation='sigmoid')(encoded)
        x = Dense(P, activation='sigmoid')(x)
        decoded = x
        self.ae = Model(input_vector, decoded)
        end = time.time()
        encoded_input = Input(shape=(NE,))
        self.encoder = Model(input_vector, encoded)
        self.decoder = Model(encoded_input,
            self.ae.layers[-1](self.ae.layers[-2](encoded_input)))
        self.ae.compile(optimizer='rmsprop', loss='mean_squared_error')
        self.initTime = end - start
        print "autoencoder summary"
        self.ae.summary()

    def trainEncoder(self):
        start = time.time()
        self.ae.fit(self.x_train, self.x_train, batch_size=BATCH,
            nb_epoch=EPOCH, validation_data=[self.x_test, self.x_test])
        end = time.time()
        self.trainTime = end - start

    def testEncoder(self):
        start = time.time()
        encoded_image = self.encoder.predict(self.x_test)
        decoded_image = self.decoder.predict(encoded_image)
        diff = decoded_image - self.x_test
        end = time.time()
        self.testTime = end - start
        self.diffs = diff.ravel()
        # print np.mean(self.diffs)
        # sys.exit(0)

    def collectResult(self):
        self.resultDict['initTime'] = self.initTime
        self.resultDict['trainTime'] = self.trainTime
        self.resultDict['testTime'] = self.testTime
        self.resultDict['epocs'] = EPOCH
        self.resultDict['unixTimeStamp'] = time.time()
        self.resultDict['installedPackages'] = self.installedPackages()
        self.resultDict['metric'] = 'mse'
        self.resultDict['metricValue'] = float(np.mean(self.diffs))
        for key in self.metaDataDict.keys():
            self.resultDict[key] = self.metaDataDict[key]
        print self.resultDict
        self.resultJson = json.dumps(self.resultDict)

    def printResults(self):
        print self.resultJson

    def plotResults(self):
        plt.hist(self.diffs, bins='auto')
        plt.title("Histogram of Errors with 'auto' bins")
        plt.savefig('histogram.png')

def saveJsonResult(jsonResult, jsonFilename):
    f = open(jsonFilename, 'w')
    f.write('[\n')
    for i, val in enumerate(jsonResult):
        if i < len(jsonResult)-1:
            f.write('\t'+val+',\n')
        else:
            f.write('\t'+val+'\n')
    f.write(']\n')
    f.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument('-t', action='store', dest='target',
                        help='target hardware')
    parser.add_argument('-m', action='store', dest='method',
                        default='dl', help='method')
    parser.add_argument('-b', action='store', dest='backend',
                        default='tf',
                        help='backend; tf: tensorflow, th:theano')
    parser.add_argument('-v', action='store', dest='vendor',
                        help='vendor')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('--user', action='store',
                               dest='user', help='user name',
                               required=True)
    requiredNamed.add_argument('--trainfile', action='store',
                               dest='trainFileName', help='train file name',
                               required=True)
    requiredNamed.add_argument('--testfile', action='store',
                               dest='testFileName',
                               help='test file name', required=True)
    requiredNamed.add_argument('--outputfile', action='store',
                               dest='outputFileName',
                               help='output file name', required=True)
    cmdLineArgs = parser.parse_args()
    print 'target       =', cmdLineArgs.target
    print 'method       =', cmdLineArgs.method
    print 'backend      =', cmdLineArgs.backend
    print 'vendor       =', cmdLineArgs.vendor
    print 'user         =', cmdLineArgs.user
    print 'trainFileName=', cmdLineArgs.trainFileName
    print 'testFileName =', cmdLineArgs.testFileName
    print 'outputFileName =', cmdLineArgs.outputFileName

    if True:
        runs = 1
        jsonResult = []
        metaDataDict = {}
        metaDataDict['benchmarkName'] = BENCHMARKNAME
        metaDataDict['type'] = TYPE
        metaDataDict['target'] = cmdLineArgs.target
        metaDataDict['method'] = cmdLineArgs.method
        metaDataDict['backend'] = cmdLineArgs.backend
        metaDataDict['vendor'] = cmdLineArgs.vendor
        metaDataDict['user'] = cmdLineArgs.user
        metaDataDict['trainFileName'] = cmdLineArgs.trainFileName
        metaDataDict['testFileName'] = cmdLineArgs.testFileName
        metaDataDict['outputFileName'] = cmdLineArgs.outputFileName
        for i in range(runs):
            autoencode = AutoEncoder(metaDataDict)
            jsonResult.append(autoencode.resultJson)
        print jsonResult
        saveJsonResult(jsonResult, metaDataDict['outputFileName'])
