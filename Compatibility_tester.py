from DataLoader import DataLoader
from TripleManager import TripleManager
from CompatibleRelationsGenerator import CompatibleRelationsGenerator
import PathUtils as pu
import os
import sys
import DatasetUtils
import time
from statistics import mean
import json
import glob
import re


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


def compare_compatibility(result_a, result_b):
    different = False
    for rel_type in ['dom_dom', 'dom_ran', 'ran_dom', 'ran_ran']:
        set_a = set((str(r), tuple(map(str, compatible))) for r, compatible in result_a[rel_type] if compatible)
        set_b = set((str(r), tuple(map(str, compatible))) for r, compatible in result_b[rel_type] if compatible)

        diff_a = set_a - set_b
        diff_b = set_b - set_a

        if diff_a or diff_b:
            print(f"Difference found in {rel_type}:")
            print(f"  In A not in B: {len(diff_a)} entries")
            print(f"  In B not in A: {len(diff_b)} entries")
            different = True
    if not different:
        print("No differences found.")


def compare_compatibility_stats(map1, map2):
    keys = set(map1.keys()) | set(map2.keys())

    diff_summary = {
        "total_keys": len(keys),
        "non_empty_map1": 0,
        "non_empty_map2": 0,
        "shared_non_empty_keys": 0,
        "average_links_map1": [],
        "average_links_map2": [],
        "keys_with_diff_length": 0
    }

    for key in keys:
        links1 = map1.get(key, [])
        links2 = map2.get(key, [])

        len1 = len(links1)
        len2 = len(links2)

        if len1 > 0:
            diff_summary["non_empty_map1"] += 1
            diff_summary["average_links_map1"].append(len1)
        if len2 > 0:
            diff_summary["non_empty_map2"] += 1
            diff_summary["average_links_map2"].append(len2)

        if len1 > 0 and len2 > 0:
            diff_summary["shared_non_empty_keys"] += 1

        if len1 != len2:
            diff_summary["keys_with_diff_length"] += 1

    # Final summaries
    print("\nCompatibility Map Statistical Comparison:")
    print(f"  Total keys: {diff_summary['total_keys']}")
    print(f"  Non-empty in Map 1: {diff_summary['non_empty_map1']}")
    print(f"  Non-empty in Map 2: {diff_summary['non_empty_map2']}")
    print(f"  Shared non-empty keys: {diff_summary['shared_non_empty_keys']}")
    print(f"  Keys with different link counts: {diff_summary['keys_with_diff_length']}")

    if diff_summary["average_links_map1"]:
        print(f"  Avg links per non-empty key in Map 1: {mean(diff_summary['average_links_map1']):.2f}")
    if diff_summary["average_links_map2"]:
        print(f"  Avg links per non-empty key in Map 2: {mean(diff_summary['average_links_map2']):.2f}\n")


def compare_compatibility_maps(map1, map2):
    total_keys = set(map1.keys()) | set(map2.keys())
    diff_count = 0

    print("\nCompatibility Map Comparison Summary:")
    for key in sorted(total_keys):
        set1 = set(map(tuple, map1.get(key, [])))
        set2 = set(map(tuple, map2.get(key, [])))

        only_in_1 = set1 - set2
        only_in_2 = set2 - set1

        if only_in_1 or only_in_2:
            diff_count += len(only_in_1) + len(only_in_2)
            print(f"\nKey: {key}")
            print(f"  ↳ Only in Map 1: {len(only_in_1)} entries")
            print(f"  ↳ Only in Map 2: {len(only_in_2)} entries")

            print("    Sample differences from Map 1:")
            for entry in list(only_in_1)[:3]:
                print(f"      {entry}")

            print("    Sample differences from Map 2:")
            for entry in list(only_in_2)[:3]:
                print(f"      {entry}")

    if diff_count == 0:
        print("✔️ The maps are identical.")
    else:
        print(f"\n❗ Total differing entries: {diff_count}")



def test_compatibility_variations(loader, OG_train_loader, OG_val_loader, OG_test_loader, output_json_path="compatibility_test_results.json"):
    # Load dataset
    # loader = DataLoader(path_to_dataset, split='train')
    # tm = TripleManager(loader)

    # Different parameter settings
    # Generate different parameter settings to test
    thresholds = [0.75, 0.8, 0.9] # 0.5, 0.6, 0.85,
    methods = ["overlap", "jaccard", "dice", "cosine"]

    # thresholds = [0.75]
    # methods = ["overlap", "jaccard"]
    test_configs = generate_test_configs(thresholds, methods)

    results = {}

    for config in test_configs:

        print(f"\nTesting {config['method']} - {config['threshold']}")

        tm = TripleManager(
            loader, OG_train_loader, OG_val_loader, OG_test_loader,
            compatible_threshold=config["threshold"],
            similarity_method=config["method"],
            alpha=config.get("alpha", 0.5),
            beta=config.get("beta", 0.5)
        )

        compatibility_map = tm.compatible_relations

        print(compatibility_map)

        key = f"{config['method']}_thresh{config['threshold']}"
        results[key] = {
            "dom_dom": [(str(r), list(map(str, rs))) for r, rs in tm.dom_dom.items() if rs],
            "dom_ran": [(str(r), list(map(str, rs))) for r, rs in tm.dom_ran.items() if rs],
            "ran_dom": [(str(r), list(map(str, rs))) for r, rs in tm.ran_dom.items() if rs],
            "ran_ran": [(str(r), list(map(str, rs))) for r, rs in tm.ran_ran.items() if rs],
            "map": compatibility_map,
            "total_compatibility_entries": len([k for k, v in compatibility_map.items() if v])
        }

        # print(results[key]["ran_ran"])

        # counter = 1
        # for k, v in compatibility_map.items():
        #     if v:
        #         print(f"{k} - {counter} \n\t{v}")
        #         counter += 1

        # Print the summary
    for key, counts in results.items():
        print(f"\nResults for {key}:")
        print(f"Dom-Dom compatible: {len(counts['dom_dom'])} relations")
        print(f"Dom-Ran compatible: {len(counts['dom_ran'])} relations")
        print(f"Ran-Dom compatible: {len(counts['ran_dom'])} relations")
        print(f"Ran-Ran compatible: {len(counts['ran_ran'])} relations")
        print(f"Total unified compatibility entries: {counts['total_compatibility_entries']}")

    keys = list(results.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            print(f"\n\nComparing {keys[i]} vs {keys[j]}")
            compare_compatibility_stats(results[keys[i]]["map"], results[keys[j]]["map"])
            # compare_compatibility(results[keys[i]], results[keys[j]])

    # Save results to JSON
    # with open(output_json_path, "w", encoding="utf-8") as f:
    #     json.dump(results, f, indent=2)

    print(f"\nTest results saved to {output_json_path}")


def print_summary(compat_relations):
    print(f"Dom-Dom relations: {len(compat_relations['dom_dom'])}")
    print(f"Dom-Ran relations: {len(compat_relations['dom_ran'])}")
    print(f"Ran-Dom relations: {len(compat_relations['ran_dom'])}")
    print(f"Ran-Ran relations: {len(compat_relations['ran_ran'])}")



def create_og_loaders(dataset_folder):

    train_file, val_file, test_file = pu.get_original_files(dataset_folder)

    train_loader = DataLoader(train_file, "train")
    val_loader = DataLoader(val_file, "valid")
    test_loader = DataLoader(test_file, "test")

    return train_loader, val_loader, test_loader


def main():
    main_folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\General Tests\\"

    reshuffled_all_datasets_folder = main_folder + "Datasets_Reshuffling\\"

    # output_folder = main_folder + f"Generated_Qrels_TSV\\"

    # Check if the base folder for the reshuffled datasets exists - needs to exist
    if not pu.check_folder_existence(reshuffled_all_datasets_folder):
        print(f"Dataset Folder {reshuffled_all_datasets_folder} not found")
        sys.exit()

    # Ensure the output folder exists - if not created, it's fine. New folder created here
    # os.makedirs(output_folder, exist_ok=True)

    test_datasets = [i for i in range(11)]

    test_datasets = [3]

    for dataset in test_datasets:

        start_time = time.time()

        # Skip if the dataset number goes out of range
        if DatasetUtils.get_dataset_name(dataset) == "":
            continue

        dataset_name = DatasetUtils.get_dataset_name(dataset)
        print(f"\nFinding Compatibility for dataset {dataset}.{dataset_name}")

        reshuffled_dataset_folder = reshuffled_all_datasets_folder + dataset_name + "\\"

        if not pu.check_folder_existence(reshuffled_dataset_folder):
            print(f"Dataset Folder {reshuffled_dataset_folder} not found")
            return

        test_files = pu.find_test_files(reshuffled_dataset_folder)

        OG_train_loader, OG_val_loader, OG_test_loader = create_og_loaders(reshuffled_dataset_folder)

        counter = 1
        for test_file in test_files:
            # if counter == 1:
            #     counter += 1
            #     continue

            reshuffle_ID = pu.get_reshuffleId(test_file, "test")

            main_loader = DataLoader(reshuffled_dataset_folder + reshuffle_ID, "test")

            test_compatibility_variations(main_loader, OG_train_loader, OG_val_loader, OG_test_loader)
            # manager = TripleManager(main_loader, OG_train_loader, OG_val_loader, OG_test_loader)

            # print("\tMain Data Loaded and Main TripleManager Created")

            break



        # generate_qrels(dataset)

        end_time(start_time)



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
