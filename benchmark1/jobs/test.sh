#!/bin/sh

python ../code/auen4.1.ff.py --user pbalapra --trainfile ../data/breast.train1.csv --testfile ../data/breast.test1.csv --outputfile ../results/result.json

python ../code/leaderboard.py --benchmarkName benchmark1 --jsonFileName ../results/result.json

python ../code/leaderboard.py --benchmarkName benchmark1
