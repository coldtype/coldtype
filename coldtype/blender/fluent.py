from coldtype.time.timeline import Timeline
import math
from contextlib import contextmanager

try:
    import bpy
    from mathutils import Vector, Euler
except ImportError:
    bpy = None
    pass

# TODO easy, chainable interface for
# blender objects (could be a separate library)

class BpyWorld():
    def __init__(self, scene="Scene"):
        try:
            self.scene = bpy.data.scenes[scene]
        except KeyError:
            self.scene = None
    
    def deselect_all(self):
        bpy.ops.object.select_all(action='DESELECT')
        return self
    
    def delete_previous(self, collection="Coldtype"):
        self.deselect_all()
        BpyCollection.Find(collection).delete_hierarchy()
        return self
    
    def timeline(self, t:Timeline):
        self.scene.frame_start = 0
        self.scene.frame_end = t.duration-1

        if isinstance(t.fps, float):
            self.scene.render.fps = round(t.fps)
            self.scene.render.fps_base = 1.001
        else:
            self.scene.render.fps = t.fps
            self.scene.render.fps_base = 1
        
        return self
    
    def render_settings(self, samples=16, denoiser=False):
        if samples > 0:
            self.scene.cycles.samples = samples
        
        if denoiser:
            self.scene.cycles.denoiser = "OPENIMAGEDENOISE" if denoiser == True else denoiser
            self.scene.cycles.use_denoising = True
        else:
            if denoiser is False:
                self.scene.cycles.use_denoising = False
        
        return self
    
    @contextmanager
    def rigidbody(self, speed=1, frame_end=250):
        try:
            bpy.ops.rigidbody.world_remove()
            yield
        except RuntimeError:
            print("Failed to reset rigidbody")
            yield
        
        if self.scene:
            rw = self.scene.rigidbody_world
            if rw:
                rw.time_scale = speed
                rw.point_cache.frame_end = frame_end
        return self


class BpyCollection():
    @staticmethod
    def Find(tag):
        bco = BpyCollection()
        try:
            bco.collection = bpy.data.collections[tag]
        except KeyError:
            bco.collection = None
        return bco

    def delete_hierarchy(self):
        if not self.collection: return

        bpy.context.view_layer.objects.active = None
        for obj in self.collection.objects:
            BpyObj.Find(obj.name).select()
        bpy.ops.object.delete()
        bpy.data.collections.remove(self.collection)
        return None


class BpyObj():
    @staticmethod
    def Find(tag):
        bobj = BpyObj()
        try:
            bobj.obj = bpy.data.objects[tag]
        except KeyError:
            bobj.obj = None
        return bobj
    
    @staticmethod
    def Norm(obj_or_tag):
        if isinstance(obj_or_tag, BpyObj):
            return obj_or_tag
        else:
            return BpyObj.Find(obj_or_tag)
    
    def select(self, selected=True):
        self.obj.select_set(selected)
        return self
    
    @contextmanager
    def obj_selected(self, yield_self=False):
        if not self.obj:
            if yield_self:
                yield None
            else:
                yield
            return
        
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        if yield_self:
            yield self
        else:
            yield
        self.obj.select_set(False)
        bpy.context.view_layer.objects.active = None
    
    @contextmanager
    def obj_selection_sequence(self, other_tag):
        other = BpyObj.Norm(other_tag)
        
        if not self.obj or not other.obj:
            yield None
            return

        bpy.context.view_layer.objects.active = None
        self.obj.select_set(True)
        other.obj.select_set(True)
        bpy.context.view_layer.objects.active = other.obj
        yield other
        bpy.ops.object.parent_set(type="OBJECT")
        
        self.obj.select_set(False)
        other.obj.select_set(False)
        bpy.context.view_layer.objects.active = None
        return self
    
    def parent(self, parent_tag, hide=False):
        with self.obj_selection_sequence(parent_tag) as o:
            bpy.ops.object.parent_set(type="OBJECT")
        if hide:
            with o.obj_selected():
                o.hide()
        return self
    
    def hide(self, hide=True):
        self.obj.hide_viewport = hide
        self.obj.hide_render = hide
        return self
    
    # Geometry Methods

    def rotate(self, x=None, y=None, z=None):
        if isinstance(x, Euler):
            self.obj.rotation_euler = x
            return self
        
        if x is not None:
            self.obj.rotation_euler[0] = math.radians(x)
        if y is not None:
            self.obj.rotation_euler[1] = math.radians(y)
        if z is not None:
            self.obj.rotation_euler[2] = math.radians(z)
        return self
    
    def apply_transform(self,
        location=True,
        rotation=True,
        scale=True,
        properties=True
        ):
        with self.obj_selected():
            bpy.ops.object.transform_apply(
                location=location,
                rotation=rotation,
                scale=scale,
                properties=properties)
        return self
    
    def origin_to_geometry(self):
        with self.obj_selected():
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        return self
    
    def origin_to_cursor(self):
        with self.obj_selected():
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return self
    
    def set_origin(self, x, y, z):
        #saved_location = bpy.context.scene.cursor.location
        bpy.context.scene.cursor.location = Vector((x, y, z))
        with self.obj_selected():
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = Vector((0, 0, 0))
        return self
    
    def locate(self, x=None, y=None, z=None):
        if isinstance(x, Vector):
            self.obj.location = x
            return self
        
        if x is not None:
            self.obj.location[0] = x
        if y is not None:
            self.obj.location[1] = y
        if z is not None:
            self.obj.location[2] = z
        return self
    
    def locate_relative(self, x=None, y=None, z=None):
        if x is not None:
            self.obj.location[0] = self.obj.location[0] + x
        if y is not None:
            self.obj.location[1] = self.obj.location[1] + y
        if z is not None:
            self.obj.location[2] = self.obj.location[2] + z
        return self

    # Convenience Methods

    def rigidbody(self,
        mode="active",
        animated=False,
        mesh=False,
        bounce=0,
        mass=1,
        deactivated=False,
        friction=0.5,
        linear_damping=0.04,
        angular_damping=0.1
        ):
        if not self.obj: return self
        
        with self.obj_selected():
            o = self.obj
            bpy.ops.rigidbody.object_add()
            if mesh:
                o.rigid_body.collision_shape = "MESH"
            o.rigid_body.type = mode.upper()
            o.rigid_body.kinematic = animated
            o.rigid_body.restitution = bounce
            o.rigid_body.mass = mass
            o.rigid_body.friction = friction
            o.rigid_body.linear_damping = linear_damping
            o.rigid_body.angular_damping = angular_damping
            if deactivated:
                o.rigid_body.use_deactivation = True
                o.rigid_body.use_start_deactivated = True
        
        return self