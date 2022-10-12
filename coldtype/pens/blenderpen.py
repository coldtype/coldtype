from contextlib import contextmanager
from coldtype.geometry import Rect, Edge, Point
from coldtype.beziers import CurveCutter, raise_quadratic
from coldtype.pens.drawablepen import DrawablePenMixin
from fontTools.pens.basePen import BasePen
from coldtype.color import Gradient, Color, normalize_color
from coldtype.blender.fluent import BpyObj

import math
import random
try:
    # Blender-specific things
    import bpy
    from mathutils import Vector, Matrix
except:
    #print(">>> Not a blender environment")
    pass


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

    def CheckExists(name, dn=False):
        if dn and name in bpy.context.scene.objects:
            obj = bpy.context.scene.objects[name]
            bpy.data.objects.remove(obj, do_unlink=True)
            return False
        return name in bpy.context.scene.objects
    
    def AddOrFind(name, add_fn, dn=False):
        if dn and name in bpy.context.scene.objects:
            obj = bpy.context.scene.objects[name]
            bpy.data.objects.remove(obj, do_unlink=True)
            
        if name not in bpy.context.scene.objects:
            add_fn()
            bc = bpy.context.active_object
            bc.name = name
            return bc
        else:
            return bpy.context.scene.objects[name]

    def Primitive(_type, coll, name, dn=False, container=None, material="ColdtypeDefault", cyclic=True):
        created = False
        
        if dn: #and name in bpy.context.scene.objects:
            # obj = bpy.context.scene.objects[name]
            # bpy.data.objects.remove(obj)

            for m in bpy.data.objects:
                if name in m.name:
                    bpy.data.objects.remove(m)

            for m in bpy.data.meshes:
                if name in m.name:
                    bpy.data.meshes.remove(m)
            
            for m in bpy.data.materials:
                if name in m.name:
                    bpy.data.materials.remove(m)

        if name not in bpy.context.scene.objects:
            created = True
            if _type == "Bezier":
                bpy.ops.curve.primitive_bezier_curve_add()
            elif _type == "plane":
                bpy.ops.mesh.primitive_plane_add()
            elif _type == "cube":
                bpy.ops.mesh.primitive_cube_add()
            bc = bpy.context.object
            bc.name = name
            bc.data.name = name
            #name = bc.name
            
            if _type == "Bezier":
                if cyclic:
                    bc.data.dimensions = "2D"
                    bc.data.fill_mode = "BOTH"
                    bc.data.extrude = 0.1
                else:
                    bc.data.dimensions = "3D"
            elif _type == "plane":
                if container:
                    bc.scale[0] = container.w/2
                    bc.scale[1] = container.h/2
                    bc.location[0] = container.x + container.w/2
                    bc.location[1] = container.y + container.h/2
                    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
                    bpy.ops.object.transform_apply()
            elif _type == "cube":
                if container:
                    bc.scale[0] = container.w/2
                    bc.scale[1] = container.h/2
                    bc.scale[2] = 0.1

                    bc.location[0] = container.x + container.w/2
                    bc.location[1] = container.y + container.h/2
                    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
                    bpy.ops.object.transform_apply()
            
            if material:
                if material == "auto":
                    mat = bpy.data.materials.new(f"Material_{name}")
                    mat.use_nodes = True
                    bc.data.materials.append(mat)
        
        bc = bpy.context.scene.objects[name]
        bc_coll = BPH.FindCollectionForItem(bc)
        if bc_coll != coll:
            coll.objects.link(bc)
            bc_coll.objects.unlink(bc)
        bc.select_set(False)

        bc.data.name = name
        #print(bc.name, bc.data.name)
        return bc, created
    
    def Vector(pt, z=0):
        x, y = pt
        return Vector((x, y, z))


class BlenderPen(BpyObj, DrawablePenMixin, BasePen):
    def __init__(self, dat):
        super().__init__(None)
        self.dat = dat
        tag = self.dat.tag()
        self._material = None
        if tag is None:
            raise Exception("BlenderPen pens must be tagged")
        self.tag = tag
    
    def record(self, dat):
        self.set_origin(0, 0, 0)
        self._spline = None
        self.splines = []
        self._value = []
        dat.replay(self)
        if self._spline and len(self._spline) > 0 and self._spline not in self.splines:
            self.splines.append(self._spline)
        x, y = self.dat.ambit().pc
        #self.set_origin(x/100, y/100, 0)

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
        return self.obj.data.materials

    def bsdf(self):
        if self._material:
            try:
                return self.materials()[0].node_tree.nodes["Principled BSDF"]
            except:
                return None
    
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
        if not self._material == "auto" or not self.bsdf():
            return
        if color:
            if isinstance(color, Gradient):
                self.fill(color.stops[0][0])
            else:
                #print("FILL>>>>>", self.tag, color)
                bsdf = self.bsdf()
                dv = bsdf.inputs[0].default_value
                self.setColorValue(dv, color)
    
    def stroke(self, weight=1, color=None, dash=None, miter=None):
        if not self._material == "auto" or not self.bsdf():
            return
        if weight and color and color.a > 0:
            #print("STROKE>>>", self.tag, weight, color)
            self.obj.data.fill_mode = "NONE"
            if isinstance(color, Gradient):
                pass
            else:
                self.fill(color)
            
    def extrude(self, amount=0.1):
        self.obj.data.extrude = amount
        return self
    
    def bevel(self, depth=0.02):
        self.obj.data.bevel_depth = depth
        return self
    
    def specular(self, amount=0.5):
        if not self._material == "auto" or not self.bsdf():
            return
        self.bsdf().inputs[7].default_value = amount
        return self
    
    def metallic(self, amount=1):
        if not self._material == "auto" or not self.bsdf():
            return
        self.bsdf().inputs[6].default_value = amount
        return self
    
    def roughness(self, amount=0.5):
        if not self._material == "auto" or not self.bsdf():
            return
        self.bsdf().inputs[9].default_value = amount
        return self
    
    def transmission(self, amount=1):
        if not self._material == "auto" or not self.bsdf():
            return
        self.bsdf().inputs[15].default_value = amount
        return self

    def emission(self, color=None, strength=1):
        if not self._material == "auto" or not self.bsdf():
            return
        if color is not None:
            self.setColorValue(self.bsdf().inputs[17].default_value, normalize_color(color))
            self.bsdf().inputs[18].default_value = strength
        return self
    
    def image(self, src=None, opacity=1, rect=None, pattern=True):
        mat = self.materials()[0]
        bsdf = self.bsdf()
        if "Image Texture" in mat.node_tree.nodes:
            imgtex = mat.node_tree.nodes["Image Texture"]
        else:
            imgtex = mat.node_tree.nodes.new("ShaderNodeTexImage")
            mat.node_tree.links.new(bsdf.inputs["Base Color"], imgtex.outputs["Color"])
        imgtex.image = bpy.data.images.load(str(src))
        return self
    
    def at_frame(self, frame, path, value=None):
        bpy.data.scenes[0].frame_set(frame)
        if value is not None:
            if callable(value):
                value(self)
            else:
                exec(f"self.obj.{path} = {value}")
        self.obj.keyframe_insert(data_path=path)
        return self
        #setattr(self.obj, path, value)

    def hide(self, hide=True):
        self.obj.hide_viewport = hide
        self.obj.hide_render = hide
        return self
    
    def set_visibility_at_frame(self, frame, visibility):
        bpy.data.scenes[0].frame_set(frame)
        self.hide(not visibility)
        self.obj.keyframe_insert(data_path="hide_render")
        self.obj.keyframe_insert(data_path="hide_viewport")
        return self
    
    def show_on_frame(self, frame):
        self.set_visibility_at_frame(0, False)
        self.set_visibility_at_frame(frame, True)
        self.set_visibility_at_frame(frame+1, False)
        return self
    
    def show_at_frame(self, frame):
        self.set_visibility_at_frame(0, False)
        self.set_visibility_at_frame(frame-1, False)
        self.set_visibility_at_frame(frame, True)
        return self
    
    def make_invisible(self):
        self.obj.cycles_visibility.camera = False
        self.obj.cycles_visibility.diffuse = False
        self.obj.cycles_visibility.glossy = False
        self.obj.cycles_visibility.transmission = False
        self.obj.cycles_visibility.scatter = False
        self.obj.cycles_visibility.shadow = False
        return self
    
    def convert_to_mesh(self):
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.object.convert(target="MESH")
        self.obj.select_set(False)
        bpy.context.view_layer.objects.active = None
        return self

    convertToMesh = convert_to_mesh
    
    def remesh_smooth(self, octree_depth=7, smooth=False):
        with self.obj_selected() as o:
            if "Remesh" not in o.modifiers:
                bpy.ops.object.modifier_add(type="REMESH")
            rm = o.modifiers["Remesh"]
            rm.mode = "SMOOTH"
            rm.octree_depth = octree_depth
            rm.use_remove_disconnected = False
            rm.use_smooth_shade = smooth
        return self
    
    def cloth(self, pressure=5):
        with self.obj_selected() as o:
            bpy.ops.object.modifier_add(type='CLOTH')
            cl = o.modifiers["Cloth"]
            cl.settings.effector_weights.gravity = 0
            cl.settings.use_pressure = True
            cl.settings.uniform_pressure_force = pressure
            cl.settings.collision_settings.use_self_collision = True
        return self
    
    def apply_transform(self,
        location=True,
        rotation=True,
        scale=True,
        properties=True
        ):
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = self.obj
        
        self.obj.select_set(True)
        bpy.ops.object.transform_apply(location=location,
            rotation=rotation,
            scale=scale,
            properties=properties)
        self.obj.select_set(False)

        bpy.context.view_layer.objects.active = None
        return self

    def with_origin(self, xyz, fn):
        if xyz == "C":
            pc = self.dat.ambit().pc
            xyz = (pc.x/100, pc.y/100, 0)
        self.set_origin(*xyz)
        fn(self)
        self.set_origin(0, 0, 0)
        return self

    def center_origin(self):
        c = self.dat.ambit().pc
        self.locate_relative(x=-c.x/100, y=-c.y/100)
        
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = self.obj
        
        self.obj.select_set(True)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        self.obj.select_set(False)

        bpy.context.view_layer.objects.active = None

        self.locate_relative(x=+c.x/100, y=+c.y/100)
        return self
    
    def draw(self, collection, style=None, scale=0.01, cyclic=True, dn=False, primitive=None, material="auto"):
        self._material = material

        if primitive is not None:
            self.obj, self.created = BPH.Primitive(primitive, collection, self.tag, dn=dn, material=material, container=self.dat.ambit().scale(scale))
        else:
            self.obj, self.created = BPH.Primitive("Bezier", collection, self.tag, dn=dn, material=material, cyclic=cyclic)

            if cyclic:
                self.obj.data.fill_mode = "BOTH"
            self.origin_to_cursor()
            
            if cyclic:
                self.record(self.dat.copy().removeOverlap().scale(scale, point=False))
            else:
                self.record(self.dat.copy().scale(scale, point=False))
            
            try:
                self.draw_on_bezier_curve(self.obj.data, cyclic=cyclic)
            except:
                pass
        
        if material and material != "auto":
            try:
                mat = bpy.data.materials[material]
            except KeyError:
                mat = bpy.data.materials.new(material)
                mat.use_nodes = True
                
            self.obj.data.materials.clear()
            self.obj.data.materials.append(mat)
        
        for attrs, attr in self.findStyledAttrs(style):
            self.applyDATAttribute(attrs, attr)

        return self

    def draw_on_bezier_curve(self, bez, cyclic=True):
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

    def noop(self, *args, **kwargs):
        return self

class BlenderPenCube(BlenderPen):
    def extrude(self, amount=0.1, apply=False):
        with self.obj_selected():
            self.obj.scale[2] = amount*10
            if apply:
                bpy.ops.object.transform_apply()
        return self