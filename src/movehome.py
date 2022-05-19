from fanucpy import Robot

robot = Robot(
    robot_model="Fanuc",
    host="127.0.0.1",
    port=18735,
    ee_DO_type="RDO",
    ee_DO_num=7,
)

robot.connect()

robot.move(
    "joint",
    vals=[0.0, -28.0, -35.0, 0.0, -55.0, 0.0],
    velocity=50,
    acceleration=50,
    cnt_val=0,
    linear=False
)