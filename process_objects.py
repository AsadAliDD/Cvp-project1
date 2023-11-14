import pymeshlab
import os
import objaverse
from glob import glob
from tqdm import tqdm
import pandas as pd


def procecss_mesh(path, output_path):
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(path)
    number_meshes = ms.number_meshes()
    print(f"Number of Meshes: {number_meshes}")
    if number_meshes > 1:
        # Converting all meshes into a single one
        ms.generate_by_merging_visible_meshes()

    # Dynamic based on the object file size
    print(f"Vertices Before: {ms.current_mesh().vertex_number()}")
    ms.meshing_decimation_quadric_edge_collapse(targetperc=0.5)
    print(f"Vertices After: {ms.current_mesh().vertex_number()}")
    ms.compute_matrix_from_scaling_or_normalization(
        uniformflag=True, unitflag=True, freeze=True, alllayers=True
    )

    try:
        ms.save_current_mesh(output_path)
    except Exception as e:
        print(e)
    del ms


def process_objects():
    result = [
        y for x in os.walk("./raw_objects/") for y in glob(os.path.join(x[0], "*.glb"))
    ]
    base_folder = "./simple_objects/"
    index = 1
    output_paths = []
    labels = []
    uids = []
    lvis_annotations = objaverse.load_lvis_annotations()
    skip_labels = [
        "stove",
        "power_shovel",
        "pitcher_(vessel_for_liquid)",
        "garbage",
        "elevator_car",
    ]
    for path in tqdm(result):
        print(path)
        uid = path.split("/")[-1].split(".glb")[0]
        file_size = os.path.getsize(path) / 1024**2

        label = [k for k, v in lvis_annotations.items() if uid in v][0]
        print(f"Label: {label}")
        if label in skip_labels:
            continue

        print(f"{uid}\nFile Size Before: {file_size}")
        if file_size < 50:
            output_path = os.path.join(base_folder, f"{index}.obj")
            print(output_path)
            try:
                procecss_mesh(path, output_path)

            except Exception as e:
                print(e)

            new_file_size = os.path.getsize(output_path) / 1024**2
            if new_file_size < 5:
                output_paths.append(output_path)
                labels.append(label)
                uids.append(uid)
                index += 1
            else:
                print("Skipping Export File Size Greater than 5 mb")
                os.remove(output_path)
        else:
            print("File Size Greater than 50. Skipping...")

    df = pd.DataFrame({"Uid": uids, "Path": output_paths, "Label": labels})
    print(df)
    df.to_csv("./annotations.csv", index=False)


process_objects()
