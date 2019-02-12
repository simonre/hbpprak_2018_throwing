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
arm_file = "arm_control_templ.py"
can_reset = False

last_sim_state = "RESET"
current_sim_state = "RESET"


def sim_is_resetting():
    return current_sim_state == "RESET" and last_sim_state == "END"

def can_run_next_iteration():
    return sim_is_resetting() and can_reset

def wait_for_simulation_reset():
    while not (can_run_next_iteration()):
        time.sleep(1)

def movement_accepted(current_movement, next_movement):
    if next_movement.fitness > current_movement.fitness:
        return True
    else:
        ratio = next_movement.fitness / current_movement.fitness
        print("[COACH] ratio is " + str(ratio))
        return random.random() < ratio


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
        return abs(distance)
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
        print("[COACH] error reading " + str(filename))

def set_new_max_fitness(movement):
    global best_move
    best_move = movement

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
            return True
    except EmptyDataError:
        print("[COACH] There has not been a state change yet")
    except Exception as e:
        print(str(e))
    return False

def make_on_status(sim, datadir): 
    def on_status(msg):  
        # get the csv files from the simulation
        save_csv(sim, datadir, pos_csv_name)
        save_csv(sim, datadir, distance_distal_csv_name)

        pos_csv_file = os.path.join(datadir, pos_csv_name)
        dist_csv_file = os.path.join(datadir, distance_distal_csv_name)

        new_states_set = set_simulation_state(pos_csv_file)

        if(sim_is_resetting() and new_states_set):
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

            global next_movement
            next_movement.fitness = fitness
            global can_reset
            can_reset = True

    return on_status

def get_next_movement(current_movement, mutation):
    mutated_movement = np.random.uniform(-mutation, mutation, current_movement.movement.shape) + current_movement.movement
    return Movement(mutated_movement)


def make_arm_control_from_movement(movement):
    with open(arm_file, 'r') as tf_file:
        move_arm_tf = tf_file.read()
        move_arm_tf = move_arm_tf.format(movement.movement.tolist())
        print("[COACH] " + str(move_arm_tf))
        return move_arm_tf

def start_sim(sim):
    global last_sim_state
    last_sim_state = "NONE"
    sim.start()

class Movement():
    movement = None
    fitness = 0
    def __init__(self, movement, fitness=0):
        self.movement = movement
        self.fitness = fitness



    

print("Starting simulation...")
vc = VirtualCoach(environment=ENV, storage_username=USER)
sim = vc.launch_experiment(EXPERIMENT)

print("Creating genetic helper object...")
current_movement = Movement(np.array([-0.45, -0.9, 0.9, 0, 0, -0.5]))
current_movement = Movement(np.array([-0.45, -0.9, 0.9, 0, 0, -0.5]))

    
weight_costs = []
trial_weights = np.linspace(0., 1.5, 10)


try:
    mutation = 2
    steps = 100
    datadir = tempfile.mkdtemp()
    sim.register_status_callback(make_on_status(sim, datadir))

    for step in range(steps):
        global can_reset
        can_reset = False

        # get next generation of movements
        global next_movement
        next_movement = get_next_movement(current_movement, mutation)

        
        # create a new transfer function that controls the arm
        arm_control_tf = make_arm_control_from_movement(next_movement)
        sim.edit_transfer_function("arm_control", arm_control_tf)
        print("[COACH] edited transfer function")

        # register a function that is called every time there is a new status

        print("[COACH] Movement {}/{}".format(step, steps))
        
        start_sim(sim)
        print("[COACH] Started simulation")

        wait_for_simulation_reset()
        print("[COACH] restarting")

        if movement_accepted(current_movement, next_movement):
            current_movement = next_movement
            print("[COACH] new movement accepted with fitness " + str(next_movement.fitness))
        
            
    print("[COACH] Finished whole simulation!")
    print("[COACH] Winner:")
    print("[COACH]" + current_movement)
    
finally:
    sim.stop()

