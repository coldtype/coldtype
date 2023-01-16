import math, time

from pathlib import Path
from typing import Callable
from contextlib import contextmanager

from coldtype.runon.path import P
from coldtype.runon.runon import Runon
from coldtype.timing.timeline import Timeline
from coldtype.geometry import Rect
from coldtype.color import Gradient, normalize_color
from coldtype.renderable.animation import animation

try:
    import bpy
    from mathutils import Vector, Euler
except ImportError:
    bpy = None
    pass

# TODO easy, chainable interface for
# blender objects (could be a separate library)

def set_b3d_color(value, color):
    color = normalize_color(color)
    value[0] = color.r
    value[1] = color.g
    value[2] = color.b
    value[3] = 1

class _Chainable():
    def noop(self):
        return self
    
    def op(self, fn):
        fn(self)
        return self
    
    def data(self, key=None, default=None, **kwargs):
        if not hasattr(self, "_data"):
            self._data = {}

        if key is None and len(kwargs) > 0:
            for k, v in kwargs.items():
                self._data[k] = v
            return self
        elif key is not None:
            return self._data.get(key, default)
        else:
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
    
    def timeline(self, t:Timeline, resetFrame=None, output=None, version=None):
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
        
        if output:
            output = Path(output)
            if output.is_file():
                folder = output.stem
                if version:
                    folder = f"{output.stem}_{version}"
                
                output = output.parent / "renders" / folder / f"{folder}_"
            
            self.scene.render.filepath = str(output)

        return self
    
    def cycles(self, samples=16, denoiser=False, canvas:Rect=None):
        self.scene.render.engine = "CYCLES"

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
    
    render_settings = cycles
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
    
    def background(self, color):
        bg = bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value
        set_b3d_color(bg, color)
        return self


class BpyCollection(_Chainable):
    @staticmethod
    def Find(tag, create=True, parent=None):
        if "/" in tag:
            if tag.startswith("/"):
                parentTag = "Coldtype"
                tag = tag[1:]
            else:
                parentTag, tag = tag.split("/")
            parent = BpyCollection.Find(parentTag, create=create)

        bc = BpyCollection()
        c = None

        if tag not in bpy.data.collections:
            if create:
                c = bpy.data.collections.new(tag)
                if parent:
                    if isinstance(parent, BpyCollection):
                        parent = parent.c
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


class BpyMaterial():
    def __init__(self, material):
        self.m = material
    
    def Find(tag, create=True, use_nodes=True):
        if not isinstance(tag, str):
            return BpyMaterial(tag)

        try:
            m = bpy.data.materials[tag]
            return BpyMaterial(m)
        except KeyError:
            if create:
                m = bpy.data.materials.new(tag)
                m.use_nodes = use_nodes
                return BpyMaterial(m)
        
        return None

    def bsdf(self):
        return self.m.node_tree.nodes["Principled BSDF"]
    
    def setColorValue(self, value, color):
        value[0] = color.r
        value[1] = color.g
        value[2] = color.b
        value[3] = 1
        if color.a != 1:
            self.transmission(1)

    def f(self, color):
        if isinstance(color, Gradient):
            return self.f(color.stops[0][0])
        else:
            color = normalize_color(color)

        bsdf = self.bsdf()
        if bsdf:
            dv = bsdf.inputs[0].default_value
            self.setColorValue(dv, color)
        
        return self
    
    fill = f
    
    def specular(self, amount=0.5):
        self.bsdf().inputs[7].default_value = amount
        return self
    
    def metallic(self, amount=1):
        self.bsdf().inputs[6].default_value = amount
        return self
    
    def roughness(self, amount=0.5):
        self.bsdf().inputs[9].default_value = amount
        return self
    
    def transmission(self, amount=1):
        self.bsdf().inputs[17].default_value = amount
        return self

    def emission(self, color, strength=1):
        self.setColorValue(self.bsdf().inputs[19].default_value, normalize_color(color))
        self.bsdf().inputs[20].default_value = strength
        return self
    
    def animation(self, anim:animation, start=0):
        src = anim.pass_path(start)
        tl = anim.timeline
        return self.image(src, timeline=tl)
    
    def image(self, src=None, opacity=1, rect=None, pattern=True, alpha=True, timeline:Timeline=None):
        bsdf = self.bsdf()
        
        if "Image Texture" in self.m.node_tree.nodes:
            tex = self.m.node_tree.nodes["Image Texture"]
        else:
            tex = self.m.node_tree.nodes.new("ShaderNodeTexImage")
            self.m.node_tree.links.new(bsdf.inputs["Base Color"], tex.outputs["Color"])
            if alpha:
                self.m.node_tree.links.new(bsdf.inputs["Alpha"], tex.outputs["Alpha"])
            
            bx, by = bsdf.location
            tex.location = (bx - 320, by)
        
        found = False

        for img in bpy.data.images:
            if src.name in img.name:
                found = True
                img.reload()

        if not found or not tex.image:
            tex.image = bpy.data.images.load(str(src))
        
        if timeline is not None:
            tex.image.source = "SEQUENCE"
            tex.image_user.frame_duration = timeline.duration
            tex.image_user.frame_start = 0
            tex.image_user.frame_offset = -1
            tex.image_user.use_cyclic = True
            tex.image_user.use_auto_refresh = True

        return self


class BpyGroup(Runon):
    def yields_wrapped(self):
        return False
    
    @staticmethod
    def Curves(pens:P, prefix=None, collection=None, cyclic=True, fill=True, tx=0, ty=0):
        curves = BpyGroup()

        def walker(p:P, pos, data):
            if pos == 0:
                name = None
                if prefix:
                    name = prefix + "_" + ".".join([str(s) for s in data["idx"]])
                curves.append(BpyObj.Curve(name=name, collection=collection).draw(p, cyclic=cyclic, fill=fill, tx=tx, ty=ty))
        
        pens.walk(walker)
        return curves


class BpyObj(_Chainable):
    def __init__(self, dat=None) -> None:
        self.eo = None

    @staticmethod
    def Find(tag):
        bobj = BpyObj()
        
        if isinstance(tag, bpy.types.Object):
            bobj.obj = tag
        else:
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
        if collection is None:
            collection = "Coldtype"
        
        if collection == "Global":
            collection = None

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
    def Empty(name=None, collection=None) -> "BpyObj":
        bpy.ops.object.empty_add(type="PLAIN_AXES")
        return BpyObj.Primitive(name, collection)

    @staticmethod
    def Cube(name=None, collection=None) -> "BpyObj":
        bpy.ops.mesh.primitive_cube_add()
        return BpyObj.Primitive(name, collection)

    @staticmethod
    def Plane(name=None, collection=None) -> "BpyObj":
        bpy.ops.mesh.primitive_plane_add()
        return BpyObj.Primitive(name, collection)
    
    @staticmethod
    def Curve(name=None, collection=None) -> "BpyObj":
        bpy.ops.curve.primitive_bezier_curve_add()
        bo = BpyObj.Primitive(name, collection)
        return bo
    
    @staticmethod
    def UVSphere(name=None, collection=None) -> "BpyObj":
        bpy.ops.mesh.primitive_uv_sphere_add()
        return BpyObj.Primitive(name, collection)
    
    @staticmethod
    def Monkey(name=None, collection=None) -> "BpyObj":
        bpy.ops.mesh.primitive_monkey_add()
        return BpyObj.Primitive(name, collection)
    
    def select(self, selected=True):
        self.obj.select_set(selected)
        return self
    
    def collect(self, collectionTag, create=True, unlink=True, parent=None):
        bc = BpyCollection.Find(collectionTag, create=create, parent=parent)
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
    
    def delete(self):
        if not self.obj: return None
        
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.object.delete()
        return None
    
    def set_visibility_at_frame(self, frame, visibility, scene=None):
        if scene is None:
            scene = bpy.data.scenes[0]
        scene.frame_set(frame)
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

#region Basic transformations

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

#endregion Basic transformations

#region Materials

    def material(self, tag, modFn:Callable[[BpyMaterial], BpyMaterial]=None, clear=False):
        if clear:
            self.obj.data.materials.clear()

        bm = BpyMaterial.Find(tag, create=True, use_nodes=True)

        if bm.m.name not in self.obj.data.materials:
            self.obj.data.materials.append(bm.m)
        
        if bm and modFn:
            modFn(bm)

        return self

#endregion Materials

#region Convenience Methods

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
    
#endregion Convenience Methods
    
#region Modifiers
    
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

#endregion Modifiers

#region Curve functions

    def draw(self, path:P, cyclic=True, fill=True, tx=0, ty=0, set_origin=True, clear=True) -> "BpyObj":
        if len(path) > 0:
            path = path.pen()
        
        path = path.removeOverlap()
        
        amb = path.ambit(tx=tx, ty=ty)

        origin = amb.x + amb.w/2, amb.y + amb.h/2

        path = path.q2c()

        #czOffset = path.data("centerZeroOffset")

        splines = []
        spline = None
        value = []

        for mv, pts in path._val.value:
            if mv == "moveTo":
                p = pts[0]
                if spline and len(spline) > 0 and spline not in splines:
                    splines.append(spline)
                spline = []
                value.append([p])
                spline.append(["BEZIER", "start", [p, p, p]])

            elif mv == "lineTo":
                p = pts[0]
                value.append([p])
                spline.append(["BEZIER", "curve", [p, p, p]])

            elif mv == "curveTo":
                p1, p2, p3 = pts
                spline[-1][-1][-1] = p1
                value.append([p1, p2, p3])
                spline.append(["BEZIER", "curve", [p2, p3, p3]])

            # elif mv == "qCurveTo":
            #     p1, p2 = pts
            #     start = value[-1][-1]
            #     q1, q2, q3 = raise_quadratic(start, (p1[0], p1[1]), (p2[0], p2[1]))
            #     spline[-1][-1][-1] = q1
            #     value.append([q1, q2, q3])
            #     spline.append(["BEZIER", "curve", [q2, q3, q3]])

            elif mv == "closePath":
                if spline and len(spline) > 0 and spline not in splines:
                    splines.append(spline)
                    spline = None
                spline = None
        
            else:
                raise Exception("blender curve unhandled curve type", mv)
            
            if spline and len(spline) > 0 and spline not in splines:
                splines.append(spline)

        bez = self.obj.data

        def zvec(pt, z=0):
            x, y = pt
            return Vector((x, y, z))

        for spline in reversed(bez.splines): # clear existing splines
            bez.splines.remove(spline)

        for spline_data in splines:
            bez.splines.new('BEZIER')
            spline = bez.splines[-1]
            spline.use_cyclic_u = cyclic
            for i, (t, style, pts) in enumerate(spline_data):
                l, c, r = pts
                if i > 0:
                    spline.bezier_points.add(1)
                pt = spline.bezier_points[-1]
                pt.co = zvec(c)
                pt.handle_left = zvec(l)
                pt.handle_right = zvec(r)
        
        if fill:
            bez.dimensions = "2D"
            bez.fill_mode = "BOTH"

        if set_origin:
            self.setOrigin(*origin, 0)

        return self

    def extrude(self, amount=0.1) -> "BpyObj":
        self.obj.data.extrude = amount
        return self
    
    def bevel(self, depth=0.02) -> "BpyObj":
        self.obj.data.bevel_depth = depth
        return self
    
    def convertToMesh(self) -> "BpyObj":
        with self.obj_selected():
            bpy.ops.object.convert(target="MESH")
        return self

#endregion

