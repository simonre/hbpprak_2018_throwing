# Imported Python Transfer Function
import numpy as np
import sensor_msgs.msg

@nrp.MapRobotPublisher("topic_index_distal", Topic('/robot/hand_j14/cmd_pos', std_msgs.msg.Float64))
@nrp.MapCSVRecorder("obj_recorder", filename="obj_positions.csv", headers=["Time", "px", "py", "pz"])
@nrp.Robot2Neuron()
def get_pos(t, topic_index_distal, obj_recorder):
    from rospy import ServiceProxy
    from gazebo_msgs.srv import GetModelState
    clientLogger.info("distal pos = " + str(topic_index_distal))
    print(str(topic_index_distal))

    model_name = 'cylinder'
    state_proxy = ServiceProxy('/gazebo/get_model_state', GetModelState, persistent=False)
    cylinder_state = state_proxy(model_name, "world")
    if cylinder_state.success:
        current_position = cylinder_state.pose.position
        obj_recorder.record_entry(t, current_position.x, current_position.y, current_position.z)
