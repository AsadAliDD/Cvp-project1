import bpy


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
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN') 
    object=bpy.context.scene.objects[0]
    print(object.location)
    object.modifiers.new("Colision_mod",'COLLISION')
    
    
    


    #Cloth
    bpy.ops.mesh.primitive_plane_add(size=2, align='WORLD', location=(0, 0, 3))
    bpy.ops.object.shade_smooth()
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=30)
    bpy.ops.object.modifier_add(type='CLOTH')
    bpy.context.object.modifiers["Cloth"].collision_settings.use_self_collision = True
    bpy.context.object.modifiers["Cloth"].collision_settings.self_distance_min = 0.001
    bpy.context.object.modifiers["Cloth"].collision_settings.distance_min = 0.001
    bpy.context.object.modifiers["Cloth"].settings.quality = 10
    bpy.context.object.modifiers["Cloth"].collision_settings.collision_quality = 10

    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = 2
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

    filename=path.split('\\')[-1]
    for frame_no in range(100):
        print ('Running frame {}..'.format(frame_no))
        bpy.context.scene.frame_set(frame_no + bpy.data.scenes["Scene"].frame_start)
    bpy.ops.export_scene.obj(filepath=filename,use_materials=False)
    

run_simulation('\\\\wsl.localhost\\Ubuntu\\home\\valkyrie\\Workspace\\CVP\\Cvp-project1\\objects\\150.obj')
run_simulation('\\\\wsl.localhost\\Ubuntu\\home\\valkyrie\\Workspace\\CVP\\Cvp-project1\\objects\\160.obj')








#print (set(bpy.context.scene.objects))


#object=bpy.context.scene.objects[0]
#print(object)
#print(object.location)
#print(object.scale)