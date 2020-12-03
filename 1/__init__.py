import pykka
import itertools
import util
import math

class Answer(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.answers = []

    def on_receive(self, message):
        self.answers.append(message)
        print(message)
        a = math.prod(list(message))
        print(a)
    
    def on_stop(self):
        return self.answers


class Adder(pykka.ThreadingActor):
    def on_receive(self, message):
        s = sum(message)
        if s == 2020.0:
            pykka.ActorRegistry.broadcast(message, target_class=Answer)


def main(inputfile):
    with open(inputfile, 'r') as f:
        ans = Answer.start()
        adder = Adder.start()
        combos = itertools.combinations(f, 3)
        for combo in combos:
            combo = map(lambda x: float(x), combo)
            combo = list(combo)
            adder.tell(combo)
        adder.stop(block=True)
        ans.stop()
