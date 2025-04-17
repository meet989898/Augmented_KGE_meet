import numpy as np
import random
import sys
import math
from DataLoader.DataLoader import DataLoader


class TripleManager():
    def __init__(self, path, splits, batch_size=None, neg_rate=None, use_bern=False, seed=None,
                 corruption_mode="Global", pairing_mode="Paired"):
        """
        Initialize TripleManager and precompute corruption strategies.

        :param path: Path to dataset
        :param splits: Data splits to consider (train, validation, test)
        :param batch_size: Batch size
        :param neg_rate: Negative sampling rate
        :param use_bern: Whether to use Bernoulli sampling
        :param seed: Random seed
        :param corruption_mode: Corruption strategy
        :param pairing_mode: Whether negative pairs are required
        """
        print("Triple Manager Called")

        self.batch_size = batch_size
        self.neg_rate = neg_rate
        self.corruption_mode = corruption_mode  # Default mode

        self.entitySet = set()
        self.relSet = set()
        self.headDict, self.tailDict = {}, {}

        loaders = []
        self.tripleList = []

        for s in splits:
            loader = DataLoader(path, s)
            self.entitySet.update(range(loader.entityTotal))
            self.relSet.update(range(loader.relationTotal))

            if len(self.tripleList) == 0:
                self.tripleList = loader.getTriples()

            for r in loader.getHeadDict():
                if r not in self.headDict:
                    self.headDict[r] = {}
                for t in loader.getHeadDict()[r]:
                    self.headDict[r][t] = set(loader.getHeadDict()[r][t])

            for r in loader.getTailDict():
                if r not in self.tailDict:
                    self.tailDict[r] = {}
                for h in loader.getTailDict()[r]:
                    self.tailDict[r][h] = set(loader.getTailDict()[r][h])

        # Precompute corrupted entities for different strategies
        self.precompute_corruptions()

    def precompute_corruptions(self):
        """
        Precomputes corrupted entities for all strategies (sensical & non_sensical).
        """
        self.sensical_corruptions = {}
        self.nonsensical_corruptions = {}

        for r in self.relSet:
            # Sensical corruptions (NLCWA)
            self.sensical_corruptions[r] = {
                "head": set(self.headDict[r].keys()) if r in self.headDict else set(),
                "tail": set(self.tailDict[r].keys()) if r in self.tailDict else set()
            }

            # Expand with compatible relations
            for ri in self.domDomCompatible.get(r, []):
                self.sensical_corruptions[r]["head"].update(self.headDict.get(ri, {}).keys())
            for ri in self.domRanCompatible.get(r, []):
                self.sensical_corruptions[r]["head"].update(self.tailDict.get(ri, {}).keys())
            for ri in self.ranRanCompatible.get(r, []):
                self.sensical_corruptions[r]["tail"].update(self.tailDict.get(ri, {}).keys())
            for ri in self.ranDomCompatible.get(r, []):
                self.sensical_corruptions[r]["tail"].update(self.headDict.get(ri, {}).keys())

            # Non-sensical corruptions (random)
            self.nonsensical_corruptions[r] = {
                "head": self.entitySet,
                "tail": self.entitySet
            }

    def get_corrupted(self, h, r, t, type='head', corruption_mode=None):
        """
        Retrieves precomputed corrupted entities based on the corruption mode.

        :param h: Head entity
        :param r: Relation
        :param t: Tail entity
        :param type: Whether to corrupt the head or tail
        :param corruption_mode: 'sensical' or 'non_sensical' (optional override)
        :return: Set of corrupted entities
        """
        mode = corruption_mode if corruption_mode else self.corruption_mode

        if mode == "sensical":
            return self.sensical_corruptions[r]["head"] if type == "head" else self.sensical_corruptions[r]["tail"]
        elif mode == "non_sensical":
            return self.nonsensical_corruptions[r]["head"] if type == "head" else self.nonsensical_corruptions[r][
                "tail"]

    def get_batch(self, corruption_mode=None):
        """
        Generates a batch of positive and negative triples using precomputed corruptions.
        """
        bs = self.batch_size if self.batch_size <= len(self.tripleList) else len(self.tripleList)

        batch_seq_size = bs * (1 + self.neg_rate)
        batch_h = np.zeros(batch_seq_size, dtype=np.int64)
        batch_t = np.zeros(batch_seq_size, dtype=np.int64)
        batch_r = np.zeros(batch_seq_size, dtype=np.int64)
        batch_y = np.zeros(batch_seq_size, dtype=np.float32)

        for i_in_batch in range(bs):
            triple = self.tripleList[i_in_batch]
            batch_h[i_in_batch] = triple.h
            batch_t[i_in_batch] = triple.t
            batch_r[i_in_batch] = triple.r
            batch_y[i_in_batch] = 1  # Positive sample

            last = bs
            for times in range(self.neg_rate):
                ch, ct = triple.h, triple.t
                r = triple.r

                for _ in range(1 if self.pairing_mode == 'Paired' else random.randint(1, 10)):
                    if random.random() < 0.5:
                        ch = random.choice(list(self.get_corrupted(ch, r, ct, "head", corruption_mode)))
                    else:
                        ct = random.choice(list(self.get_corrupted(ch, r, ct, "tail", corruption_mode)))

                batch_h[i_in_batch + last] = ch
                batch_t[i_in_batch + last] = ct
                batch_r[i_in_batch + last] = r
                batch_y[i_in_batch + last] = -1  # Negative sample
                last += bs

        return {
            "batch_h": batch_h,
            "batch_t": batch_t,
            "batch_r": batch_r,
            "batch_y": batch_y
        }
