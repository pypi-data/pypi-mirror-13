# -*- coding:utf-8 -*-

"""
    String similarity measure.
"""


def tokenize(string, length):
    """Split a string into a set of length-grams
    http://en.wikipedia.org/wiki/N-gram"""
    ngrams = set()
    for i in range(len(string) - length - 1):
        ngrams.add(string[i:i + length])
    return ngrams


def dice_coefficient(set1, set2):
    """Sørensen–Dice coefficient
    http://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient"""
    divisor = len(set1) + len(set2)
    if not divisor:
        return 0
    return 2.0 * len(set1 & set2) / divisor


def string_similarity(n, s1, s2):
    """Return an index of similarity between the two strings.
    Higher values indicate more similarity.
    Note: you'll get better performance by tokenizing the search
    string once and calling dice_coefficient directly."""
    return dice_coefficient(tokenize(s1, n), tokenize(s2, n))


def list_similarity(n, s1, s_list):
    """Return an ordered list of tuples in the form (similarity index, string),
    by matching the reference string against each string in the specified list.
    Ordered from more to less similar."""
    t1 = tokenize(s1, n)
    sim = [(dice_coefficient(t1, tokenize(s2, n)), s2) for s2 in s_list]
    sim.sort(reverse=True)
    return sim


if __name__ == '__main__':
    print(list_similarity(3, "sheet", ["cow", "sheep"]))
