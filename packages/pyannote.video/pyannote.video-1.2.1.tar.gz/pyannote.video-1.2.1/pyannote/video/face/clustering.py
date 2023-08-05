#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2015-2016 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


from __future__ import print_function
from pyannote.core import Annotation
from pyannote.core import Segment
from pyannote.core import Unknown
from pyannote.core.time import _t_iter as getLabelGenerator
import sklearn.cluster
import numpy as np


class Cluster(object):

    def __init__(self, min_duration=1.0, min_size=60):
        super(Cluster, self).__init__()
        self.min_duration = min_duration
        self.min_size = min_size

    def _load(self, features, tracking):

        # track duration
        groups = features.groupby('track')

        # track timespan
        timespans = groups.apply(lambda x: Segment(np.min(x.time), np.max(x.time)))

        # track duration
        duration = groups.apply(lambda faces: np.max(faces.time) - np.min(faces.time))

        # track size
        size = tracking.groupby('track').apply(lambda faces: np.mean([face.right-face.left for _, face in faces.iterrows()]))

        # track descriptor (average Openface features)
        descriptor = groups.mean().drop('time', axis=1)

        # get rid of short and small tracklets
        keep = (duration > self.min_duration) & (size > self.min_size)
        kept_descriptor = descriptor[keep]
        kept_timespans = timespans[keep]
        X = np.array(kept_descriptor)

        return X, kept_timespans

    def _cluster_to_annotation(self, clusters, kept_timespans):

        labelGenerator = getLabelGenerator()
        annotation = Annotation()

        for cluster in np.unique(clusters):

            label = Unknown() if cluster == -1 else next(labelGenerator)

            for track, segment in kept_timespans[clusters == cluster].iteritems():
                annotation[segment, track] = label

        return annotation

    def __call__(self, features, tracking, n_clusters=50):

        X, kept_timespans = self._load(features, tracking)

        annotation = Annotation()
        if len(X) == 0:
            return annotation

        # # precompute pairwise euclidean distance
        # S = np.sqrt(((X[np.newaxis, :, :] - X[:, np.newaxis, :]) ** 2).sum(2))

        # ward = sklearn.cluster.AgglomerativeClustering(
        #     n_clusters=n_clusters, affinity='euclidean', linkage='ward')
        # clusters = ward.fit_predict(X)

        affinityPropagation = sklearn.cluster.AffinityPropagation(
            damping=0.5, max_iter=200, convergence_iter=15, copy=True,
            preference=None, affinity='euclidean', verbose=True)
        clusters = affinityPropagation.fit_predict(X)

        # birch = sklearn.cluster.Birch(threshold=0.2, n_clusters=n_clusters)
        # clusters = birch.fit_predict(X)

        return self._cluster_to_annotation(clusters, kept_timespans)

    def visualize(self, video, annotation, tracking):

        import scipy.misc

        faces = tracking.groupby('track').first()

        mugshots = {}

        for i, (label, _) in enumerate(annotation.chart()):

            print(i)

            mugshots[label] = []

            for _, track in annotation.subset(set([label])).itertracks():

                face = faces.xs(track)
                t = face.time

                left, right = max(0, int(face.left)), int(face.right)
                top, bottom = max(0, int(face.top)), int(face.bottom)

                print(t, left, right, top, bottom)

                frame = video(t)
                cropped = frame[top:bottom, left:right, :]
                mugshot = scipy.misc.imresize(cropped, (60, 60), interp='bilinear')

                mugshots[label].append(mugshot)

            mugshots[label] = np.hstack(mugshots[label])

        return mugshots
