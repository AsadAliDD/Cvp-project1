import open3d as o3d
import os
import pandas as pd


# Load .obj file
ROOT_DIR = "/home/orcun/Downloads/wetransfer_annotations-csv_2023-11-15_0139/"
OBJ_DIR = f"{ROOT_DIR}/Archive/cloth"
df = pd.read_csv(f"{ROOT_DIR}/annotations.csv")
OBJ_NAMES = list(df["Label"])
OBJ_FILES = [f for f in os.listdir(OBJ_DIR) if f.endswith(".obj")]
OBJ_IDX = 0
OBJ_DF_IDX = 0
OBJ_NAME = ""
APPROVED_OBJS = []


def vis_mesh(vis, obj_file):
    global OBJ_IDX, OBJ_FILES

    cloth_model = o3d.io.read_triangle_model(
        f"{OBJ_DIR}/{obj_file}"
    )  # read_triangle_mesh() only loads simple object, misses the cloth

    # Visualize the mesh
    vis.clear_geometries()
    for m in cloth_model.meshes:
        vis.add_geometry(m.mesh)


def get_next():
    global OBJ_IDX, OBJ_DF_IDX, OBJ_FILES, OBJ_NAME
    OBJ_IDX += 1
    obj_file_ = OBJ_FILES[OBJ_IDX]
    df_obj_idx_ = int(obj_file_.split(".")[0]) - 1  # obj file naming starts from 1
    OBJ_DF_IDX = df_obj_idx_
    OBJ_NAME = OBJ_NAMES[df_obj_idx_]
    print(f"Now showing: {OBJ_NAME}")
    return obj_file_, df_obj_idx_


def approve(vis):
    global OBJ_IDX, OBJ_FILES, OBJ_NAME, APPROVED_OBJS
    APPROVED_OBJS.append((OBJ_FILES[OBJ_IDX], OBJ_NAME))
    print(f"[APPROVED] OBJ_FILE: {OBJ_FILES[OBJ_IDX]}, NAME: {OBJ_NAME}")
    obj_file_, df_obj_idx_ = get_next()
    vis_mesh(vis, obj_file_)


def reject(vis):
    obj_file_, df_obj_idx_ = get_next()
    vis_mesh(vis, obj_file_)


def main():
    # Create visualizer
    vis = o3d.visualization.VisualizerWithKeyCallback()

    vis.create_window()
    vis.get_render_option().load_from_json("opts.json")
    vis.update_renderer()

    init_obj_file, init_obj_df_idx = get_next()
    vis_mesh(vis, init_obj_file)
    # Register key callback
    vis.register_key_callback(ord("Y"), approve)
    vis.register_key_callback(ord("N"), reject)

    vis.run()
    vis.destroy_window()

    with open("selection.txt", "w") as f:
        for obj_file, obj_name in APPROVED_OBJS:
            f.write(f"{obj_file},{obj_name}\n")


if __name__ == "__main__":
    main()
