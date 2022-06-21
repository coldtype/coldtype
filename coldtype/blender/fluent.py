from coldtype.time.timeline import Timeline
from coldtype.geometry import Rect
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

class _Chainable():
    def noop(self):
        return self

class BpyWorld(_Chainable):
    def __init__(self, scene="Scene"):
        try:
            self.scene = bpy.data.scenes[scene]
        except KeyError:
            self.scene = None
    
    def deselect_all(self):
        bpy.ops.object.select_all(action='DESELECT')
        return self
    
    deselectAll = deselect_all
    
    def delete_previous(self, collection="Coldtype", keep=[], materials=True, curves=True, meshes=True, objects=True):
        self.deselect_all()

        BpyCollection.Find(collection, create=False).delete_hierarchy()
        self.deleteOrphans(keep=keep, materials=materials, curves=curves, meshes=meshes, objects=objects)
        return self
    
    deletePrevious = delete_previous

    def deleteOrphans(self, keep=[], **kwargs):
        from bpy import data as D
        
        props = ["curves", "meshes", "materials", "objects"]
        for x in range(2):
            for c in D.collections:
                if ("RigidBodyWorld" in c.name or c.users == 0) and c.name not in keep:
                    bpy.data.collections.remove(c)

            for p in props:
                if kwargs.get(p):
                    for block in getattr(D, p):
                        if block.users == 0 and block.name not in keep:
                            getattr(D, p).remove(block)
        
        return self
    
    def timeline(self, t:Timeline, resetFrame=None):
        self.scene.frame_start = 0
        self.scene.frame_end = t.duration-1

        if isinstance(t.fps, float):
            self.scene.render.fps = round(t.fps)
            self.scene.render.fps_base = 1.001
        else:
            self.scene.render.fps = t.fps
            self.scene.render.fps_base = 1
        
        if resetFrame is not None:
            self.scene.frame_set(resetFrame)

        return self
    
    def render_settings(self, samples=16, denoiser=False, canvas:Rect=None):
        if samples > 0:
            self.scene.cycles.samples = samples
        
        if denoiser:
            self.scene.cycles.denoiser = "OPENIMAGEDENOISE" if denoiser == True else denoiser
            self.scene.cycles.use_denoising = True
        else:
            if denoiser is False:
                self.scene.cycles.use_denoising = False
        
        if canvas is not None:
            self.scene.render.resolution_x = canvas.w
            self.scene.render.resolution_y = canvas.h

        return self
    
    renderSettings = render_settings
    
    @contextmanager
    def rigidbody(self, speed=1, frame_end=250):
        try:
            bpy.ops.rigidbody.world_remove()
            yield
        except RuntimeError as e:
            print("! Failed to reset rigidbody !", e)
            yield
        
        if self.scene:
            try:
                bpy.ops.rigidbody.world_add()
            except RuntimeError:
                pass
            rw = self.scene.rigidbody_world
            if rw:
                rw.time_scale = speed
                rw.point_cache.frame_end = frame_end
        return self
    
    def insertKeyframe(self, frame, path, value=None):
        bpy.data.scenes[0].frame_set(frame)
        if value is not None:
            if callable(value):
                value(self)
            else:
                exec(f"self.scene.{path} = {value}")
        self.scene.keyframe_insert(data_path=path)
        return self
        #setattr(self.obj, path, value)


class BpyCollection(_Chainable):
    @staticmethod
    def Find(tag, create=True, parent=None):
        bc = BpyCollection()
        c = None

        if tag not in bpy.data.collections:
            if create:
                c = bpy.data.collections.new(tag)
                if parent:
                    parent.children.link(c)
                else:
                    bpy.context.scene.collection.children.link(c)
        
        c = bpy.data.collections.get(tag)
        bc.c = c
        return bc

        # try:
        #     bc.c = bpy.data.collections[tag]
        # except KeyError:
        #     if create:
        #         print("CREATING", tag)
        #         bc.c = bpy.data.collections.new(tag)
        #     else:
        #         bc.c = None
        # return bc

    def delete_hierarchy(self):
        if not self.c: return

        bpy.context.view_layer.objects.active = None
        for obj in self.c.objects:
            try:
                BpyObj.Find(obj.name).select()
            except Exception as e:
                print("deleteHierarchy failed to delete object:", obj.name, e)
        bpy.ops.object.delete()
        bpy.data.collections.remove(self.c)
        return None
    
    deleteHierarchy = delete_hierarchy


class BpyObj(_Chainable):
    def __init__(self, dat=None) -> None:
        self.eo = None

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
    
    @staticmethod
    def Primitive(name=None, collection="Coldtype") -> "BpyObj":
        created = bpy.context.object
        bobj = BpyObj()
        bobj.obj = created
        if collection:
            bobj.collect(collection)
        created.select_set(False)
        if name is not None:
            bobj.obj.name = name
        return bobj

    @staticmethod
    def Cube(name=None, collection="Coldtype") -> "BpyObj":
        bpy.ops.mesh.primitive_cube_add()
        return BpyObj.Primitive(name, collection)

    @staticmethod
    def Plane(name=None, collection="Coldtype") -> "BpyObj":
        bpy.ops.mesh.primitive_plane_add()
        return BpyObj.Primitive(name, collection)
    
    @staticmethod
    def UVSphere(name=None, collection="Coldtype") -> "BpyObj":
        bpy.ops.mesh.primitive_uv_sphere_add()
        return BpyObj.Primitive(name, collection)
    
    @staticmethod
    def Monkey(name=None, collection="Coldtype") -> "BpyObj":
        bpy.ops.mesh.primitive_monkey_add()
        return BpyObj.Primitive(name, collection)
    
    def select(self, selected=True):
        self.obj.select_set(selected)
        return self
    
    def collect(self, collectionTag, create=True, unlink=True):
        bc = BpyCollection.Find(collectionTag, create=create)
        bc.c.objects.link(self.obj)
        if unlink:
            for c in self.obj.users_collection:
                if c != bc.c:
                    c.objects.unlink(self.obj)
        return self
    
    @contextmanager
    def obj_selected(self, yield_self=False):
        if not self.obj:
            if yield_self:
                yield None
            else:
                yield
            return self
        
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        if yield_self:
            yield self
        else:
            yield
        self.obj.select_set(False)
        bpy.context.view_layer.objects.active = None
        return self
    
    objSelected = obj_selected
    
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
        
        try:
            self.obj.select_set(False)
        except ReferenceError:
            pass
        try:
            other.obj.select_set(False)
        except ReferenceError:
            pass
        bpy.context.view_layer.objects.active = None
        return self
    
    objSelectionSequence = obj_selection_sequence
    
    @contextmanager
    def all_vertices_selected(self):
        with self.obj_selected():
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            yield
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
        return self
    
    allVerticesSelected = all_vertices_selected
    
    @contextmanager
    def select_vertices(self, selector, keep_selected=False):
        with self.obj_selected():
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            for idx, v in enumerate(self.obj.data.vertices):
                if selector(v):
                    v.select = True
                else:
                    pass
            bpy.ops.object.mode_set(mode='EDIT')
            yield
            if not keep_selected:
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
        return self
    
    selectVertices = select_vertices
    
    def make_vertex_group(self, selector, name=None):
        with self.select_vertices(selector):
            bpy.ops.object.vertex_group_add()
            bpy.ops.object.vertex_group_assign()
            if name:
                self.obj.vertex_groups[-1].name = name
        return self
    
    makeVertexGroup = make_vertex_group
    
    def select_and_delete(self, select_mode, selector):
        with self.select_vertices(selector):
            bpy.ops.mesh.select_mode(type=select_mode)
            bpy.ops.mesh.delete(type=select_mode)
        return self
    
    selectAndDelete = select_and_delete

    def separateByLooseParts(self):
        with self.all_vertices_selected():
            bpy.ops.mesh.separate(type="LOOSE")
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
    
    # Manipulation Methods

    def vertex_group_all(self):
        with self.all_vertices_selected():
            bpy.ops.object.vertex_group_add()
            bpy.ops.object.vertex_group_assign()
        return self
    
    vertexGroupAll = vertex_group_all

    def addEmptyOrigin(self, collection="Coldtype"):
        bpy.ops.object.empty_add(type="PLAIN_AXES")
        bc = bpy.context.object
        bc.name = self.obj.name + "_EmptyOrigin"
        self.eo = bc
        BpyObj.Find(bc.name).collect(collection)
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
    
    applyTransform = apply_transform

    def applyScale(self):
        return self.applyTransform(location=False, rotation=False, scale=True, properties=False)

    def apply_modifier(self, name):
        with self.obj_selected():        
            #bpy.ops.object.modifier_set_active(modifier=name)
            bpy.ops.object.modifier_apply(modifier=name)
            self.obj.to_mesh(preserve_all_data_layers=True)
        return self
    
    applyModifier = apply_modifier

    def applyAllModifiers(self):
        with self.obj_selected():
            for mod in self.obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=mod.name)
                self.obj.to_mesh(preserve_all_data_layers=True)
        return self
    
    def origin_to_geometry(self):
        with self.obj_selected():
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        return self
    
    originToGeometry = origin_to_geometry
    
    def origin_to_cursor(self):
        with self.obj_selected():
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return self
    
    originToCursor = origin_to_cursor
    
    def set_origin(self, x, y, z):
        #saved_location = bpy.context.scene.cursor.location
        bpy.context.scene.cursor.location = Vector((x, y, z))
        with self.obj_selected():
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = Vector((0, 0, 0))
        return self
    
    setOrigin = set_origin
    
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
        
        if self.eo:
            (BpyObj.Find(self.eo.name)
                .locate_relative(x=x, y=y, z=z))
        return self
    
    locateRelative = locate_relative

    def scale(self, x=None, y=None, z=None):
        if x is not None:
            self.obj.scale[0] = x
        if y is not None:
            self.obj.scale[1] = y
        if z is not None:
            self.obj.scale[2] = z
        return self
    
    def addMaterial(self, material, clear=False):
        if not material:
           pass
        elif material == "auto":
            # auto material
            pass
        else:
            if isinstance(material, str):
                try:
                    mat = bpy.data.materials[material]
                except KeyError:
                    mat = bpy.data.materials.new(material)
                    mat.use_nodes = True
            else:
                mat = material
            
            if clear:
                self.obj.data.materials.clear()
            
            if mat.name not in self.obj.data.materials:
                self.obj.data.materials.append(mat)

        return self

        if material and material != "auto":
            try:
                mat = bpy.data.materials[material]
            except KeyError:
                mat = bpy.data.materials.new(material)
                mat.use_nodes = True
                
            self.obj.data.materials.clear()
            self.obj.data.materials.append(mat)

    # Convenience Methods

    def rigidbody(self,
        mode="active",
        animated=False,
        mesh=False,
        bounce=0,
        mass=1,
        bake=0,
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
            if bake:
                bpy.ops.rigidbody.bake_to_keyframes()
        
        return self
    
    # Modifiers
    
    def solidify(self, thickness=1):
        with self.obj_selected():
            bpy.ops.object.modifier_add(type="SOLIDIFY")
            m = self.obj.modifiers["Solidify"]
            m.thickness = thickness
        return self
    
    def remesh(self, octree_depth=7, smooth=False):
        with self.obj_selected():
            bpy.ops.object.modifier_add(type="REMESH")
            m = self.obj.modifiers["Remesh"]
            m.mode = "SHARP"
            m.octree_depth = octree_depth
            m.use_remove_disconnected = False
            m.use_smooth_shade = smooth
        return self
    
    def array(self, count=2, relative=(1, 0, 0), constant=(0.1, 0, 0)):
        with self.obj_selected():
            bpy.ops.object.modifier_add(type='ARRAY')
            m = self.obj.modifiers[-1]
            m.count = count
            
            if relative:
                m.use_relative_offset = True
                m.relative_offset_displace[0] = relative[0]
                m.relative_offset_displace[1] = relative[1]
                m.relative_offset_displace[2] = relative[2]
            else:
                m.use_relative_offset = False

            if constant:
                m.use_constant_offset = True
                m.constant_offset_displace[0] = constant[0]
                m.constant_offset_displace[1] = constant[1]
                m.constant_offset_displace[2] = constant[2]
            else:
                m.use_constant_offset = False
        return self
    
    def arrayX(self, count=2, relative=1, constant=0.1):
        return self.array(count=count, relative=(relative, 0, 0), constant=(constant, 0, 0))
    
    def arrayY(self, count=2, relative=-1, constant=-0.1):
        return self.array(count=count, relative=(0, relative, 0), constant=(0, constant, 0))
    
    def remove_doubles(self, threshold=0.01):
        with self.all_vertices_selected():
            bpy.ops.mesh.remove_doubles(threshold=threshold)
        return self
    
    removeDoubles = remove_doubles
    
    def smooth(self,
        factor=0.5,
        repeat=1,
        x=True,
        y=True,
        z=True
        ):
        with self.obj_selected():
            bpy.ops.object.modifier_add(type="SMOOTH")
            m = self.obj.modifiers["Smooth"]
            m.factor = factor
            m.iterations = repeat
            m.use_x = bool(x)
            m.use_y = bool(y)
            m.use_z = bool(z)
        return self
    
    def displace(self,
        strength=1,
        midlevel=0.5,
        texture=None,
        coords_object=None,
        direction="NORMAL",
        vertex_group=None
        ):
        with self.obj_selected():
            bpy.ops.object.modifier_add(type="DISPLACE")
            
            m = self.obj.modifiers["Displace"]
            m.strength = strength
            m.mid_level = midlevel
            m.direction = direction

            if texture and isinstance(texture, str):
                try:
                    t = bpy.data.textures[texture]
                    m.texture = t
                except KeyError:
                    bpy.ops.texture.new()
                    t = bpy.data.textures[len(bpy.data.textures)-1]
                    t.name = texture
                    t.type = "CLOUDS"
                    m.texture = t
            if coords_object:
                try:
                    m.texture_coords = "OBJECT"
                    m.texture_coords_object = bpy.data.objects[coords_object]
                except KeyError:
                    print("coords_object not found", coords_object)
            
            if vertex_group and isinstance(vertex_group, str):
                m.vertex_group = vertex_group
        return self
    
    def boolean(self, object):
        with self.obj_selected():
            bpy.ops.object.modifier_add(type="BOOLEAN")
            m = self.obj.modifiers["Boolean"]
            m.operation = "INTERSECT"
            try:
                m.object = bpy.data.objects[object]
            except KeyError:
                print("object for boolean not found", object)
        return self
    
    def shade_smooth(self):
        with self.obj_selected():
            bpy.ops.object.shade_smooth()
        return self
    
    shadeSmooth = shade_smooth
    
    def auto_smooth(self, angle=30):
        if angle is None:
            self.obj.data.use_auto_smooth = False
        else:
            self.obj.data.use_auto_smooth = True
            self.obj.data.auto_smooth_angle = math.radians(angle)
        return self
    
    autoSmooth = auto_smooth
    
    def subsurface(self):
        with self.obj_selected():
            bpy.ops.object.modifier_add(type="SUBSURF")
        return self
    
    def simpleDeform(self, method="BEND", angle=180, axis="Z", origin=None):
        with self.obj_selected():
            bpy.ops.object.modifier_add(type="SIMPLE_DEFORM")
            m = self.obj.modifiers["SimpleDeform"]
            m.deform_method = "BEND"
            m.deform_axis = axis
            m.angle = math.radians(angle)
            if origin:
                m.origin = bpy.data.objects[origin]
        return self
    
    def decimate_planar(self):
        with self.obj_selected():
            bpy.ops.object.modifier_add(type="DECIMATE")
            m = self.obj.modifiers["Decimate"]
            m.decimate_type = "DISSOLVE"
        return self
    
    decimatePlanar = decimate_planar