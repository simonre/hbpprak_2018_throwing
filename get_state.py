# Imported Python Transfer Function
import numpy as np
import sensor_msgs.msg

@nrp.MapRobotSubscriber("sim_state", Topic('/arm_robot/arm_commands', std_msgs.msg.Float32))
@nrp.MapCSVRecorder("state_recorder", filename="state.csv", headers=["state"])
@nrp.Robot2Neuron()
def get_state(t, sim_state, state_recorder):
    
    if sim_state.changed:
        state_recorder.record_entry(sim_state.value)
