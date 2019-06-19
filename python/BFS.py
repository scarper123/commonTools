#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-06-17 16:26:26
# @Author  : Shanming Liu
# @Version : 1.0


def bfs(graph, start):
    explored, queue = set(), [start]
    explored.add(start)

    while queue:
        v = queue.pop(0)
        for w in graph[v]:
            if w not in explored:
                explored.add(w)
                queue.append(w)

    return explored


def main():
    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'F'],
        'D': ['B'],
        'E': ['B', 'F'],
        'F': ['C', 'E']
    }
    print(bfs(graph, 'A'))


if __name__ == '__main__':
    main()
