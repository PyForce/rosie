# porting
This project is the python version of cporting project.

This project implements some robotics task in a Raspberry Pi.

This is the base code for many other projects and it's written in python language. The main purpose of this project is to port all code developed in my thesis to get Eng. title in 2013. The original code targets a dsPIC microcontroller in a very specific hardware designed and built by me. My thesis goal is a Robot capable to make trajectory tracking and communicating with a PC for supervision and control.

A Raspberry Pi is now the main controller of the robot and it uses MD25 board via I2C to control the motors of a differential mobile robot. It uses threads to do the job and sockets for communications.

