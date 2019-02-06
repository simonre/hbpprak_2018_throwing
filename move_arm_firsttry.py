@nrp.MapRobotPublisher('arm_1', Topic('/robot/arm_1_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('arm_2', Topic('/robot/arm_2_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('arm_3', Topic('/robot/arm_3_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('arm_4', Topic('/robot/arm_4_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('arm_5', Topic('/robot/arm_5_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('arm_6', Topic('/robot/arm_6_joint/cmd_pos', std_msgs.msg.Float64))

@nrp.Neuron2Robot()
def move_arm(t,
                     arm_1,
                     arm_2,
                     arm_3,
                     arm_4 ,
                     arm_5,
                     arm_6):

    arm_1.send_message(std_msgs.msg.Float64(1.2))
    arm_2.send_message(std_msgs.msg.Float64(0.92))
    arm_3.send_message(std_msgs.msg.Float64(1.97))
    arm_4.send_message(std_msgs.msg.Float64(1.10))
    arm_5.send_message(std_msgs.msg.Float64(0.98))
    arm_6.send_message(std_msgs.msg.Float64(0.15))



    0.58844752 -1.28026769 -0.32768624  0.37819158 -0.2001222  -0.72348491