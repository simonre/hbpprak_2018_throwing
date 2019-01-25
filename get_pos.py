# Imported Python Transfer Function
import numpy as np
import sensor_msgs.msg


@nrp.MapRobotSubscriber("topic_index_distal", Topic('/robot/hand_Index_Finger_Distal/cmd_pos', std_msgs.msg.Float64))
@nrp.MapCSVRecorder("obj_recorder", filename="obj_position.csv", headers=["Time", "px", "py", "pz", "distal_pos"])
@nrp.Robot2Neuron()
def get_pos(t, topic_index_distal, obj_recorder):
    from rospy import ServiceProxy
    from gazebo_msgs.srv import GetModelState

    distal_pos_msg = topic_index_distal.value
    distal_pos = 0
    if 'data' in dir(distal_pos_msg):
    	distal_pos = distal_pos_msg.data

    model_name = 'cylinder'
    state_proxy = ServiceProxy('/gazebo/get_model_state', GetModelState, persistent=False)
    cylinder_state = state_proxy(model_name, "world")
    if cylinder_state.success and distal_pos != 0:
        current_position = cylinder_state.pose.position
        clientLogger.info(current_position)
        clientLogger.info(distal_pos)
        obj_recorder.record_entry(t, current_position.x, current_position.y, current_position.z, distal_pos)
