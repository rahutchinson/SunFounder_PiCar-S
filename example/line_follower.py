#!/usr/bin/env python
'''
**********************************************************************
* Filename    : line_follower
* Description : An example for sensor car kit to followe line
* Author      : Dream
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Dream    2016-09-21    New release
**********************************************************************
'''

from SunFounder_Line_Follower import Line_Follower
from picar import front_wheels
from picar import back_wheels
import time
import picar


class Buggy:
    def __init__(self):
        picar.setup()

        self.REFERENCES = [20.5, 25.0, 28.0, 21.5, 20.5]
        # self.calibrate = True
        self.calibrate = False
        self.forward_speed = 40
        self.turning_angle = 45

        self.delay = 0.0005

        self.fw = front_wheels.Front_Wheels(db='config')
        self.bw = back_wheels.Back_Wheels(db='config')
        self.lf = Line_Follower.Line_Follower()

        self.lf.references = self.REFERENCES
        self.fw.ready()
        self.bw.ready()
        self.fw.turning_max = 60

    def straight_run(self):
        while True:
            self.bw.speed = 70
            self.bw.forward()
            self.fw.turn_straight()

    def line_follow(self):
        self.bw.speed = self.forward_speed

        a_step = 6
        b_step = 12
        c_step = 30
        d_step = 50
        self.bw.forward()
        while True:
            lt_status_now = self.lf.read_digital()
            print(lt_status_now)
            print(self.lf.read_analog())
            # Angle calculate
            step = 0
            if lt_status_now == [0, 0, 1, 0, 0]:
                step = 0
            elif lt_status_now == [0, 1, 1, 0, 0] or lt_status_now == [0, 0, 1, 1, 0]:
                step = a_step
            elif lt_status_now == [0, 1, 0, 0, 0] or lt_status_now == [0, 0, 0, 1, 0]:
                step = b_step
            elif lt_status_now == [1, 1, 0, 0, 0] or lt_status_now == [0, 0, 0, 1, 1]:
                step = c_step
            elif lt_status_now == [1, 0, 0, 0, 0] or lt_status_now == [0, 0, 0, 0, 1]:
                step = d_step

            turning_angle = int(90)
            # Direction calculate
            if lt_status_now == [0, 0, 1, 0, 0]:
                self.fw.turn(90)
            # turn right
            elif lt_status_now in ([0, 1, 1, 0, 0], [0, 1, 0, 0, 0], [1, 1, 0, 0, 0], [1, 0, 0, 0, 0]):
                turning_angle = int(90 - step)
            # turn lefts
            elif lt_status_now in ([0, 0, 1, 1, 0], [0, 0, 0, 1, 0], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1]):
                turning_angle = int(90 + step)
            elif lt_status_now in ([1, 1, 1, 1, 1], [0, 1, 1, 1, 1], [1, 1, 1, 1, 0]):
                break

            self.fw.turn(turning_angle)
            time.sleep(self.delay)

    def cali(self):
        references = [0, 0, 0, 0, 0]
        print("cali for module:\n  first put all sensors on white, then put all sensors on black")
        mount = 50
        self.fw.turn(60)
        print("\n cali white")
        time.sleep(4)
        self.fw.turn(90)
        white_references = self.lf.get_average(mount)
        self.fw.turn(110)
        time.sleep(0.5)
        self.fw.turn(80)
        time.sleep(0.5)
        self.fw.turn(90)
        time.sleep(1)

        self.fw.turn(110)
        print("\n cali black")
        time.sleep(4)
        self.fw.turn(90)
        black_references = self.lf.get_average(mount)
        self.fw.turn(100)
        time.sleep(0.5)
        self.fw.turn(80)
        time.sleep(0.5)
        self.fw.turn(90)
        time.sleep(1)
        print(f"White References: {white_references}")
        print(f"Black References: {black_references}")
        for i in range(0, 5):
            references[i] = (white_references[i] + black_references[i]) / 2
        self.lf.references = references
        print("Middle references =", references)
        time.sleep(1)

    def destroy(self):
        self.bw.stop()
        self.fw.turn(90)

    def pick_up(self):
        self.bw.stop()
        print("PickUp")

    def continue_to_next(self):
        self.bw.speed = 25
        self.bw.forward()
        time.sleep(.5)
        self.bw.stop()

    def setup(self):
        if self.calibrate:
            self.cali()
            self.calibrate = False


if __name__ == '__main__':
    buggy = Buggy()

    current_station = 0
    go_to_station = 2
    try:
        try:
            while True:
                buggy.setup()
                buggy.line_follow()
                current_station += 1
                if current_station == go_to_station:
                    buggy.destroy()
                    print("at location")
                    break
                else:
                    print("going to next")
                    buggy.continue_to_next()
        except Exception as e:
            print(e)
            print('error try again in 5')
            buggy.destroy()
            time.sleep(5)
    except KeyboardInterrupt:
        buggy.destroy()
