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
    j=random.random()
    if j < 0.2:
        map[150][i] = 1
        map[149][i] = 2
    if j<0.1:
        for k in range (i-2,i+3):
            map[150][k] = 1
            map[149][k] = 2
        map[149][i] = 1
        map[148][i] = 2
# Generate -the fixed dirt layer
for i in range(0, 4):
    for j in range(0, 2000):
        map[151 + i][j] = 1
        if map[150][j]!=1:
            map[150][j]=2
def house(n,map):
    for i in range (n,n+10):
        for j in range (141,151):
            map[j][i] = 4
    for k in range (136,141):
        y=k-136
        for x in range (n+5-y,n+5+y):
            map[k][x] = 4
    map[145][n+2]=11
    map[145][n+7]=11
    return map
def tree(n,map):
    for i in range (141,145):
        for k in range (n-3,n+4):
            map[i][k]=5
    for j in range (145,151):
        map[j][n]=3
    return map
ls=[]
for i in range(1,5):
    x=random.randint(1,1900)
    if x not in ls:
        map=house(x,map)
    for a in range (0,10):
        ls.append(x+a)
ls1=[]
for i in range(1,50):
    x=random.randint(1,1900)
    if x not in ls1:
        map=tree(x,map)
    for a in range (0,10):
        ls1.append(x+a) 
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