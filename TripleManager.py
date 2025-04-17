import numpy as np
from collections import defaultdict
from DataLoader import DataLoader
import DatasetUtils
import time


class TripleManager:
    def __init__(self, main_loader, *secondary_loaders):
        """
        Initializes the TripleManager with a main data loader and optional secondary loaders.

        :param main_loader: The primary DataLoader instance
        :param secondary_loaders: Optional secondary DataLoader instances
        """
        self.main_loader = main_loader
        self.secondary_loaders = secondary_loaders

        # Aggregating structures across all loaders
        self.head_dict = defaultdict(lambda: defaultdict(set))
        self.tail_dict = defaultdict(lambda: defaultdict(set))
        self.domain = defaultdict(set)
        self.range = defaultdict(set)
        self.entities = np.array(list(main_loader.entities))  # Convert to NumPy array for efficiency? Still testing

        # Unioning all structures
        self._aggregate_structures()

        # Convert sets to NumPy arrays for efficiency
        self._convert_to_numpy()

        # Get the pre-made compatible relations dictionaries
        self.compatible_relations = self._build_compatible_relations()

        print(f"TM {main_loader.split_type} Created")

    def _aggregate_structures(self):
        """Precomputes the union of domains and relations from all provided loaders."""
        for loader in (self.main_loader, *self.secondary_loaders):
            for r in loader.head_dict:
                for t, heads in loader.head_dict[r].items():
                    self.head_dict[r][t].update(heads)

            for r in loader.tail_dict:
                for h, tails in loader.tail_dict[r].items():
                    self.tail_dict[r][h].update(tails)

            for r, dom_entities in loader.domain.items():
                self.domain[r].update(dom_entities)

            for r, range_entities in loader.range.items():
                self.range[r].update(range_entities)

        self.dom_dom = self.main_loader.domDomCompatible
        self.dom_ran = self.main_loader.domRanCompatible
        self.ran_dom = self.main_loader.ranDomCompatible
        self.ran_ran = self.main_loader.ranRanCompatible

    def _convert_to_numpy(self):
        """Converts sets in dictionaries to NumPy arrays for optimized operations."""
        for r in self.head_dict:
            for t in self.head_dict[r]:
                self.head_dict[r][t] = np.array(list(self.head_dict[r][t]))
        for r in self.tail_dict:
            for h in self.tail_dict[r]:
                self.tail_dict[r][h] = np.array(list(self.tail_dict[r][h]))

        # Convert these to numpy too to be used in corruption modes
        for r in self.domain:
            self.domain[r] = np.array(list(self.domain[r]))
        for r in self.range:
            self.range[r] = np.array(list(self.range[r]))

    def get_triples(self):
        """Returns all triples in the main data loader."""
        return self.main_loader.get_triples()

    def _build_compatible_relations(self):
        """
        Constructs a unified compatible_relations dictionary based on type of compatibility.

        :return: Dictionary {(r, elem_type): [(r', elem_type'), ...]}
        """
        compat = {}
        all_relations = set(self.dom_dom.keys()) | set(self.dom_ran.keys()) | \
                        set(self.ran_dom.keys()) | set(self.ran_ran.keys())

        for r in all_relations:
            domain_compat = []
            range_compat = []

            if r in self.dom_dom:
                domain_compat.extend([(r_prime, "domain") for r_prime in self.dom_dom[r]])
            if r in self.dom_ran:
                domain_compat.extend([(r_prime, "range") for r_prime in self.dom_ran[r]])
            if r in self.ran_dom:
                range_compat.extend([(r_prime, "domain") for r_prime in self.ran_dom[r]])
            if r in self.ran_ran:
                range_compat.extend([(r_prime, "range") for r_prime in self.ran_ran[r]])

            compat[(r, "domain")] = domain_compat
            compat[(r, "range")] = range_compat

        return compat

    def _get_elements(self, relation, elem_type):
        """
        Retrieves the set of elements (domain or range) for a given relation.

        :param relation: Relation ID or name
        :param elem_type: Either 'domain' or 'range'
        :return: Set of entities
        """
        if elem_type == "domain":
            return self.domain.get(relation, np.array([]))
        elif elem_type == "range":
            return self.range.get(relation, np.array([]))
        else:
            raise ValueError("elem_type must be 'domain' or 'range'")

    def _get_extended_elements(self, relation, elem_type):
        """
        Computes the union of compatible elements for one-hop extended corruption.

        :param relation: Relation ID or name
        :param elem_type: 'domain' or 'range'
        :return: Union of compatible elements (set)
        """
        extended = set()
        for (rel_prime, type_prime) in self.compatible_relations.get((relation, elem_type), []):
            elems = self._get_elements(rel_prime, type_prime)
            extended.update(elems)
        return np.array(list(extended))

    def get_corrupted_old(self, h, r, t, corruption_type='tail', corruption_mode='LCWA'):
        """
        Corrupts a given triple using the specified corruption mode.
        :param h: Head entity
        :param r: Relation
        :param t: Tail entity
        :param corruption_type: Either 'head' or 'tail'
        :param corruption_mode: Either 'LCWA' or 'sensical' or 'nonsensical'
        :return: A NumPy array of corrupted entities
        """
        if corruption_mode == 'LCWA':
            if corruption_type == 'tail':
                return np.setdiff1d(self.entities, self.tail_dict[r].get(h, np.empty(0)), assume_unique=True)
            elif corruption_type == 'head':
                return np.setdiff1d(self.entities, self.head_dict[r].get(t, np.empty(0)), assume_unique=True)

        elif corruption_mode == 'sensical':
            if corruption_type == 'tail':#
                # self.get_elements(r, "range", self.domain, self.range)
                # self.get_extended_elements(r, "range", self.compatible_dict, self.domain, self.range)
                return np.setdiff1d(self.range[r], self.tail_dict[r].get(h, np.array([])), assume_unique=True)
            elif corruption_type == 'head':
                # self.get_elements(r, "domain", self.domain, self.range)
                # self.get_extended_elements(r, "domain", self.compatible_dict, self.domain, self.range)
                return np.setdiff1d(self.domain[r], self.head_dict[r].get(t, np.array([])), assume_unique=True)

        elif corruption_mode == 'nonsensical':
            if corruption_type == 'tail':
                # self.get_elements(r, "domain", self.domain, self.range)
                # self.get_extended_elements(r, "domain", self.compatible_dict, self.domain, self.range)
                return np.setdiff1d(self.domain[r], self.tail_dict[r].get(h, np.array([])), assume_unique=True)
            elif corruption_type == 'head':
                # self.get_elements(r, "range", self.domain, self.range)
                # self.get_extended_elements(r, "range", self.compatible_dict, self.domain, self.range)
                return np.setdiff1d(self.range[r], self.head_dict[r].get(t, np.array([])), assume_unique=True)

        else:
            raise ValueError("corruption_mode must be 'LCWA', 'sensical', or 'nonsensical'")

    def get_corrupted(self, h, r, t, corruption_type='tail', corruption_mode='LCWA'):
        if corruption_mode == 'LCWA':
            if corruption_type == 'tail':
                return np.setdiff1d(self.entities, self.tail_dict[r].get(h, np.empty(0)), assume_unique=True)
            elif corruption_type == 'head':
                return np.setdiff1d(self.entities, self.head_dict[r].get(t, np.empty(0)), assume_unique=True)

        elif corruption_mode == 'sensical':
            if corruption_type == 'tail':
                extended_range = self._get_elements(r, "range")
                return np.setdiff1d(extended_range, self.tail_dict[r].get(h, np.array([])), assume_unique=True)
            elif corruption_type == 'head':
                extended_domain = self._get_elements(r, 'domain')
                return np.setdiff1d(extended_domain, self.head_dict[r].get(t, np.array([])), assume_unique=True)

        elif corruption_mode == 'nonsensical':
            if corruption_type == 'tail':
                extended_domain = self._get_elements(r, 'domain')
                return np.setdiff1d(extended_domain, self.tail_dict[r].get(h, np.array([])), assume_unique=True)
            elif corruption_type == 'head':
                extended_range = self._get_elements(r, 'range')
                return np.setdiff1d(extended_range, self.head_dict[r].get(t, np.array([])), assume_unique=True)

        elif corruption_mode == 'one-hop sensical':
            if corruption_type == 'tail':
                extended_range = self._get_extended_elements(r, 'range')
                return np.setdiff1d(extended_range, self.tail_dict[r].get(h, np.array([])), assume_unique=True)
            elif corruption_type == 'head':
                extended_domain = self._get_extended_elements(r, 'domain')
                return np.setdiff1d(extended_domain, self.head_dict[r].get(t, np.array([])), assume_unique=True)

        elif corruption_mode == 'one-hop nonsensical':
            if corruption_type == 'tail':
                extended_domain = self._get_extended_elements(r, 'domain')
                return np.setdiff1d(extended_domain, self.tail_dict[r].get(h, np.array([])), assume_unique=True)
            elif corruption_type == 'head':
                extended_range = self._get_extended_elements(r, 'range')
                return np.setdiff1d(extended_range, self.head_dict[r].get(t, np.array([])), assume_unique=True)

        else:
            raise ValueError("Unsupported corruption_mode: {}".format(corruption_mode))

    # def get_corrupted_new_old(self, h, r, t, corruption_type='tail'):
    #     """
    #     Corrupts a given triple by replacing either the head or the tail.
    #
    #     :param h: Head entity
    #     :param r: Relation
    #     :param t: Tail entity
    #     :param corruption_type: Either 'head' or 'tail'
    #     :return: A set of corrupted entities
    #     """
    #     if corruption_type == 'tail':
    #         return np.setdiff1d(self.entities, self.tail_dict[r].get(h, np.array([])), assume_unique=True)
    #     elif corruption_type == 'head':
    #         return np.setdiff1d(self.entities, self.head_dict[r].get(t, np.array([])), assume_unique=True)
    #     else:
    #         raise ValueError("corruption_type must be either 'head' or 'tail'")
    #
    #
    # def get_corrupted_vold(self, h, r, t, type='head'):
    #     # headEntities and tailEntities point to -1 for every relation when using Global.
    #     if type == "head":
    #         corrupted = set(self.headEntities[r]) - self.headDict[r][t]
    #     elif type == "tail":
    #         corrupted = set(self.tailEntities[r]) - self.tailDict[r][h]
    #     return corrupted


def end_time(start_time):
    # Print the total execution time of the entire code
    total_time = time.time() - start_time
    time_taken = (f"\tTime Taken: "
                  f"{total_time // 3600} Hours, "
                  f"{(total_time % 3600) // 60} Minutes, "
                  f"and {(total_time % 3600) % 60} seconds.")
    print(time_taken)


# test case
def test_triple_manager(dataset):
    dataset_name = DatasetUtils.get_dataset_name(dataset)

    print(f"Testing {dataset}.{dataset_name}")

    folder = "D:\\Masters\\RIT\\Semesters\\Sem 4\\RA\\Augmented KGE\\"

    path = folder + "Datasets/" + dataset_name + "/"

    train_loader = DataLoader(path, "train")
    val_loader = DataLoader(path, "valid")
    test_loader = DataLoader(path, "test")

    train_manager = TripleManager(train_loader)
    valid_manager = TripleManager(val_loader, train_loader)
    test_manager = TripleManager(test_loader, val_loader, train_loader)

    for manager in [train_manager, valid_manager, test_manager]:
        print(f"\tTesting TripleManager with", len(manager.get_triples()), "triples")
        for triple in manager.get_triples():
            print(f"Triple: {triple}")
            h, r, t = triple
            corrupted_heads = manager.get_corrupted(h, r, t, 'head')
            corrupted_tails = manager.get_corrupted(h, r, t, 'tail')
            # corrupted_heads_old = manager.get_corrupted_old(h, r, t, 'head')
            # corrupted_tails_old = manager.get_corrupted_old(h, r, t, 'tail')
            # print(f"Original: ({h}, {r}, {t})")
            print(f"New Corrupted Heads: {list(corrupted_heads)[:5]}")
            print(f"New Corrupted Tails: {list(corrupted_tails)[:5]}")
            # print(f"Old Corrupted Heads: {list(corrupted_heads_old)[:5]}")
            # print(f"Old Corrupted Tails: {list(corrupted_tails_old)[:5]}")


def test_all_datasets():
    test_datasets = [i for i in range(12)]

    test_datasets = [11]

    for dataset in test_datasets:
        start_time = time.time()

        test_triple_manager(dataset)

        end_time(start_time)


def main():
    test_all_datasets()


if __name__ == "__main__":
    main()
