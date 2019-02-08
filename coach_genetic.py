"""
Runs a genetic optimization algorithm on the HBP.

Important: Ctrl-C seems to work poorly when attempting to interrupt the script manually. The best solution I found so far is to go to the web interface and stop the simulation in the "Running simulations" tab. This will cause the script to fail when attempting to communicate with the backend and it will quit (not very gracefully though).
"""

import time
import random
import numpy as np
from hbp_nrp_virtual_coach.virtual_coach import VirtualCoach
from genetic.genetic import Genetic
import csv
import os
import tempfile
import pandas as pd
from pandas.errors import EmptyDataError
import math
import re
import string 
ENV = 'local'
USER = 'nrpuser'
EXPERIMENT = 'hbpprak_2018_throwing'
move_joint_text = "arm_{}.send_message(std_msgs.msg.Float64({}))" 
RUNNING = 0 
STOPPED = 1
sim_status = RUNNING

max_fitness = 0
best_move = [0,0,0,0,0]

pos_csv_name = "obj_position.csv"
distance_distal_csv_name = "distance.csv"
state_csv_name = "state.csv"
arm_file = "arm_control_editable.py"

last_sim_state = "RESET"
current_sim_state = "RESET"

def sim_is_resetting():
    return current_sim_state == "RESET" and last_sim_state == "HIT"

def wait_for_simulation_reset():
    while not (sim_is_resetting()):
        time.sleep(1)

def get_distance(pos_initial, pos_end):
    px_initial = pos_initial['px']
    py_initial = pos_initial['py']
    pz_initial = pos_initial['pz']
    px_end = pos_end['px']
    py_end = pos_end['py']
    pz_end = pos_end['pz']
    sum_initial = px_initial ** 2 + py_initial ** 2 + pz_initial ** 2
    sum_end = px_end ** 2 + py_end ** 2 + pz_end ** 2
    distance = math.sqrt(abs(sum_initial - sum_end))
    return abs(distance)
        

def calculate_fitness(pos_csv, dist_csv):
    try:
        # fitness in this case is just the distance between initial position and end position
        #position_initial = pos_csv.iloc[0]
        #position_end = pos_csv.tail(1)
        #distance = get_distance(position_initial, position_end)
        distance = dist_csv.tail(1)['dist'].item()
        return distance
    except Exception as e:
        return None  

# Get a csv from the simulation, save it with the same filename
def save_csv(sim, datadir, filename): 
    try:
        with open(os.path.join(datadir, filename), 'wb') as f: 
            cf = csv.writer(f) 
            csv_data = sim.get_csv_data(filename)
            cf.writerows(csv_data) 
    except:
        print("[DEBUG] error reading " + str(filename))

def set_new_max_fitness(fitness):
    global max_fitness
    max_fitness = fitness
    global best_move
    best_move = next_gen[move_index]
    print("NEW BEST MOVE: ")
    print(best_move)
    print("FITNESS = " + str(max_fitness))

def set_simulation_state(csv_file):
    try:
        sim_state_data = pd.read_csv(csv_file)
        current_state = sim_state_data.tail(1)["state"].max()
        pattern = re.compile('[\W_]+') 

        current_state = pattern.sub('', current_state)

        global current_sim_state
        if current_state != current_sim_state:
            global last_sim_state
            last_sim_state = current_sim_state
            current_sim_state = current_state
    except EmptyDataError:
        print("[DEBUG] There has not been a state change yet")
    except Exception:
        print("SIMUL Other exception")

def make_on_status(sim, datadir): 
    def on_status(msg):  
        # get the csv files from the simulation
        save_csv(sim, datadir, pos_csv_name)
        save_csv(sim, datadir, distance_distal_csv_name)

        pos_csv_file = os.path.join(datadir, pos_csv_name)
        dist_csv_file = os.path.join(datadir, distance_distal_csv_name)

        set_simulation_state(pos_csv_file)

        if(sim_is_resetting()):
            sim.pause()
            pos_obj_csv = None
            dis_obj_csv = None
            fitness = 0
            try: 
                pos_obj_csv = pd.read_csv(pos_csv_file) 
                dis_obj_csv = pd.read_csv(dist_csv_file)  
                fitness = calculate_fitness(pos_obj_csv, dis_obj_csv) 
                print("SIMUL fitness of movement is " + str(fitness))
            except Exception as e:
                print(str(e)) 

            gen.set_fitness(move_index, fitness)
            if fitness > max_fitness:
                set_new_max_fitness(fitness)

    return on_status

def make_arm_control_from_gen(next_gen, move_index):
    gen = next_gen[move_index]
    with open(arm_file, 'r') as tf_file:
        move_arm_tf = tf_file.read()
        gen_list = gen.tolist()
        move_arm_tf = move_arm_tf.format(gen_list[:6], gen_list[6:])
        #print("[DEBUG] " + str(move_arm_tf))
        print("Prepare " + str(gen_list[:6]))
        print("Hit "     + str(gen_list[6:]))
        return move_arm_tf

def start_sim(sim):
    global last_sim_state
    last_sim_state = "NONE"
    sim.start()
    

print("Starting simulation...")
vc = VirtualCoach(environment=ENV, storage_username=USER)
sim = vc.launch_experiment(EXPERIMENT)

print("Creating genetic helper object...")
prepare_default = np.array([-0.45, -0.9, 0.9, 0, 0, -0.5])
hit_default     = np.array([-0.45, -0.9, 0.9, 0, 0, -0.5])
# decent hit: [   -2, -0.9, 0.9, 0, 0, -0.5]

start_movement = np.append(prepare_default, hit_default)

gen = Genetic(start_movement, pool_size=15, mutation=0.25, mating_pool_size=3)

try:
    # register a function that is called every time there is a new status
    datadir = tempfile.mkdtemp()
    sim.register_status_callback(make_on_status(sim, datadir))
    
    for _ in range(10):
        generations = 8
        for gen_index in range(generations):
            # get next generation of movements
            next_gen = gen.next_gen()
            
            for move_index in range(next_gen.shape[0]):
                # create a new transfer function that controls the arm
                arm_control_tf = make_arm_control_from_gen(next_gen, move_index)
                sim.edit_transfer_function("arm_control", arm_control_tf)
                print("SIMUL edited transfer function")
    
                print("[COACH] Generation {}/{} Movement {}/{}".format(gen_index+1,generations,move_index+1,next_gen.shape[0]))
                
                start_sim(sim)
                print("Started simulation")
    
                wait_for_simulation_reset()
                print("SIMUL restarting")
                
                if (move_index+1) % 3 == 0: sim.reset('full')
                
            gen.mutation *= 0.9
    
            
                
        print("SIMUL Finished whole simulation!")
        print(" SIMUL Winner:")
        print("SIMUL " + str(gen.fittest()))
        
        with open("results.txt", "a+") as out_file:
            out_file.write(str(gen.fittest()) + "\n")
    
finally:
    sim.stop()

