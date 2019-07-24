import random
# Block IDs
# air 0
# dirt_block 1
# grass 2
# tree_branch 3
# wood 4
# leaves 5
# stone_block 6
# steel 7
# silver 8
# gold 9
# diamond 10
# window 11
map = []
for i in range(0, 300):
    current_row = []
    for j in range(0, 2000):
        current_row.append(0)
    map.append(current_row)
# Generate the varying dirt layer
for i in range(0, 2000):
    if random.random() < 0.2:
        map[150][i] = 1
# Generate -the fixed dirt layer
for i in range(0, 4):
    for j in range(0, 2000):
        map[151 + i][j] = 1
# Generate the rock layer
for i in range(0, 145):
    for j in range(0, 2000):
        rand_num = random.random()
        current_block = 6
        if rand_num <= 0.001:
             current_block = 7
        if 0.001 < rand_num <= 0.0015:
            current_block = 8
        if 0.0015 < rand_num <= 0.0018:
             current_block = 9
        if 0.0018 < rand_num <= 0.002:
             current_block = 10
        map[155 + i][j] = current_block

with open("map.mp","w") as f:
    for i in range(0, 300):
        for j in range(0, 2000):
            f.write(str(map[i][j])+" ")
        f.write("\n")



