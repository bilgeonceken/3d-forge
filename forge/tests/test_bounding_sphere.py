# -*- coding: utf-8 -*-

import unittest
from forge.models.terrain import TerrainTile
from forge.lib.bounding_sphere import BoundingSphere
from forge.lib.llh_ecef import LLH2ECEF


class TestBoundingSphere(unittest.TestCase):

    def testBoundingSphereAssign(self):
        center = [1, 3, 12]
        radius = 8
        sphere = BoundingSphere(center=center, radius=radius)
        self.failUnless(sphere.center[0] == 1.0)
        self.failUnless(sphere.center[1] == 3.0)
        self.failUnless(sphere.center[2] == 12.0)
        self.failUnless(sphere.radius == 8.0)

    def testBoundingSphereFromPoints(self):
        sphere = BoundingSphere()
        self.failUnless(len(sphere.center) == 0)
        self.failUnless(sphere.radius == 0.0)

        self.failUnless(sphere.minPointX[0] == float('inf'))
        self.failUnless(sphere.minPointY[1] == float('inf'))
        self.failUnless(sphere.minPointZ[2] == float('inf'))

        self.failUnless(sphere.maxPointX[0] == float('-inf'))
        self.failUnless(sphere.maxPointY[1] == float('-inf'))
        self.failUnless(sphere.maxPointZ[2] == float('-inf'))

        points = [[1.1, 3.2, 4.9], [3.1, 1.0, 21.4], [9.1, 3.2, 2.0], [2.0, 4.0, 9.5]]
        sphere.fromPoints(points)

        self.failUnless(sphere.minPointX[0] != float('inf'))
        self.failUnless(sphere.minPointY[1] != float('inf'))
        self.failUnless(sphere.minPointZ[2] != float('inf'))

        self.failUnless(sphere.maxPointX[0] != float('-inf'))
        self.failUnless(sphere.maxPointY[1] != float('-inf'))
        self.failUnless(sphere.maxPointZ[2] != float('-inf'))

        for point in points:
            distance = sphere.distance(sphere.center, point)
            self.failUnless(distance <= sphere.radius)

        # Point outside the sphere
        pointOutside = [1000.0, 1000.0, 1000.0]
        distance = sphere.distance(sphere.center, pointOutside)
        self.failUnless(distance > sphere.radius)

    def testBoundingSpherePrecision(self):
        tilePath = 'forge/data/quantized-mesh/raron.flat.1.terrain'
        ter = TerrainTile()
        ter.fromFile(tilePath, 7.80938, 7.81773, 46.30261, 46.30799)
        coords = ter.getVerticesCoordinates()
        llh2ecef = lambda x: LLH2ECEF(x[0], x[1], x[2])
        coords = map(llh2ecef, coords)
        sphere = BoundingSphere()
        sphere.fromPoints(coords)
        for coord in coords:
            distance = sphere.distance(sphere.center, coord)
            self.failUnless(distance <= sphere.radius)