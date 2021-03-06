import socket, threading
import time
import datetime
import sys
import os
import board
import digitalio
import adafruit_max31855

#d
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
max31855 = adafruit_max31855.MAX31855(spi,cs)
cs2 = digitalio.DigitalInOut(board.D22)
max31855_2 = adafruit_max31855.MAX31855(spi,cs2)


def racs():
    RACS_st = 1
    message = ''
    while True:
        time.sleep(0.25)
        time.sleep(0.25)
        state = 1 #acscontroller.GetInput(0,26)
        if state == 1 :
            msgstate = 'Enabled.'
        else :
            msgstate = 'Disabled.'
        message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        message = message + '\tDIGITAL_IO\tRACS status: ' + msgstate + '\tserver_HX_RACS_BEAM'
        #broadcast_usr( message )
        if RACS_st != state :
            RACS_st = state
            broadcast_usr(message)

def fake_plc():
    HX_st = 1
    message = ''
    BEAM_st = 1
    while True:
        state = 0 # acscontroller.GetInput(0,22)
        time.sleep(0.25)  
        if state == 0 :
            message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            message = message + '\tDIGITAL_IO\tX-ray status: ' + 'ON.' + '\tserver_HX_RACS_BEAM'
        else:
            message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            message = message + '\tDIGITAL_IO\tX-ray status: ' + 'OFF.' + '\tserver_HX_RACS_BEAM'
        if BEAM_st != state :
            BEAM_st = state
            broadcast_usr(message)
        
        msgstate = ''
        state = 1 #acscontroller.GetInput(0,24)
        time.sleep(0.1)
        if state==1 :
            msgstate = 'Enabled.'
        else :
            msgstate = 'Disabled.'
        message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        message = message + '\tDIGITAL_IO\tHX status: ' + msgstate + '\tserver_HX_RACS_BEAM'
        if HX_st != state :
            HX_st = state
            broadcast_usr(message)

def read_temp():
        while True:
            try :
                temp = str(max31855.temperature)
                temp2 = str(max31855_2.temperature)
                #message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') 
                #message = message + '\tANALOG\tXRAD temp: {0:0.3F}:C : {1:0.3F}:F :'.format(temp, 86.0 ) 
                #message = message + '\tNote: internal temp not reported'
                #print( message, len(message) )
                message = str(temp+','+temp2)
                broadcast_usr( message ) 
                time.sleep(50)
            except KeyboardInterrupt as exc:
                print('***** Interrupted! *****')
                print(exc)
                #CONNECTION_LIST[0].close()
                exit()

def accept_client():
    while True:
        try:
            #accept    
            cli_sock, cli_add = ser_sock.accept()
            if len( CONNECTION_LIST ) == 0 :
                CONNECTION_LIST.append( cli_sock )
            else :
                CONNECTION_LIST[0] = cli_sock
        except KeyboardInterrupt as exc:
            print('***** Interrupted! *****')
            print( exc )
            #CONNECTION_LIST[0].close()
            exit()

def broadcast_usr( msg ):
    msg = msg + '\r'
    print('Sending message ',msg,' to client ', len(msg))
    for i in range(len(CONNECTION_LIST)):
        try:
            #data = CONNECTION_LIST[i][1].recv(256)
            data = msg
            if data:
                CONNECTION_LIST[i].send(data.encode())
        except Exception as x:
            print(x)
            break

if __name__ == "__main__":    
    CONNECTION_LIST = []
    # socket
    ser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind
    HOST = '10.0.0.4'
    PORT = 5023
    ser_sock.bind((HOST, PORT))

    # listen    
    ser_sock.listen(1)
    print('simulated PLC and thermocouple data server started on port : ' + str(PORT))
    thread_ac = threading.Thread(target = accept_client)
    thread_ac.daemon = True
    thread_ac.start()

    thread_ad = threading.Thread( target = read_temp )
    thread_ad.daemon = True
    thread_ad.start()
    #thread_PLC = threading.Thread( target = fake_plc )
    #thread_PLC.daemon = True
    #thread_PLC.start()
    #thread_racs = threading.Thread( target = racs )
    #thread_racs.daemon = True
    #thread_racs.start()

    while True:
        try:
            time.sleep(10.0)
        except KeyboardInterrupt:
            print('***** Interrupted! *****')
            if len( CONNECTION_LIST ) > 0:
                CONNECTION_LIST[0].close()
            exit(1)
  
  