# Imported Python Transfer Function
import numpy as np
import sensor_msgs.msg


@nrp.MapRobotSubscriber("sim_state", Topic('/arm_robot/arm_commands', std_msgs.msg.String))
@nrp.MapCSVRecorder("obj_recorder", filename="obj_position.csv", headers=["Time", "px", "py", "pz", "state"])
@nrp.Robot2Neuron()
def get_pos(t, sim_state, obj_recorder):
    from rospy import ServiceProxy
    from gazebo_msgs.srv import GetModelState
    
    try:
        model_name = 'cylinder'
        state_proxy = ServiceProxy('/gazebo/get_model_state', GetModelState, persistent=False)
        cylinder_state = state_proxy(model_name, "world")
        current_position = cylinder_state.pose.position
        obj_recorder.record_entry(t, current_position.x, current_position.y, current_position.z, sim_state.value)
    except Exception:
        pass
