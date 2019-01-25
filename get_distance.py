# Imported Python Transfer Function
import numpy as np
import sensor_msgs.msg

@nrp.MapRobotSubscriber("cylinder_distance", Topic('/cylinder_distance', std_msgs.msg.Float32))
@nrp.MapCSVRecorder("dist_recorder", filename="distance.csv", headers=["dist"])
@nrp.Robot2Neuron()
def get_distance(t, cylinder_distance, dist_recorder):
    
    if cylinder_distance.changed:
        dist_recorder.record_entry(cylinder_distance.value)
