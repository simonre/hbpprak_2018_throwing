import numpy as np

@nrp.MapRobotPublisher("topic_arm_1", Topic('/robot/arm_1_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_2", Topic('/robot/arm_2_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_3", Topic('/robot/arm_3_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_4", Topic('/robot/arm_4_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_5", Topic('/robot/arm_5_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_6", Topic('/robot/arm_6_joint/cmd_pos', std_msgs.msg.Float64))

@nrp.MapRobotPublisher("hand_index_proximal", Topic('/robot/hand_Index_Finger_Proximal/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("hand_index_distal", Topic('/robot/hand_Index_Finger_Distal/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("hand_middle_proximal", Topic('/robot/hand_Middle_Finger_Proximal/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("hand_middle_distal", Topic('/robot/hand_Middle_Finger_Distal/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("hand_ring_proximal", Topic('/robot/hand_Ring_Finger/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("hand_ring_distal", Topic('/robot/hand_j12/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("hand_pinky_proximal", Topic('/robot/hand_Pinky/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("hand_pinky_distal", Topic('/robot/hand_j13/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("hand_thumb_flexion", Topic('/robot/hand_j4/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("hand_thumb_distal", Topic('/robot/hand_j3/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("test", Topic("/robot/hand_Thumb_Opposition/cmd_pos", std_msgs.msg.Float64))

@nrp.MapRobotSubscriber('command', Topic('/arm_robot/arm_commands', std_msgs.msg.String))
@nrp.MapVariable("last_command_executed", initial_value=None)

@nrp.Neuron2Robot()
def arm_control(t,
                command, last_command_executed,
                hand_index_proximal,
                hand_index_distal,
                hand_middle_proximal,
                hand_middle_distal,
                hand_ring_proximal,
                hand_ring_distal,
                hand_pinky_proximal,
                hand_pinky_distal,
                hand_thumb_flexion,
                hand_thumb_distal,
                test,
                topic_arm_1, topic_arm_2,
                topic_arm_3, topic_arm_4,
                topic_arm_5, topic_arm_6):
    
    def grasp(strength):
        for topic in [
                hand_index_proximal,
                hand_index_distal,
                hand_middle_proximal,
                hand_middle_distal,
                hand_ring_proximal,
                hand_ring_distal,
                hand_pinky_proximal,
                hand_pinky_distal,
                hand_thumb_flexion,
                hand_thumb_distal
        ]:
            topic.send_message(std_msgs.msg.Float64(strength))
        #hand_thumb_flexion.send_message(std_msgs.msg.Float64(0.7))
        test.send_message(std_msgs.msg.Float64(2))

    def send_joint_config(topics_list, config_list):
        for topic, value in zip(topics_list, config_list):
            topic.send_message(std_msgs.msg.Float64(value))

    import collections

    if command.value is None: return
    else: command_str = command.value.data

    # if we receive a repeated command executed just return (last command was already sent)
    if command_str == last_command_executed.value: return
    topics_arm = [topic_arm_1, topic_arm_2, topic_arm_3, topic_arm_4, topic_arm_5, topic_arm_6]

    commands_confs = {{
            "RESET":   ([0, 0,    0, 0, 0, 0], 0),
            "PREPARE": ([-0.45, -1, 1.05, 0.5, -0.7, -0.5], 0),
            "GRASP1":  ([-0.45, -1, 1.05, 0.5, -0.7, -0.5], 0.3),
            "GRASP2":  ([-0.45, -1, 1.05, 0.5, -0.7, -0.5], 0.7),
            "THROW":   ([-0.45, 5, -2, 0.5, -0.7, -0.5], 0.7),
            "END":     ({}, 0)
        }}


    # parse command
    split_command = command_str.split('_')
    action = split_command[0]
    new_config, strength = commands_confs[action]
    last_command_executed.value = command_str
    send_joint_config(topics_arm, new_config)
    grasp(strength)
