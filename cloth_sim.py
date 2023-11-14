import bpy
import os
import sys

import pip

pip.main(["install", "pandas", "--user"])
# sys.path.append("/Users/valkyrie/anaconda3/envs/cvp-1")
import pandas as pd


def purge_orphans():
    if bpy.app.version >= (3, 0, 0):
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True
        )
    else:
        # call purge_orphans() recursively until there are no more orphan data blocks to purge
        result = bpy.ops.outliner.orphans_purge()
        if result.pop() != "CANCELLED":
            purge_orphans()


def clean_scene():
    """
    Removing all of the objects, collection, materials, particles,
    textures, images, curves, meshes, actions, nodes, and worlds from the scene
    """
    if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.editmode_toggle()

    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    collection_names = [col.name for col in bpy.data.collections]
    for name in collection_names:
        bpy.data.collections.remove(bpy.data.collections[name])

    # in the case when you modify the world shader
    world_names = [world.name for world in bpy.data.worlds]
    for name in world_names:
        bpy.data.worlds.remove(bpy.data.worlds[name])
    # create a new world data block
    bpy.ops.world.new()
    bpy.context.scene.world = bpy.data.worlds["World"]

    purge_orphans()


def run_simulation(path):
    clean_scene()
    bpy.ops.import_scene.obj(filepath=path)
    bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="MEDIAN")
    object = bpy.context.scene.objects[0]
    print(object.location)
    object.modifiers.new("Colision_mod", "COLLISION")
    object.collision.use_culling = False

    # Cloth
    bpy.ops.mesh.primitive_plane_add(size=3, align="WORLD", location=(0, 0, 3))
    bpy.ops.object.shade_smooth()
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=30)
    bpy.ops.object.modifier_add(type="CLOTH")
    bpy.context.object.modifiers["Cloth"].collision_settings.use_self_collision = True
    bpy.context.object.modifiers["Cloth"].collision_settings.self_distance_min = 0.001
    bpy.context.object.modifiers["Cloth"].collision_settings.distance_min = 0.0015
    bpy.context.object.modifiers["Cloth"].settings.quality = 10
    bpy.context.object.modifiers["Cloth"].collision_settings.collision_quality = 10

    bpy.ops.object.modifier_add(type="SUBSURF")
    bpy.context.object.modifiers["Subdivision"].levels = 4
    bpy.context.object.modifiers["Subdivision"].render_levels = 4
    bpy.ops.object.editmode_toggle()

    #    #bpy.app.handlers.frame_change_pre.append(stop_playback)
    #    #bpy.ops.screen.animation_play()

    #    # assume we have a particle system
    #    #ps = ob.particle_systems[0]
    #    #pc = ps.point_cache

    #    ## match bake to animation
    #    #print(pc.frame_start, pc.frame_end)

    #    #bpy.ops.ptcache.bake({"point_cache": pc}, bake=True)
    #    #scene.frame_set(100)

    filename = path.split("/")[-1]
    export_path = f"/Users/valkyrie/Desktop/Workspace/Cvp-project1/cloth/{filename}"
    print(export_path)
    for frame_no in range(100):
        print("Running frame {}..".format(frame_no))
        bpy.context.scene.frame_set(frame_no + bpy.data.scenes["Scene"].frame_start)
    bpy.ops.export_scene.obj(filepath=export_path, use_materials=False)


def get_objects(annot):
    paths = annot["Path"]
    for obj_path in paths[0:3]:
        file_size = os.path.getsize(obj_path) / 1024**2
        if file_size < 5:
            print(f"Processing File: {obj_path}")
            run_simulation(obj_path)

        else:
            print(f"Skipping {obj_path}")


def main():
    annot = pd.read_csv("./annotations.csv")
    get_objects(annot)


# run_simulation("/Users/valkyrie/Desktop/Workspace/Cvp-project1/objects/23.obj")
if __name__ == "__main__":
    main()
