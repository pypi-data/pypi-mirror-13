import random
from random import random as rand
from random import choice
from collections import deque as queue
from math import floor
try:
    from collections import UserDict
    from itertools import accumulate
except ImportError:
    from backwards_compat import old_accumulate
    accumulate = old_accumulate
    from UserDict import UserDict
import bisect

class AbstractElement:
    def __init__(self, element, terminal=False):
        self.element = element
        self.isTerminal = terminal
        return
    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return self.element == other.element and self.isTerminal == other.isTerminal
        else:
            return False
    def __hash__(self):
        return hash((self.element,self.isTerminal))


class ProbDict(UserDict):

    def __init__(self):
        try:
            super().__init__(self)
        except TypeError:
            UserDict.__init__(self)
        return

    def __getitem__(self,key):
        weightedoptions = list(self.data[key].items())
        choices, weights = zip(*weightedoptions)
        cumdist = list(accumulate(weights))
        x = random.random() * cumdist[-1]
        return choices[bisect.bisect(cumdist, x)]

    def __setitem__(self,key,value):
        if key not in self.data:
            self.data[key] = {value:1}
        else:
            if value in self.data[key]:
                self.data[key][value] += 1
            else:
                self.data[key][value] = 1
        return


#MarkovModel takes a sequence of sequences and a depth and creates a model using
# the ProbDict class. Class must be instantiated before calling any of its methods.

#resynth- method used in instantiation and in strengthening based on new
# sequences to feed the model.

#generate- method used to put out new sequence based on succession probabilities
# in the mappings ProbDict.
class MarkovModel:

    def __init__(self,metasequence = [],depth = 1):
        self.mappings = ProbDict()
        self.initlists = ProbDict()
        self.depth = depth
        for sequence in metasequence:
            self.resynth(sequence)
        return

    def resynth(self,sequence):
        running_list = queue([])
        for i, element in enumerate(sequence):
            wrappedelem = AbstractElement(element,i == len(sequence)-1)
            if (len(running_list) < self.depth):
                running_list.append(wrappedelem)
                if (i == self.depth-1):
                    self.initlists[None] = tuple(running_list)
            else:
                self.mappings[tuple(running_list)] = wrappedelem
                running_list.popleft()
                running_list.append(wrappedelem)
        return

    def generate(self):
        running_list = queue(self.initlists[None])
        generated_sequence = []
        for elem in running_list:
            generated_sequence.append(elem.element)
            if elem.isTerminal:
                return generated_sequence
        next_elem = self.mappings[tuple(running_list)]
        running_list.popleft()
        running_list.append(next_elem)
        generated_sequence.append(next_elem.element)

        while not next_elem.isTerminal:
            next_elem = self.mappings[tuple(running_list)]
            running_list.popleft()
            running_list.append(next_elem)
            generated_sequence.append(next_elem.element)

        return generated_sequence
