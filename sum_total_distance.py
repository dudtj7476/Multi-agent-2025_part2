#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math
import rosbag

# 🔧 분석할 bag 파일들이 들어 있는 폴더 경로
BAG_DIR = "rosbag 파일 폴더 경로"

# 🔧 사용할 오도메트리 토픽 이름
ODOM_TOPIC = "/gps/odom"    # nav_msgs/Odometry


def compute_distance_from_bag(bag_path, odom_topic=ODOM_TOPIC):
    """
    한 개 rosbag 파일에서 /gps/odom 기반 주행거리(m)를 계산
    """
    print("▶ bag 처리:", bag_path)
    bag = rosbag.Bag(bag_path)

    prev_x = None
    prev_y = None
    total_dist_m = 0.0

    msg_count = 0

    for topic, msg, t in bag.read_messages(topics=[odom_topic]):
        # nav_msgs/Odometry 기준
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        if prev_x is not None:
            dx = x - prev_x
            dy = y - prev_y
            step = math.sqrt(dx * dx + dy * dy)
            total_dist_m += step

        prev_x = x
        prev_y = y
        msg_count += 1

    bag.close()

    print("   사용한 odom 메시지 수:", msg_count)
    print("   이 bag에서 주행거리: {:.3f} m ({:.3f} km)".format(
        total_dist_m, total_dist_m / 1000.0
    ))

    return total_dist_m


def main():
    total_m = 0.0
    bag_files = []

    # 하위 폴더까지 모두 순회하면서 .bag 찾기
    for root, dirs, files in os.walk(BAG_DIR):
        for f in files:
            if f.endswith(".bag"):
                bag_files.append(os.path.join(root, f))

    if not bag_files:
        print("⚠ 찾은 .bag 파일이 없습니다. 폴더 경로를 확인하세요.")
        return

    bag_files.sort()

    print("총 발견 bag 개수:", len(bag_files))

    for bag_path in bag_files:
        dist_m = compute_distance_from_bag(bag_path)
        total_m += dist_m

    total_km = total_m / 1000.0

    print("\n=====================================")
    print("✅ 전체 bag 기준 총 주행거리:")
    print("   {:.3f} m (약 {:.3f} km)".format(total_m, total_km))
    print("=====================================")


if __name__ == "__main__":
    main()

