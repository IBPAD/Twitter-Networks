import glob
import os
import json
import sys
import argparse

from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--screen-name", required=True, help="Screen name of twitter user")
args = vars(ap.parse_args())

SEED = args['screen_name']

users = defaultdict(lambda: { 'followers': 0 })

for f in glob.glob('twitter-users/*.json'):
    print("loading " + str(f))
    data = json.load(open(f))
    screen_name = data['screen_name']
    users[screen_name] = { 'followers': data['followers_count'], 'id':data['id'], 'name':data['name'] }

def process_follower_list(screen_name, edges=[], depth=0, max_depth=5):
    f = os.path.join('following', screen_name + '.csv')
    print("processing " + str(f))

    if not os.path.exists(f):
        return edges

    followers = [line.strip().split('\t') for line in open(f)]

    for follower_data in followers:
        if len(follower_data) < 2:
            continue

        screen_name_2 = follower_data[1]

        # use the number of followers for screen_name as the weight
        weight = users[screen_name]['followers']

        edges.append([users[screen_name]['id'], follower_data[0], weight])

        if depth+1 < max_depth:
            process_follower_list(screen_name_2, edges, depth+1, max_depth)

    return edges

edges = process_follower_list(SEED, max_depth=5)

def process_follower_nodes(screen_name, nodes=[], depth=0, max_depth=5):
    f = os.path.join('following', screen_name + '.csv')
    print("processing " + str(f))

    if not os.path.exists(f):
        return nodes

    followers = [line.strip().split('\t') for line in open(f)]

    for follower_data in followers:
        if len(follower_data) < 2:
            continue

        screen_name_2 = follower_data[1]

        nodes.append([users[screen_name]['id'], users[screen_name]['name']])

        if depth+1 < max_depth:
            process_follower_nodes(screen_name_2, nodes, depth+1, max_depth)

    return nodes

nodes = process_follower_nodes(SEED, max_depth=5)

with open('twitter_network_edges.csv', 'w') as outf:
    edge_exists = {}
    for edge in edges:
        key = ','.join([str(x) for x in edge])
        if not(key in edge_exists):
            outf.write('%s,%s,%d\n' % (edge[0], edge[1], edge[2]))
            edge_exists[key] = True

with open('twitter_network_nodes.csv', 'w') as outf:
    node_exists = {}
    for node in nodes:
        key = ','.join([str(x) for x in node])
        if not(key in node_exists):
            outf.write('%s,%s\n' % (node[0], node[1]))
            node_exists[key] = True
