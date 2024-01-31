import json
import sys
import math
import csv

# My modules
import satellite
import satutils
import bot

# open_stream
# loop through json data - for each one get xyz, name, ID, type
# then write out to file and close


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
    

    if len(sys.argv) != 3:
        print("Usage: python greedy_path.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    
    #print(input_file)
    #output_file = sys.argv[2]

    print(f"Reading from file {input_file}")
    sat_data = satutils.get_sat_data(input_file)

    #print(sat_data)
    bot = bot.Bot(7250, 0, 0, 1000)
    box_data = satutils.box_sat(sat_data, bot)
    bot = gen_greedy_path(box_data, bot)
    print("Here")
    print(bot.dist_travelled)
    print(bot.cleaned)
    bot.print_path_json(output_file)