import sys
from itertools import combinations

support_cache = {}


def load_transactions(filename):
    transactions = []
    with open(filename, 'r') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            items = frozenset(int(x) for x in stripped.split('\t'))
            transactions.append(items)
    return transactions


def get_support(transactions, itemset):
    key = frozenset(itemset)
    if key in support_cache:
        return support_cache[key]

    count = 0
    for transaction in transactions:
        if key.issubset(transaction):
            count += 1

    result = count / len(transactions) * 100
    support_cache[key] = result
    return result


def get_frequent_1_itemsets(transactions, min_support):
    items = set()
    for transaction in transactions:
        for item in transaction:
            items.add(item)

    frequent = []
    for item in sorted(items):
        if get_support(transactions, [item]) >= min_support:
            frequent.append([item])

    return frequent


def generate_candidates(frequent_itemsets):
    candidates = []
    k = len(frequent_itemsets[0])
    frequent_set = set(map(tuple, frequent_itemsets))

    for i in range(len(frequent_itemsets)):
        for j in range(i + 1, len(frequent_itemsets)):
            if frequent_itemsets[i][:k-1] == frequent_itemsets[j][:k-1]:
                candidate = frequent_itemsets[i] + [frequent_itemsets[j][-1]]

                valid = True
                for subset in combinations(candidate, k):
                    if subset not in frequent_set:
                        valid = False
                        break

                if valid:
                    candidates.append(candidate)

    return candidates


def get_frequent_itemsets(transactions, candidates, min_support):
    frequent = []
    for candidate in candidates:
        if get_support(transactions, candidate) >= min_support:
            frequent.append(candidate)
    return frequent


def generate_rules(frequent_all, transactions):
    rules = []

    for itemsets in frequent_all:
        for itemset in itemsets:
            if len(itemset) < 2:
                continue

            for i in range(1, len(itemset)):
                for A in combinations(itemset, i):
                    A = list(A)
                    B = [x for x in itemset if x not in A]

                    support = get_support(transactions, itemset)
                    confidence = get_support(transactions, itemset) / get_support(transactions, A) * 100

                    rules.append((A, B, support, confidence))

    return rules


min_support = float(sys.argv[1])
input_file = sys.argv[2]
output_file = sys.argv[3]

transactions = load_transactions(input_file)
frequent_1 = get_frequent_1_itemsets(transactions, min_support)

frequent_all = [frequent_1]
current_frequent = frequent_1

while current_frequent:
    candidates = generate_candidates(current_frequent)
    if len(candidates) == 0:
        break

    current_frequent = get_frequent_itemsets(transactions, candidates, min_support)
    if len(current_frequent) == 0:
        break

    frequent_all.append(current_frequent)

rules = generate_rules(frequent_all, transactions)

with open(output_file, 'w', newline='\n') as f:
    for A, B, support, confidence in rules:
        A_str = '{' + ', '.join(map(str, A)) + '}'
        B_str = '{' + ', '.join(map(str, B)) + '}'
        f.write(f'{A_str}\t{B_str}\t{support:.2f}\t{confidence:.2f}\n')
