import json
import sys
import math
import csv
import random

# My modules
import satellite
import satutils
import bot

# open_stream
# loop through json data - for each one get xyz, name, ID, type
# then write out to file and close
def las_vegas_shuffle(path):
    max_switches = 20
    switches = int (random.random()*max_switches) + 1
    length = len(path) - 1
    
    for i in range(switches):
        a = int (random.random()*length)
        b = int (random.random()*length)
        temp = path[a]
        path[a] = path[b]
        path[b] = temp
    return path

def optimize_las_vegas(box_data, bot):
    print("test")
    best_bot = bot.create_similar()
    best_bot.clean_ALL_debris(box_data)

    print ("Starting Las Vegas Search")
    for i in range(400000):
        new_bot = best_bot.create_similar()
        new_path = best_bot.path
        new_path = las_vegas_shuffle(new_path)
        new_bot.clean_ALL_debris(new_path)
        if i%10000 == 0:
            print (f"{i} iterations complete. Best dist is {best_bot.dist_travelled} ")
        if new_bot.dist_travelled < best_bot.dist_travelled:
            best_bot = new_bot
            #print(best_bot.dist_travelled)
        
    return best_bot

def gen_greedy_path(box_data, bot):
    #print(bot)
    for i in range(len(box_data)):
        min_dist = -1
        best_sat = None
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
        #print (best_sat)
        #print (bot.dist_travelled)
    return bot

# main 
if __name__ == "__main__":
    

    if len(sys.argv) != 3:
        print("Usage: python las_vegas_path.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    
    #print(input_file)
    #output_file = sys.argv[2]

    print(f"Reading from file {input_file}")
    sat_data = satutils.get_sat_data(input_file)

    #print(sat_data)
    bot = bot.Bot(7250, 0, 0, 2500)
    box_data = satutils.box_sat(sat_data, bot)

    bot = gen_greedy_path(box_data, bot)
    
    print(f"Best from Greedy: {bot.dist_travelled}")
    
    new_bot = bot.create_similar()

    
    #new_bot = optimize_las_vegas(box_data, new_bot)
    new_bot = optimize_las_vegas(bot.path, new_bot)
    print(f"Best from LV: {new_bot.dist_travelled}")
    print(new_bot.cleaned)
    new_bot.print_path_json(output_file)