from pkg_resources import resource_filename
from random import randint, choice
import linecache
import re

__all__ = ["getword", "getname"]

counts = {
    'noun': 877,
    'adjective': 1132,
    'verb': 631,
    'adverb': 401
}


def callback(match):
    return getword(match.group(0)[1:-1])


def getfilename(t):
    f = 'data/%s.txt' if t[-1] == 's' else 'data/%ss.txt'
    return resource_filename('namesake', f % (t,))


def getword(t):
    return linecache.getline(getfilename(t), randint(1, counts[t])).strip()


def getname():
    templates = ['{adjective}-{noun}', '{adverb}-{verb}']
    template = "%s-%d" % (choice(templates), randint(1, 999))
    return re.sub('({(?:noun|adjective|adverb|verb)})', callback, template)


def main():
    print(getname())
