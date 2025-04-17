import time
from DataLoader import DataLoader
from TripleManager import TripleManager
import GenerateQrels
import DatasetUtils
import PathUtils
import os
import glob
import re


main_folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\"


def generate_qrels(dataset):

    policies = ["Max", "Min", "Avg_Floor", "Avg_Ciel"]

    dataset_name = DatasetUtils.get_dataset_name(dataset)
    print(f"\nGenerating Qrels for dataset {dataset}.{dataset_name}")

    reshuffled_dataset_folder = main_folder + "General Tests\\Datasets_Reshuffling\\" + dataset_name + "\\"

    output_folder = main_folder + f"General Tests\\Generated_Qrels_TSV\\{str(dataset)}_{dataset_name}\\"

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    test_files = PathUtils.find_test_files(reshuffled_dataset_folder)

    OG_train_loader, OG_val_loader, OG_test_loader = create_og_loaders(reshuffled_dataset_folder)
    # OG_manager = TripleManager(OG_test_loader, OG_train_loader, OG_val_loader)

    # ent_idx_map = {e: i for i, e in enumerate(OG_manager.entities)}

    for test_file in test_files:

        reshuffle_ID = PathUtils.get_reshuffleId(test_file, "test")

        main_loader = DataLoader(reshuffled_dataset_folder + reshuffle_ID, "test")
        manager = TripleManager(main_loader, OG_train_loader, OG_val_loader, OG_test_loader) # Very slow
        # manager = TripleManager(main_loader) # Faster but not enough

        print("\tMain Data Loaded and Main TripleManager Created")

        output_files = PathUtils.get_policy_output_files(dataset, test_file, output_folder)





        # print(f"\tProcessing {dataset_path}")
        # entity_path = os.path.dirname(dataset_path)
        # print(f"\tProcessing {entity_path}")
        # continue

        # filename = dataset_path + "15_test2id.txt"  # e.g., "0_test2id.txt" or "test2id.txt"
        # filename = re.sub(r"^\d+_", "", filename) # remove leading numbers + underscore
        # print(f"Processing {filename}")
        # sys.exit()

        GenerateQrels.generate_qrels_tsv(manager, output_files)
        break


def find_test_files(dataset_folder):
    # Find all test2id files (e.g., 0_test2id.txt to 25_test2id.txt)
    test_files = glob.glob(os.path.join(dataset_folder, "*test2id.txt"))
    print(f"\tFound {len(test_files)} test files")
    # test_files = sorted(test_files, key=lambda x: int(os.path.basename(x).split("_")[0]))  # sort by index
    return sort_test_files(test_files)


def sort_test_files(files):
    def sort_key(f):
        name = os.path.basename(f)
        match = re.match(r"(\d+)_test2id\.txt", name)
        return int(match.group(1)) if match else -1  # Put 'test2id.txt' last
    return sorted(files, key=sort_key)


def create_og_loaders(dataset_folder):

    train_file, val_file, test_file = PathUtils.get_original_files(dataset_folder)

    train_loader = DataLoader(train_file, "train")
    val_loader = DataLoader(val_file, "valid")
    test_loader = DataLoader(test_file, "test")

    return train_loader, val_loader, test_loader


def main():
    test_datasets = [i for i in range(11)]

    test_datasets = [3]

    for dataset in test_datasets:
        start_time = time.time()

        generate_qrels(dataset)

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