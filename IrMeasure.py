from collections import defaultdict
import ir_measures
import random
import time
from TripleManager import TripleManager
from DataLoader import DataLoader
import DatasetUtils
import PathUtils as pu
import GenerateQrels
import sys
import os
import csv


def generate_queries_and_qrels_old(dataset_path, sample_size=10):
    """
    Generates queries (head/tail corruptions) and relevance judgments (qrels).
    :param dataset_path: Path to dataset.
    :param sample_size: Number of queries to generate.
    """
    corruption_modes = ['LCWA', 'sensical', 'nonsensical']
    managers = ["train_manager", "valid_manager", "test_manager"]

    # Load the dataset
    train_loader = DataLoader(dataset_path, "train")
    val_loader = DataLoader(dataset_path, "valid")
    test_loader = DataLoader(dataset_path, "test")

    train_manager = TripleManager(train_loader)
    valid_manager = TripleManager(val_loader, train_loader)
    test_manager = TripleManager(test_loader, val_loader, train_loader)

    # Load dataset
    # train_loader = DataLoader(dataset_path, "train")
    # manager = TripleManager(train_loader, corruption_mode='LCWA')
    #
    # triples = random.sample(manager.get_triples(), min(sample_size, len(manager.get_triples())))
    queries = []
    qrels = []
    run = []

    for mode in corruption_modes:
        print(f"Benchmarking corruption mode: {mode}")
        for i, manager in enumerate([train_manager, valid_manager, test_manager]):
            print(f"\tTesting TripleManager {managers[i]} with", len(manager.get_triples()), "triples")
            # train_loader = DataLoader(dataset_path, "train")
            # manager = TripleManager(train_loader, corruption_mode=mode)

            triples = manager.get_triples()
            start_time = time.time()

            for h, r, t in triples:
                # Convert queries to string format
                head_query = f"({h}, {r}, ?)"
                tail_query = f"(?, {r}, {t})"

                # Head corruption query: (h, r, ?)
                corrupted_heads = manager.get_corrupted(h, r, t, 'head', mode)
                queries.append(head_query)
                qrels.extend([(h_neg, r, t, random.randint(0, 5)) for h_neg in corrupted_heads])
                run.extend([(h_neg, r, t, random.uniform(0, 1)) for h_neg in corrupted_heads])

                # Tail corruption query: (?, r, t)
                corrupted_tails = manager.get_corrupted(h, r, t, 'tail', mode)
                queries.append(tail_query)
                qrels.extend([(h, r, t_neg, random.randint(0, 5)) for t_neg in corrupted_tails])
                run.extend([(h, r, t_neg, random.uniform(0, 1)) for t_neg in corrupted_tails])

            elapsed_time = time.time() - start_time

            hours, minutes, seconds = int(elapsed_time // 3600), int((elapsed_time % 3600) // 60), elapsed_time % 60
            print(f"\tTime Taken: {hours} Hours, {minutes} Minutes, and {seconds:.3f} seconds.\n")

    return queries, qrels, run


def evaluate_ir_system_old(dataset_path):
    """
    Evaluates retrieval performance using ir-measures.
    :param dataset_path: Path to dataset.
    """
    queries, qrels, run = generate_queries_and_qrels_old(dataset_path)

    # Convert queries/qrels into expected IR format
    qrels_dict = {q: {str(doc): score for doc, _, _, score in qrels} for q in queries}
    run_dict = {q: {str(doc): score for doc, _, _, score in run} for q in queries}

    # print(qrels_dict)
    # print(run_dict)

    # Define retrieval measures to evaluate
    measures = [ir_measures.AP, ir_measures.P @ 10, ir_measures.NDCG @ 10]

    # Perform evaluation
    results = ir_measures.calc_aggregate(measures, qrels_dict, run_dict)

    print("\nIR Evaluation Results:")
    for measure, value in results.items():
        print(f"{measure}: {value:.4f}")


def load_top_k_scores_old(file_path):
    """
    Parses the Top-K Scores file and extracts queries, document IDs, and model scores.
    :param file_path: Path to the Top-K Scores file.
    :return: List of (query_id, document_id, score)
    """
    qrels = []
    run = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # print(line)
            parts = line.strip().split()
            if len(parts) != 3:
                print("Invalid number of elements found")
                continue  # Skip invalid lines, if any

            query_raw, neg_doc_id, score = parts
            neg_doc_id = int(float(neg_doc_id))  # Convert float to int
            score = float(score)  # Model prediction score

            # Extract query type (head/tail corruption)
            if query_raw.endswith('-h'):
                query_id = query_raw.replace('-h', '')  # Format: (h, r, t)-h → head corruption
            elif query_raw.endswith('-t'):
                query_id = query_raw.replace('-t', '')  # Format: (h, r, t)-t → tail corruption
            else:
                print("Invalid line found")
                continue  # Skip malformed queries, if any

            # Assign relevance score
            relevance_score = random.randint(1, 5)  # Not sure yet how to use this. ASK PROFESSOR
            qrels.append((query_id, neg_doc_id, relevance_score))
            run.append((query_id, neg_doc_id, score))

    return qrels, run


def evaluate_ir_from_top_k_v_old(directory_path):
    """
    Evaluates retrieval performance using Top-K Scores data.
    :param top_k_file: Path to the Top-K Scores file.
    """
    all_qrels = []
    all_run = []

    for filename in os.listdir(directory_path):
        if filename.endswith(".tsv"):  # Only process TSV files
            file_path = os.path.join(directory_path, filename)
            print(f"Processing {filename}...")
            qrels, run = load_top_k_scores_old(file_path)
            all_qrels.extend(qrels)
            all_run.extend(run)

    # Convert qrels and run into IR-measures format
    qrels_dict = {}
    for q, doc, score in all_qrels:
        if q not in qrels_dict:
            qrels_dict[q] = {}
        qrels_dict[q][str(doc)] = score

    run_dict = {}
    for q, doc, score in all_run:
        if q not in run_dict:
            run_dict[q] = {}
        run_dict[q][str(doc)] = score

    # Define evaluation measures
    measures = [ir_measures.AP, ir_measures.P @ 10, ir_measures.NDCG @ 10]

    # Perform evaluation
    results = ir_measures.calc_aggregate(measures, qrels_dict, run_dict)

    print("\nIR Evaluation Results from Top-K Scores:")
    for measure, value in results.items():
        print(f"{measure}: {value:.4f}")


def load_qrels(qrels_file):
    """
    Loads qrels from a TSV file.
    :param qrels_file: Path to the qrels TSV file.
    :return: Dictionary of qrels {query_id: {doc_id: relevance_score}}
    """
    print("Loading qrels...")
    qrels_dict = {}

    # with open(qrels_file, 'r', encoding='utf-8') as file:
    #     reader = csv.reader(file, delimiter='\t')
    #     for query_id, doc_id, relevance in reader:
    #         if query_id not in qrels_dict:
    #             qrels_dict[query_id] = {}
    #         qrels_dict[query_id][str(doc_id)] = int(relevance)

    with open(qrels_file, 'r', encoding='utf-8') as file:
        # reader = csv.reader(file, delimiter='\t')
        for line in file:
            parts = line.strip().split()
            query_id, doc_id, relevance = parts
            # for query_id, doc_id, relevance in reader:
            if query_id not in qrels_dict:
                qrels_dict[query_id] = {}
            qrels_dict[query_id][str(int(float(doc_id)))] = int(relevance)

    print("Qrels loaded.")
    return qrels_dict


def load_run(run_file):
    """
    Loads retrieval run data from a TSV file.
    :param run_file: Path to the run TSV file.
    :return: Dictionary of run {query_id: {doc_id: model_score}}
    """
    print("Loading run...")
    run_dict = {}

    # with open(run_file, 'r', encoding='utf-8') as file:
    #     reader = csv.reader(file, delimiter='\t')
    #     for query_id, doc_id, score in reader:
    #         if query_id not in run_dict:
    #             run_dict[query_id] = {}
    #         run_dict[query_id][str(doc_id)] = float(score)

    with open(run_file, 'r', encoding='utf-8') as file:
        # reader = csv.reader(file, delimiter='\t')
        for line in file:
            parts = line.strip().split()
            query_id, doc_id, score = parts
        # for query_id, doc_id, score in reader:
            if query_id not in run_dict:
                run_dict[query_id] = {}
            run_dict[query_id][str(int(float(doc_id)))] = float(score)

    print("Run loaded.")
    return run_dict


def evaluate_ir_from_top_k_old(run_path, qrel_path):
    """
    Evaluates retrieval performance using Top-K Scores data.
    :param qrel_path: Folder from where relevance scores are fetched
    :param run_path: Folder from where models run scores are fetched
    """
    # all_qrels = []
    # all_run = []

    output_file = "3_Nell_IrMeasures.txt"

    qrels_dict = load_qrels(qrel_path)

    # Write results to file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("IR Evaluation Results:\n\n")
        print("IR Evaluation Results:\n\n")
        for filename in os.listdir(run_path):
            if filename.endswith(".tsv"):  # Only process TSV files
                file_path = os.path.join(run_path, filename)

                if filename != "boxe_resplit__0_bottom.tsv" and filename != "boxe_resplit__0_top.tsv":
                    continue

                print(f"\nProcessing {filename}...")
                file.write(f"\nProcessing {filename}...\n")
                # qrels, run = load_top_k_scores(file_path)
                # all_qrels.extend(qrels)
                # all_run.extend(run)

                run_dict = load_run(file_path)

                # Define all official IR measures
                base_measures = [
                    ir_measures.AP, ir_measures.BPref, ir_measures.MAP, ir_measures.MRR, ir_measures.RR
                ]

                # Measures that support @K
                at_k_measures = [ir_measures.P, ir_measures.NDCG, ir_measures.Recall, ir_measures.Success, ir_measures.R]

                # Extend @K evaluations from 10 to 50 - 100
                for k in range(10, 60, 10):
                    for measure in at_k_measures:
                        base_measures.append(measure @ k)

                # Perform IR evaluation
                results = ir_measures.calc_aggregate(base_measures, qrels_dict, run_dict)

                for measure, value in results.items():
                    file.write(f"{measure}: {value:.4f}\n")
                    print(f"{measure}: {value:.4f}\n")

        print(f"IR Evaluation Results saved to {output_file}")


def evaluate_ir_from_top_k(run_path, qrel_path, dataset_name, output_json_path):
    qrels_dict = load_qrels(qrel_path)

    # Define evaluation measures
    base_measures = [
        ir_measures.AP, ir_measures.BPref, ir_measures.MAP, ir_measures.MRR, ir_measures.RR
    ]

    # at_k_measures = [ir_measures.P(rel=1), ir_measures.NDCG(rel=1), ir_measures.Recall(rel=1),
    #                  ir_measures.Success(rel=1), ir_measures.R(rel=1)]

    at_k_measures = [ir_measures.P, ir_measures.NDCG, ir_measures.Recall,
                     ir_measures.Success, ir_measures.R]

    k_values = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90]

    for k in range(100, 501, 50):
        k_values.append(k)

    print(k_values)

    for k in k_values:
        for measure in at_k_measures:
            base_measures.append(measure @ k)

    results_json = {
        "metadata": {
            "dataset": dataset_name,
            "rel_threshold": 1,
            "k_values": k_values,
            "metrics": [str(m) for m in base_measures],
            "model": "boxe"
        },
        "results": {}
    }

    results_json["metadata"]["relevance"] = {
        "LCWA": 0,
        "nonsensical": 1,
        "one-hop nonsensical": 2,
        "one-hop sensical": 3,
        "sensical": 4,
        "positive": 5
    }

    results_json["metadata"]["hyperparameters"] = {
        "compatible_threshold": 0.75,
        "similarity_method": "overlap",  # or dice/jaccard/etc.
        "alpha": 0.5,
        "beta": 0.5
    }

    for filename in os.listdir(run_path):
        if not filename.endswith(".tsv"):
            continue

        if filename != "boxe_resplit__0_bottom.tsv" and filename != "boxe_resplit__0_top.tsv":
            continue

        print(f"Processing {filename}...")
        run_dict = load_run(os.path.join(run_path, filename))
        eval_result = ir_measures.calc_aggregate(base_measures, qrels_dict, run_dict)

        parsed = pu.parse_run_filename(filename)
        results_json["results"][filename] = {
            **parsed,
            "metrics": {
                str(measure): float(f"{value:.4f}") for measure, value in eval_result.items()
            }
        }

    pu.write_json_file(output_json_path, results_json)
    print(f"IR Evaluation Results written to {output_json_path}")


def test_ir_measure(dataset):
    dataset_name = DatasetUtils.get_dataset_name(dataset)

    print(f"Testing {dataset}.{dataset_name}")

    folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\"

    path = folder + "Datasets/" + dataset_name + "/"

    # validate_negatives(path)
    evaluate_ir_system_old(path)


def qrel_file_path_generate(dataset):

    folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\General Tests\\Generated_Qrels_TSV\\"

    dataset_name = DatasetUtils.get_dataset_name(dataset)

    path = folder + f"{dataset}_{dataset_name}\\3_NELL-995_0_resplit_qrels_avg_ceil.tsv"

    return path


def count_lines_in_tsv(file_path):
    """Counts the number of lines in a TSV file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return sum(1 for line in file)


def analyze_qrels_conflicts(qrels_file, output_summary):
    """
    Identifies cases where the same query-document pair appears with different relevance scores.
    Writes a summary of these conflicts to a text file.

    :param qrels_file: Path to the qrels TSV file.
    :param output_summary: Path to the summary text file.
    """
    print("Finding conflicting pairs...")
    conflicts = {}
    conflicting_pairs = {}

    with open(qrels_file, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split()
            query_id, doc_id, relevance = parts
            key = (query_id, doc_id)

            if key in conflicts:
                conflicting_pairs[key] = [conflicts[key], relevance]
            else:
                conflicts[key] = relevance

    print(f"Found {len(conflicting_pairs)} conflicting pairs...")

    # Identify conflicting entries
    # conflicting_pairs = {k: v for k, v in conflicts.items() if len(v) > 1}

    # Write summary
    with open(output_summary, 'w', encoding='utf-8') as out_file:
        out_file.write("Conflicting Qrels Summary:\n\n")
        for (query_id, doc_id), scores in conflicting_pairs.items():
            out_file.write(f"Query: {query_id}, Document: {doc_id}, Relevance Scores: {sorted(scores)}\n")

    print(f"Summary of conflicts saved to: {output_summary}")


def main():
    test_datasets = [3]

    TopK_Scores_folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\General Tests\\TopK_Scores\\"

    Generated_Qrels_folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\General Tests\\Generated_Qrels_TSV\\"

    Output_folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\General Tests\\IR_Measures\\"

    for dataset in test_datasets:
        start_time = time.time()

        dataset_path = TopK_Scores_folder + f"{dataset}"

        dataset_name = DatasetUtils.get_dataset_name(dataset)

        qrel_file_path = Generated_Qrels_folder + f"{dataset}_{dataset_name}\\3_NELL-995_0_resplit_qrels_Avg_Ceil.tsv"

        dataset_output_path = Output_folder + f"{dataset}_{dataset_name}\\IR_Measures_Results.json"

        # test_ir_measure(dataset)
        # GenerateQrels.generate_qrels_tsv(dataset)
        evaluate_ir_from_top_k(dataset_path, qrel_file_path, dataset_name, dataset_output_path)

        # load_qrels(qrel_file_path(dataset))
        # print(count_lines_in_tsv(qrel_file_path(dataset))) # 199976994 ~ 200 Million

        # analyze_qrels_conflicts(qrel_file_path(dataset), f"{dataset}_qrel_conflicts.txt")

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
