import matplotlib.pyplot as plt
from sklearn import manifold # importing MDS
from sklearn.cluster import KMeans

from common import damerau_levenshtein_distance
import itertools
import numpy as np
import matplotlib

matplotlib.use("Agg")


class ClusterMotifs(object):

    def __init__(self, num_of_clusters):

        self.num_of_clusters = num_of_clusters
        self.groupsD = None

    def clusterMotifs(self, motifsL):

        if self.groupsD == None:
            self.num_of_motifs = len(motifsL)
            self.motifs = motifsL
            num_motifs = len(motifsL)

            # creating the distance matrix.
            distance_matrix = self.createDistanceMatrix(motifsL, damerau_levenshtein_distance)

            # performing MDS to plot the 2d coordinates
            mds = manifold.MDS()
            mds.dissimilarity = "precomputed"
            self.coordinates = mds.fit(distance_matrix).embedding_

            # performing k-means on the coordinates
            km = KMeans(n_clusters=self.num_of_clusters)
            labels = km.fit(self.coordinates).labels_

            groupsD = {}
            for index, item in enumerate(labels):
                groupsD[item] = groupsD.get(item, [])+[self.motifsD[index]]

            self.groupsD = groupsD
            return groupsD

        return self.groupsD


    def createDistanceMatrix(self, motifsL, distanceFunction):

            num_motifs = len(motifsL)
            self.motifsD = {}
            counter = 0

            for i in motifsL:
                self.motifsD[counter] = i
                counter += 1
            reverseMotifsD = {}

            for index, motifS in self.motifsD.iteritems():
                reverseMotifsD[motifS] = index

            distance_matrix = np.zeros( shape=(num_motifs, num_motifs) )

            for motif1, motif2 in itertools.combinations(motifsL, 2):
                distance = distanceFunction(motif1, motif2)
                motif1_index = reverseMotifsD[motif1]
                motif2_index = reverseMotifsD[motif2]
                # assigning the distance value for the 2 cells
                distance_matrix[motif1_index, motif2_index] = distance
                distance_matrix[motif2_index, motif1_index] = distance
            return distance_matrix


    def showPlot(self):
        plt.scatter(list(self.coordinates[:, 0]), list(self.coordinates[:, 1]))
        for index, item in enumerate(self.coordinates):
          plt.annotate(self.motifsD[index], xy=item)

        plt.show(block=False)