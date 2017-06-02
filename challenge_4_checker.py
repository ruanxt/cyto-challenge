from collections import defaultdict
from solution_checker import read_key_file
import argparse
import csv
import sys


def parseargs():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('submitted_answer')
    parser.add_argument('solution_key')
    parser.add_argument('-n', '--new', action='append',
                        help=('Specify novel class. '
                              'Can be used multiple times'))
    args = parser.parse_args()
    return args.submitted_answer, args.solution_key, set(args.new)


def get_known_classes(solution, novel_classes):
    """Gets all classes that the challengers should already know"""
    known_classes = set()
    for line in csv.reader(open(solution)):
        for class_ in line[1:]:
            class_ = class_.strip()
            if class_ in novel_classes:
                continue
            known_classes.add(class_)
    return known_classes


def get_novel_ids(solution, novel_classes):
    """Gets all ids with novel classes, and their full annotations"""
    novel = {}
    for line in csv.reader(open(solution)):
        id_ = line[0]
        classes = {x.strip() for x in line[1:]}

        if any(x in classes for x in novel_classes):
            novel[id_] = classes
    return novel


def translate_unknowns(submitted, novel, known_classes):
    novel_to_submitted = defaultdict(lambda: defaultdict(int))
    submitted_to_novel = defaultdict(lambda: defaultdict(int))
    submitted_translation = {}
    occupied = set()
    for id_ in novel:
        submitted_classes = submitted.get(id_)
        if submitted_classes is None or submitted_classes[0] == '':
            print('%s has a bad input line' % id_)
            sys.exit(1)
        submitted_classes = set(submitted_classes) - known_classes
        solution_classes = novel[id_] - known_classes

        for c in solution_classes:
            for d in submitted_classes:
                novel_to_submitted[c][d] += 1
                submitted_to_novel[d][c] += 1

    # I am aware that this is fugly, but it works
    # translates the classes submitted by the competitor into the novel class
    # that is present the most times for that unknown class.
    # If for example the class UC1 has been applied to the class A twice and
    # the class B once, UC1 will be translated to A in every instance.
    for d in submitted_to_novel:
        max_ = -1
        current = ''
        for c in submitted_to_novel[d]:
            if submitted_to_novel[d][c] > max_:
                max_ = submitted_to_novel[d][c]
                current = c
        occupied.add(current)
        submitted_translation[d] = current

    for sub in submitted:
        sub_classes = submitted[sub]
        for i in range(len(sub_classes)):
            if sub_classes[i] in submitted_translation:
                sub_classes[i] = submitted_translation[sub_classes[i]]
    return submitted

def main():
    submitted_answer, solution_key, novel_classes = parseargs()
    known_classes = get_known_classes(solution_key, novel_classes)
    novel = get_novel_ids(solution_key, novel_classes)
    submitted = read_key_file(submitted_answer)
    translated_submitted = translate_unknowns(submitted, novel, known_classes)


if __name__ == '__main__':
    main()
