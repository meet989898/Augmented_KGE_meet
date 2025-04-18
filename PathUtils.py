import os
import glob
import re
import DatasetUtils

# Update this per machine/environment
BASE_PATHS = {
    "WN18": "/absolute/path/to/WN18",
    "FB13": "/absolute/path/to/FB13",
    "Custom": "/absolute/path/to/custom"
}

FILE_TEMPLATES = {
    "train": "{base}/train2id.txt",
    "valid": "{base}/valid2id.txt",
    "test": "{base}/test2id.txt",
    "entity": "{base}/entity2id.txt",
    "relation": "{base}/relation2id.txt",
    "anomaly": "{base}/relation2anomaly.txt",
    "compat": "{base}/compatible_relations.txt"
}


def get_path(dataset_name, file_key):
    base = BASE_PATHS[dataset_name]
    if file_key not in FILE_TEMPLATES:
        raise ValueError(f"Unknown file key: {file_key}")
    return FILE_TEMPLATES[file_key].format(base=base)


def get_test_files(dataset_name, reshuffled=False):
    """
    Returns all test2id.txt files (e.g., 0_test2id.txt ... 25_test2id.txt) if reshuffled=True,
    or just test2id.txt if reshuffled=False.
    """
    base = BASE_PATHS[dataset_name]
    if reshuffled:
        return sorted(glob.glob(os.path.join(base, "*_test2id.txt")),
                      key=lambda f: int(os.path.basename(f).split('_')[0]))
    else:
        return [os.path.join(base, "test2id.txt")]


def find_test_files(dataset_folder):
    # Find all test2id files (e.g., 0_test2id.txt to 25_test2id.txt)
    test_files = [
        f for f in glob.glob(os.path.join(dataset_folder, "*test2id.txt"))
        if os.path.basename(f)[0].isdigit()
    ]

    print(f"\tFound {len(test_files)} test files")
    # test_files = sorted(test_files, key=lambda x: int(os.path.basename(x).split("_")[0]))  # sort by index
    return _sort_test_files(test_files)


def _sort_test_files(files):
    def sort_key(f):
        name = os.path.basename(f)
        match = re.match(r"(\d+)_test2id\.txt", name)
        return int(match.group(1)) if match else -1  # Put 'test2id.txt' last

    return sorted(files, key=sort_key)


def get_reshuffleId(test_file, split_type):
    base_name = os.path.basename(test_file)
    print(f"\tProcessing {base_name}")

    reshuffle_id = None

    if f"_{split_type}" in base_name:
        reshuffle_id = base_name.split(f"_{split_type}")[0] + "_"

    return reshuffle_id


def get_original_files(dataset_folder):

    train_file = [
        f for f in glob.glob(os.path.join(dataset_folder, "*train2id.txt"))
        if re.match(r"^[A-Za-z]", os.path.basename(f))
    ]
    print(f"\tFound {len(train_file)} original train files")

    train_reshuffle_id = get_reshuffleId(train_file[0], "train")
    if train_reshuffle_id:
        train_file = dataset_folder + train_reshuffle_id
    else:
        train_file = dataset_folder
    print(f"\tFound {train_file}")

    val_file = [
        f for f in glob.glob(os.path.join(dataset_folder, "*valid2id.txt"))
        if re.match(r"^[A-Za-z]", os.path.basename(f))
    ]
    print(f"\tFound {len(val_file)} original validation files")

    val_reshuffle_id = get_reshuffleId(val_file[0], "valid")
    if val_reshuffle_id:
        val_file = dataset_folder + val_reshuffle_id
    else:
        val_file = dataset_folder
    print(f"\tFound {val_file}")

    test_file = [
        f for f in glob.glob(os.path.join(dataset_folder, "*test2id.txt"))
        if re.match(r"^[A-Za-z]", os.path.basename(f))
    ]
    print(f"\tFound {len(test_file)} original test files")

    test_reshuffle_id = get_reshuffleId(test_file[0], "test")
    if test_reshuffle_id:
        test_file = dataset_folder + test_reshuffle_id
    else:
        test_file = dataset_folder
    print(f"\tFound {test_file}")

    return train_file, val_file, test_file


def get_policy_output_files(dataset, test_file, output_folder):

    dataset_name = DatasetUtils.get_dataset_name(dataset)

    reshuffle_ID = get_reshuffleId(test_file, "test")

    policies = ["Max", "Min", "Avg_Floor", "Avg_Ciel"]

    output_files = []

    for policy in policies:
        output_file = output_folder + f"{dataset}_{dataset_name}_{reshuffle_ID}_Qrels_{policy}.tsv"

        output_files.append(output_file)

    return output_files