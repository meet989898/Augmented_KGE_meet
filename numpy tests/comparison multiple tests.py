import numpy as np
import time
import pandas as pd


def benchmark_set_operations(iterations=10, sizes=None):
    if sizes is None:
        sizes = [100, 1000, 10000, 100000, 1000000]
    results = []

    for size in sizes:
        np_union_times, np_intersection_times = [], []
        py_union_times, py_intersection_times = [], []

        for _ in range(iterations):
            # Generate random datasets
            set1 = np.random.randint(0, size * 10, size=size)
            set2 = np.random.randint(0, size * 10, size=size)

            # Convert to Python sets
            py_set1, py_set2 = set(set1), set(set2)

            # NumPy union
            start = time.time()
            np.union1d(set1, set2)
            np_union_times.append(time.time() - start)

            # NumPy intersection
            start = time.time()
            np.intersect1d(set1, set2)
            np_intersection_times.append(time.time() - start)

            # Python set union
            start = time.time()
            py_set1.union(py_set2)
            py_union_times.append(time.time() - start)

            # Python set intersection
            start = time.time()
            py_set1.intersection(py_set2)
            py_intersection_times.append(time.time() - start)

        # Store averaged results
        results.append({
            "Dataset Size": size,
            "NumPy Union (Avg Time s)": np.mean(np_union_times),
            "NumPy Intersection (Avg Time s)": np.mean(np_intersection_times),
            "Python Set Union (Avg Time s)": np.mean(py_union_times),
            "Python Set Intersection (Avg Time s)": np.mean(py_intersection_times)
        })

    # Convert results to DataFrame and print
    df = pd.DataFrame(results)
    print(df.to_string(index=False))


# Run the benchmark
benchmark_set_operations()
