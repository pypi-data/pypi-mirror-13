#!/usr/bin/env python

try:
    from pyspark import SparkContext
except:
    print "### NO PYSPARK"
import sys
from optparse import OptionParser
from digSparkUtil.fileUtil import FileUtil
from digLshClustering.hasher.hasher import Hasher
from digLshClustering.clusterer.clusterer import Clusterer
from digLshClustering.clusterer.unionFind import UnionFind
from digSparkUtil.dictUtil import as_dict, dict_minus

def testLSH(sc, inputFilename,outputFilename,limit=0,sampleSeed=1234,debug=0,location='hdfs',**kwargs):

    '''
    kwargs is a dictionary of inputs a sample input would look like
    options = {"numHashes":kwargs.get("numHashes",100) ,
               "numItemsInBand": kwargs.get("numItemsInBand",10),
               "computeSimilarity": kwargs.get("computeSimilarity",False),
               "computeIdenticalClusters":kwargs.get("computeIdenticalClusters",False),
               "threshold":kwargs.get("threshold",0.0),
               "base":kwargs.get("base",""),
               "topk":kwargs.get("topk",""),
               "numPartitions":kwargs.get("numPartitions",10),
               "candidatesName":kwargs.get("candidatesName","candidates")
               }
    '''


    futil = FileUtil(sc)
    outOptions = {}

    #Hashing
    #######################

    # LOAD DATA
    # please specify the format of input file and data type
    rdd_hash = sc.sequenceFile(inputFilename)
    rdd_hash.setName('rdd_minhash')
    hasher = Hasher(**kwargs)
    rdd_minHashes = hasher.perform(rdd_hash)
    ##you can call futil_save_file here if you want to save this rdd.
    #futil.save_file(rdd_minHashes,"/Users/rajagopal/Desktop/github_repos/dig-unicode/ht_data/LSH/hashes-sample"
     #               ,file_format='sequence',data_type='json',**outOptions)

    #clustering
    #########################

    clusterer = Clusterer(**kwargs)

    if kwargs.get("computeIdenticalClusters") is True:
        (rdd_clusters,rdd_key_cluster_ids) = clusterer.perform(rdd_minHashes)
    else:
        rdd_clusters = clusterer.perform(rdd_minHashes)
    #you can save the clusters if you want by calling futil.save_file
    #futil.save_file(rdd_clusters,"/Users/rajagopal/Desktop/github_repos/dig-unicode/ht_data/LSH/clusters-sample"
     #               ,file_format='text',data_type='json',**outOptions)


    #unionfind
    #########################
    ##using union-find to merge the similar clusters
    unionFind = UnionFind(**kwargs)
    rdd_unionfind = unionFind.perform(rdd_clusters)


    # SAVE DATA

    futil.save_file(rdd_unionfind,outputFilename,file_format='text',data_type='json',**outOptions)

def main():

    #input to this is always a sequencefile of type json
    sc = SparkContext(appName="LSH-HASHER")

    parser = OptionParser()
    #arguments for minhashing
    parser.add_option("-n", "--numHashes", dest="numHashes", type="int",
                      help="number of minhashes", default=100)
    parser.add_option("-b", "--numItemsInBand", dest="numItemsInBand", type="int",
                      help="number of items in each band", default=10)

    #arguments for clustering
    parser.add_option("-s", "--computeSimilarity", action="store_true",
                      dest="computeSimilarity", default=False, help="compute similarity")
    parser.add_option("-j", "--computeIdenticalClusters", action="store_true",
                      dest="computeIdenticalClusters", default=False, help="compute identical clusters")
    parser.add_option("-t", "--threshold", type="float",
                      dest="threshold", default=0.0, help="similarity threshold")
    parser.add_option("-e", "--base", dest="base", type="string",
                      help="base file", default="")
    parser.add_option("-k", "--topk", dest="topk", type="int",
                      help="top n matches", default=3)
    parser.add_option("-x", "--numPartitions", dest="numPartitions", type="int",
                      help="number of partitions", default=10)
    parser.add_option("-z", "--candidatesName", dest="candidates_name", type="string",
                        help="name for json element for matching candidates", default="candidates")

    (c_options, args) = parser.parse_args()
    #print "Got options:", c_options
    inputFilename = args[0]
    outputFilename = args[1]
    c_options = as_dict(c_options)
    testLSH(sc,inputFilename,outputFilename,**c_options)

if __name__ == "__main__":
    sys.exit(main())
