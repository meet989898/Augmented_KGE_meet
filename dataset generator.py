import os


def create_sample_dataset(base_path):
    """
    Creates a small sample dataset in the given base path, structured similarly to existing datasets.
    :param base_path: The folder where the dataset should be created.
    """
    os.makedirs(base_path, exist_ok=True)

    entities = {
        "entity2id.txt": [
            "Alice 0", "Bob 1", "Charlie 2", "David 3", "Eve 4"
        ],
        "relation2id.txt": [
            "knows 0", "likes 1", "works_with 2"
        ],
        "train2id.txt": [
            "0 1 0",  # Alice knows Bob
            "1 2 0",  # Bob knows Charlie
            "2 3 1",  # Charlie likes David
            "3 4 2"  # David works_with Eve
        ],
        "valid2id.txt": [
            "1 3 1",  # Bob likes David
            "2 4 2"  # Charlie works_with Eve
        ],
        "test2id.txt": [
            "0 2 0",  # Alice knows Charlie
            "3 1 1"  # David likes Bob
        ]
    }

    for filename, lines in entities.items():
        with open(os.path.join(base_path, filename), 'w') as f:
            f.write("\n".join(lines) + "\n")

    print(f"Sample dataset created at {base_path}")


# Example usage
create_sample_dataset("D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\Datasets\\Sample Test")
