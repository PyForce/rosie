# -*- coding: utf-8 -*-

__all__=['config','reset','speeds_regulation','process_time']

import time
import math

#### constants ####
constant_kc = 2.0
constant_ki = 1.0
constant_kd = 1.0

#### variables ####
u1k1=0			
u1k1 = 0
u2k1 = 0
e1k1 = 0
e1k2 = 0
e2k1 = 0
e2k2 = 0			

previous = 0
missed = 0
accurate = 0
max_elapsed = 0
sample_time = 0.05

#### functions ####
def config(prev, sample):
    global previous, sample_time
    
    previous=prev
    sample_time=sample

def reset():
    """
    Reset PID values.
    """
    global accurate, missed, max_elapsed
    global u1k1, u1k1, u2k1, e1k1, e1k2, e2k1, e2k2
    
    u1k1 = u2k1 = 0
    e1k1 = e1k2 = 0
    e2k1 = e2k2 = 0

    missed = 0
    accurate = 0
    max_elapsed = 0

def process_time():
    global previous, accurate, missed, max_elapsed, sample_time
    
    now = time.time()
    elapsed = now - previous
    previous = now
    max_elapsed = elapsed if max_elapsed < elapsed else max_elapsed
    if elapsed > sample_time:
        missed += 1
    else:
        accurate += 1
    return elapsed
	
def speeds_regulation(set_point1, set_point2, delta_encoder_1, delta_encoder_2, elapsed, current1, current2, battery):
    
    global constant_kc, constant_ki, constant_kd
    global u1k1, u1k1, u2k1, e1k1, e1k2, e2k1, e2k2

    steps_per_sec1 = delta_encoder_1 / elapsed
    angular_speed1 = steps_per_sec1 * 2 * math.pi / 360

    steps_per_sec2 = delta_encoder_2 / elapsed
    angular_speed2 = steps_per_sec2 * 2 * math.pi / 360

    e1k = set_point1 - angular_speed1

    if constant_ki == 0:
        uuu1 = e1k * constant_kc
    else:
        uuu1 = e1k * constant_kc + (constant_ki - constant_kc) * e1k1 + u1k1

    if constant_kd != 0:
        uuu1 = constant_kc * (e1k - e1k1) + constant_ki * e1k + u1k1 + constant_kd * (e1k - 2 * e1k1 + e1k2)

    if uuu1 > 127.0:
        uuu1 = 127.0
    if uuu1 < - 128.0:
        uuu1 = - 128.0

    u1k1 = uuu1
    e1k2 = e1k1
    e1k1 = e1k

    um1 = int(uuu1)

    e2k = (set_point2 - angular_speed2)

    if constant_ki == 0:
        uuu2 = e2k * constant_kc
    else:
        uuu2 = e2k * constant_kc + (constant_ki - constant_kc) * e2k1 + u2k1

    if constant_kd != 0:
        uuu2 = constant_kc * (e2k - e2k1) + constant_ki * e2k + u2k1 + constant_kd * (e2k - 2 * e2k1 + e2k2)

    if uuu2 > 127.0:
        uuu2 = 127.0
    if uuu2 < - 128.0:
        uuu2 = - 128.0

    u2k1 = uuu2
    e2k2 = e2k1
    e2k1 = e2k

    um2 = int(uuu2)

    return um1, um2