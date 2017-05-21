import smbus
bus = smbus.SMBus(1)

import time 
import numpy as np

adress=0x10
Tm=60.0 # ms
Stat_Reg1=0x00
Stat_Reg2=0x80

# SR1 S05 S04 S03 S02 S01 _T_ GB_
#  0   X   X   X   X   X   X   X  -> Status Register1

# SR2 S12 S11 S10 S09 S08 S07 S06
#  1   X   X   X   X   X   X   X  -> Status Register2

# 0-> Disable
# 1-> Enable

Temp=28.0 # C

C=347.8

sensor_data = []

IOError_cont=0
temp_measurement=0
cont_temp_measurement=0

def change_adress(new_adress):
	global adress
	global IOError_cont
	try:
		if(new_adress>=120):

			print ("adress value error")
			print ("it must be betwen 3 and 119 (0x03 to 0x77)")
			# adress=system_adress
			# return system_adress
		else:
			operation=0x01
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			bus.write_byte(adress,new_adress)
			adress=new_adress
			# return new_adress
			IOError_cont=0
	except KeyboardInterrupt:
		print("keyboard IT at change_adress")
	except IOError:
		if(IOError_cont==5):
			print("IOError at change_adress 5 times")
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at change_adress")
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			change_adress(new_adress)


def get_Temp():
	global Temp
	global adress
	global Stat_Reg1
	global IOError_cont
	try:
		value1=(Stat_Reg1>>1)&1		
		value2=Stat_Reg1&1
		if(value1 and value2):
			operation=0x02
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			ADRESL=bus.read_byte(adress) 
			# print (hex(ADRESL))
			ADRESH=bus.read_byte(adress)
			# print (hex(ADRESH))
			AD_data=(ADRESH<<8)|ADRESL;
			# print (AD_data)
			# temp_C=AD_data*500/1023
			Temp_=AD_data*50.0/1023.0
			IOError_cont=0
			return round(Temp_,2)
		else:
			if(value1!=1):
				text="Lm35 it isn't active, by default Temp is 28"
			if(value2!=1):
				text="Gb isn't active, by default Temp is 28"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and Lm35 it isn't active, by default Temp is 28"
			global temp_measurement
			global cont_temp_measurement
			cont_temp_measurement=cont_temp_measurement+1
			if(temp_measurement and cont_temp_measurement==10):
				print text
				temp_measurement=0
				cont_temp_measurement=0
			elif(temp_measurement==0):				
				temp_measurement=0
				cont_temp_measurement=0
				print text
			return round(Temp,2)
	except KeyboardInterrupt:
		print("keyboard IT at get_Temp")
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Temp 5 times")
			#print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			# print("IOError at get_Temp")
			# reset()
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Temp()


def Mean (object):
	mean=0
	number_of_samples=len(object)
	for item in object:
		mean=mean+item		
	mean=mean/number_of_samples
	return mean


def Temp_Mean(number_of_samples):

	global Temp
	global temp_measurement	
	global IOError_cont
	try:
		data_temp = []
		temp_measurement=1
		for i in range(1, number_of_samples+1):
			data=get_Temp()
			while(type(data)!=float):
				#print(i)
				data=get_Temp()
				#print(data)	
			data_temp.append(data)
			time.sleep(0.1)
		Temp=round(Mean(data_temp),2)
		# print(data_temp)
	except KeyboardInterrupt:
		print("keyboard IT at Temp_Mean")
	# except TypeError:
	#  	print("TypeError IT at Temp_Mean")


def actualize_C():
	global C
	global Temp
	try:		
		C=round(((Temp*0.6)+331),2)
	except KeyboardInterrupt:
		print("keyboard IT at actualize_C")


def change_Tm_ms(new_Tm):
	global Tm
	global adress
	global IOError_cont
	try:		
		if(new_Tm<60):

			print ("Tm value error")
			print ("it must be over 60 ms")
		else:			
			operation=0x03
			bus.write_byte(adress,operation)			
			bus.write_byte(adress,operation)
			Tm_L=np.uint8(new_Tm)
			bus.write_byte(adress,Tm_L)
			Tm_H=np.uint8(new_Tm>>8)
			# time.sleep(0.5)
			bus.write_byte(adress,Tm_H)
			Tm=(Tm_H<<8)|Tm_L
			IOError_cont=0
	except KeyboardInterrupt:
		print("keyboard IT at change_Tm_ms")
	except IOError:
		if(IOError_cont==5):
			print("IOError at change_Tm_ms 5 times")
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at change_Tm_ms")
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			change_Tm_ms(new_Tm)


def get_Tm_ms():
	global Tm
	global adress
	global IOError_cont
	try:
		operation=0x04
		bus.write_byte(adress,operation)
		bus.write_byte(adress,operation)
		Tm_L=bus.read_byte(adress)
		# print(hex(Tm_L))
		Tm_H=bus.read_byte(adress)
		Tm=(Tm_H<<8)|Tm_L
		# print(hex(Tm_H))
		# print (hex(Tm))
		IOError_cont=0
	except KeyboardInterrupt:
		print("keyboard IT at get_Tm_ms")
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Tm_ms 5 times")
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Tm_ms")
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Tm_ms()


def change_Stat_Reg(new_Stat_Reg):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global IOError_cont
	try:
		if(new_Stat_Reg&0x80==0x80):
			Stat_Reg2=new_Stat_Reg
		else:
			Stat_Reg1=new_Stat_Reg
		operation=0x05
		bus.write_byte(adress,operation)
		bus.write_byte(adress,operation)
		bus.write_byte(adress,new_Stat_Reg)
		IOError_cont=0
	except KeyboardInterrupt:
		print("keyboard IT at change_Stat_Reg")
	except IOError:
		if(IOError_cont==5):
			print("IOError at change_Stat_Reg 5 times")
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at change_Stat_Reg")
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			change_Stat_Reg(new_Stat_Reg)


def Enable_Sensor(no):
	try:
		value=1
		if(no<1 or no>12):
			print "sensor number error"			
			print "it must be betwen 1 and 12"
		elif(no<=5):
			value=(value<<(1+no))|Stat_Reg1
			# print bin(value)
		else:
			value=(value<<(no-6))|Stat_Reg2
			# print bin(value)		
		change_Stat_Reg(value)
	except KeyboardInterrupt:
		print("keyboard IT at Enable_Sensor ",no)


def Disable_Sensor(sensor_no):
	try:
		value=0xfe
		if(sensor_no<1 or sensor_no>12):
			print "sensor number error"			
			print "it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value=(value<<(1+sensor_no))&Stat_Reg1
			# print bin(value)
		else:
			value=(value<<(sensor_no-6))&Stat_Reg2
			# print bin(value)		
		change_Stat_Reg(value)
	except KeyboardInterrupt:
		print("keyboard IT at Disable_Sensor ",sensor_no)


def Global_Enable():
	try:
		value=0x01
		value=value|Stat_Reg1
		# print bin(value)	
		change_Stat_Reg(value)
	except KeyboardInterrupt:
		print("keyboard IT at Global_Enable ")


def Global_Disable():
	try:
		value=0xfe
		value=value&Stat_Reg1
		# print bin(value)	
		change_Stat_Reg(value)
	except KeyboardInterrupt:
		print("keyboard IT at Global_Disable ")


def Lm35_Enable():
	try:
		value=0x02
		value=value|Stat_Reg1
		# print bin(value)	
		change_Stat_Reg(value)
	except KeyboardInterrupt:
		print("keyboard IT at Lm35_Enable ")


def Lm35_Disable():
	try:
		value=0xfc
		value=value&Stat_Reg1
		# print bin(value)	
		change_Stat_Reg(value)
	except KeyboardInterrupt:
		print("keyboard IT at Lm35_Disable ")


def get_Stat_Reg():
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global IOError_cont
	try:
		operation=0x06
		bus.write_byte(adress,operation)
		bus.write_byte(adress,operation)
		Stat_Reg1=bus.read_byte(adress) 		
		# print (hex(ADRESL))
		Stat_Reg2=bus.read_byte(adress)	
		IOError_cont=0	
	except KeyboardInterrupt:
		print("keyboard IT at get_Stat_Reg")
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Stat_Reg 5 times")
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Stat_Reg")
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Stat_Reg()

def cal_dist_cm(TL,TH):
    # asumiendo una temperatura de 28 grados Celsius
    # segun la ecuacion de newton modificada por laplace
    # C = 331+(0,6 x T) [m/s] -> T en grados Celsius   
    # C=347.8
    global C 
    TMR=(TH<<8)|TL
    #distancia=(valor*4*C)/(2*12)#en um
    # 4/(2*12)~=0.17
    return round(((TMR*0.17*C)/10000),2)#en cm


def cal_tof(dist_cm,C_):
    dist_um=dist_cm*10000
    tmr_=dist_um/(0.17*C_)
    tiempo_ = tmr_*0.00000033333
    return tiempo_


def correct_Sensor_lecture(lecture):
	if(lecture<=10):
		return round((lecture-lecture*0.1),2)
	elif(lecture>10 and lecture<=20):
		return round((lecture-lecture*0.06),2)
	elif(lecture>20 and lecture<=30):
		return round((lecture-lecture*0.03),2)
	elif(lecture>30 and lecture<=40):
		return round((lecture-lecture*0.04),2)
	else:
		return round((lecture-lecture*0.02),2)


def get_Sensor(sensor_no,correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x07
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			bus.write_byte(adress,sensor_no)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor1(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=1
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x09
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor2(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=2
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x0A
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor3(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=3
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x0B
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor4(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=4
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x0C
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor5(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=5
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x0D
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor6(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=6
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x0E
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor7(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=7
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x0F
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor8(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=8
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x10
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor9(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=9
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x11
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor10(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=10
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x12
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor11(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=11
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x13
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)

def get_Sensor12(correct_measurement):
	global Stat_Reg1
	global Stat_Reg2
	global adress
	global sensor_data
	global IOError_cont
	global C
	sensor_no=12
	try:
		value1=1
		value2=1
		if(sensor_no<1 or sensor_no>12):
			return "sensor number error, it don't exist, it must be betwen 1 and 12"
		elif(sensor_no<=5):
			value1=(Stat_Reg1>>(1+sensor_no))&1
			value2=Stat_Reg1&1
			# print bin(value)
		else:
			value1=(Stat_Reg2>>(sensor_no-6))&1			
			value2=Stat_Reg1&1
			# print bin(value)			
		if(value1 and value2):
			operation=0x14
			bus.write_byte(adress,operation)
			bus.write_byte(adress,operation)
			TMRL=bus.read_byte(adress)
			# print (hex(TMRL)) 
			TMRH=bus.read_byte(adress) 
			# print (hex(TMRH)) 
			IOError_cont=0
			if(correct_measurement):
				return correct_Sensor_lecture(cal_dist_cm(TMRL,TMRH))
			else:			
				C_old=C
				C=347.8
				val= cal_dist_cm(TMRL,TMRH)
				C=C_old
				return val
		else:			
			# print "sensor number ",sensor_no,
			# TMRL=0
			# # print (hex(TMRL)) 
			# TMRH=0
			# # print (hex(TMRH)) 
			if(value1!=1):
				text="it isn't active"
			if(value2!=1):
				text="Gb isn't active"
			if(value1!=1 and value2!=1):
				text="Gb isn't active and sensor "+str(sensor_no)+" it isn't active"
			return text
	except KeyboardInterrupt:
		print("keyboard IT at get_Sensor",sensor_no)
	except IOError:
		if(IOError_cont==5):
			print("IOError at get_Sensor 5 times",sensor_no)
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at get_Sensor",sensor_no)
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			get_Sensor(sensor_no,correct_measurement)


		
def print_sensor(sensor_no,correct_measurement):
	data=get_Sensor(sensor_no,correct_measurement)
	if(type(data)!=float):
		if(sensor_no<10):
			print "S0"+str(sensor_no)+": ",data
		else:
			print "S"+str(sensor_no)+": ",data
	else:
		if(sensor_no<10):
			print "S0"+str(sensor_no)+": ",data,"cm"
		else:
			print "S"+str(sensor_no)+": ",data, "cm"
	time.sleep(0.1)

def get_Sensor(sensor_no,correct_measurement):
	if(sensor_no==1):
		return get_Sensor1(correct_measurement)
	elif(sensor_no==2):
		return get_Sensor2(correct_measurement)
	elif(sensor_no==3):
		return get_Sensor3(correct_measurement)
	elif(sensor_no==4):
		return get_Sensor4(correct_measurement)
	elif(sensor_no==5):
		return get_Sensor5(correct_measurement)
	elif(sensor_no==6):
		return get_Sensor6(correct_measurement)
	elif(sensor_no==7):
		return get_Sensor7(correct_measurement)
	elif(sensor_no==8):
		return get_Sensor8(correct_measurement)
	elif(sensor_no==9):
		return get_Sensor9(correct_measurement)
	elif(sensor_no==10):
		return get_Sensor10(correct_measurement)
	elif(sensor_no==11):
		return get_Sensor11(correct_measurement)
	elif(sensor_no==12):
		return get_Sensor12(correct_measurement)

def print_sensor_new(sensor_no,correct_measurement):
	if(sensor_no==1):
		data=get_Sensor1(correct_measurement)
	elif(sensor_no==2):
		data=get_Sensor2(correct_measurement)
	elif(sensor_no==3):
		data=get_Sensor3(correct_measurement)
	elif(sensor_no==4):
		data=get_Sensor4(correct_measurement)
	elif(sensor_no==5):
		data=get_Sensor5(correct_measurement)
	elif(sensor_no==6):
		data=get_Sensor6(correct_measurement)
	elif(sensor_no==7):
		data=get_Sensor7(correct_measurement)
	elif(sensor_no==8):
		data=get_Sensor8(correct_measurement)
	elif(sensor_no==9):
		data=get_Sensor9(correct_measurement)
	elif(sensor_no==10):
		data=get_Sensor10(correct_measurement)
	elif(sensor_no==11):
		data=get_Sensor11(correct_measurement)
	elif(sensor_no==12):
		data=get_Sensor12(correct_measurement)
	if(type(data)!=float):
		if(sensor_no<10):
			print "S0"+str(sensor_no)+": ",data
		else:
			print "S"+str(sensor_no)+": ",data
	else:
		if(sensor_no<10):
			print "S0"+str(sensor_no)+": ",data,"cm"
		else:
			print "S"+str(sensor_no)+": ",data, "cm"
	time.sleep(0.1)


def reset():
	global adress
	global Tm
	global Stat_Reg1
	global Stat_Reg2
	global Temp
	global IOError_cont
	try:		
		operation=0x08
		bus.write_byte(adress,operation)
		bus.write_byte(adress,operation)	
		current_adress=adress
		adress=0x10
		change_adress(current_adress)
		change_Stat_Reg(Stat_Reg1)
		change_Stat_Reg(Stat_Reg2)
		change_Tm_ms(int(Tm))
		IOError_cont=0

	except KeyboardInterrupt:
		print("keyboard IT at reset")
	except IOError:
		if(IOError_cont==5):
			print("IOError at reset 5 times")
			print("please check the connection")
			time.sleep(0.5)
			IOError_cont=0
		else:
			print("IOError at reset")
			time.sleep(0.5)
			IOError_cont= IOError_cont+1
			reset()

def save_data():
	global adress
	global Tm
	global Stat_Reg1
	global Stat_Reg2
	global Temp
	txt_data = open("data.txt", 'w')
	txt_data.seek(0)
	txt_data.write("adress:\n")
	txt_data.write(str(adress))
	txt_data.write("\nTm:\n")
	txt_data.write(str(Tm))
	txt_data.write("\nStat_Reg1:\n")
	txt_data.write(str(Stat_Reg1))
	txt_data.write("\nStat_Reg2:\n")
	txt_data.write(str(Stat_Reg2))
	txt_data.write("\nTemp:\n")
	txt_data.write(str(Temp))
	txt_data.close()

def get_saved_data():
	global adress
	global Tm
	global Stat_Reg1
	global Stat_Reg2
	global Temp
	txt_data = open("data.txt", 'r')
	txt_data.readline()
	adress=int(txt_data.readline())
	# print hex(adress)
	txt_data.readline()
	Tm=float(txt_data.readline())
	# print Tm
	txt_data.readline()
	Stat_Reg1=int(txt_data.readline())
	# print bin(Stat_Reg1)
	txt_data.readline()
	Stat_Reg2=int(txt_data.readline())
	# print bin(Stat_Reg2)
	txt_data.readline()
	Temp=float(txt_data.readline())	
	# print Temp
	txt_data.close()



def get_all_sensors():
	Lm35_Enable()
	Global_Enable()
	for i in range(12):
		Enable_Sensor(i+1)
	return [get_Sensor(i+1,True) for i in range (12)]
