# -*- coding: utf-8 -*-

import sys
import time
import datetime
import logging
import multiprocessing
import ConfigParser
from forge.lib.helpers import timestamp
from boto import connect_s3
from forge.lib.logs import getLogger
from boto.s3.key import Key

from forge.lib.poolmanager import PoolManager

logging.getLogger('boto').setLevel(logging.CRITICAL)

tmsConfig = ConfigParser.RawConfigParser()
tmsConfig.read('tms.cfg')
basePath = tmsConfig.get('General', 'bucketpath')

# Init logging
dbConfig = ConfigParser.RawConfigParser()
dbConfig.read('database.cfg')
log = getLogger(dbConfig, __name__, suffix=timestamp())

bucketName = 'tms3d.geo.admin.ch'


def _getS3Conn(profileName='tms3d_filestorage'):
    try:
        conn = connect_s3(profile_name=profileName)
    except Exception as e:
        raise Exception('S3: Error during connection %s' % e)
    return conn


connS3 = _getS3Conn()


def getBucket(bucketName=bucketName):
    try:
        bucket = connS3.get_bucket(bucketName)
    except Exception as e:
        raise Exception('Error during connection %s' % e)
    return bucket


def writeToS3(b, path, content, origin, contentType='application/octet-stream'):
    headers = {'Content-Type': contentType}
    k = Key(b)
    k.key = basePath + path
    k.set_metadata('IWI_Origin', origin)
    headers['Content-Encoding'] = 'gzip'
    k.set_contents_from_file(content, headers=headers)

copycount = multiprocessing.Value('i', 0)


def copyKey(args):
    (keyname, toPrefix, t0) = args
    try:
        bucket = getBucket()
        key = bucket.lookup(keyname)
        key.copy(bucketName, toPrefix + keyname)
        copycount.value += 1
        val = copycount.value
        if val % 100 == 0:
            log.info('Created %s copies in %s.' % (val, str(datetime.timedelta(seconds=time.time() - t0))))

    except Exception as e:
        log.info('Caught an exception when copying %s exception: %s' % (keyname, str(e)))


class KeyIterator:

    def __init__(self, prefix, toPrefix, t0):
        self.bucketlist = getBucket().list(prefix=prefix)
        self.toPrefix = toPrefix
        self.t0 = t0

    def __iter__(self):
        for entry in self.bucketlist:
            yield (entry.name, self.toPrefix, self.t0)


def copyKeys(fromPrefix, toPrefix, zooms):
    t0 = time.time()
    copycount.value = 0
    for zoom in zooms:
        log.info('doing zoom ' + str(zoom))
        t0zoom = time.time()
        keys = KeyIterator(fromPrefix + str(zoom) + '/', toPrefix, t0)

        pm = PoolManager()

        pm.process(keys, copyKey, 50)

        log.info('It took %s to copy this zoomlevel (total %s)' % (str(datetime.timedelta(seconds=time.time() - t0zoom)), copycount.value))
    log.info('It took %s to copy for all zoomlevels (total %s)' % (str(datetime.timedelta(seconds=time.time() - t0)), copycount.value))


class S3Keys:

    def __init__(self, prefix, applyBasePath=True):
        self.bucket = getBucket()
        self.counter = 0
        if prefix is not None:
            if applyBasePath:
                self.prefix = basePath + prefix
            else:
                self.prefix = prefix
        else:
            raise Exception('One must define a prefix')
        self.keysList = self.bucket.list(prefix=self.prefix)

    def delete(self):
        keysToDelete = []
        print 'Are you sure you want to delete all tiles starting with %s? (y/n)' % self.prefix
        answer = raw_input('> ')
        if answer.lower() != 'y':
            sys.exit(1)
        print 'Deleting keys for prefix %s...' % self.prefix
        for key in self.keysList:
            keysToDelete.append(key)
            if len(keysToDelete) % 1000 == 0:
                self._deleteKeysResults(self.bucket.delete_keys(keysToDelete))
                keysToDelete = []
        if len(keysToDelete) > 0:
            self._deleteKeysResults(self.bucket.delete_keys(keysToDelete))
        print '%s keys have been deleted' % self.counter

    def listKeys(self):
        print 'Listing keys for prefix %s...' % self.prefix
        for key in self.keysList:
            print "{name}\t{size}\t{modified}".format(
                name=key.name,
                size=key.size,
                modified=key.last_modified,
            )
            # So that one can interrput it from keyboard
            time.sleep(.2)

    def count(self):
        print 'Counting keys for prefix %s...' % self.prefix
        nbKeys = len(list(self.keysList))
        print '%s keys have been found for prefix %s' % (nbKeys, self.prefix)

    def _deleteKeysResults(self, results):
        nbDeleted = len(results.deleted)
        print '%s could not be deleted.' % len(results.errors)
        print '%s have been deleted.' % nbDeleted
        self.counter += len(results.deleted)
