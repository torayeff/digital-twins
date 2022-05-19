"""Assembly Simulation"""
import json

import robodk
import random
import numpy as np
from lib.RDKSimulation import RDKSimulation


class PickablePart:
    """Item class."""

    def __init__(self,
                 item,
                 part_id,
                 pick_approach_pose_offset,
                 pick_pose_offset,
                 pick_retract_offset,
                 place_approach_pose_offset,
                 place_pose_offset,
                 place_retract_offset):
        self.item = item
        self.part_id = part_id
        self.pick_approach_pose_offset = pick_approach_pose_offset
        self.pick_pose_offset = pick_pose_offset
        self.pick_retract_pose_offset = pick_retract_offset
        self.place_approach_pose_offset = place_approach_pose_offset
        self.place_pose_offset = place_pose_offset
        self.place_retract_pose_offset = place_retract_offset


class Assembly(RDKSimulation):
    """Assembly of parts."""

    def __init__(self, recipe):
        super().__init__()

        # set simulation speed
        self.rblink.setSimulationSpeed(1)

        # get robot
        self.robot = self.rblink.Item('robot')
        # wrt to the station, useful for calculating positions
        self.rinv = robodk.invH(self.robot.PoseAbs())

        # TCP
        self.tcp = self.rblink.Item('tcp')

        # assembly place like table
        self.assembly_place = self.rblink.Item('assembly_place')
        # target assembly pose in robot reference frame
        self.target_pos3d = np.array([550, -150, 0])  # should be checked for the reachability

        # initial assembly parts position
        self.parts_ref = self.rblink.Item('parts_ref')

        # read recipe
        self.assembly_sequence = recipe['sequence']
        self.parts = {}
        for part_data in recipe['parts']:
            part_id = part_data['part_id']
            self.parts[part_id] = PickablePart(item=self.rblink.Item(part_id),
                                               part_id=part_id,
                                               pick_approach_pose_offset=part_data['pick_approach_pose_offset'],
                                               pick_pose_offset=part_data['pick_pose_offset'],
                                               pick_retract_offset=part_data['pick_retract_pose_offset'],
                                               place_approach_pose_offset=part_data['place_approach_pose_offset'],
                                               place_pose_offset=part_data['place_pose_offset'],
                                               place_retract_offset=part_data['place_retract_pose_offset'])

        # this is fixed for now
        self.initial_poses = {
            'base_plate': [0, 60, 0, 0, 0, 0],
            'compound_gear': [0, -30, 0, 0, 0, 0],
            'gear1': [0, -120, 0, 0, 0, 0],
            'gear2': [90, -160, 0, 0, 0, 0],
            'shaft1': [100, 0, 39, 0, -180, 0],
            'shaft2': [100, -70, 39, 0, -180, 0]
        }

        self.reset()

    def run(self):
        """Runs simulation."""
        # target_pose = robodk.Pose(550, -70, 0, 0, 0, 0)
        # self.pick_and_place(item, target_pose)
        self.assemble()

    def move_robot(self, pos3d, offset):
        """Moves robot to the 3d position with given offset."""
        pose = robodk.Pose(*(np.array([*pos3d, 0, 0, 0]) + offset))
        self.robot.MoveJ(pose)

    def assemble(self):
        """Assemble the parts in the sequence."""
        for part_id in self.assembly_sequence:
            part = self.parts[part_id]
            self.pick_and_place(part)

    def pick_and_place(self, part):
        """Picks and places the part."""
        part_pos3d = (self.rinv * part.item.PoseAbs()).Pos()

        # 1. Go to the pick approach pose.
        self.move_robot(part_pos3d, part.pick_approach_pose_offset)

        # 2. Go to the pick pose.
        self.move_robot(part_pos3d, part.pick_pose_offset)

        # 3. Pick the part.
        part.item.setParentStatic(self.tcp)

        # 4. Go to the pick retract pose.
        self.move_robot(part_pos3d, part.pick_retract_pose_offset)

        # 5. Go to the place approach pose.
        self.move_robot(self.target_pos3d, part.place_approach_pose_offset)

        # 6. Go to the place pose.
        self.move_robot(self.target_pos3d, part.place_pose_offset)

        # 7. Place the part.
        part.item.setParentStatic(self.assembly_place)

        # 8. Go to the place retract pose.
        self.move_robot(self.target_pos3d, part.place_retract_pose_offset)

    def reset(self):
        """Resets simulation."""

        # reset robot to the home position
        # for KUKA LBR iiwa 14 R820
        self.robot.setJoints([0, 0, 0, -90, 0, 0, 0])

        for part in self.parts.values():
            part.item.setParentStatic(self.parts_ref)
            part.item.setPose(robodk.Pose(*self.initial_poses[part.part_id]))


if __name__ == '__main__':
    with open('assembly_recipe.json', 'r') as f:
        assembly_recipe = json.loads(f.read())

    sim = Assembly(assembly_recipe)
    sim.run()
