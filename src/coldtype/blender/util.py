import bpy, json
from pathlib import Path


def find_sequence():
    from coldtype.blender import b3d_sequencer, b3d_animation

    rs = bpy.app.driver_namespace.get("_coldtypes", [])
    sq = None
    for r in rs:
        if isinstance(r, b3d_sequencer) or isinstance(r, b3d_animation):
            sq = r
    return sq


def remote(command, args=None, sq=None):
    #print("REMOTE", command, args, sq)
    if sq is None:
        sq = find_sequence()
    input_command_file = bpy.app.driver_namespace["_coldtype_command_input_file"]
    (Path(input_command_file)
        .expanduser()
        .write_text(json.dumps(dict(
            action=command if isinstance(command, str) else command.value,
            args=args,
            filepath=str(sq.filepath)))))
    return sq