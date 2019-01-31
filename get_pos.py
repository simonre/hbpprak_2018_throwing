# Imported Python Transfer Function
import numpy as np
import sensor_msgs.msg


@nrp.MapRobotSubscriber("topic_index_distal", Topic('/robot/hand_Index_Finger_Distal/cmd_pos', std_msgs.msg.Float64))
@nrp.MapCSVRecorder("obj_recorder", filename="obj_position.csv", headers=["Time", "px", "py", "pz"])
@nrp.Robot2Neuron()
def get_pos(t, topic_index_distal, obj_recorder):
    from rospy import ServiceProxy
    from gazebo_msgs.srv import GetModelState

    model_name = 'cylinder'
    state_proxy = ServiceProxy('/gazebo/get_model_state', GetModelState, persistent=False)
    cylinder_state = state_proxy(model_name, "world")
    current_position = cylinder_state.pose.position
    clientLogger.info(current_position)
    obj_recorder.record_entry(t, current_position.x, current_position.y, current_position.z)
