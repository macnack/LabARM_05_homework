#!/usr/bin/env python3
import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from aruco_tracking_action.action import ArucoTracking
from geometry_msgs.msg import Pose
from ros2_aruco_interfaces.msg import ArucoMarkers


class ArucoTrackingActionServer(Node):
    def __init__(self):
        super().__init__('aruco_tracking_action_server')
        self._action_server = ActionServer(
            self,
            ArucoTracking,
            'aruco_tracking',
            self.execute_callback)

        self.aruco_markers_subscriber = self.create_subscription(
            ArucoMarkers,
            'aruco_markers',
            self.aruco_markers_callback,
            10)

        self.aruco_poses = dict()

    def aruco_markers_callback(self, msg):
        for i in range(len(msg.marker_ids)):
            self.aruco_poses[msg.marker_ids[i]] = msg.poses[i]

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        feedback_msg = ArucoTracking.Feedback()
        # create while when aruco_poses is smaller than 5
        while len(self.aruco_poses) < 5:
            feedback_msg.remaining_ids = 5 - len(self.aruco_poses)
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1)

        result = ArucoTracking.Result()
        result.aruco_ids = []
        result.aruco_poses = []
        for item in self.aruco_poses.items():
            result.aruco_ids.append(item[0])
            result.aruco_poses.append(item[1])
        goal_handle.succeed()
        return result


def main(args=None):
    rclpy.init(args=args)

    action_server = ArucoTrackingActionServer()

    # Create the executor
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(action_server)

    try:
        executor.spin()
    finally:
        executor.shutdown()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
