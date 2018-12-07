"""
Runs a genetic optimization algorithm on the HBP.

Important: Ctrl-C seems to work poorly when attempting to interrupt the script manually. The best solution I found so far is to go to the web interface and stop the simulation in the "Running simulations" tab. This will cause the script to fail when attempting to communicate with the backend and it will quit (not very gracefully though).
"""

import time
import random
import numpy as np
from hbp_nrp_virtual_coach.virtual_coach import VirtualCoach
from genetic.genetic import Genetic

ENV = 'local'
USER = 'nrpuser'
EXPERIMENT = 'hbpprak_2018_throwing'
OLD_TF = 'simple_move_robot'
TF_NAME = 'move_arm_tf'
TF_FILE = TF_NAME+'.py'
GENS = 30
move_joint_text = "    arm_{}.send_message(std_msgs.msg.Float64({}))\n"

last_status = None

def on_status(status):
    global last_status
    last_status = status
    print("    Sim. time: {} s".format(last_status['simulationTime']))

def wait_condition(timeout, condition):
    global last_status
    start = time.time()
    while time.time() < start + timeout:
        time.sleep(0.25)
        if last_status is not None and condition(last_status):
            print("    ERROR: Timeout waiting for condition")
            return
    raise Exception('Condition check failed')



move_arm_tf = None
with open(TF_FILE, 'r') as tf_file:
    move_arm_tf = tf_file.read()

print("Starting simulation...")
vc = VirtualCoach(environment=ENV, storage_username=USER)
sim = vc.launch_experiment(EXPERIMENT)
sim.register_status_callback(on_status)

print("Creating genetic helper object...")
start_movement = np.array([1,1,1,1,1,1])
gen = Genetic(start_movement, pool_size=10, mutation=0.1, mating_pool_size=4)
    
try:
    for gen_index in range(GENS):
        # get next generation of movements
        next_gen = gen.next_gen()
        
        for move_index in range(next_gen.shape[0]):
            movement = next_gen[move_index]
            
            # Generate transfer function code for this movement
            tf_text = ""
            for joint in range(movement.shape[0]):
                force = round(movement[joint], 4)
                # compose new transfer function
                tf_text += move_joint_text.format(joint + 1, force)
                
            # add transfer function code to platform
            sim.edit_transfer_function(OLD_TF, move_arm_tf)
            print("\nGeneration {}/{} Movement {}/{}".format(gen_index+1,GENS,move_index+1,next_gen.shape[0]))
            print(tf_text)
            
            # start simulation and wait for 10 seconds until movement finishes
            sim.start()
            print("Started simulation")
            wait_condition(60, lambda x: x['simulationTime'] >= 10)
            
            # pause simulation and read out state
            print("Paused simulation")
            sim.pause()
            print("Reading out state")
            fitness = random.uniform(0, 10)  # THIS IS JUST FOR TESTING!
            gen.set_fitness(move_index, fitness)
            print("Restarting simulation")
            sim.reset('full')
            print("-----------------------------------------------------")
    print("     Finished whole simulation!")
    print("Winner:")
    print(gen.fittest())
    
finally:
    sim.stop()

