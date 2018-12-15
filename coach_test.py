"""
VirtualCoach Tutorial:
https://developer.humanbrainproject.eu/docs/projects/HBP%20Neurorobotics%20Platform/1.2/nrp/tutorials/virtual_coach/index.html

VirtualCoach API:
https://developer.humanbrainproject.eu/docs/projects/HBP%20Neurorobotics%20Platform/2.0/nrp/user_manual/virtual_coach/API.html#print-transfer-functions

Evolutionary tutorial:
https://developer.humanbrainproject.eu/docs/projects/HBP%20Neurorobotics%20Platform/2.0/nrp/tutorials/virtual_coach/batch_simulations.html#running-batch-simulations


Important things to note:
- Any change that is made to the simulation is only valid while the virtualcoach scipt (this one) is running! As soon as the script finishes the original transfer functions etc are restored to its original state, even if the simulaiton is already running! Make sure to keep the script alive 

Useful virtualcoach functions:

VirtualCoach object:
  vc.launch_experiment(experiment_id, server=None, reservation=None)
  vc.print_running_experiments()
  vc.print_cloned_experiments()
  vc.print_available_servers()
  
Simulation object:
  sim.get_state()
  sim.print_transfer_functions()
  sim.get_transfer_function(transfer_function_name)
  sim.add_transfer_function(transfer_function)
  sim.edit_transfer_function(transfer_function_name, transfer_function)
  sim.delete_transfer_function(transfer_function_name)
  sim.start()
  sim.pause()
  sim.stop()
  sim.reset(full / robot_pose / world / brain)
"""

import time
from hbp_nrp_virtual_coach.virtual_coach import VirtualCoach

ENV = 'local'
USER = 'nrpuser'
EXPERIMENT = 'hbpprak_2018_throwing'
TF = 'simple_move_robot'
TF_FILE = 'move_arm_tf.py'

last_status = None

# from https://forum.humanbrainproject.eu/t/virtual-coach-functionality/746/5
def on_status(status):
    global last_status
    last_status = status
    print("Sim. time: {} s".format(last_status['simulationTime']))

def wait_condition(timeout, condition):
    """
    Takes a condition and a timeout, and check if the condition has been satisfied withing this timeout.
    """
    global last_status
    start = time.time()
    while time.time() < start + timeout:
        time.sleep(0.25)
        if last_status is not None and condition(last_status):
            print("    ERROR: Timeout waiting for condition")
            return
    raise Exception('Condition check failed')
#------------------------------------------------------------



# ------------------------- MAIN -------------------------
vc = VirtualCoach(environment=ENV, storage_username=USER)
sim = vc.launch_experiment(EXPERIMENT)

# registers a callback that is called whenever a new simulation status message is received
sim.register_status_callback(on_status)

try:    
    # load new transfer function from file
    move_arm_tf = None
    with open(TF_FILE, 'r') as tf_file:
        move_arm_tf = tf_file.read()
    
    # add new transfer function to platform
    sim.edit_transfer_function(TF, move_arm_tf)
    
    sim.start()
    print("\n\n-> Started simulation\n")
    wait_condition(60, lambda x: x['simulationTime'] >= 10)

    sim.pause()
    print("\n\nReading out state...\n\n")
    # TODO: read out state

finally:
    # make sure to clean up after an (unexpected?) exception
    sim.stop()




