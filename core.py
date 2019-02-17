import os
import re
import math

import maya.cmds as mc
import maya.mel as mm

def parentShape(source = '', target = ''):
	
	src = Dag(source)
	trgt = Dag(target)
	
	mc.parent(src.shape, trgt, s = True, r = True)
	mc.delete(src)

def arclen(*args, **kwargs):
	cif = mc.arclen(*args, **kwargs)
	return Node(cif)

def circle(*args, **kwargs):
	return Dag(mc.circle(*args, **kwargs)[0])

def curve(*args, **kwargs):
	return Dag(mc.curve(*args, **kwargs))

def duplicateCurve(*args, **kwargs):
	tmp = mc.duplicateCurve(*args, **kwargs)
	crv = Dag(tmp[0])
	cfs = Node(tmp[1])
	return crv, cfs

def nurbsPlane(*args, **kwargs):
	return Dag(mc.nurbsPlane(*args, **kwargs)[0])

def group(*args, **kwargs):
	grp = Dag(mc.group(*args, **kwargs))
	grp.attr('rp').value = (0,0,0)
	grp.attr('sp').value = (0,0,0)
	return grp

def listAllChildren(obj = ''):
	return mc.listRelatives(obj, ad = True, type = 'transform')

def parentConstraint(*args, **kwargs):
	return Constraint(mc.parentConstraint(*args, **kwargs)[0])

def pointConstraint(*args, **kwargs):
	return Constraint(mc.pointConstraint(*args, **kwargs)[0])

def orientConstraint(*args, **kwargs):
	return Constraint(mc.orientConstraint(*args, **kwargs)[0])

def aimConstraint(*args, **kwargs):
	return Constraint(mc.aimConstraint(*args, **kwargs)[0])

def scaleConstraint(*args, **kwargs):
	return Constraint(mc.scaleConstraint(*args, **kwargs)[0])

def poleVectorConstraint(*args, **kwargs):
	return Constraint(mc.poleVectorConstraint(*args, **kwargs)[0])

def tangentConstraint(*args, **kwargs):
	return Constraint(mc.tangentConstraint(*args, **kwargs)[0])

# Math tools
def pos(obj):
	return mc.xform(obj, q=True, t=True, ws=True)

def add(a, b):
	return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]

def diff(a, b):
	return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]

def dot(a, b):
	return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def cross(a, b):
	c = [a[1]*b[2] - a[2]*b[1],
		a[2]*b[0] - a[0]*b[2],
		a[0]*b[1] - a[1]*b[0]]

	return c

def mag(vct=(0, 0, 0)):
	return pow(pow(vct[0],2) + pow(vct[1],2) + pow(vct[2],2), 0.5)

def norm(vct=(0, 0, 0)):
	return [ix/mag(vct) for ix in vct]

def angle(a, b):
	return math.acos(dot(a, b) / (mag(a) * mag(b)))

def distance(a='', b=''):
	
	objA = Dag(a)
	objB = Dag(b)
		
	return mag(diff(objB.ws, objA.ws))

def toMat(m=[]):
	"""Converts list of numbers to square matrix.
	a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
	result = [
				[1, 2, 3,],
				[4, 5, 6],
				[7, 8, 9]
			]
	"""
	range_ = range(int(pow(len(m), 0.5)))
	result = []
	
	ix = 0
	for iy in range_:
		col = []
		for iz in range_:
			col.append(m[ix])
			ix += 1
		result.append(col)

	return result

def matMult(a=[], b=[]):
	"""Multiplies two matrices
	a = [
			[a0, a1, a2, a3],
			[a4, a5, a6, a7],
			[a8, a9, a10, a11],
			[a12, a13, a14, a15]
		]
	b = [
			[b0, b1, b2, b3],
			[b4, b5, b6, b7],
			[b8, b9, b10, b11],
			[b12, b13, b14, b15]
		]
	"""
	return [[sum(a*b for a, b in zip(aRow, bCol)) for bCol in zip(*b)] for aRow in a]

def composeName(ndNm='', ndIdx='', ndSide='', ndType=''):
	"""composeName('Arm', '1', 'L', 'Jnt')
	composeName('Arm', '', 'L', 'Jnt')
	composeName('Spine', '', '', 'Jnt')
	"""
	# Capitalize first character.
	ndNm = '%s%s' % (ndNm[0].upper(), ndNm[1:])
	ndType = '%s%s' % (ndType[0].upper(), ndType[1:])

	# Clean side
	ndSide = ndSide.replace('_', '')
	if ndSide:
		ndSide = '_%s_' % ndSide
	else:
		ndSide = '_'

	# Clean index
	ndIdx = str(ndIdx).replace('_', '')
	if ndIdx:
		ndIdx = '_%s' % ndIdx

	return '%s%s%s%s' % (ndNm, ndIdx, ndSide, ndType)

def decomposeName(ndNm=''):
	"""Splits given name to elements.
	"""
	elems = ndNm.split('_')
	
	ndNm = ''
	ndIdx = ''
	ndSide = ''
	ndType = ''
	
	if len(elems) == 1:
	
		ndNm = elems[0]
		ndType = 'None'
	
	elif len(elems) == 2:
	
		ndNm = elems[0]
		ndType = elems[1]
	
	elif len(elems) == 3:
	
		ndNm = elems[0]
		ndNm = elems[2]
	
		if elems[1].isdigit():
		
			ndIdx = elems[1]

		else:
		
			ndSide = elems[1]
	
	elif len(elems) == 4:
	
		ndNm = elems[0]
		ndIdx = elems[1]
		ndSide = elems[2]
		ndType = elems[3]
	
	return ndNm, ndIdx, ndSide, ndType

class Attribute(object):
	"""Template class for all Attributes in this module
	"""
	def __init__(self, attrName=''):
		self.name = str(attrName)
	
	def __str__(self):
		return str(self.name)
	
	def __repr__(self):
		return str(self.name)
	
	def __floordiv__(self, attr=''):
		mc.disconnectAttr(self, attr)
	
	def __rshift__(self, target=''):
		try:
			mc.connectAttr(self, target, f = True)
		except RuntimeError:
			print '%s has already connected to %s' % (self, target)

	# v/value property
	def getVal(self):
	
		val = mc.getAttr(self)
	
		if type(val) is type([]) or type(val) is type(()):
			return val[0]
		else:
			return val
	
	def setVal(self, val):
		if type(val) == type(()) or type(val) == type([]):
			node, attr = self.name.split('.')
			chldrn = mc.attributeQuery(attr, node = node, lc = True)
		
			for ix in range(0, len(chldrn)):
				mc.setAttr('%s.%s' % (node, chldrn[ix]), val[ix])
		else:
			mc.setAttr(self, val)
	
	value = property(getVal, setVal, None, None)
	v = property(getVal, setVal, None, None)

	# cb/channelBox property
	def getCb(self):
		return mc.getAttr(self, cb=True)
	
	def setCb(self, val=False):
		mc.setAttr(self, cb=val)
	
	channelBox = property(getCb, setCb, None, None)
	cb = property(getCb, setCb, None, None)
	
	# l/lock property
	def getLock(self):
		return mc.getAttr(self, l=True)
	
	def setLock(self, val=False):
		mc.setAttr(self, l=val)
	
	lock = property(getLock, setLock, None, None)
	l = property(getLock, setLock, None, None)
	
	# h/hide property
	def getHide(self):
		return not mc.getAttr(self, k=True)
	
	def setHide(self, val=False):
		mc.setAttr(self, k = not val)
		mc.setAttr(self, cb = not val)
	
	hide = property(getHide, setHide, None, None)
	h = property(getHide, setHide, None, None)
	
	# Lock and hide attribute
	def lockHide(self):
		mc.setAttr(self, l=True)
		mc.setAttr(self, k=False)
	
	def set(self, *args, **kwargs):
	
		mc.setAttr(self, *args, **kwargs)
	
	# Exists property
	def getExists(self):
		return mc.objExists(self)
	
	exists = property(getExists, None, None, None)

class Node(object):
	"""Template class for all maya nodes in this module.
	"""
	def __init__(self, name):
		self.__name = str(name)
		mc.select(cl = True)
	
	def __str__(self):
		return str(self.name)
	
	def __repr__(self):
		return str(self.name)
	
	# Name properties
	def getName(self):
		return self.__name
	
	def rename(self, newName):
		self.__name = str(mc.rename(self.__name, newName))
	
	name = property(getName, rename, None, None)
	
	# Type property
	def getType(self):
		return mc.nodeType(self.name)
	
	type = property(getType, None, None, None)
	
	# Exists property
	def getExists(self):
		return mc.objExists(self)
	
	exists = property(getExists, None, None, None)
	
	# Attribute tools
	def attr(self, attrName = ''):
		return Attribute('%s.%s' % (self, attrName))
	
	def add(self, *args, **kwargs):
		mc.addAttr(self, *args, **kwargs)
	
	def lockHideAttrs(self, *args):
		for arg in args:
			if arg in ('t', 'r', 's'):
				for ax in ('x', 'y', 'z'):
					mc.setAttr('%s.%s%s' % (self, arg, ax), l = True, k = False)
			else:
				mc.setAttr('%s.%s' % (self, arg), l = True, k = False)
	
	def lockAttrs(self, *args):
		for arg in args:
			if arg in ('t', 'r', 's'):
				for ax in ('x', 'y', 'z'):
					mc.setAttr('%s.%s%s' % (self, arg, ax), l = True)
			else:
				mc.setAttr('%s.%s' % (self, arg), l = True)
	
	def lockHideKeyableAttrs(self):
		# Lock and hide keyable attributes
		attrs = mc.listAttr(self.name, k = True)
	
		for attr in attrs:
			# Do nothing if attribute is multi
			if mc.attributeQuery(attr.split('.')[0], n = self.name, multi = True):
				continue
			else:
				mc.setAttr('%s.%s' % (self.name, attr), l = True, k = False)
	
	def lockKeyableAttrs(self):
		# Lock and hide keyable attributes
		attrs = mc.listAttr(self.name, k = True)
	
		for attr in attrs:
			# Do nothing if attribute is multi
			if mc.attributeQuery(attr.split('.')[0], n = self.name, multi = True):
				continue
			else:
				mc.setAttr('%s.%s' % (self.name, attr), l = True)

class SetRange(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('setRange'))

class RemapValue(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('remapValue'))

class PointOnCurveInfo(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('pointOnCurveInfo'))

class NearestPointOnCurve(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('nearestPointOnCurve'))

class ClosestPointOnSurface(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('closestPointOnSurface'))

class PointOnSurfaceInfo(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('pointOnSurfaceInfo'))

class CurveInfo(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('curveInfo'))

class AddDoubleLinear(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('addDoubleLinear'))

class Condition(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('condition'))

class MultDoubleLinear(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('multDoubleLinear'))

class PlusMinusAverageTemplate(Node):
	"""A base class for plusMinusAverage object.
	"""
	def __init__(self, name=''):
		Node.__init__(self, name)
	
	def last1D(self):
		# Find the first connectable input1D attribute
		sources = mc.listConnections('%s.input1D' % self.name, d=False, s=True, p=True)
		if sources:
			for ix in range(len(sources) + 1):
				if not mc.listConnections('%s.input1D[%s]' % (self.name, str(ix)), d=False, s=True, p=True):
					return Attribute('%s.input1D[%s]' % (self.name, str(ix)))
		else:
			return Attribute('%s.input1D[0]' % self.name)

	def last3D(self):
		# Find the first connectable input3D attribute
		sources = mc.listConnections('%s.input3D' % self.name, d=False, s=True, p=True)
		if sources:
			for ix in range(len(sources) + 1):
				if not mc.listConnections('%s.input3D[%s]' % (self.name, str(ix)), d=False, s=True, p=True):
					return Attribute('%s.input3D[%s]' % (self.name, str(ix)))
		else:
			return Attribute('%s.input3D[0]' % self.name)

class PlusMinusAverage(PlusMinusAverageTemplate):
	def __init__(self):
		PlusMinusAverageTemplate.__init__(self, mc.createNode('plusMinusAverage'))
	
class MultiplyDivide(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('multiplyDivide'))

class VectorProduct(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('vectorProduct'))

class BlendColors(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('blendColors'))

class BlendTwoAttr(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('blendTwoAttr'))
	
	def last(self):
		# Find connectable input1D attribute.
		sources = mc.listConnections('%s.input' % self.name, d = False, s = True, p = True)
		if sources:
			for ix in range(len(sources) + 1):
				if not mc.listConnections('%s.input[%s]' % (self.name, str(ix)), d = False, s = True, p = True):
					return Attribute('%s.input[%s]' % (self.name, str(ix)))
		else:
			return Attribute('%s.input[0]' % self.name)
	
class DistanceBetween(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('distanceBetween'))

class AngleBetween(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('angleBetween'))

class Reverse(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('reverse'))

class CurveFromMeshEdge(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('curveFromMeshEdge'))

class Loft(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('loft'))

class Clamp(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('clamp'))

class Fractal(Node):
	def __init__(self):
		Node.__init__(self, mc.createNode('fractal'))

class SkinCluster(Node):
	def __init__(self, *args, **kwargs):
	
		Node.__init__(self, mc.skinCluster(*args, **kwargs)[0])

class Dag(Node):
	"""Template class for DAG nodes in this module.
	"""
	def __init__(self, nodeName = ''):
		Node.__init__(self, nodeName)
	
	# shape properties
	def getShape(self):
		shapes = mc.listRelatives(self.name, shapes = True)
		if shapes:
			if len(shapes) > 1:
				return shapes[0]
			else:
				return shapes[0]
	
	def renameShape(self, newName):
		shapes = mc.listRelatives(self.name, shapes = True)
		if shapes:
			for shape in shapes:
				mc.rename(shape, newName)
	
	shape = property(getShape, None, None, None)
	
	# color property
	def getColor(self):
		return mc.getAttr('%s.overrideColor' % self.shape)
	
	def setColor(self, cin):
	
		obj = self.shape
	
		cDic = {'black': 1, 'gray': 2, 'softGray': 3, 'darkBlue': 15, 'blue': 6, 
			'darkGreen': 7, 'brown': 11, 'darkRed': 12, 'red': 13, 'green': 14, 
			'white': 16, 'yellow': 17, 'softYellow': 21, 'softBlue': 18, 'softRed': 31}
	
		if type(cin) == type(str()):
			if cin in cDic.keys():
				cid = cDic[cin]
			else:
				cid = 0
		else:
			cid = cin
	
		if type(obj) is type([]):
		
			mc.setAttr('%s.overrideEnabled' % obj[0], 1)
			mc.setAttr('%s.overrideColor' % obj[0], cid)
		else:
		
			mc.setAttr('%s.overrideEnabled' % obj, 1)
			mc.setAttr('%s.overrideColor' % obj, cid)
	
	color = property(getColor, setColor, None, None)
	
	# rotate order property
	def getRotateOrder(self):
		roDct = {'xyz': 0, 'yzx': 1, 'zxy': 2, 'xzy': 3, 
			'yxz': 4, 'zyx': 5}
		roId = mc.getAttr('%s.rotateOrder' % self.name)
	
		for key in roDct.keys():
			if roId == roDct[key]:
				return roId

	def setRotateOrder(self, ro):
		roDct = {'xyz': 0, 'yzx': 1, 'zxy': 2, 'xzy': 3, 
			'yxz': 4, 'zyx': 5}
	
		if ro in roDct.keys():
			val = roDct[ro]
		else:
			val = ro
	
		mc.setAttr('%s.rotateOrder' % self.name, val)
	
	rotateOrder = property(getRotateOrder, setRotateOrder, None, None)
	
	# World space property
	def getWs(self):
	
		validTypes = ('transform','joint')
	
		if self.type in validTypes:
			pos = mc.xform(self, q = True, ws = True, t = True)
			return (float(pos[0]),float(pos[1]),float(pos[2]))
	
	ws = property(getWs, None, None, None)
	
	# Transform tools
	def getParent(self):
		# Get parent node
		obj = mc.listRelatives(self, p = True)
	
		if obj:
			return Dag(obj[0])
		else:
			return None
	
	def parent(self, target = '', **kwargs):
		if target:
			try:
				mc.parent(self, target, **kwargs)
			except:
				mc.warning('Cannot parent %s to %s' % (self.name, target))
		else:
			mc.parent(self, w = True, **kwargs)
		mc.select(cl = True)
	
	def freeze(self, **kwargs):
		mc.makeIdentity(self, a=True, **kwargs)
	
	def snap(self, target):
		# Match current position and orientation to target
		mc.delete(mc.parentConstraint(target, self.name, mo=False))
	
	def snapPoint(self, target):
		# Match current position to target
		mc.delete(mc.pointConstraint(target, self.name, mo=False))
	
	def snapOrient(self, target):
		# Match current orientation to target
		mc.delete(mc.orientConstraint(target, self.name, mo=False))
	
	def snapScale(self, target):
		# Match current scale to target
		mc.delete(mc.scaleConstraint(target, self.name, mo=False))

	# Curve shape tools
	def curveParameter(self, curveType):
		"""Returns parameter by specific curve type.
		The valid types are
		'crossArrow', 'plus', 'circle', 'cube', 'capsule', 'stick' and 'sphere'
		"""
		if curveType == 'crossArrow':
			parameter = [(0, 0, -2.193), (0.852, 0, -1.267), (0.511, 0, -1.267), (0.511, 0, -0.633),
				(0.633, 0, -0.511), (1.267, 0, -0.511), (1.267, 0, -0.852), (2.193, 0, 0),
				(1.267, 0, 0.852), (1.267, 0, 0.511), (0.633, 0, 0.511), (0.511, 0, 0.633),
				(0.511, 0, 1.267), (0.852, 0, 1.267), (0, 0, 2.193), (-0.852, 0, 1.267),
				(-0.511, 0, 1.267), (-0.511, 0, 0.633), (-0.633, 0, 0.511), (-1.267, 0, 0.511),
				(-1.267, 0, 0.852), (-2.193, 0, 0), (-1.267, 0, -0.852), (-1.267, 0, -0.511),
				(-0.633, 0, -0.511), (-0.511, 0, -0.633), (-0.511, 0, -1.267), (-0.852, 0, -1.267),
				(0, 0, -2.193)]
	
		elif curveType == 'plus':
			parameter = [(0,1,0), (0,-1,0), (0,0,0), (-1,0,0), (1,0,0), (0,0,0), (0,0,-1), (0,0,1)]
	
		elif curveType == 'circle':
			parameter = [(1.125, 0, 0), (1.004, 0, 0), (0.992, 0, -0.157), (0.955, 0, -0.31),
				(0.895, 0, -0.456), (0.812, 0, -0.59), (0.71, 0, -0.71), (0.59, 0, -0.812),
				(0.456, 0, -0.895), (0.31, 0, -0.955), (0.157, 0, -0.992), (0, 0, -1.004),
				(0, 0, -1.125), (0, 0, -1.004), (-0.157, 0, -0.992), (-0.31, 0, -0.955),
				(-0.456, 0, -0.895), (-0.59, 0, -0.812), (-0.71, 0, -0.71), (-0.812, 0, -0.59),
				(-0.895, 0, -0.456), (-0.955, 0, -0.31), (-0.992, 0, -0.157), (-1.004, 0, 0),
				(-1.125, 0, 0), (-1.004, 0, 0), (-0.992, 0, 0.157), (-0.955, 0, 0.31),
				(-0.895, 0, 0.456), (-0.812, 0, 0.59), (-0.71, 0, 0.71), (-0.59, 0, 0.812),
				(-0.456, 0, 0.895), (-0.31, 0, 0.955), (-0.157, 0, 0.992), (0, 0, 1.004),
				(0, 0, 1.125), (0, 0, 1.004), (0.157, 0, 0.992), (0.31, 0, 0.955),
				(0.456, 0, 0.895), (0.59, 0, 0.812), (0.71, 0, 0.71), (0.812, 0, 0.59),
				(0.895, 0, 0.456), (0.955, 0, 0.31), (0.992, 0, 0.157), (1.004, 0, 0)]
	
		elif curveType == 'cube':
			parameter = [(-1, 0, -1), (-1, 0, 1), (-1, 2, 1), (-1, 0, 1), (1, 0, 1), (1, 2, 1),
			(1, 0, 1), (1, 0, -1), (1, 2, -1), (1, 0, -1), (-1, 0, -1), (-1, 2, -1), (1, 2, -1),
			(1, 2, 1), (-1, 2, 1), (-1, 2, -1)]
	
		elif curveType == 'capsule':
			parameter = [(-2.011, 0, 0), (-1.977, 0.262, 0), (-1.876, 0.506, 0), (-1.715, 0.715, 0),
				(-1.506, 0.876, 0), (-1.262, 0.977, 0), (-1, 1.011, 0), (1, 1.011, 0),
				(1.262, 0.977, 0), (1.506, 0.876, 0), (1.715, 0.715, 0), (1.876, 0.506, 0),
				(1.977, 0.262, 0), (2.011, 0, 0), (1.977, -0.262, 0), (1.876, -0.506, 0),
				(1.715, -0.715, 0), (1.506, -0.876, 0), (1.262, -0.977, 0), (1, -1.011, 0),
				(-1, -1.011, 0), (-1.262, -0.977, 0), (-1.506, -0.876, 0), (-1.715, -0.715, 0),
				(-1.876, -0.506, 0), (-1.977, -0.262, 0), (-2.011, 0, 0)]
	
		elif curveType == 'stick':
			parameter = [(0, 0, 0), (0, 1.499, 0), (0.052, 1.502, 0), (0.104, 1.51, 0), (0.155, 1.524, 0),
				(0.204, 1.542, 0), (0.25, 1.566, 0), (0.294, 1.595, 0), (0.335, 1.628, 0),
				(0.372, 1.665, 0), (0.405, 1.706, 0), (0.434, 1.75, 0), (0.458, 1.796, 0),
				(0.476, 1.845, 0), (0.49, 1.896, 0), (0.498, 1.948, 0), (0.501, 2, 0),
				(0.498, 2.052, 0), (0.49, 2.104, 0), (0.476, 2.155, 0), (0.458, 2.204, 0),
				(0.434, 2.25, 0), (0.405, 2.294, 0), (0.372, 2.335, 0), (0.335, 2.372, 0),
				(0.294, 2.405, 0), (0.25, 2.434, 0), (0.204, 2.458, 0), (0.155, 2.476, 0),
				(0.104, 2.49, 0), (0.052, 2.498, 0), (0, 2.501, 0), (-0.052, 2.498, 0),
				(-0.104, 2.49, 0), (-0.155, 2.476, 0), (-0.204, 2.458, 0), (-0.25, 2.434, 0),
				(-0.294, 2.405, 0), (-0.335, 2.372, 0), (-0.372, 2.335, 0), (-0.405, 2.294, 0),
				(-0.434, 2.25, 0), (-0.458, 2.204, 0), (-0.476, 2.155, 0), (-0.49, 2.104, 0),
				(-0.498, 2.052, 0), (-0.501, 2, 0), (-0.498, 1.948, 0), (-0.49, 1.896, 0),
				(-0.476, 1.845, 0), (-0.458, 1.796, 0), (-0.434, 1.75, 0), (-0.405, 1.706, 0),
				(-0.372, 1.665, 0), (-0.335, 1.628, 0), (-0.294, 1.595, 0), (-0.25, 1.566, 0),
				(-0.204, 1.542, 0), (-0.155, 1.524, 0), (-0.104, 1.51, 0), (-0.052, 1.502, 0),
				(0, 1.499, 0)]
	
		elif curveType == 'sphere':
			parameter = [(-1.5, 0, 0), (-1, 0, 0), (-0.966, 0.259, 0), (-0.866, 0.5, 0),
				(-0.707, 0.707, 0), (-0.5, 0.866, 0), (-0.259, 0.966, 0), (0, 1, 0),
				(0, 1.5, 0), (0, 1, 0), (0.259, 0.966, 0), (0.5, 0.866, 0), (0.707, 0.707, 0),
				(0.866, 0.5, 0), (0.966, 0.259, 0), (1, 0, 0), (1.5, 0, 0), (1, 0, 0),
				(0.966, -0.259, 0), (0.866, -0.5, 0), (0.707, -0.707, 0), (0.5, -0.866, 0),
				(0.259, -0.966, 0), (0, -1, 0), (0, -1.5, 0), (0, -1, 0), (-0.259, -0.966, 0),
				(-0.5, -0.866, 0), (-0.707, -0.707, 0), (-0.866, -0.5, 0), (-0.966, -0.259, 0),
				(-1, 0, 0), (-0.951, 0, 0.309), (-0.809, 0, 0.588), (-0.588, 0, 0.809),
				(-0.309, 0, 0.951), (-0.0, 0, 1), (0, 0, 1.5), (-0.0, 0, 1), (0.309, 0, 0.951),
				(0.588, 0, 0.809), (0.809, 0, 0.588), (0.951, 0, 0.309), (1, 0, 0),
				(0.951, 0, -0.309), (0.809, 0, -0.588), (0.588, 0, -0.809), (0.309, 0, -0.951),
				(0, 0, -1), (0, 0, -1.5), (0, 0, -1), (0, 0.259, -0.966), (0, 0.5, -0.866),
				(0, 0.707, -0.707), (0, 0.866, -0.5), (0, 0.966, -0.259), (0, 1, 0),
				(-0.0, 0.966, 0.259), (-0.0, 0.866, 0.5), (-0.0, 0.707, 0.707), (-0.0, 0.5, 0.866),
				(-0.0, 0.259, 0.966), (-0.0, 0, 1), (-0.0, -0.259, 0.966), (-0.0, -0.5, 0.866),
				(-0.0, -0.707, 0.707), (-0.0, -0.866, 0.5), (-0.0, -0.966, 0.259), (0, -1, 0),
				(0, -0.966, -0.259), (0, -0.866, -0.5), (0, -0.707, -0.707), (0, -0.5, -0.866),
				(0, -0.259, -0.966), (0, 0, -1), (-0.309, 0, -0.951), (-0.588, 0, -0.809),
				(-0.809, 0, -0.588), (-0.951, 0, -0.309), (-1, 0, 0)]
	
		elif curveType == 'square':
			parameter = [(-1, 0, 0), (-1, 2, 0), (1, 2, 0), (1, 0, 0), (-1, 0, 0)]

		elif curveType == 'pentagon':
			parameter = [(0, 0, 1.12558), (0, 0, 1), (-1, 0, 1), (-1, 0, -0.5),
			(0, 0, -1), (0, 0, -1.12558), (0, 0, -1), (1, 0, -0.5), (1, 0, 1), (0, 0, 1)]

		elif curveType == 'null':
			parameter = [(0,0,0), (0,0,0)]
	
		else: # null shape
			parameter = [(0,0,0), (0,0,0)]
	
		return parameter

	def resetShape(self):

		shpDict = {80: 'sphere', 62: 'stick', 48: 'circle', 29: 'crossArrow', 
			27: 'capsule', 16: 'cube', 10: 'pentagon', 8: 'plus', 5: 'square'}

		cvsNo = mc.getAttr('%s.spans' % self.shape) + mc.getAttr('%s.degree' % self.shape)
		crvType = shpDict[cvsNo]
		parameter = self.curveParameter(crvType)

		for ix in range(cvsNo):
			currPos = parameter[ix]
			currVtx = '%s.cv[%s]' % (self.shape, str(ix))
			mc.xform(currVtx, os=True, t=(currPos[0], currPos[1], currPos[2]))

	def createCurve(self, curveType = ''):
		"""Creates a curve shape for current transform object
		Returns shape node."""
		curve = ''

		if curveType == 'nrbCircle':
			curve = mc.circle(d=3, s=8, ch=False)[0]
		else:
			curve = mc.curve(d = 1, p = self.curveParameter(curveType))
	
		curveShape = mc.listRelatives(curve, s = True)[0]
	
		mc.parent(curveShape, self.name, s = True, r = True)
		mc.delete(curve)
		mc.select(cl = True)
	
		return mc.rename(curveShape, '%sShape' % self.name)
	
	# Shape tools
	def scaleShape(self, val = 1.0000):
		if self.shape:
			typ = mc.nodeType(self.shape)
			if typ == 'nurbsCurve':
				cvsNo = mc.getAttr('%s.spans' % self.shape) + mc.getAttr('%s.degree' % self.shape)
				cvs = '%s.cv[%s:%s]' % (self.name, str(0), str(cvsNo))
				piv = mc.xform(self.name, q = True, rp = True, ws = True)
			elif typ == 'nurbsSurface':
				cvU = mc.getAttr('%s.spansU' % self.shape) + mc.getAttr('%s.degreeU' % self.shape) - 1
				cvV = mc.getAttr('%s.spansV' % self.shape) + mc.getAttr('%s.degreeV' % self.shape) - 1
				cvs = '%s.cv[%s:%s][%s:%s]' % (self.name, str(0), str(cvU), str(0), str(cvV))
				piv = mc.xform(self.name, q = True, rp = True, ws = True)
		
			mc.scale(val, val, val, cvs, pivot = (piv[0], piv[1], piv[2]), r = True)
	
	def rotateShape(self, ro = (0, 0, 0) ):
		if self.shape:
			typ = mc.nodeType(self.shape)
			if typ == 'nurbsCurve':
				cvsNo = mc.getAttr('%s.spans' % self.shape) + mc.getAttr('%s.degree' % self.shape)
				cvs = '%s.cv[%s:%s]' % (self.name, str(0), str(cvsNo))
			elif typ == 'nurbsSurface':
				cvU = mc.getAttr('%s.spansU' % self.shape) + mc.getAttr('%s.degreeU' % self.shape) - 1
				cvV = mc.getAttr('%s.spansV' % self.shape) + mc.getAttr('%s.degreeV' % self.shape) - 1
				cvs = '%s.cv[%s:%s][%s:%s]' % (self.name, str(0), str(cvU), str(0), str(cvV))
		
			mc.rotate(ro[0], ro[1], ro[2], cvs, r = True, os = True)

	def moveShape(self, mo = (0, 0, 0) ):
		if self.shape:
			typ = mc.nodeType(self.shape)
			if typ == 'nurbsCurve':
				cvsNo = mc.getAttr('%s.spans' % self.shape) + mc.getAttr('%s.degree' % self.shape)
				cvs = '%s.cv[%s:%s]' % (self.name, str(0), str(cvsNo))
			elif typ == 'nurbsSurface':
				cvU = mc.getAttr('%s.spansU' % self.shape) + mc.getAttr('%s.degreeU' % self.shape) - 1
				cvV = mc.getAttr('%s.spansV' % self.shape) + mc.getAttr('%s.degreeV' % self.shape) - 1
				cvs = '%s.cv[%s:%s][%s:%s]' % (self.name, str(0), str(cvU), str(0), str(cvV))
		
			mc.move(mo[0], mo[1], mo[2], cvs, r = True, os = True)

	# Hide/Show object
	def hide(self):
	
		if self.attr('v').l:
			self.attr('v').l = 0
			self.attr('v').v = 0
			self.attr('v').l = 1
		else:
			self.attr('v').v = 0
	
	def show(self):
	
		if self.attr('v').l:
			self.attr('v').l = 0
			self.attr('v').v = 1
			self.attr('v').l = 1
		else:
			self.attr('v').v = 1

class Locator(Dag):
	def __init__(self):
		Dag.__init__(self, mc.spaceLocator()[0])

class Joint(Dag):
	def __init__(self, curveType = ''):
		Dag.__init__(self, mc.createNode('joint'))
		if curveType: self.createCurve(curveType)

	# Draw Styles
	def getDrawStyle(self):
		return mc.getAttr('%s.drawStyle' % self.name)

	def setDrawStyle(self, style=None):

		if type(style) == type(int()):
			mc.setAttr('%s.drawStyle' % self.name, style)

		elif type(style) == type(str()):
			styleDict = {'bone':0, 'box': 1, 'none': 2}
			mc.setAttr('%s.drawStyle' % self.name, styleDict[style])

	drawStyle = property(getDrawStyle, setDrawStyle, None, None)

class Control(Dag):
	"""Control object
	If no curveType specified, create an empty group."""
	def __init__(self, curveType = ''):
		Dag.__init__(self, mc.group(em = True))
		if curveType: self.createCurve(curveType)

class Null(Dag):
	def __init__(self, nodeName=''):
		Dag.__init__(self, mc.group(em = True, n=nodeName))

class Ik(Dag):
	"""Template class for IK handle object in this module.
	"""
	def __init__(self, nodeName = ''):
		Dag.__init__(self, nodeName)
	
		# name overriding
		self.__name = nodeName
	
	# Name properties
	def getName(self):
		return self.__name
	
	def rename(self, newName):
		self.__name = mc.rename(self.__name, newName)
		self.eff = '%sEff' % newName
	
	name = property(getName, rename, None, None)
	
	# Eff property
	def getEff(self):
		return mc.listConnections('%s.endEffector' % self.__name, s = True, d = False)[0]
	
	def setEff(self, newName = ''):
		mc.rename(self.eff, newName)
	
	eff = property(getEff, setEff, None, None)

class IkRp(Ik):
	# IKRP object
	def __init__(self, sj = '', ee = ''):
		Ik.__init__(self, mc.ikHandle(sj = sj, ee = ee, sol = 'ikRPsolver')[0])

class IkSc(Ik):
	# IKSC object
	def __init__(self, sj = '', ee = ''):
		Ik.__init__(self, mc.ikHandle(sj = sj, ee = ee, sol = 'ikSCsolver')[0])

class IkShoot(Ik):
	# IK object
	def __init__(self, **kwargs):
	
		Ik.__init__(self, mc.ikHandle(**kwargs)[0])
	
class Constraint(Dag):
	# Template class for constraint object in this module
	def __init__(self, nodeName = ''):
		Dag.__init__(self, nodeName)
	
	# target property
	def getTargets(self):
		return mc.listConnections('%s.target' % self.name, s = True)
	
	target = property(getTargets, None, None, None)

class ParentConstraint(Constraint):
	def __init__(self):
	
		Constraint.__init__(self, mc.createNode('parentConstraint'))

class ScaleConstraint(Constraint):
	def __init__(self):
	
		Constraint.__init__(self, mc.createNode('scaleConstraint'))

class PointConstraint(Constraint):
	def __init__(self ):
	
		Constraint.__init__(self, mc.createNode('pointConstraint'))

class OrientConstraint(Constraint):
	def __init__(self ):
	
		Constraint.__init__(self, mc.createNode('orientConstraint'))

class PoleVectorConstraint(Constraint):
	def __init__(self ):
	
		Constraint.__init__(self, mc.createNode('poleVectorConstraint'))

class TangentConstraint(Constraint):
	def __init__(self ):
	
		Constraint.__init__(self, mc.createNode('tangentConstraint'))

class AimConstraint(Constraint):
	def __init__(self ):
	
		Constraint.__init__(self, mc.createNode('aimConstraint'))

class SplineFkControl(Dag):
	"""This is a FK controller which can derive twisting value separately 
	from the other rotate values.
	"""
	def __init__(self):

		self.zrGrp = Null()
		self.oriGrp = Null()
		self.ofstGrp = Null()
		self.ctrl = Control('circle')
		self.postCtrl = Control('cube')
		self.jnt = Joint()

		self.ctrl.rotateOrder = 'xzy'
		self.ctrl.lockHideAttrs('s', 'v')
		self.ctrl.scaleShape(4)
		self.postCtrl.lockHideAttrs('r', 's', 'v')
		self.jnt.parent(self.postCtrl)
		self.postCtrl.parent(self.ctrl)
		self.ctrl.parent(self.ofstGrp)
		self.oriGrp.parent(self.zrGrp)
		self.ofstGrp.parent(self.oriGrp)
		self.postCtrl.moveShape((0, -1, 0))

		# Non-roll joints
		self.twJnt = Joint()
		self.nrJnt = Joint()
		self.nrJntTip = Joint()

		self.twJnt.rotateOrder = 'xzy'
		self.twJnt.parent(self.nrJnt)
		self.nrJntTip.parent(self.nrJnt)
		self.nrJntTip.attr('ty').v = 1
		self.nrJnt.parent(self.ofstGrp)

		# IK handle
		self.nrIkh = IkRp(self.nrJnt, self.nrJntTip)
		self.nrIkh.attr('poleVector').v = (0, 0, 0)
		self.nrIkh.parent(self.ctrl)

		# Constraints
		self.nrJntPntCstr = Constraint(mc.pointConstraint(self.ctrl, self.nrJnt)[0])
		self.twJntAimCstr = Constraint(mc.aimConstraint(self.nrIkh, 
			self.twJnt, aim=(0, 1, 0), u=(0, 0, 1), wut='objectrotation', 
			wuo=self.ctrl, wu=(0, 0, 1))[0])

		# Cleanup
		self.jnt.drawStyle = 'none'
		self.twJnt.drawStyle = 'none'
		self.nrJnt.drawStyle = 'none'
		self.nrJntTip.drawStyle = 'none'
		self.nrIkh.hide()

	def rename(self, part='', index='', side=''):

		self.ctrl.name = composeName(part, index, side, 'Ctrl')
		self.postCtrl.name = composeName('%sPost' % part, index, side, 'Ctrl')
		self.jnt.name = composeName('%sPost' % part, index, side, 'Jnt')
		self.ofstGrp.name = composeName('%sCtrlOfst' % part, index, side, 'Grp')
		self.oriGrp.name = composeName('%sCtrlOri' % part, index, side, 'Grp')
		self.zrGrp.name = composeName('%sCtrlZr' % part, index, side, 'Grp')

		self.twJnt.name = composeName('%sTw' % part, index, side, 'Jnt')
		self.nrJnt.name = composeName('%sNr' % part, index, side, 'Jnt')
		self.nrJntTip.name = composeName('%sNrTip' % part, index, side, 'Jnt')

		self.nrIkh.name = composeName('%sNr' % part, index, side, 'Ikh')

		self.nrJntPntCstr.name = '%s_pointConstraint' % self.nrJnt.name
		self.twJntAimCstr.name = '%s_aimConstraint' % self.twJnt.name

class BaseRigTemplate(object):
	"""A template class for BaseRig.

	:param node: A string represents node name.
	"""
	def __init__(self, node):

		self.Ctrl_Grp = node

	def _init_node(self, node, name, nodeIdx, side, nodeType):
		"""To initialize a rigging node in the rigging module.
		"""
		node.name = composeName(name, nodeIdx, side, nodeType)
		attrName = composeName(name, nodeIdx, '', nodeType)
	
		self.Ctrl_Grp.add(ln=attrName, dt='string')
	
		node.attr('message') >> self.Ctrl_Grp.attr(attrName)

		return node

	def _to_rig_node(self, node):
		"""To cast an existed node to the rig node.
	
		:param node: A pkrig node.
		"""
		attrName = decomposeName(node)
	
		self.Ctrl_Grp.add(ln=attrName, dt='string')
	
		node.attr('message') >> self.Ctrl_Grp.attr(attrName)
	
		return node

class BaseRig(BaseRigTemplate):
	"""A base class for all rigging modules in pkrig.
	"""
	def __init__(self):
	
		grp = Null()
		super(BaseRig, self).__init__(grp)

class AxisAngle(object):
	"""Axis Angle is a system to drive corrective blend shape on
	folding axes.
	"""
	def __init__(self):

		self.orig = Joint()
		self.point = Null()
		self.point.parent(self.orig)
	
		self.rot = Null()
		self.rot.parent(self.point)

		self.rotTip = Null()
		self.rotTip.parent(self.rot)
		addVectorAttribute(self.orig, 'defaultVector', True)
		self.orig.attr('defaultVector').v = (0, 1, 0)
		self.orig.attr('defaultVector') >> self.rotTip.attr('t')

		self.tar = Null()
		self.tar.parent(self.point)
		self.tarPntCon = pointConstraint(self.rotTip, self.tar)

		#xp
		self.xpAngle, self.xpRem = self._addAxisAngle('xp', (1, 0, 0))

		#xm
		self.xmAngle, self.xmRem = self._addAxisAngle('xm', (-1, 0, 0))

		#zp
		self.zpAngle, self.zpRem = self._addAxisAngle('zp', (0, 0, 1))

		#zm
		self.zmAngle, self.zmRem = self._addAxisAngle('zm', (0, 0, -1))

		#ym
		self.ymAngle, self.ymRem = self._addAxisAngle('ym', (0, -1, 0))

	def _addAxisAngle(self, axis='', vector=(0, 0, 1)):

		angleAttr = '%sAngle' % axis
		vectAttr = '%sVect' % axis

		self.orig.add(ln=angleAttr, k=True)
		addVectorAttribute(self.orig, vectAttr, True)
		self.orig.attr(vectAttr).v = vector

		angle = AngleBetween()
		self.tar.attr('t') >> angle.attr('vector1')
		self.orig.attr(vectAttr) >> angle.attr('vector2')

		rem = RemapValue()

		angle.attr('angle') >> rem.attr('i')

		rem.attr('value[0].value_Interp').v = 1
		rem.attr('value[0].value_FloatValue').v = 0
		rem.attr('value[0].value_Position').v = 90

		rem.attr('value[1].value_Interp').v = 1
		rem.attr('value[1].value_FloatValue').v = 90
		rem.attr('value[1].value_Position').v = 0

		rem.attr('ov') >> self.orig.attr(angleAttr)

		return angle, rem

	def rename(self, part='', index='', side=''):
	
		self.orig.name = composeName('%sAaOrig' % part, index, side, 'Jnt')
		self.point.name = composeName('%sAaPoint' % part, index, side, 'Grp')
		self.tar.name = composeName('%sAaTar' % part, index, side, 'Grp')
		self.rot.name = composeName('%sAaRot' % part, index, side, 'Grp')
		self.rotTip.name = composeName('%sAaRotTip' % part, index, side, 'Grp')

		self.tarPntCon.name = '%sPointConstraint1' % self.tar.name
	
		#zp
		self.zpAngle.name = composeName('%sAaZpOrig' % part, index, side, 'Angle')
		self.zpRem.name = composeName('%sAaZpOrig' % part, index, side, 'Rem')

		#zm
		self.zmAngle.name = composeName('%sAaZmOrig' % part, index, side, 'Angle')
		self.zmRem.name = composeName('%sAaZmOrig' % part, index, side, 'Rem')

		#xp
		self.xpAngle.name = composeName('%sAaXpOrig' % part, index, side, 'Angle')
		self.xpRem.name = composeName('%sAaXpOrig' % part, index, side, 'Rem')

		#xm
		self.xmAngle.name = composeName('%sAaXmOrig' % part, index, side, 'Angle')
		self.xmRem.name = composeName('%sAaXmOrig' % part, index, side, 'Rem')

		#ym
		self.ymAngle.name = composeName('%sAaYmOrig' % part, index, side, 'Angle')
		self.ymRem.name = composeName('%sAaYmOrig' % part, index, side, 'Rem')
