from contextlib import contextmanager

# TODO easy, chainable interface for
# blender objects (could be a separate library)

@contextmanager
def obj_selected(tag):
    try:
        obj = bpy.data.objects[tag]
    except KeyError:
        yield None
        return
    bpy.context.view_layer.objects.active = None
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    yield obj
    obj.select_set(False)
    bpy.context.view_layer.objects.active = None

def add_rigidbody(tag,
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
    with obj_selected(tag) as obj:
        if not obj:
            print("NO OBJ")
            return
        bpy.ops.rigidbody.object_add()
        if mesh:
            obj.rigid_body.collision_shape = "MESH"
        obj.rigid_body.type = mode.upper()
        obj.rigid_body.kinematic = animated
        obj.rigid_body.restitution = bounce
        obj.rigid_body.mass = mass
        obj.rigid_body.friction = friction
        obj.rigid_body.linear_damping = linear_damping
        obj.rigid_body.angular_damping = angular_damping
        if deactivated:
            obj.rigid_body.use_deactivation = True
            obj.rigid_body.use_start_deactivated = True