# sstvis
Python (PyGame) visualizer for sst (https://github.com/hugoledoux/sst)


# Usage
`cat data\crop_10.sma | python sstvis.py`

Leave PyGame window open; don't click away

## Continuous pipe
`./target/release/sstfin ./data/crop.laz 10 |  ./target/release/sstdt | python sstvis.py | ./target/release/sstobj > ~/temp/crop.obj`
