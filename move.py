import RPi.GPIO as GPIO
from time import sleep
import time
import pigpio
import srte
 
GPIO.setmode(GPIO.BCM)

MotorE = 26


Motor1 = [20,21]

Motor2 = [13,19]

Motor3 = [5,6]

Motor4 = [12,16]


GPIO.cleanup(MotorE)


GPIO.cleanup(Motor1[0])
GPIO.cleanup(Motor1[1])
GPIO.cleanup(Motor2[0])
GPIO.cleanup(Motor2[1])
GPIO.cleanup(Motor3[0])
GPIO.cleanup(Motor3[1])
GPIO.cleanup(Motor4[0])
GPIO.cleanup(Motor4[1])


GPIO.setup(MotorE,GPIO.OUT)

GPIO.setup(Motor1[0],GPIO.OUT)
GPIO.setup(Motor1[1],GPIO.OUT)
GPIO.setup(Motor2[0],GPIO.OUT)
GPIO.setup(Motor2[1],GPIO.OUT)
GPIO.setup(Motor3[0],GPIO.OUT)
GPIO.setup(Motor3[1],GPIO.OUT)
GPIO.setup(Motor4[0],GPIO.OUT)
GPIO.setup(Motor4[1],GPIO.OUT)

pi = pigpio.pi()

if not pi.connected:
   exit()

S=[]
S.append(srte.sonar(pi, 23, 22))
S.append(srte.sonar(pi, 17, 27))
r = 1

CHANGE_DISTANCE = 35		# 10 cm of any ostacles
CRITICAL_DISTANCE = 15		# 5 cm if too close, so move around or something
# any distance far than CHANGE - just move

#     \L|  |R/
#    M1------M2
#      |    |
#      |    |
#    M4------M3

#              M1   M2   M3   M4
Motors_status=['S', 'S', 'S' ,'S']		#[S]top- [F]orward /\ [B]ackward \/
#               L R
Sensors_values=[0,0]
Sensors_status=['unknown','unknown']

def show_status():
   print ("M1 {}, M2 {}, M3 {}, M4 {}".format(Motors_status[0],Motors_status[1],Motors_status[2],Motors_status[3]));
   print ("L '{}' {}, R '{}' {}".format(Sensors_status[0],Sensors_values[0],Sensors_status[1],Sensors_values[1]));

def choose_way():
   print "choose the way"
   if (Sensors_status[0]=='move' and Sensors_status[1]=='move'):
      Motors_status[0]="F";
      Motors_status[1]="F";
      Motors_status[2]="F";
      Motors_status[3]="F";
   elif (Sensors_status[0]=='obstacle' and Sensors_status[1]=='move'):
      Motors_status[0]="F";
      Motors_status[1]="B";
      Motors_status[2]="B";
      Motors_status[3]="F";
   elif (Sensors_status[0]=='move' and Sensors_status[1]=='obstacle'):
      Motors_status[0]="B";
      Motors_status[1]="F";
      Motors_status[2]="F";
      Motors_status[3]="B";
   elif (Sensors_status[0]=='critical' and Sensors_status[1]!='critical'):
      Motors_status[0]="F";
      Motors_status[1]="B";
      Motors_status[2]="B";
      Motors_status[3]="F";
   elif (Sensors_status[0]!='critical' and Sensors_status[1]=='critical'):
      Motors_status[0]="B";
      Motors_status[1]="F";
      Motors_status[2]="F";
      Motors_status[3]="B";
   else:
     do_back();
     do_rotate();

def do_back():
   Motors_status[0]="B";
   Motors_status[1]="B";
   Motors_status[2]="B";
   Motors_status[3]="B";
   do_motors(1);	# move with delay TODO choose delay time for rotate
   

def do_rotate():
   Motors_status[0]="B";
   Motors_status[1]="F";
   Motors_status[2]="F";
   Motors_status[3]="B";
   do_motors(0.1);	# move with delay TODO choose delay time for rotate

def do_motor(status,motor):
   if (status=='B'):
      #GPIO.output(motor[0],GPIO.LOW)
      GPIO.output(motor[0],GPIO.HIGH)
      GPIO.output(motor[1],GPIO.LOW)
   elif (status=='F'):
      GPIO.output(motor[0],GPIO.LOW)
      GPIO.output(motor[1],GPIO.HIGH)
   else:
      GPIO.output(motor[0],GPIO.HIGH)
      GPIO.output(motor[1],GPIO.HIGH)

def do_motors(d):
   #print "Do motors"

   m_id=0
   for way in Motors_status:
      if m_id==0:
         do_motor(way,Motor1)
      elif m_id==1:
         do_motor(way,Motor2)
      elif m_id==2:
         do_motor(way,Motor3)
      elif m_id==3:
         do_motor(way,Motor4)
      else:
         print "Unknown motor"
      m_id+=1;

   GPIO.output(MotorE,GPIO.HIGH)
   if (Sensors_status[0]!='move' or Sensors_status[1]!='move'):
      time.sleep(0.1)
      GPIO.output(MotorE,GPIO.LOW)
      print "!!! ROTATE !!!!";
      #time.sleep(0.3)
      GPIO.output(MotorE,GPIO.LOW)
      #time.sleep(3)
      GPIO.output(MotorE,GPIO.LOW)

   if d>0:
      time.sleep(d)

try:
   while True:
      GPIO.output(MotorE,GPIO.LOW)
      for s in S:
         s.trigger()

      time.sleep(0.03)
      r=0
      for s in S:
         #print("{} {:.1f}".format(r, s.read()))
         d=s.read()
         Sensors_values[r]=d;
         if d>CHANGE_DISTANCE:
            Sensors_status[r]='move';
         elif d>CRITICAL_DISTANCE:
            Sensors_status[r]='obstacle';
         else:
            Sensors_status[r]='critical';
         r+=1;
      time.sleep(0.06)	# sleep 60ms NOT TESTED
      choose_way()
      show_status()
      do_motors(0.1)

except KeyboardInterrupt:
   pass

print("\ntidying up")

for s in S:
   s.cancel()

pi.stop()


GPIO.output(MotorE,GPIO.LOW)
 
GPIO.cleanup()
