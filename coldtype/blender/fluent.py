from coldtype.sh import context
from contextlib import contextmanager
try:
    import bpy
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
    
    @contextmanager
    def rigidbody(self, speed=1):
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
        return self


class BpyObj():
    def __init__(self, tag):
        try:
            self.obj = bpy.data.objects[tag]
        except KeyError:
            self.obj = None
    
    @contextmanager
    def obj_selected(self):
        if not self.obj:
            yield
            return
        
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        yield
        self.obj.select_set(False)
        bpy.context.view_layer.objects.active = None
    
    @contextmanager
    def obj_selection_sequence(self, other_tag):
        other = BpyObj(other_tag)
        if not self.obj or not other.obj:
            yield None, None
            return

        bpy.context.view_layer.objects.active = None
        self.obj.select_set(True)
        other.obj.select_set(True)
        bpy.context.view_layer.objects.active = other.obj
        yield self.obj, other.obj
        bpy.ops.object.parent_set(type="OBJECT")
        
        self.bez.select_set(False)
        other.obj.select_set(False)
        bpy.context.view_layer.objects.active = None
        return self

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