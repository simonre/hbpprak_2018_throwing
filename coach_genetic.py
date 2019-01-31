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
import math

ENV = 'local'
USER = 'nrpuser'
EXPERIMENT = 'hbpprak_2018_throwing'
OLD_TF = 'simple_move_robot'
TF_NAME = 'move_arm_tf'
TF_FILE = TF_NAME+'.py'
GENS = 4
move_joint_text = "arm_{}.send_message(std_msgs.msg.Float64({}))" 
last_status = None
RUNNING = 0 
STOPPED = 1
sim_status = RUNNING

def run_for_t_seconds(t):
    start = time.time()
    while time.time() < start + t:
        time.sleep(0.25)

pos_csv_name = "obj_position.csv"
distance_distal_csv_name = "distance.csv"

def calculate_fitness(pos_csv, dist_csv):
    #pos_initial = obj_csv.iloc[0]
    #pos_end = obj_csv.tail(1)
    #px_initial = pos_initial['px']
    #py_initial = pos_initial['py']
    #pz_initial = pos_initial['pz']
    #px_end = pos_end['px']
    #py_end = pos_end['py']
    #pz_end = pos_end['pz']
    #sum_initial = px_initial ** 2 + py_initial ** 2 + pz_initial ** 2
    #sum_end = px_end ** 2 + py_end ** 2 + pz_end ** 2
    #distance = math.sqrt(abs(sum_initial - sum_end))
    distance = 0
    try:
        pos_initial = pos_csv.iloc[0]
        pos_end = pos_csv.tail(1)
        px_initial = pos_initial['px']
        py_initial = pos_initial['py']
        pz_initial = pos_initial['pz']
        px_end = pos_end['px']
        py_end = pos_end['py']
        pz_end = pos_end['pz']
        sum_initial = px_initial ** 2 + py_initial ** 2 + pz_initial ** 2
        sum_end = px_end ** 2 + py_end ** 2 + pz_end ** 2
        distance = math.sqrt(abs(sum_initial - sum_end))
        distance_sim = dist_csv.iloc[0]['dist']
        print("FITNESS = " + str(distance))
        return abs(distance)*100
    except Exception as e:
        print("Simulation still running")
        return None

    distal = 0

    try: 
        #pos_initial = obj_csv.iloc[0]
        pos_end = pos_csv.tail(1)
        print(pos_end)
        distal = pos_end['distal_pos'].iloc[0]
        print(distal)
    except Exception as e:
        print("could not read distal pos")
        distal = 0

    fitness = abs(distance) * 100 + distal * 10
    print("[COACH] fitness = " + str(fitness))
    return fitness 
    #sum_initial = px_initial ** 2 + py_initial ** 2 + pz_initial ** 2
    #sum_end = px_end ** 2 + py_end ** 2 + pz_end ** 2
    #distance = math.sqrt(abs(sum_initial - sum_end))
    #dist_row = obj_csv.tail(1)
    #distance = dist_row['dist']
    



def save_position_csv(sim, datadir): 
    try:
        with open(os.path.join(datadir, pos_csv_name), 'wb') as f: 
            cf = csv.writer(f) 
            ################################################# ,
            # Insert code here: ,
            # get the CSV data from the simulation ,
            ################################################# ,
            csv_data = sim.get_csv_data(pos_csv_name) #solution ,
            cf.writerows(csv_data) 
    except:
        pass

def save_distance_csv(sim, datadir): 
    with open(os.path.join(datadir, distance_distal_csv_name), 'wb') as f: 

        cf = csv.writer(f) 
        ################################################# ,
        # Insert code here: ,
        # get the CSV data from the simulation ,
        ################################################# ,
        csv_data = sim.get_csv_data(distance_distal_csv_name) #solution ,
        cf.writerows(csv_data) 

# The function make_on_status() returns a on_status() function ,
# This is called a "closure":  ,
# it is here used to pass the sim and datadir objects to on_status() ,
def make_on_status(sim, datadir): 
    def on_status(msg): 

        print("Current simulation time: {}".format(msg['simulationTime'])) 

        save_position_csv(sim, datadir)
        save_distance_csv(sim, datadir) 

        global last_status
        last_status = msg

        pos_csv_file = os.path.join(datadir, pos_csv_name)
        dist_csv_file = os.path.join(datadir, distance_distal_csv_name)

        # wait until we have written the file
        while not os.path.isfile(pos_csv_file):
            time.sleep(1)

        if os.path.isfile(pos_csv_file):
            pos_obj_csv = None
            dis_obj_csv = None
            try: 
                pos_obj_csv = pd.read_csv(pos_csv_file) 
                dis_obj_csv = pd.read_csv(dist_csv_file)  
            except:
                pass 
            fitness = calculate_fitness(pos_obj_csv, dis_obj_csv) 
            print(fitness)
            if None != fitness :
                sim.pause()
                gen.set_fitness(move_index, fitness)
                sim.reset('full')
                print("-----------------------------------------------------")
                global sim_status
                sim_status = STOPPED
    return on_status

def make_transfer_function_from_gen(gen):
    movement = next_gen[move_index]
            
    # Generate transfer function code for this movement
    tf_text = ""
    for joint in range(movement.shape[0]):
        force = round(movement[joint], 4)
        # compose new transfer function
        tf_text += "    "
        tf_text += move_joint_text.format(joint + 1, force)
        tf_text += "\n"
        print("TF: {} -> {}".format(joint + 1, force))

    move_arm_tf = None
    with open(TF_FILE, 'r') as tf_file:
        move_arm_tf = tf_file.read()
    move_arm_tf += "\n" + tf_text

    return move_arm_tf

def wait_for_callback():
    global sim_status
    while sim_status == RUNNING:
        time.sleep(1)
    # reset the variable
    sim_status = RUNNING


print("Starting simulation...")
vc = VirtualCoach(environment=ENV, storage_username=USER)
sim = vc.launch_experiment(EXPERIMENT)
sim.delete_transfer_function(OLD_TF)

print("Creating genetic helper object...")
start_movement = np.array([1,1,1,1,1,1])

gen = Genetic(start_movement, pool_size=5, mutation=0.5, mating_pool_size=4)
    
weight_costs = []
trial_weights = np.linspace(0., 1.5, 10)

try:
    for gen_index in range(GENS):
        # get next generation of movements
        next_gen = gen.next_gen()
        
        for move_index in range(next_gen.shape[0]):
            move_arm_tf = make_transfer_function_from_gen(next_gen)

            #sim.print_transfer_functions()
                
            # add transfer function code to platform
            #sim.add_transfer_function(record_obj_tf)
            sim.edit_transfer_function("move_arm", move_arm_tf)
            datadir = tempfile.mkdtemp()
            sim.register_status_callback(make_on_status(sim, datadir))
            print("[COACH] Generation {}/{} Movement {}/{}".format(gen_index+1,GENS,move_index+1,next_gen.shape[0]))
            
            # start simulation and wait for 10 seconds until movement finishes
            sim.start()
            print("Started simulation")
            wait_for_callback()

            
    print("     Finished whole simulation!")
    print("Winner:")
    print(gen.fittest())
    
finally:
    sim.stop()

