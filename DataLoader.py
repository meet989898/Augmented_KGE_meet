import numpy as np
import PathUtils


class DataLoader(object):

    def __init__(self, path, split_type):
        # rather than path just the function to read the folder
        # split_type (str): Type of split to load. Type can be "train", "test", "valid"
        self.path = path
        self.split_type = split_type
        self.head_entities = set()
        self.tail_entities = set()
        self.relations = set()
        self.head_dict = {}
        self.tail_dict = {}
        self.domain = {}
        self.range = {}
        self.domDomCompatible = {}
        self.domRanCompatible = {}
        self.ranDomCompatible = {}
        self.ranRanCompatible = {}
        self.triple_count_by_pred = {}

        self.entities = PathUtils.get_entities(self.path)

        self.triple_list = []
        self.import_file(path + split_type + "2id.txt")

        # print(f"DL {split_type} Created")

    def import_file(self, file_path):
        with open(file_path) as fp:
            for line in fp:
                triple = line.strip().split()
                if len(triple) != 3:
                    continue

                h, t, r = triple
                h, t, r = int(h), int(t), int(r)

                self.head_entities.add(h)
                self.tail_entities.add(t)
                self.relations.add(r)

                if r not in self.head_dict:
                    self.head_dict[r] = {}
                    self.domain[r] = set()
                if r not in self.tail_dict:
                    self.tail_dict[r] = {}
                    self.range[r] = set()
                if r not in self.triple_count_by_pred:
                    self.triple_count_by_pred[r] = 0

                if t not in self.head_dict[r]:
                    self.head_dict[r][t] = set()
                if h not in self.tail_dict[r]:
                    self.tail_dict[r][h] = set()

                self.head_dict[r][t].add(h)
                self.tail_dict[r][h].add(t)
                self.domain[r].add(h)
                self.range[r].add(t)

                self.triple_count_by_pred[r] += 1

                self.triple_list.append((h, r, t))

        # Transform all to numpy arrays.
        self.head_dict = {r: {t: np.array(list(self.head_dict[r][t]))
                              for t in self.head_dict[r]} for r in self.head_dict}
        self.tail_dict = {r: {h: np.array(list(self.tail_dict[r][h]))
                              for h in self.tail_dict[r]} for r in self.tail_dict}

        self.domain = {r: np.array(list(self.domain[r])) for r in self.domain}
        self.range = {r: np.array(list(self.range[r])) for r in self.range}

    def get_triples(self):
        return self.triple_list
