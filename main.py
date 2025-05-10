import sys
import time
from DataLoader import DataLoader
from TripleManager import TripleManager
import GenerateQrels
import IrMeasure
import DatasetUtils
import PathUtils as pu
import os
import glob
import re

# Write Qrels to file?
WRITE_QREL_TO_FILE = False

# Write ir-measure jsons to files?
WRITE_JSON_TO_FILE = False

# Datasets to run it on. Check the DatasetUtils.py file to see all the dataset names and
# confirm whether all these datasets do exist in the reshuffle folder below and in the run scores folder
datasets = [3]

# Define the main folders to be used here to generate the qrels and calculate the ir measures
main_folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\General Tests\\"

# Folder containing the dataset folders for the run score files for each
run_scores_folder = main_folder + "TopK_Scores\\"

# The folder that contains the folder for all the dataset folder with the reshuffled files
reshuffled_all_datasets_folder = main_folder + "Datasets_Reshuffling\\"

# Folder where the qrel outputs will be stored if things are printed to files
qrel_output_folder = main_folder + f"Generated_Qrels_TSV\\"

# Folder where the json outputs will be stored if things are printed to files
json_output_folder = main_folder + f"IR_Measures\\"

# Check if the base folder for the reshuffled datasets exists - needs to exist
if not pu.check_folder_existence(reshuffled_all_datasets_folder):
    print(f"Dataset Folder {reshuffled_all_datasets_folder} not found")
    sys.exit()

# Ensure the output folder exists - if not created, it's fine. New folder created here
os.makedirs(qrel_output_folder, exist_ok=True)
os.makedirs(json_output_folder, exist_ok=True)

# Decide models to use
models = ["boxe"] # blank means all.Insert model names as strings - for eg. "boxe"

# Thresholds to consider when making compatible relations
thresholds_to_run = [0.75, ]

# Methods to consider when making compatible relations
methods_to_run = ["overlap", ] # or dice/jaccard/cosine, etc.


def generate_qrels_and_calculate_ir(dataset):

    policies = ["Max", "Min", "Avg_Floor", "Avg_Ciel"]

    dataset_name = DatasetUtils.get_dataset_name(dataset)
    # print(f"\nGenerating Qrels for dataset {dataset}.{dataset_name}")

    # Dataset folder
    reshuffled_dataset_folder = reshuffled_all_datasets_folder + dataset_name + "\\"

    # Run score folder
    run_scores_dataset_folder = run_scores_folder + f"{dataset}\\"

    # Qrel dataset output folder
    qrel_dataset_output_folder = qrel_output_folder + f"{str(dataset)}_{dataset_name}" + "\\"

    # Json dataset output folder
    json_dataset_output_folder = json_output_folder + f"{str(dataset)}_{dataset_name}" + "\\"

    if not pu.check_folder_existence(reshuffled_dataset_folder):
        print(f"Dataset Folder {reshuffled_dataset_folder} not found")
        return

    # Ensure the output folders exists
    os.makedirs(qrel_dataset_output_folder, exist_ok=True)
    os.makedirs(json_dataset_output_folder, exist_ok=True)

    test_files = pu.find_test_files(reshuffled_dataset_folder)

    OG_train_loader, OG_val_loader, OG_test_loader = create_og_loaders(reshuffled_dataset_folder)
    # OG_manager = TripleManager(OG_test_loader, OG_train_loader, OG_val_loader)

    # ent_idx_map = {e: i for i, e in enumerate(OG_manager.entities)}

    test_configs = generate_test_configs(thresholds_to_run, methods_to_run)

    for test_file in test_files:

        reshuffle_ID = pu.get_reshuffleId(test_file, "test")

        for config in test_configs:
            # print(f"\nTesting {config['method']} - {config['threshold']}")

            output_json_path = (json_dataset_output_folder
                                + f"{str(dataset)}_{dataset_name}"
                                + f"_{str(reshuffle_ID)}"
                                + f"_{config['method']}({config['threshold']})"
                                + "IR_results.json")

            with open(output_json_path, "w", newline='') as f:
                pass

            main_loader = DataLoader(reshuffled_dataset_folder + reshuffle_ID, "test")
            manager = TripleManager(
                    main_loader, OG_train_loader, OG_val_loader, OG_test_loader,
                    compatible_threshold=config["threshold"],
                    similarity_method=config["method"],
                    alpha=config.get("alpha", 0.5),
                    beta=config.get("beta", 0.5)
                ) # Very slow
            # manager = TripleManager(main_loader) # Faster but not enough

            # print("\tMain Data Loaded and Main TripleManager Created")

            output_files = pu.get_policy_output_files(dataset, test_file, qrel_dataset_output_folder)

            # print(f"\tProcessing {dataset_path}")
            # entity_path = os.path.dirname(dataset_path)
            # print(f"\tProcessing {entity_path}")
            # continue

            # filename = dataset_path + "15_test2id.txt"  # e.g., "0_test2id.txt" or "test2id.txt"
            # filename = re.sub(r"^\d+_", "", filename) # remove leading numbers + underscore
            # print(f"Processing {filename}")
            # sys.exit()

            qrels = GenerateQrels.generate_qrels_tsv(manager, output_files, WRITE_QREL_TO_FILE)

            IrMeasure.calculate_ir_measures(test_file, run_scores_dataset_folder, qrels, dataset_name,
                                            output_json_path, config['threshold'], config['method'], models, WRITE_JSON_TO_FILE)
        break


def find_test_files(dataset_folder):
    # Find all test2id files (e.g., 0_test2id.txt to 25_test2id.txt)
    test_files = glob.glob(os.path.join(dataset_folder, "*test2id.txt"))
    print(f"\tFound {len(test_files)} test files")
    # test_files = sorted(test_files, key=lambda x: int(os.path.basename(x).split("_")[0]))  # sort by index
    return sort_test_files(test_files)


def generate_test_configs(thresholds, methods):
    configs = []
    for method in methods:
        for threshold in thresholds:
            config = {"threshold": threshold, "method": method}
            if method == "tversky":
                config["alpha"] = 0.5
                config["beta"] = 0.5
            configs.append(config)
    return configs


def sort_test_files(files):
    def sort_key(f):
        name = os.path.basename(f)
        match = re.match(r"(\d+)_test2id\.txt", name)
        return int(match.group(1)) if match else -1  # Put 'test2id.txt' last
    return sorted(files, key=sort_key)


def create_og_loaders(dataset_folder):

    train_file, val_file, test_file = pu.get_original_files(dataset_folder)

    train_loader = DataLoader(train_file, "train")
    val_loader = DataLoader(val_file, "valid")
    test_loader = DataLoader(test_file, "test")

    return train_loader, val_loader, test_loader


def main():
    test_datasets = [i for i in range(11)]

    test_datasets = [3]

    for dataset in datasets:

        # Skip if the dataset number goes out of range
        if DatasetUtils.get_dataset_name(dataset) == "":
            continue

        start_time = time.time()

        generate_qrels_and_calculate_ir(dataset)

        end_time(start_time)

    # dataset = 5

    # generate_qrels_tsv(dataset)


def end_time(start_time):
    # Print the total execution time of the entire code
    total_time = time.time() - start_time
    time_taken = (f"\tTime Taken: "
                  f"{total_time // 3600} Hours, "
                  f"{(total_time % 3600) // 60} Minutes, "
                  f"and {(total_time % 3600) % 60} seconds.")
    print(time_taken)


if __name__ == "__main__":
    main()
