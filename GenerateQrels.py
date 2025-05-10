import PathUtils as pu
import numpy as np
import time


def resolve_policies(row):
    max_val = np.max(row)
    min_val = np.min(row)
    avg_val = np.sum(row) / np.count_nonzero(row)
    return int(max_val), int(min_val), int(np.floor(avg_val)), int(np.ceil(avg_val))


def generate_qrels_tsv(manager, output_files, WRITE=False):
    """
    Generates a TSV file containing qrels based on different corruption strategies.
    :param WRITE: Flag to decide if we want to write the file or just return the dictionary
    :param output_files: All the policy related output files
    :param manager: Triple Manager object.
    """

    # relavance_map = {
    #     "LCWA": 0,
    #     "nonsensical": 1,
    #     "sensical": 4,
    #     "one-hop sensical": 3,
    #     "one-hop nonsensical": 2,
    #     "positive": 5
    # }

    RELEVANCE_MAP = {
        "LCWA": 0,
        "nonsensical": 1,
        "one-hop nonsensical": 2,
        "one-hop sensical": 3,
        "sensical": 4,
        "positive": 5
    }

    CORRUPTION_STRATEGIES = [
        "LCWA", "nonsensical", "one-hop nonsensical", "one-hop sensical", "sensical"
    ]

    # POLICIES = ["max", "min", "avg"]

    STRATEGY_IDX = {strategy: idx for idx, strategy in enumerate(CORRUPTION_STRATEGIES)}

    POLICIES = ["max", "min", "avg_floor", "avg_ceil"]
    POLICY_IDX = {p: i for i, p in enumerate(POLICIES)}

    # dataset_name = DatasetUtils.get_dataset_name(dataset)

    # print(f"\nGenerating Qrels for dataset {dataset}.{dataset_name}")
    # print("Mapping Used:")
    #
    # for key, value in relavance_map.items():
    #     print(f"\t{key}: {value}")

    # folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\"

    # dataset_folder = folder + "General Tests\\Datasets_Reshuffling\\" + dataset_name + "\\"

    # output_folder = ("D:\\Mast ers\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\General Tests\\Generated_Qrels_TSV\\"
    #                  + f"{str(dataset)}_{dataset_name}")

    # Ensure the output folder exists
    # os.makedirs(output_folder, exist_ok=True)

    # Find all test2id files (e.g., 0_test2id.txt to 25_test2id.txt)
    # test_files = glob.glob(os.path.join(dataset_folder, "*test2id.txt"))
    # print(f"\tFound {len(test_files)} test files")
    # test_files = sorted(test_files, key=lambda x: int(os.path.basename(x).split("_")[0]))  # sort by index
    # test_files = sort_test_files(test_files)

    # for test_file in test_files:
    #     print(f"Processing {test_file}")
    #
    # sys.exit()




    # for test_file in test_files:
    #     base_name = os.path.basename(test_file)
    #     print(f"\n\tProcessing {base_name}")
    #     # print(f"Processing {test_file}")
    #     # print()
    #     # continue
    #     # reshuffle_id = base_name.split("_")[0] + "_" if "_" in base_name else None
    #
    #     if "_test" in base_name:
    #         reshuffle_id = base_name.split("_test")[0]
    #         dataset_path = dataset_folder + f"{reshuffle_id}_"
    #
    #     else:
    #         reshuffle_id = "Original"
    #         dataset_path = dataset_folder

        # print(f"\tProcessing {dataset_path}")
        # entity_path = os.path.dirname(dataset_path)
        # print(f"\tProcessing {entity_path}")
        # continue

        # filename = dataset_path + "15_test2id.txt"  # e.g., "0_test2id.txt" or "test2id.txt"
        # filename = re.sub(r"^\d+_", "", filename) # remove leading numbers + underscore
        # print(f"Processing {filename}")
        # sys.exit()

        # # train_loader = DataLoader(dataset_path, "train")
        # loader = DataLoader(dataset_path, "test")
        # manager = TripleManager(loader)

        # print("\tData Loaded and TripleManager Created")
        #
        # # Define the full output file path
        # output_tsv = os.path.join(output_folder, f"{dataset}_{dataset_name}_{reshuffle_id}.tsv")
        #
        # # Open all output files at once
        # f_max = open(os.path.join(output_folder, f"{dataset}_{dataset_name}_{reshuffle_id}_qrels_max.tsv"), "w", newline='')
        # f_min = open(os.path.join(output_folder, f"{dataset}_{dataset_name}_{reshuffle_id}_qrels_min.tsv"), "w", newline='')
        # f_floor = open(os.path.join(output_folder, f"{dataset}_{dataset_name}_{reshuffle_id}_qrels_avg_floor.tsv"), "w", newline='')
        # f_ceil = open(os.path.join(output_folder, f"{dataset}_{dataset_name}_{reshuffle_id}_qrels_avg_ceil.tsv"), "w", newline='')
        #
        # writer_max = csv.writer(f_max, delimiter='\t')
        # writer_min = csv.writer(f_min, delimiter='\t')
        # writer_floor = csv.writer(f_floor, delimiter='\t')
        # writer_ceil = csv.writer(f_ceil, delimiter='\t')

        # with open(output_tsv, 'w', newline='', encoding='utf-8') as file:
        #     writer = csv.writer(file, delimiter='\t')

    # print(f"\tFinding corrupted Qrels for {len(manager.get_triples())} triples")

    i = 1

    entity_list = manager.entities
    entity_count = len(entity_list)
    ent_idx_map = {e: i for i, e in enumerate(entity_list)}
    num_strategies = len(CORRUPTION_STRATEGIES)

    # Preallocate reusable relevance matrix
    rel_matrix = np.zeros((num_strategies, entity_count), dtype=int)

    # Clear all qrels files at the beginning, this won't work if we want to resume
    for file in output_files:
        with open(file, "w", newline='') as f:
            pass  # just truncates the file

    # Prepare in-memory storage
    result_dict = {
        output_files[0]: [],  # max
        output_files[1]: [],  # min
        output_files[2]: [],  # avg_floor
        output_files[3]: []  # avg_ceil
    }

    for h, r, t in manager.get_triples():

        # print(f"Positive {i}: ({h}, {r}, {t})")

        i += 1
        #
        # head_query = f"({h},{r},{t})-h"
        # tail_query = f"({h},{r},{t})-t"
        #
        # # Get corrupted entities for each corruption strategy
        # corrupted_lcwa_head = test_manager.get_corrupted(h, r, t, 'head', 'LCWA')
        # corrupted_lcwa_tail = test_manager.get_corrupted(h, r, t, 'tail', 'LCWA')
        # corrupted_sensical_head = test_manager.get_corrupted(h, r, t, 'head', 'sensical')
        # corrupted_sensical_tail = test_manager.get_corrupted(h, r, t, 'tail', 'sensical')
        # corrupted_nonsensical_head = test_manager.get_corrupted(h, r, t, 'head', 'nonsensical')
        # corrupted_nonsensical_tail = test_manager.get_corrupted(h, r, t, 'tail', 'nonsensical')
        #
        # # print(f"Corrupted LCWA head: {len(corrupted_lcwa_head)}")
        # # print(f"Corrupted LCWA tail: {len(corrupted_lcwa_tail)}")
        # # print(f"Corrupted sensical head: {len(corrupted_sensical_head)}")
        # # print(f"Corrupted sensical tail: {len(corrupted_sensical_tail)}")
        # # print(f"Corrupted nonsensical head: {len(corrupted_nonsensical_head)}")
        # # print(f"Corrupted nonsensical tail: {len(corrupted_nonsensical_tail)}")
        #
        # # # Write LCWA corrupted entities
        # # for entity in corrupted_lcwa_head:
        # #     writer.writerow([head_query, entity, relavance_map['LCWA']])
        # # for entity in corrupted_lcwa_tail:
        # #     writer.writerow([tail_query, entity, relavance_map['LCWA']])
        #
        # # Write nonsensical corrupted entities (relevance = 1)
        # for entity in corrupted_nonsensical_head:
        #     writer.writerow([head_query, entity, relavance_map['nonsensical']])
        # for entity in corrupted_nonsensical_tail:
        #     writer.writerow([tail_query, entity, relavance_map['nonsensical']])
        #
        # # Write sensical corrupted entities (relevance = 4)
        # for entity in corrupted_sensical_head:
        #     writer.writerow([head_query, entity, relavance_map['sensical']])
        # for entity in corrupted_sensical_tail:
        #     writer.writerow([tail_query, entity, relavance_map['sensical']])
        #
        # # Write positive triple
        # writer.writerow([f"({h},{r},{t})-h", h, relavance_map['positive']])
        # writer.writerow([f"({h},{r},{t})-t", t, relavance_map['positive']])

    #     queries = [(f"({h},{r},{t})-h", "head", h), (f"({h},{r},{t})-t", "tail", t)]
    #
    #     for query_id, direction, true_entity in queries:
    #         all_entities = set()
    #         rel_matrix = np.zeros((len(CORRUPTION_STRATEGIES), len(manager.entities)), dtype=int)
    #
    #         for strategy in CORRUPTION_STRATEGIES:
    #             if strategy == "LCWA" or strategy == "one-hop sensical" or strategy == "one-hop nonsensical":
    #                 continue
    #             # print(f"\t{strategy}")
    #             corrupted = manager.get_corrupted(h, r, t, direction, strategy)
    #             # print(f"\t{len(corrupted)}")
    #             row_idx = STRATEGY_IDX[strategy]
    #             for e in corrupted:
    #                 if e in ent_idx_map:
    #                     col_idx = ent_idx_map[e]
    #                     rel_matrix[row_idx][col_idx] = RELEVANCE_MAP[strategy]
    #                     all_entities.add(e)
    #
    #         # Add the positive entity
    #         if true_entity in ent_idx_map:
    #             # print(f"\tPositive entity: {true_entity}")
    #             idx = ent_idx_map[true_entity]
    #             for writer in [writer_max, writer_min, writer_floor, writer_ceil]:
    #                 writer.writerow([query_id, true_entity, RELEVANCE_MAP['positive']])
    #
    #         # Resolve and write for each candidate
    #         for e in all_entities:
    #             col_idx = ent_idx_map[e]
    #             row = rel_matrix[:, col_idx]
    #             if np.count_nonzero(row) == 0:
    #                 continue
    #             v_max, v_min, v_floor, v_ceil = resolve_policies(row)
    #
    #             writer_max.writerow([query_id, e, v_max])
    #             writer_min.writerow([query_id, e, v_min])
    #             writer_floor.writerow([query_id, e, v_floor])
    #             writer_ceil.writerow([query_id, e, v_ceil])
    #
    # f_max.close()
    # f_min.close()
    # f_floor.close()
    # f_ceil.close()
    # print("All qrels written with masking and tie-breaking applied.")
    # print(f"\tQrels file generated at: {os.path.basename(output_tsv)}")
        queries = [(f"({h},{r},{t})-h", "head", h), (f"({h},{r},{t})-t", "tail", t)]

        for query_id, direction, true_entity in queries:
            # Reset rel_matrix in-place to zero
            rel_matrix.fill(0)

            for strategy in CORRUPTION_STRATEGIES:
                if strategy == "LCWA":
                    continue
                corrupted = manager.get_corrupted(h, r, t, direction, strategy)
                row_idx = STRATEGY_IDX[strategy]
                for e in corrupted:
                    col_idx = ent_idx_map.get(e, -1)
                    if col_idx != -1:
                        rel_matrix[row_idx][col_idx] = RELEVANCE_MAP[strategy]

            if true_entity in ent_idx_map:
                for file in result_dict:
                    result_dict[file].append([query_id, true_entity, RELEVANCE_MAP['positive']])

            # Vectorized resolution
            nonzero_mask = np.any(rel_matrix > 0, axis=0)
            rel_matrix_nonzero = rel_matrix[:, nonzero_mask]
            col_indices = np.where(nonzero_mask)[0]

            if rel_matrix_nonzero.shape[1] == 0:
                continue

            max_vals = np.max(rel_matrix_nonzero, axis=0)
            min_vals = np.min(rel_matrix_nonzero, axis=0)
            avg_vals = np.floor(np.sum(rel_matrix_nonzero, axis=0) / np.count_nonzero(rel_matrix_nonzero, axis=0))
            avg_vals_ceil = np.ceil(np.sum(rel_matrix_nonzero, axis=0) / np.count_nonzero(rel_matrix_nonzero, axis=0))

            # compute this like a cube
            for idx, e_idx in enumerate(col_indices):
                e = entity_list[e_idx]
                result_dict[output_files[0]].append([query_id, e, int(max_vals[idx])])
                result_dict[output_files[1]].append([query_id, e, int(min_vals[idx])])
                result_dict[output_files[2]].append([query_id, e, int(avg_vals[idx])])
                result_dict[output_files[3]].append([query_id, e, int(avg_vals_ceil[idx])])

    if WRITE:
        # Write all results after computation
        for file, rows in result_dict.items():
            pu.write_qrel_rows(file, rows)

    # print("Qrels Generated successfully.")

    return result_dict


def generate_qrels_tsv_cube(manager, output_files):
    """
    Generates a TSV file containing qrels based on different corruption strategies.
    :param output_files: All the policy related output files
    :param manager: Triple Manager object.
    """
    RELEVANCE_MAP = {
        "LCWA": 0,
        "nonsensical": 1,
        "one-hop nonsensical": 2,
        "one-hop sensical": 3,
        "sensical": 4,
        "positive": 5
    }

    CORRUPTION_STRATEGIES = [
        "LCWA", "nonsensical", "one-hop nonsensical", "one-hop sensical", "sensical"
    ]

    STRATEGY_IDX = {strategy: idx for idx, strategy in enumerate(CORRUPTION_STRATEGIES)}

    POLICIES = ["max", "min", "avg_floor", "avg_ceil"]
    POLICY_IDX = {p: i for i, p in enumerate(POLICIES)}

    print(f"\tFinding corrupted Qrels for {len(manager.get_triples())} triples")

    entity_list = manager.entities
    entity_count = len(entity_list)
    ent_idx_map = {e: i for i, e in enumerate(entity_list)}
    num_strategies = len(CORRUPTION_STRATEGIES)

    rel_matrix = np.zeros((num_strategies, entity_count), dtype=int)

    result_cube = {}  # {query_id: cube [4, 5, num_entities]}

    for i, (h, r, t) in enumerate(manager.get_triples(), 1):
        print(f"Positive {i}: ({h}, {r}, {t})")

        queries = [(f"({h},{r},{t})-h", "head", h), (f"({h},{r},{t})-t", "tail", t)]

        for query_id, direction, true_entity in queries:
            rel_matrix.fill(0)

            for strategy in CORRUPTION_STRATEGIES:
                if strategy == "LCWA":
                    continue
                corrupted = manager.get_corrupted(h, r, t, direction, strategy)
                row_idx = STRATEGY_IDX[strategy]
                for e in corrupted:
                    col_idx = ent_idx_map.get(e, -1)
                    if col_idx != -1:
                        rel_matrix[row_idx][col_idx] = RELEVANCE_MAP[strategy]

            cube = np.zeros((4, num_strategies, entity_count), dtype=int)
            if true_entity in ent_idx_map:
                true_idx = ent_idx_map[true_entity]
                for policy in POLICY_IDX:
                    cube[POLICY_IDX[policy], :, true_idx] = RELEVANCE_MAP['positive']

            nonzero_mask = np.any(rel_matrix > 0, axis=0)
            rel_matrix_nonzero = rel_matrix[:, nonzero_mask]
            col_indices = np.where(nonzero_mask)[0]

            if rel_matrix_nonzero.shape[1] > 0:
                max_vals = np.max(rel_matrix_nonzero, axis=0)
                min_vals = np.min(rel_matrix_nonzero, axis=0)
                avg_vals = np.floor(np.sum(rel_matrix_nonzero, axis=0) / np.count_nonzero(rel_matrix_nonzero, axis=0))
                avg_vals_ceil = np.ceil(np.sum(rel_matrix_nonzero, axis=0) / np.count_nonzero(rel_matrix_nonzero, axis=0))

                for idx, e_idx in enumerate(col_indices):
                    for s in range(num_strategies):
                        cube[POLICY_IDX['max'], s, e_idx] = max_vals[idx]
                        cube[POLICY_IDX['min'], s, e_idx] = min_vals[idx]
                        cube[POLICY_IDX['avg_floor'], s, e_idx] = int(avg_vals[idx])
                        cube[POLICY_IDX['avg_ceil'], s, e_idx] = int(avg_vals_ceil[idx])

            result_cube[query_id] = cube

    result_dict = {output_files[i]: [] for i in range(4)}
    for query_id, cube in result_cube.items():
        for policy, idx in POLICY_IDX.items():
            for s in range(num_strategies):
                for e_idx, score in enumerate(cube[idx][s]):
                    if score > 0:
                        result_dict[output_files[idx]].append([query_id, entity_list[e_idx], score])

    for file, rows in result_dict.items():
        pu.write_qrel_rows(file, rows)

    print("Qrels written successfully.")


def main():
    test_datasets = [i for i in range(11)]

    test_datasets = [3]

    for dataset in test_datasets:
        start_time = time.time()

        # generate_qrels_tsv(dataset)

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
