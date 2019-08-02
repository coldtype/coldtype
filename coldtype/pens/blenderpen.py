import os
import sys
import time
dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, Point
from coldtype.color import Gradient, Color
from coldtype.beziers import CurveCutter, raise_quadratic
from coldtype.pens.drawablepen import DrawablePenMixin
from fontTools.pens.basePen import BasePen

import math
import random
try:
    import bpy
    from mathutils import Vector, Matrix
except:
    print("Not a blender environment")


class BPH():
    def FindCollectionForItem(item):
        collections = item.users_collection
        if len(collections) > 0:
            return collections[0]
        return bpy.context.scene.collection

    def Collection(name, parent=None):
        if name not in bpy.data.collections:
            coll = bpy.data.collections.new(name)
            if parent:
                parent.children.link(coll)
            else:
                bpy.context.scene.collection.children.link(coll)
        return bpy.data.collections.get(name)

    def Bezier(coll, name, deleteExisting=False):
        print("Bezier", name, deleteExisting, name in bpy.context.scene.objects)
        if deleteExisting and name in bpy.context.scene.objects:
            obj = bpy.context.scene.objects[name]
            bpy.data.objects.remove(obj, do_unlink=True)
            #bpy.context.view_layer.objects.active = None
            #obj.select_set(True)
            #bpy.context.view_layer.objects.active = obj
            #print(">>>>>>", obj.users)
            #bpy.ops.object.delete()

        if name not in bpy.context.scene.objects:
            bpy.ops.curve.primitive_bezier_curve_add()
            bpy.context.scene.objects["BezierCurve"].name = name
            bc = bpy.context.scene.objects[name]
            bc.data.name = name
            bc.data.dimensions = "2D"
            bc.data.fill_mode = "BOTH"
            bc.data.extrude = 0.1
            mat = bpy.data.materials.new(f"Material_{name}")
            mat.use_nodes = True
            #dv = mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value
            bc.data.materials.append(mat)
        bc = bpy.context.scene.objects[name]
        bc_coll = BPH.FindCollectionForItem(bc)
        if bc_coll != coll:
            coll.objects.link(bc)
            bc_coll.objects.unlink(bc)
        bc.select_set(False)
        return bc
    
    def Vector(pt, z=0):
        x, y = pt
        return Vector((x, y, z))


class BlenderPen(DrawablePenMixin, BasePen):
    def __init__(self, dat):
        super().__init__(None)
        self.dat = dat
        tag = self.dat.getTag()
        self.tag = tag if tag and tag != "Unknown" else f"Curve_{random.randint(0, 1000000)}"
    
    def record(self, dat):
        self._spline = None
        self.splines = []
        self._value = []
        dat.replay(self)
        if self._spline and len(self._spline) > 0 and self._spline not in self.splines:
            self.splines.append(self._spline)

    def _moveTo(self, p):
        if self._spline and len(self._spline) > 0 and self._spline not in self.splines:
            self.splines.append(self._spline)
        self._spline = []
        self._value.append([p])
        self._spline.append(["BEZIER", "start", [p, p, p]])

    def _lineTo(self, p):
        self._value.append([p])
        self._spline.append(["BEZIER", "curve", [p, p, p]])

    def _curveToOne(self, p1, p2, p3):
        self._spline[-1][-1][-1] = p1
        self._value.append([p1, p2, p3])
        self._spline.append(["BEZIER", "curve", [p2, p3, p3]])

    def _qCurveToOne(self, p1, p2):
        start = self._value[-1][-1]
        q1, q2, q3 = raise_quadratic(start, (p1[0], p1[1]), (p2[0], p2[1]))
        self._spline[-1][-1][-1] = q1
        self._value.append([q1, q2, q3])
        self._spline.append(["BEZIER", "curve", [q2, q3, q3]])

    def _closePath(self):
        if self._spline and len(self._spline) > 0 and self._spline not in self.splines:
            self.splines.append(self._spline)
            self.spline = None
        self.spline = None
    
    def materials(self):
        return self.bez.data.materials

    def bsdf(self):
        return self.materials()[0].node_tree.nodes["Principled BSDF"]
    
    def shadow(self, clip=None, radius=10, alpha=0.3, color=Color.from_rgb(0,0,0,1)):
        pass
    
    def fill(self, color):
        if color:
            if isinstance(color, Gradient):
                self.fill(color.stops[0][0])
            else:
                print("FILL>>>>>", self.tag, color)
                bsdf = self.bsdf()
                dv = bsdf.inputs[0].default_value
                dv[0] = color.red
                dv[1] = color.green
                dv[2] = color.blue
                dv[3] = 1 #color.alpha
                if color.alpha == 0:
                    dv[0] = 1
                    dv[1] = 1
                    dv[2] = 1
                    dv[3] = 1

    
    def stroke(self, weight=1, color=None):
        if weight and color and color.alpha > 0:
            print("STROKE>>>", self.tag, weight, color)
            self.bez.data.fill_mode = "NONE"
            if isinstance(color, Gradient):
                pass
            else:
                self.fill(color)
            
    def extrude(self, amount=0.1):
        self.bez.data.extrude = amount
        return self
    
    def bevel(self, depth=0.02):
        self.bez.data.bevel_depth = depth
        return self
    
    def metallic(self, amount=1):
        self.bsdf().inputs[4].default_value = amount
        return self
    
    def transmission(self, amount=1):
        self.bsdf().inputs[15].default_value = amount
        return self
    
    def image(self, path):
        mat = self.materials()[0]
        bsdf = self.bsdf()
        imgtex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        imgtex.image = bpy.data.images.load(path)
        mat.node_tree.links.new(bsdf.inputs["Base Color"], imgtex.outputs["Color"])
        return self
    
    def convertToMesh(self):
        self.bez.select_set(True)
        bpy.ops.object.convert(target="MESH")
        self.bez.select_set(False)
        return self
    
    def rotate(self, x=None, y=None, z=None):
        if x is not None:
            self.bez.rotation_euler[0] = math.radians(x)
        if y is not None:
            self.bez.rotation_euler[1] = math.radians(y)
        if z is not None:
            self.bez.rotation_euler[2] = math.radians(z)
        return self
    
    def draw(self, collection, style=None, scale=0.01, cyclic=True, deleteExisting=False):
        self.bez = BPH.Bezier(collection, self.tag, deleteExisting=deleteExisting)
        self.bez.data.fill_mode = "BOTH"
        self.record(self.dat.copy().removeOverlap().scale(scale))
        self.drawOnBezierCurve(self.bez.data, cyclic=cyclic)
        for attr in self.findStyledAttrs(style):
            self.applyDATAttribute(attr)
        return self

    def drawOnBezierCurve(self, bez, cyclic=True):
        for spline in reversed(bez.splines): # clear existing splines
            bez.splines.remove(spline)

        for spline_data in self.splines:
            bez.splines.new('BEZIER')
            spline = bez.splines[-1]
            spline.use_cyclic_u = cyclic
            for i, (t, style, pts) in enumerate(spline_data):
                l, c, r = pts
                if i > 0:
                    spline.bezier_points.add(1)
                pt = spline.bezier_points[-1]
                pt.co = BPH.Vector(c)
                pt.handle_left = BPH.Vector(l)
                pt.handle_right = BPH.Vector(r)


if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.pens.datpen import DATPen

    dp1 = DATPen()
    dp1.oval(Rect(0, 0, 500, 500).inset(200, 200))
    bp = BlenderPen(dp1)
    print(bp.splines)