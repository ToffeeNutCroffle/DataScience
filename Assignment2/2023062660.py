import sys
import math
from collections import Counter


def entropy(data, label_col):
    counts = Counter(row[label_col] for row in data)
    total = len(data)
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)


def information_gain(data, attribute, label_col):
    total = len(data)
    base_entropy = entropy(data, label_col)

    subsets = {}
    for row in data:
        val = row[attribute]
        if val not in subsets:
            subsets[val] = []
        subsets[val].append(row)

    weighted_entropy = sum(
        (len(subset) / total) * entropy(subset, label_col)
        for subset in subsets.values()
    )
    return base_entropy - weighted_entropy


def split_information(data, attribute):
    total = len(data)
    counts = Counter(row[attribute] for row in data)
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)


def gain_ratio(data, attribute, label_col):
    ig = information_gain(data, attribute, label_col)
    si = split_information(data, attribute)
    if si == 0:
        return 0
    return ig / si


def majority_class(data, label_col):
    counts = Counter(row[label_col] for row in data)
    return counts.most_common(1)[0][0]


def build_tree(data, attributes, label_col):
    labels = [row[label_col] for row in data]

    if len(set(labels)) == 1:
        return labels[0]

    if not attributes:
        return majority_class(data, label_col)

    best_attr = max(attributes, key=lambda a: gain_ratio(data, a, label_col))

    default = majority_class(data, label_col)
    tree = {'_attr': best_attr, '_default': default, '_branches': {}}

    remaining = [a for a in attributes if a != best_attr]

    subsets = {}
    for row in data:
        val = row[best_attr]
        if val not in subsets:
            subsets[val] = []
        subsets[val].append(row)

    for val, subset in subsets.items():
        tree['_branches'][val] = build_tree(subset, remaining, label_col)

    return tree


def classify(tree, row):
    if not isinstance(tree, dict):
        return tree

    attr = tree['_attr']
    val = row.get(attr)

    if val not in tree['_branches']:
        return tree['_default']

    return classify(tree['_branches'][val], row)


def read_tsv(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().strip().split('\n')
    headers = lines[0].split('\t')
    data = []
    for line in lines[1:]:
        values = line.split('\t')
        row = {headers[i]: values[i] for i in range(len(values))}
        data.append(row)
    return headers, data


def main():
    train_file = sys.argv[1]
    test_file = sys.argv[2]
    result_file = sys.argv[3]

    train_headers, train_data = read_tsv(train_file)
    label_col = train_headers[-1]
    attributes = train_headers[:-1]

    tree = build_tree(train_data, attributes, label_col)
    default = majority_class(train_data, label_col)

    test_headers, test_data = read_tsv(test_file)

    result_headers = test_headers + [label_col]
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write('\t'.join(result_headers) + '\n')
        for row in test_data:
            label = classify(tree, row)
            if label is None:
                label = default
            values = [row[h] for h in test_headers] + [label]
            f.write('\t'.join(values) + '\n')


if __name__ == '__main__':
    main()
