import objaverse
import multiprocessing
import warnings
import random
import json
import pandas as pd


def select_objects(seed,object_type,object_number):
    lvis_annotations = objaverse.load_lvis_annotations()
    labels=[]
    uids=[]
    random.seed(seed)
    keys=random.choices(list(lvis_annotations.keys()),k=object_type)
    for key in keys:
        obj_uid=lvis_annotations[key]
        uids.extend(random.choices(obj_uid,k=object_number))
        label=[key]*object_number
        labels.extend(label)
        

    df=pd.DataFrame({'Labels':labels,'Uids':uids})
    return df


def download_objects(uids):

    processes = multiprocessing.cpu_count()
    objects = objaverse.load_objects(
        uids=uids,
        download_processes=processes
    )
    return objects

def get_annotations(uids):
    anon=objaverse.load_annotations(uids)
    return anon


def main():



    selected_objects=select_objects(seed=10,object_type=50,object_number=2)
    # objects=download_objects(uids)
    # print (objects)

if __name__ == '__main__':
    main()