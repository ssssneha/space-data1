import json
import sys
import math
import csv
import random

# My modules
import satellite
import satutils
import bot

# shuffle
def shuffle(path):
    max_switches = 20
    switches = int (random.random()*max_switches) + 1
    length = len(path) - 1
    
    for i in range(switches):
        a = int (random.random()*length)
        b = int (random.random()*length)
        #print(f"{a}, {b}, {length}")
        temp = path[a]
        path[a] = path[b]
        path[b] = temp
    return path

# genetic
def gen_genetic_path(bot):
    bot_home = bot.create_similar()
    population = 100
    # Create initial population
    members = []
    member = bot_home.create_similar()
    member.clean_ALL_debris(bot.path)
    members.append(member)
    for i in range(population-1):
        member_bot = bot_home.create_similar()
        new_path = bot.path
        new_path = shuffle(new_path)
        member_bot.clean_ALL_debris(new_path)
        members.append(member_bot)

    # Sort
    members.sort(key=lambda x: x.dist_travelled, reverse=False)
    print(f"Best solution: {members[0].dist_travelled}")

    # Evolution loops
    for i in range(10000):
        #print(f"Evolution: {i}")
        # Natural Selection
        members = members[0: int(population/2)]
        for j in range(0, int(population/2), 2):
            #print(f"Here: {j}")
            # Recombination
            child1 = marry(members[j], members[j+1])
            child2 = marry(members[j+1], members[j])
            # Mutation
            mutate(child1)
            mutate(child2)
            #print(child1.path)
            #print(child2.path)
            child1.clean_ALL_debris(child1.path)
            child2.clean_ALL_debris(child2.path)
            #print(f"Cleaned:")
            members.append(child1)
            members.append(child2)
            #print(f"Woah")
        # Best candidate
        members.sort(key=lambda x: x.dist_travelled, reverse=False)
        if i%1000 == 0:
            for k in range(10):
                print(f"Best solution: {members[k].dist_travelled}, [{i}], k={k}")

    return members[0]

# marry
def marry(parent1, parent2):
    num_sat = len(parent1.path)
    new_path = parent1.path[0: int (num_sat/2)]
    for i in range(num_sat):
        if parent2.path[i] not in new_path:
            new_path.append(parent2.path[i])
    new_bot = parent1.create_similar()
    new_bot.path = new_path
    return new_bot

# mutate
def mutate(member):
    path = member.path
    max_switches = int (len(path) * 0.2)
    if max_switches == 0:
        switches = 1
    else:
        switches = max_switches
    length = len(path) - 1
    
    for i in range(switches):
        #print(f"Switching: {i}")
        a = int (random.random()*length)
        b = int (random.random()*length)
        temp = path[a]
        path[a] = path[b]
        path[b] = temp
    
    member.path = path

    return member

def gen_greedy_path(box_data, bot):

    for i in range(len(box_data)):
        min_dist = -1
        best_sat = box_data[0]
        for sat in box_data:
            if not sat in bot.path:
                dist = bot.get_dist_sat(sat)
                if dist < min_dist or min_dist < 0:
                    min_dist = dist
                    best_sat = sat

        
        if best_sat == None:
            print ("Something bad happened")
            sys.exit()
        #print(best_sat)
        bot.clean_debris(best_sat)
        print(bot.dist_travelled)
    return bot

# main
if __name__ == "__main__":
    

    if len(sys.argv) != 2:
        print("Usage: python genetic_path.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    
    #print(input_file)
    #output_file = sys.argv[2]

    print(f"Reading from file {input_file}")
    sat_data = satutils.get_sat_data(input_file)

    #print(sat_data)
    bot = bot.Bot(-7250, 0, 0, 1000)
    box_data = satutils.box_sat(sat_data, bot)

    bot = gen_greedy_path(box_data, bot)
    
    print(f"Best from Greedy: {bot.dist_travelled}")
    
    #new_bot = optimize_las_vegas(box_data, new_bot)
    new_bot = gen_genetic_path(bot)
    print(f"Best from Genetic: {new_bot.dist_travelled}")
    print(new_bot.cleaned)
    #new_bot.print_path()