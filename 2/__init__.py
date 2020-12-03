import re
import pykka
import itertools
import util
import math
from fastcore import utils
import operator
import traceback

class Answer(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.part1_answers = []
        self.part2_answers = []

    def on_receive(self, message):
        if message['part']==1:
            self.part1_answers.append(message)
        else:
            self.part2_answers.append(message)

    def on_stop(self):
        print("Part 1: %s"%len(self.part1_answers))
        print("Part 2: %s"%len(self.part2_answers))


class Validator(pykka.ThreadingActor):
    """Checks lower/upper bound occurence of character in string
    returns compare result
    """
    def __init__(self, opr):
        super().__init__()
        self.opr = opr

    def on_receive(self, message):
        limit, char, pswd = int(message[0]), message[1], message[2]
        return self.opr(list(pswd).count(char), limit)

class CharValidator(pykka.ThreadingActor):
    """Checks via xor if char is at two index in string
    """
    def on_receive(self, message):
        def xor(a,b):
            return bool(a) ^ bool(b)
        def get(s,i):
            i=int(i)-1 # elves start index at 1 not 0
            if i>len(s)-1 or i<0:
                print("index error!")
                return None
            return s[i]

        pswd = message.password
        a = message.upper
        b = message.lower
        char = message.char
        return xor(get(pswd, a)==char, get(pswd, b)==char)

class Rule:
    def __init__(self, lower, upper, char, password):
        utils.store_attr()
    __repr__ = utils.basic_repr('lower,upper,char,password')

class RuleChecker(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.lower = Validator.start(operator.ge)
        self.upper = Validator.start(operator.le)
        self.char_val = CharValidator.start()

    def on_receive(self, message):
        if isinstance(message, Rule):
            l = self.lower.ask((message.lower, message.char, message.password), block=False)
            u = self.upper.ask((message.upper, message.char, message.password), block=False)
            c = self.char_val.ask(message, block=False)
            r = pykka.get_all([l,u])
            if all(r):
                pykka.ActorRegistry.broadcast({'msg':message, 'part':1}, target_class=Answer)
            if c.get():
                pykka.ActorRegistry.broadcast({'msg':message, 'part':2}, target_class=Answer)

    def on_failure(self, exception_type, exception_value, tb):
        traceback.print_tb(tb)
        print(exception_value)

class Parser(pykka.ThreadingActor):
    """
    Splits the following
    `lower-upper character: string`
    """
    def __init__(self):
        super().__init__()
        self.pattern = re.compile("(\d+)-(\d+)\s([a-z]+):\s([a-z]+)")
        self.rule_checkers = [RuleChecker.start(), RuleChecker.start(), RuleChecker.start()]
        self.itr = itertools.cycle(self.rule_checkers)

    def on_receive(self, message):
        m = self.pattern.match(message)
        lower = m.group(1)
        upper = m.group(2)
        char = m.group(3)
        password = m.group(4)
        rule = Rule(lower, upper, char, password)
        act_ref = next(self.itr)
        act_ref.tell(rule)
    
    def on_failure(self, exception_type, exception_value, tb):
        traceback.print_tb(tb)
        print(exception_value)
    
    def on_stop(self):
        for a in self.rule_checkers:
            a.stop(block=True)


def main(inputfile):
    with open(inputfile, 'r') as f:
        ans = Answer.start()
        parser = Parser.start()
        for rule_line in f:
            parser.tell(rule_line)
        parser.stop(block=True)
        ans.stop()
    pykka.ActorRegistry.stop_all()
