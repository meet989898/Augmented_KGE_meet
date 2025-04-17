# import ir_measures
# import ir_datasets
#
# # Load ANTIQUE dataset
# dataset = ir_datasets.load("antique")
#
# print("Available components:", dir(dataset))
#
# # Convert qrels to dictionary format
# qrels_dict = {}
# for qrel in dataset.judgments_iter():
#     if qrel.query_id not in qrels_dict:
#         qrels_dict[qrel.query_id] = {}
#     qrels_dict[qrel.query_id][qrel.doc_id] = qrel.relevance
#
# # Simulated retrieval scores (Random for now)
# run_dict = {}
# for query in dataset.queries_iter():
#     run_dict[query.query_id] = {}
#     for doc in dataset.docs_iter():
#         run_dict[query.query_id][doc.doc_id] = 1.0  # Simulated relevance score
#
# # Define evaluation measures
# measures = [ir_measures.AP, ir_measures.P@10, ir_measures.NDCG@10]
#
# # Compute evaluation
# results = ir_measures.calc_aggregate(measures, qrels_dict, run_dict)
#
# print("ANTIQUE IR Evaluation Results:")
# for measure, value in results.items():
#     print(f"{measure}: {value:.4f}")


import ir_datasets
import ir_measures
import random
from collections import defaultdict
import os
import sys

os.environ["PYTHONUTF8"] = "1"  # Force UTF-8 for Windows
sys.stdout.reconfigure(encoding="utf-8")  # Ensure UTF-8 output



def load_antique_data(sample_size=10):
    """
    Loads a sample of queries, documents, and creates synthetic qrels for ANTIQUE dataset.
    """
    dataset = ir_datasets.load("antique")

    queries = []
    docs = {}
    qrels = defaultdict(dict)
    run = defaultdict(dict)

    # Load a sample of documents
    for doc in dataset.docs_iter():
        doc_text = doc.text.encode('utf-8', 'ignore').decode('utf-8')  # Fix encoding
        docs[doc.doc_id] = doc_text  # Store corrected text in dictionary

        if len(docs) >= sample_size * 10:  # Load 10x documents for retrieval
            break

    # Create synthetic qrels and queries
    for i, doc_id in enumerate(docs.keys()):
        query_id = f"q{i}"
        query_text = f"Find information about: {docs[doc_id][:50]}..."
        queries.append((query_id, query_text))

        # Assign random relevance (1 for relevant, 0 for non-relevant)
        for neg_doc_id in random.sample(list(docs.keys()), min(5, len(docs))):
            qrels[query_id][neg_doc_id] = 1 if random.random() > 0.7 else 0
            run[query_id][neg_doc_id] = random.uniform(0, 1)  # Simulated ranking score

    return queries, qrels, run


def evaluate_antique_ir():
    """
    Evaluates IR performance on the ANTIQUE dataset using synthetic qrels.
    """
    queries, qrels, run = load_antique_data()

    # Define evaluation measures
    measures = [ir_measures.AP, ir_measures.P @ 10, ir_measures.NDCG @ 10]

    # Compute evaluation
    results = ir_measures.calc_aggregate(measures, qrels, run)

    print("ANTIQUE IR Evaluation Results:")
    for measure, value in results.items():
        print(f"{measure}: {value:.4f}")


# Run the evaluation
# evaluate_antique_ir()

import ir_measures
# Get all available measures
all_measures = list(ir_measures.iter_supported())

# Print the full list
print("Available IR Measures:")
for measure in all_measures:
    print(measure)

