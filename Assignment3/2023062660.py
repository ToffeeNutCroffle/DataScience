import sys
import math
noise = 'noise'

def parsing(file_path):
    points = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            id = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            points[id] = (x, y)
    return points

def find_neighbor(points, pid, eps):
    neighbors = []
    x1, y1 = points[pid]
    for id, (x2, y2) in points.items():
        dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        if dist <= eps:
            neighbors.append(id)
    return neighbors

def dbscan(points, eps, minPts):
    label = {}  
    clusters = []

    for p in points:
        if p in label:
            continue
        
        N = find_neighbor(points, p, eps)

        if len(N) < minPts:
            label[p] = noise
            continue

        c = len(clusters)
        label[p] = c
        S = []
        for temp in N:
            if temp != p:
                S.append(temp)

        
        for q in S:
            #undefined == not in label
            if q in label:
                if label[q] == noise:
                    label[q] = c
                continue

            N = find_neighbor(points, q, eps)
            label[q] = c
        
            if len(N) < minPts:
                continue

            S.extend(N)
        
        cluster = []
        for pid, cluster_id in label.items():
            if cluster_id == c:
                cluster.append(pid)
        clusters.append(cluster)

    return clusters


if __name__ == '__main__':
    input_file = sys.argv[1]
    n = int(sys.argv[2])
    eps = float(sys.argv[3])
    min_pts = int(sys.argv[4])

    points = parsing(input_file)
    clusters = dbscan(points, eps, min_pts)

    clusters.sort(key=len, reverse=True)
    clusters = clusters[:n]

    format = input_file
    if format.endswith('.txt'):
        format = format[:-4]

    i = 0
    for cluster in clusters:
        out_file = format + '_cluster_' + str(i) + '.txt'
        with open(out_file, 'w') as f:
            for pid in cluster:
                f.write(str(pid) + '\n')
        i += 1
