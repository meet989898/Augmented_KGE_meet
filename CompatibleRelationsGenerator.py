import numpy as np
import json
import ast
import os


class CompatibleRelationsGenerator:
    def __init__(self, headDict, tailDict, domain, range, threshold=0.75):
        """
        Initialize with precomputed domain, range, headDict, and tailDict.

        Args:
            headDict (dict): {relation: {tail: set(heads)}}
            tailDict (dict): {relation: {head: set(tails)}}
            domain (dict): {relation: set of head entities}
            range (dict): {relation: set of tail entities}
        """
        self.headDict = headDict
        self.tailDict = tailDict
        self.domain = domain
        self.range = range
        self.threshold = threshold

        self.domDomCompatible = {}
        self.domRanCompatible = {}
        self.ranDomCompatible = {}
        self.ranRanCompatible = {}

    def compute_compatible_relations(self, threshold=0.75, method="overlap", alpha=0.5, beta=0.5):
        """
        Compute compatible relations based on entity overlaps.

        Args:
            threshold (float): Overlap coefficient threshold for compatibility.
            method (str): Similarity measure to use (options: "overlap", "jaccard",
                          "dice", "cosine", "tversky").
            alpha (float): Tversky parameter for weighting A-B.
            beta (float): Tversky parameter for weighting B-A.
        """
        relation_list = list(self.domain.keys())

        # Convert dictionary sets to NumPy arrays for faster computations
        domain_arrays = {r: np.array(list(self.domain[r])) for r in self.domain}
        range_arrays = {r: np.array(list(self.range[r])) for r in self.range}

        for r1 in relation_list:
            self.domDomCompatible[r1] = []
            self.domRanCompatible[r1] = []
            self.ranDomCompatible[r1] = []
            self.ranRanCompatible[r1] = []

            for r2 in relation_list:
                if r1 == r2:
                    continue  # Skip self-comparison

                # Compute overlaps using NumPy
                domain_overlap = self._compute_similarity(domain_arrays[r1], domain_arrays[r2], method, alpha, beta)
                range_overlap = self._compute_similarity(range_arrays[r1], range_arrays[r2], method, alpha, beta)
                dom_ran_overlap = self._compute_similarity(domain_arrays[r1], range_arrays[r2], method, alpha, beta)
                ran_dom_overlap = self._compute_similarity(range_arrays[r1], domain_arrays[r2], method, alpha, beta)

                # Apply thresholds
                if domain_overlap > threshold:
                    self.domDomCompatible[r1].append(r2)
                if dom_ran_overlap > threshold:
                    self.domRanCompatible[r1].append(r2)
                if ran_dom_overlap > threshold:
                    self.ranDomCompatible[r1].append(r2)
                if range_overlap > threshold:
                    self.ranRanCompatible[r1].append(r2)

        # for key, value in self.domDomCompatible.items():
        #     print(type(key), key, type(value), value)

    # ---------------------------------------------------------------
    # Overlap Coefficient:
    # The overlap coefficient measures the similarity between two sets
    # based on their intersection size relative to the smaller set.
    #
    # Formula:
    #     Overlap(A, B) = |A ∩ B| / min(|A|, |B|)
    #
    # Where:
    #     - A and B are two sets.
    #     - |A ∩ B| is the number of common elements.
    #     - min(|A|, |B|) ensures normalization based on the smaller set.
    #
    # This metric ranges from 0 (no overlap) to 1 (complete subset match).
    #
    # References:
    # - Wikipedia: https://en.wikipedia.org/wiki/Overlap_coefficient
    #
    # ---------------------------------------------------------------
    def _compute_overlap(self, array1, array2):
        """ Compute overlap coefficient between two NumPy arrays. """
        if array1.size == 0 or array2.size == 0:
            return 0.0
        intersection = np.intersect1d(array1, array2).size
        return intersection / min(array1.size, array2.size)

    def _compute_similarity(self, array1, array2, method="overlap", alpha=0.5, beta=0.5):
        """
        Compute similarity between two NumPy arrays using different methods.

        Args:
            array1 (np.array): First entity set.
            array2 (np.array): Second entity set.
            method (str): Similarity measure ("overlap", "jaccard", "dice", "cosine", "tversky").
            alpha (float): Tversky parameter for weighting A-B.
            beta (float): Tversky parameter for weighting B-A.

        Returns:
            float: Similarity score (0 to 1).
        """
        if array1.size == 0 or array2.size == 0:
            return 0.0

        intersection_size = np.intersect1d(array1, array2).size
        len_a = array1.size
        len_b = array2.size
        union_size = len_a + len_b - intersection_size

        # ---------------------------------------------------------------
        # 1. Overlap Coefficient:
        # Measures how much one set is a subset of another.
        # Formula: Overlap(A, B) = |A ∩ B| / min(|A|, |B|)
        # Reference: https://en.wikipedia.org/wiki/Overlap_coefficient
        # ---------------------------------------------------------------
        if method == "overlap":
            return intersection_size / min(len_a, len_b)

        # ---------------------------------------------------------------
        # 2. Jaccard Similarity:
        # Measures similarity considering both intersection and union.
        # Formula: Jaccard(A, B) = |A ∩ B| / |A ∪ B|
        # Reference: https://en.wikipedia.org/wiki/Jaccard_index
        # ---------------------------------------------------------------
        elif method == "jaccard":
            return intersection_size / union_size

        # ---------------------------------------------------------------
        # 3. Sørensen-Dice Coefficient (Dice Similarity):
        # Weighs intersection more heavily.
        # Formula: Dice(A, B) = (2 * |A ∩ B|) / (|A| + |B|)
        # Reference: https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient
        # ---------------------------------------------------------------
        elif method == "dice":
            return (2 * intersection_size) / (len_a + len_b)

        # ---------------------------------------------------------------
        # 4. Cosine Similarity:
        # Treats sets as vectors in a multi-dimensional space.
        # Formula: Cosine(A, B) = |A ∩ B| / (sqrt(|A|) * sqrt(|B|))
        # Reference: https://en.wikipedia.org/wiki/Cosine_similarity
        # ---------------------------------------------------------------
        elif method == "cosine":
            return intersection_size / (np.sqrt(len_a) * np.sqrt(len_b))

        # ---------------------------------------------------------------
        # 5. Tversky Index:
        # A generalized form allowing asymmetric weighting.
        # Formula: Tversky(A, B) = |A ∩ B| / (|A ∩ B| + α |A - B| + β |B - A|)
        # Reference: https://en.wikipedia.org/wiki/Tversky_index
        # ---------------------------------------------------------------
        elif method == "tversky":
            a_minus_b = len_a - intersection_size
            b_minus_a = len_b - intersection_size
            return intersection_size / (intersection_size + alpha * a_minus_b + beta * b_minus_a)

        else:
            raise ValueError(f"Unknown similarity method: {method}")

    def save_to_file(self, file_path="compatible_relations.txt"):
        """ Save the computed compatible relations to a file. """
        with open(file_path, "w") as file:
            # json.dump(self.domDomCompatible, file)
            file.write(str(dict(sorted(self.domDomCompatible.items()))) + "\n")
            # json.dump(self.domRanCompatible, file)
            file.write(str(self.domRanCompatible) + "\n")
            # json.dump(self.ranDomCompatible, file)
            file.write(str(self.ranDomCompatible) + "\n")
            # json.dump(self.ranRanCompatible, file)
            file.write(str(self.ranRanCompatible) + "\n")

    def load_from_file(self, file_path="compatible_relations.txt"):
        """ Load the compatible relations from a file. """
        with open(file_path, "r") as file:
            self.domDomCompatible = json.loads(file.readline())
            self.domRanCompatible = json.loads(file.readline())
            self.ranDomCompatible = json.loads(file.readline())
            self.ranRanCompatible = json.loads(file.readline())

    def generate(self):
        """ Main function to compute and save compatible relations. """
        self.compute_compatible_relations(self.threshold)
        self.save_to_file()


class Triple():
    """
        Triple is the class that contains functionality for triples
    """
    __slots__ = "h", "r", "t"

    def __init__(self, h, r, t):
        """
            Initialise a triples
        Args:
            h (int): Head entity
            r (int): Relation entity
            t (int): Tail entity
        """
        self.h = h
        self.r = r
        self.t = t

    def __eq__(self, other):
        """
            Checks for equality between two triples
        Args:
            other (Triple): Triple object to be compared to

        Returns:
            bool: Returns true if triples are equal, false otherwise
        """
        return (self.h, self.r, self.t) == (other.h, other.r, other.t)

    def __str__(self):
        """
        Converts triple into a string

        Returns:
            str: [h,r,t]
        """
        return "[" + str(self.h) + "," + str(self.r) + "," + str(self.t) + "]"

    def __hash__(self):
        return int(self.pi(self.pi(self.h, self.r), self.t))

    def __str__(self):
        return str(self.h) + " " + str(self.r) + " " + str(self.t)

    # https://en.wikipedia.org/wiki/Pairing_function#Cantor_pairing_function
    def pi(self, k1, k2):
        return .5 * (k1 + k2) * (k1 + k2 + 1) + k2


class DataLoader(object):

    def __init__(self, path, type):
        """
        Init function to initialise the data loader

        Args:
            path (str): Path to folder containing dataset
            type (str): Type of split to load. Type can be "train", "test", "valid"

        Returns:

        """

        print(f"Data Loader Initialised with type {type} and path {path}")

        self.path = path
        self.headEntities = set()
        self.tailEntities = set()
        self.relations = set()
        self.headDict = {}
        self.tailDict = {}
        self.domain = {}
        self.range = {}
        self.domDomCompatible = {}
        self.domRanCompatible = {}
        self.ranDomCompatible = {}
        self.ranRanCompatible = {}
        self.triple_count_by_pred = {}

        # Just reads the first line from the file to get the total types of relations
        self.relationTotal = 0
        relationPath = path + "relation2id.txt"
        with open(relationPath) as fp:
            self.relationTotal = int(fp.readline())

        # Just reads the first line from the file to get the total nodes
        self.entityTotal = 0
        entityPath = path + "entity2id.txt"
        with open(entityPath, encoding='utf-8') as fp:
            self.entityTotal = int(fp.readline())

        # Read the files for creating the graph
        filePath = path + type + "2id.txt"
        self.list = self.importFile(filePath)

        # Generate compatible relations using existing dictionaries
        generator = CompatibleRelationsGenerator(self.headDict, self.tailDict, self.domain, self.range)
        generator.generate()

        def load_compatible_from_file():
            # Get all the data from these files directly in the form of dictionaries
            if os.path.isfile(path + "compatible_relations.txt"):
                with open(path + "compatible_relations.txt") as fp:
                    self.domDomCompatible = ast.literal_eval(fp.readline())
                    self.domRanCompatible = ast.literal_eval(fp.readline())
                    self.ranDomCompatible = ast.literal_eval(fp.readline())
                    self.ranRanCompatible = ast.literal_eval(fp.readline())

        # load_compatible_from_file()

        def load_compatible_from_generator():
            self.domDomCompatible = generator.domDomCompatible
            self.domRanCompatible = generator.domRanCompatible
            self.ranDomCompatible = generator.ranDomCompatible
            self.ranRanCompatible = generator.ranRanCompatible

        load_compatible_from_generator()

        self.relation_anomaly = {}
        for r in self.relations:
            self.relation_anomaly[r] = 0
        if os.path.isfile(path + "relation2anomaly.txt"):
            with open(path + "relation2anomaly.txt") as fp:
                line = fp.readline()
                while line:
                    pair = line.strip().split()
                    self.relation_anomaly[int(pair[0])] = float(pair[1])
                    line = fp.readline()

    def importFile(self, filePath):
        """
        Function to import file

        Args:
            filePath (str): Path to file that is required to be opened

        Returns:

        """
        list = []
        with open(filePath) as fp:
            fp.readline()
            line = fp.readline()
            while line:
                triple = line.strip().split()
                h = int(triple[0])
                t = int(triple[1])
                r = int(triple[2])

                self.headEntities.add(h)
                self.tailEntities.add(t)
                self.relations.add(r)

                if r not in self.headDict:
                    self.headDict[r] = {}
                    self.domain[r] = set()
                if r not in self.tailDict:
                    self.tailDict[r] = {}
                    self.range[r] = set()
                if r not in self.triple_count_by_pred:
                    self.triple_count_by_pred[r] = 0

                if t not in self.headDict[r]:
                    self.headDict[r][t] = set()
                if h not in self.tailDict[r]:
                    self.tailDict[r][h] = set()

                self.headDict[r][t].add(h)
                self.tailDict[r][h].add(t)
                self.domain[r].add(h)
                self.range[r].add(t)

                self.triple_count_by_pred[r] += 1

                triple = Triple(h, r, t)
                list.append(triple)
                line = fp.readline()

        return list

    def getTriples(self):
        """
        Returns the list of triples

        Returns:
            list (list): List of all triples

        """
        return self.list

    def getHeadEntities(self):
        """
        Returns all the entites that appear in the head

        Returns:
            headEntities (set): Set of all entities that appear in the head

        """
        return self.headEntities

    def getTailEntities(self):
        """
        Returns all the entites that appear in the tail

        Returns:
            tailEntities (set): Set of all entities that appear in the tail

        """
        return self.tailEntities

    def getHeadDict(self):
        """
        Returns a dictionary where keys are relations and values are head entities for that relation

        Returns:
            headDict (dict): Head dictionary

        """
        return self.headDict

    def getTailDict(self):
        """
        Returns a dictionary where keys are relations and values are tail entities for that relation

        Returns:
            tailDict (dict): Tail dictionary

        """
        return self.tailDict

    def getDomain(self):
        """
        Returns a dictionary where keys are relations and values are the domain for that relation

        Returns:
            domain (dict): Domain dictionary

        """
        return self.domain

    def getRange(self):
        """
        Returns a dictionary where keys are relations and values are the range for that relation

        Returns:
            range (dict): Range dictionary

        """
        return self.range


def main():
    path = "Datasets/WN18/"
    file_type = "train"

    file_path = os.path.join(os.path.dirname(__file__), "..", path)

    loader = DataLoader(file_path, file_type)


if __name__ == "__main__":
    main()
