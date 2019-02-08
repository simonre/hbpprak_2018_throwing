import numpy as np

@nrp.MapRobotPublisher("topic_arm_1", Topic('/robot/arm_1_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_2", Topic('/robot/arm_2_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_3", Topic('/robot/arm_3_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_4", Topic('/robot/arm_4_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_5", Topic('/robot/arm_5_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher("topic_arm_6", Topic('/robot/arm_6_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotSubscriber('command', Topic('/arm_robot/arm_commands', std_msgs.msg.String))
@nrp.MapVariable("last_command_executed", initial_value=None)
@nrp.Neuron2Robot()
def arm_control(t,
                command, last_command_executed,
                topic_arm_1, topic_arm_2,
                topic_arm_3, topic_arm_4,
                topic_arm_5, topic_arm_6):

    def send_joint_config(topics_list, config_list):
        for topic, value in zip(topics_list, config_list):
            topic.send_message(std_msgs.msg.Float64(value))

    import collections

    if command.value is None: return
    else: command_str = command.value.data

    # if we receive a repeated command executed just return (last command was already sent)
    if command_str == last_command_executed.value: return
    topics_arm = [topic_arm_1, topic_arm_2, topic_arm_3, topic_arm_4, topic_arm_5, topic_arm_6]

    commands_confs = {
            "RESET":   [0, 0, 0, 0, 0, 0],
            "PREPARE": [-0.45, -0.9, 0.9, 0, 0, -0.5],
            "HIT":     [-2, -0.9, 0.9, 0, 0, -0.5]
        }


    # parse command
    split_command = command_str.split('_')
    action = split_command[0]
    new_config = commands_confs[action]
    last_command_executed.value = command_str
    send_joint_config(topics_arm, new_config)
