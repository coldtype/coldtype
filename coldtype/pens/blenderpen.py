from coldtype import *
from drafting.geometry import Rect, Edge, Point
from coldtype.beziers import CurveCutter, raise_quadratic
from coldtype.pens.drawablepen import DrawablePenMixin
from fontTools.pens.basePen import BasePen

import math
import random
try:
    import bpy
    from mathutils import Vector, Matrix
except:
    print(">>> Not a blender environment")


class BPH():
    def Clear():
        print(">>>CLERAING")
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)

        for block in bpy.data.textures:
            if block.users == 0:
                bpy.data.textures.remove(block)

        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)

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

    def Primitive(_type, coll, name, dn=False, container=None):
        created = False
        
        if dn and name in bpy.context.scene.objects:
            obj = bpy.context.scene.objects[name]
            bpy.data.objects.remove(obj, do_unlink=True)

        if name not in bpy.context.scene.objects:
            created = True
            if _type == "Bezier":
                bpy.ops.curve.primitive_bezier_curve_add()
            elif _type == "Plane":
                bpy.ops.mesh.primitive_plane_add()
            bc = bpy.context.active_object
            bc.name = name
            bc.data.name = name
            if _type == "Bezier":
                bc.data.dimensions = "2D"
                bc.data.fill_mode = "BOTH"
                bc.data.extrude = 0.1
            elif _type == "Plane":
                if container:
                    bc.scale[0] = container.w/2
                    bc.scale[1] = container.h/2
                    bc.location[0] = container.x + container.w/2
                    bc.location[1] = container.y + container.h/2
                    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
                    bpy.ops.object.transform_apply()
            mat = bpy.data.materials.new(f"Material_{name}")
            mat.use_nodes = True
            bc.data.materials.append(mat)
        
        bc = bpy.context.scene.objects[name]
        bc_coll = BPH.FindCollectionForItem(bc)
        if bc_coll != coll:
            coll.objects.link(bc)
            bc_coll.objects.unlink(bc)
        bc.select_set(False)

        return bc, created
    
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

    def setColorValue(self, value, color):
        value[0] = color.r
        value[1] = color.g
        value[2] = color.b
        value[3] = 1
        if color.a != 1:
            self.transmission(1)
            #value[0] = 1
            #value[1] = 1
            #value[2] = 1
            #value[3] = 1
    
    def fill(self, color):
        if color:
            if isinstance(color, Gradient):
                self.fill(color.stops[0][0])
            else:
                #print("FILL>>>>>", self.tag, color)
                bsdf = self.bsdf()
                dv = bsdf.inputs[0].default_value
                self.setColorValue(dv, color)
    
    def stroke(self, weight=1, color=None, dash=None):
        if weight and color and color.a > 0:
            #print("STROKE>>>", self.tag, weight, color)
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
    
    def subsurface(self, amount=0.01):
        self.bsdf().inputs[1].default_value = amount
        return self

    def emission(self, color=None):
        if color is not None:
            self.setColorValue(self.bsdf().inputs[17].default_value, normalize_color(color))
        return self
    
    def image(self, path):
        mat = self.materials()[0]
        bsdf = self.bsdf()
        if "Image Texture" in mat.node_tree.nodes:
            imgtex = mat.node_tree.nodes["Image Texture"]
        else:
            imgtex = mat.node_tree.nodes.new("ShaderNodeTexImage")
            mat.node_tree.links.new(bsdf.inputs["Base Color"], imgtex.outputs["Color"])
        imgtex.image = bpy.data.images.load(path)
        return self
    
    def convertToMesh(self):
        self.bez.select_set(True)
        bpy.ops.object.convert(target="MESH")
        self.bez.select_set(False)
        return self
    
    def solidify(self, thickness=1):
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = self.bez
        self.bez.select_set(True)
        if "Solidify" not in self.bez.modifiers:
            bpy.ops.object.modifier_add(type="SOLIDIFY")
        self.bez.modifiers["Solidify"].thickness = thickness
        self.bez.select_set(False)
        bpy.context.view_layer.objects.active = None
        return self
    
    def applyModifier(self):
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = self.bez
        self.bez.select_set(True)
        bpy.ops.object.modifier_apply(apply_as="DATA")
        self.bez.select_set(False)
        bpy.context.view_layer.objects.active = None
        return self
    
    def rotate(self, x=None, y=None, z=None):
        if x is not None:
            self.bez.rotation_euler[0] = math.radians(x)
        if y is not None:
            self.bez.rotation_euler[1] = math.radians(y)
        if z is not None:
            self.bez.rotation_euler[2] = math.radians(z)
        return self
    
    def locate(self, x=None, y=None, z=None):
        if x is not None:
            self.bez.location[0] = x
        if y is not None:
            self.bez.location[1] = y
        if z is not None:
            self.bez.location[2] = z
        return self
    
    def draw(self, collection, style=None, scale=0.01, cyclic=True, dn=False, plane=False):
        if plane:
            self.bez, self.created = BPH.Primitive("Plane", collection, self.tag, dn=dn, container=self.dat.getFrame().scale(scale))
        else:
            self.bez, self.created = BPH.Primitive("Bezier", collection, self.tag, dn=dn)
            self.bez.data.fill_mode = "BOTH"
            self.record(self.dat.copy().removeOverlap().scale(scale, point=False))
            self.drawOnBezierCurve(self.bez.data, cyclic=cyclic)
        for attrs, attr in self.findStyledAttrs(style):
            self.applyDATAttribute(attrs, attr)
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
