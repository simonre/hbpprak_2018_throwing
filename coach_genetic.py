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
notify_next_move = False

def sim_is_resetting():
    return current_sim_state == "RESET" and last_sim_state == "HIT"

def calculate_fitness(pos_csv, dist_csv):
    try:
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
    print("NEW BEST MOVE: ", np.round(best_move, 2))

def set_simulation_state(csv_file):
    try:
        sim_state_data = pd.read_csv(csv_file)
        current_state = sim_state_data.tail(1)["state"].max()
        pattern = re.compile('[\W_]+') 
        
        if isinstance(current_state, float): return
        current_state = pattern.sub('', current_state)

        global current_sim_state
        if current_state != current_sim_state:
            global last_sim_state
            print("Current state: " + str(current_state))
            last_sim_state = current_sim_state
            current_sim_state = current_state
    except EmptyDataError:
        pass
        #print("[DEBUG] There has not been a state change yet")
    except Exception as e:
        print("Set sim state Exception:", e)
        print("-------------------------")

def make_on_status(sim, datadir):
    def on_status(msg):
        global notify_next_move
        # get the csv files from the simulation
        save_csv(sim, datadir, pos_csv_name)
        save_csv(sim, datadir, distance_distal_csv_name)

        pos_csv_file = os.path.join(datadir, pos_csv_name)
        dist_csv_file = os.path.join(datadir, distance_distal_csv_name)

        set_simulation_state(pos_csv_file)

        if(sim_is_resetting() and not notify_next_move):
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
                print("Make status Exception: ", e)
                print("-------------------------")

            if fitness is None: gen.set_fitness(move_index, 0) # something strange happened
            else: gen.set_fitness(move_index, fitness)
            if fitness > max_fitness:
                set_new_max_fitness(fitness)
            notify_next_move = True

    return on_status

def make_arm_control_from_gen(next_gen, move_index):
    gen = next_gen[move_index]
    with open(arm_file, 'r') as tf_file:
        move_arm_tf = tf_file.read()
        gen_list = gen.tolist()
        move_arm_tf = move_arm_tf.format(gen_list[:6], gen_list[6:])
        #print("[DEBUG] " + str(move_arm_tf))
        print("Prepare " + str(np.round(gen_list[:6], 2)))
        print("Hit     " + str(np.round(gen_list[6:], 2)))
        return move_arm_tf

def start_sim(sim):
    global last_sim_state
    last_sim_state = "NONE"
    sim.start()
    

vc = VirtualCoach(environment='local', storage_username='nrpuser')
print("Starting simulation...")
sim = vc.launch_experiment('hbpprak_2018_throwing')

print("Creating genetic helper object...")
prepare_default = np.array([-0.45, -0.9, 0.9, 0, 0, -0.5])
hit_default     = np.array([   -2, -0.9, 0.9, 0, 0, -0.5])
# decent hit: [   -2, -0.9, 0.9, 0, 0, -0.5]

start_movement = np.append(prepare_default, hit_default)
gen = Genetic(start_movement, pool_size=10, mutation=0.25, mating_pool_size=3)

try:
    # register a function that is called every time there is a new status
    datadir = tempfile.mkdtemp()
    sim.register_status_callback(make_on_status(sim, datadir))
    
    for _ in range(10):
        generations = 6
        for gen_index in range(generations):
            last_sim_state = "RESET"
            current_sim_state = "RESET"
            next_gen = gen.next_gen()
            
            for move_index in range(next_gen.shape[0]):
                print("\n----------------------------------------")
                print("Generation {}/{} Movement {}/{}".format(gen_index+1,generations,move_index+1,next_gen.shape[0]))
                print("----------------------------------------")
                
                # create a new transfer function that controls the arm
                arm_control_tf = make_arm_control_from_gen(next_gen, move_index)
                sim.edit_transfer_function('arm_control', arm_control_tf)
                print("Applied new transfer function")
                
                start_sim(sim)
                print("Started simulation")
    
                while not notify_next_move:
                    time.sleep(1)
                notify_next_move = False
                
            gen.mutation *= 0.9
            print("Full reset simulation")
            sim.reset('full')
    
            
                
        print("SIMUL Finished whole simulation!")
        print("SIMUL Winner:")
        print("SIMUL " + str(gen.fittest()))
        
        with open("results.txt", "a+") as out_file:
            out_file.write(str(gen.fittest()) + "\n")
    
finally:
    sim.stop()

