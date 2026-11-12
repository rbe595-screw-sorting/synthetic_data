import os
import bpy #type: ignore
import math
import random
import numpy as np
from mathutils import Vector


def delete_collection_objects(name):
    for object in bpy.data.collections[name].objects:
        bpy.data.objects.remove(object)

def duplicate(name, number, xy_bound, collection=None, rand=True):
    '''
    generate a number of objects with a random orientation within specific bounds
    
    params:
        name: the name of the object being duplicated
        number: how many objects to generate
        xy_bound: distance from the origin to place the object
        collection: name of the collection to put the items into
    '''
    src = bpy.data.objects[name] # from the og collection
    
    # main object loop
    for i in range(number):
        
        # copy the screw
        new_obj = src.copy()
        new_obj.data = src.data.copy()
        
        if rand:
            # send to new random location (0 to 1 for now)
            new_obj.location.x = random.uniform(-xy_bound, xy_bound)
            new_obj.location.y = random.uniform(-xy_bound, xy_bound)
            
            # random rotation about z axis
            yaw = random.uniform(0, 2 * 3.14) # in rad
       
        # rotate so flat on table
        pitch = math.radians(90) 
        
        # apply rotation (rpy)
        new_obj.rotation_euler = (0, pitch, yaw)
        
        # add to collection
        if collection is not None:
            bpy.data.collections[collection].objects.link(new_obj)
            
def random_cube(cube_length, object_names, number, collection=None):
    
    bounds = cube_length/2 # center cube at (0,0,0)
    
    # iterate through objects listed
    for name in object_names:
        src = bpy.data.objects[name] # base object from "Collection"
        
        for i in range(number):
            # copy the object
            new_obj = src.copy()
            new_obj.data = src.data.copy()
            
            # random location
            new_obj.location.x = random.uniform(-bounds, bounds)
            new_obj.location.y = random.uniform(-bounds, bounds)
            new_obj.location.z = random.uniform(-bounds, bounds)
            
            # random orientation
            roll = random.uniform(0, 2 * 3.14)
            pitch = random.uniform(0, 2 * 3.14)
            yaw = random.uniform(0, 2 * 3.14)
            
            # apply rotation
            new_obj.rotation_euler = (roll, pitch, yaw)

            # add to collection
            if collection is not None:
                    bpy.data.collections[collection].objects.link(new_obj)
                    
def randomize_light(name, color, distance, light_type="POINT"):
    light_obj = bpy.data.objects.get(name)

    if light_obj is None:
        light_data = bpy.data.lights.new(name, type=light_type)
        light_obj = bpy.data.objects.new(name, light_data)
        bpy.context.collection.objects.link(light_obj)

    # (mostly) random position
    light_obj.location = (
        random.uniform(-distance, distance),
        random.uniform(-distance, distance),
        random.uniform(0.5, distance),
    )
    
    # random orientation
    roll = random.uniform(0, 2 * 3.14)
    pitch = random.uniform(0, 2 * 3.14)
    yaw = random.uniform(0, 2 * 3.14)
    
    # apply rotation
    light_obj.rotation_euler = (roll, pitch, yaw)

    light = light_obj.data
    light.energy = random.uniform(300.0, 1200.0)  # power in watts
    
    if color:
        light.color = (
            random.uniform(0.7, 1.0),
            random.uniform(0.7, 1.0),
            random.uniform(0.7, 1.0)
        )
    else:
        light_obj.data.color = (1.0, 1.0, 1.0)

def randomize_hdri(folder):
    '''randomize the scene background'''
    
    # get file paths
    hdri_paths = [
        os.path.join(folder, filename)
        for filename in os.listdir(folder)
        if filename.lower().endswith((".hdr", ".exr"))
    ]

    # if no HDRI files are found
    if not hdri_paths:
        raise RuntimeError("No .hdr or .exr files found")
    
    world = bpy.context.scene.world
    
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
        
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    env = nodes.get("Environment Texture")
    if env is None:
        env = nodes.new("ShaderNodeTexEnvironment")

    background = nodes.get("Background")
    if background is None:
        background = nodes.new("ShaderNodeBackground")

    output = nodes.get("World Output")
    if output is None:
        output = nodes.new("ShaderNodeOutputWorld")
        
    if not any(link.from_node == env and link.to_node == background for link in links):
        links.new(env.outputs["Color"], background.inputs["Color"])

    if not any(link.from_node == background and link.to_node == output for link in links):
        links.new(background.outputs["Background"], output.inputs["Surface"])
    
    path = random.choice(hdri_paths)
    env.image = bpy.data.images.load(str(path), check_existing=True)
    
    return str(path)
        
def random_camera(camera_name, radius):

    camera = bpy.data.objects[camera_name]
    
    # random location on a sphere
    z = random.uniform(-1.0, 1.0)
    angle = random.uniform(0.0, 2.0 * math.pi)
    horizontal = math.sqrt(1.0 - z * z)

    direction = Vector((
        horizontal * math.cos(angle),
        horizontal * math.sin(angle),
        z
    ))

    camera.location = direction * radius

    # point the camera toward the origin
    direction_to_origin = -camera.location
    camera.rotation_euler = direction_to_origin.to_track_quat('-Z', 'Y').to_euler()
    
    
def render(output_folder, filename, cycles=False):
    os.makedirs(output_folder, exist_ok=True)
        
    scene = bpy.context.scene
    
    # choose render engine
    if cycles:
        scene.render.engine = "CYCLES" 
    else:
        scene.render.engine = "BLENDER_EEVEE" 
    
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = os.path.join(output_folder, f"{filename}.png")

    bpy.ops.render.render(write_still=True)
     