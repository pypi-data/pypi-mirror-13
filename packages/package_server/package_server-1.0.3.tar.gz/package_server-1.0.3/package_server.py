import numpy as np
import cv2
import socket
import time
import sys

class pickup_table:
    def __init__(self):
        # Create a black image
        self.img = np.zeros((300,1200,3), dtype='uint8')
        cv2.rectangle(self.img,(0,0),(300,300),(255,255,255),-1)
        cv2.rectangle(self.img,(300,0),(600,300),(255,255,255),-1)
        cv2.rectangle(self.img,(600,0),(900,300),(255,255,255),-1)
        cv2.rectangle(self.img,(900,0),(1200,300),(255,255,255),-1)
        cv2.imshow("Packages on the Robot",self.img)
        time.sleep(1)
        cv2.waitKey(1)
        self.token = [['E' for x in range(2)] for x in range(4)]
        input1 = ''
        input2 = ''
        input3 = 2
                        
        ##create a socket object
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (socket.gethostname(), 10002)
        #bind to port'
        try:
            serversocket.bind(server_address)
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message' + msg[1]
            sys.exit()
        print 'Socket bind complete'
        # queue up to 10 requests
        serversocket.listen(10)
        print 'Socket now listening'
        while True:
            # establish a connection
            print >>sys.stderr, 'waiting for a connection'
            connection,client_address = serversocket.accept()      
            try:
                print >>sys.stderr, 'connection from',client_address
                # Receive the data in small chunks and re transmit it
                while True:
                    data = connection.recv(3)
                    print >>sys.stderr, 'received "%s"' % data
                    if data == 'CCC':
                        print >>sys.stderr,'Socket closed'
                        connection.close()
                        serversocket.close()
                        break
                    if data:
                        print >>sys.stderr, 'sending data back to the client'
                        ram = str(data)
                        input1 = ram[0]
                        input2 = ram[1]
                        input3 = ram[2]
                        self.FillPackage(input1,input2,input3)
                        connection.sendall(data)
                    else:
                        connection,client_address = serversocket.accept()
                        continue
            finally:
                cv2.destroyAllWindows()
                break
        
            

        


    #####################################################
    #####################################################
    def CheckEmptySection(self):
        for i in xrange(0,4):
            if (self.token[i][0] == 'E' and self.token[i][1] == 'E'):
                return i+1
        return -1

    def whichPackage(self,Color,Shape):
        for i in xrange(0,4):
            if (self.token[i][0] == Color and self.token[i][1] == Shape):
                return i+1
        return 0

    def FillPackage(self,Color,Shape,fill):
        '''
        * Function Name: FillPackage
        * Input:
            @param1: Color of the Package
            @param2: Shape of the Package
            @param3: fill for filling fill = 1 and empting the Package fill = 0 
        * Output: An image Showing Package
        * Example Call: FillPackage('P','T',1) # fill triangle Package of Pink color 
        '''

        Startx = 0
        Starty = 0
        Endx = 0
        Endy = 0
        blue = 255
        green = 255
        red = 255
    ##################################    
        try:
            if(Color == 'G'):
                blue = 0
                green = 255
                red = 0
            elif(Color == 'P'):
                blue = 255
                green = 0
                red = 255
            elif(Color == 'B'):
                blue = 255
                green = 255
                red = 0
            elif(Color == 'O'):
                blue = 0
                green = 165
                red = 255
        except:
            print "Input for Color is not given as per the format...it can be 'P','G','SB' or 'O'"
            
    ######################################        
        try:
            if(fill == '1'):
                section = self.CheckEmptySection()
            else:
                section = self.whichPackage(Color,Shape)
        except:
            print "Input for Fill is not given as per the format...it can only be '0' or '1'"
    ########################################
        if(section==1):
            Startx = 0
            Starty = 0
            Endx = 300
            Endy = 300
        elif(section==2):
            Startx = 300
            Starty = 0
            Endx = 600
            Endy = 300   
        elif(section==3):
            Startx = 600
            Starty = 0
            Endx = 900
            Endy = 300
        elif(section==4):
            Startx = 900
            Starty = 0
            Endx = 1200
            Endy = 300
        elif(section == -1):
            print "Sorry :( Bag is Full"
            fill = '-1'
        elif(section == 0):
            print "No such Package available in the Bag"
            fill = '-2'
    ##########################################
        if(fill == '1'):
            self.token[section-1][0] = Color
            self.token[section-1][1] = Shape
            count = 0
            while(count<2):
                
                if(Shape == 'T'):
                    triangle = np.array([[ [Startx+150,0], [Startx,Endy], [Endx,Endy]]], dtype = 'int32')
                    cv2.fillPoly(self.img, triangle,(blue,green,red))
                    cv2.imshow("Packages on the Robot",self.img)
                    time.sleep(1)
                    cv2.waitKey(1)
                elif(Shape == 'C'):
                    cv2.circle(self.img,(Startx+150,150),150,(blue,green,red),-1)
                    cv2.imshow("Packages on the Robot",self.img)
                    time.sleep(1)
                    cv2.waitKey(1)
                else:
                    cv2.rectangle(self.img,(Startx,Starty),(Endx,Endy),(blue,green,red),-1)
                    cv2.imshow("Packages on the Robot",self.img)
                    time.sleep(1)
                    cv2.waitKey(1)
                
                cv2.rectangle(self.img,(Startx,Starty),(Endx,Endy),(255,255,255),-1)
                cv2.imshow("Packages on the Robot",self.img)
                time.sleep(1)
                cv2.waitKey(1)
                count += 1


            if(Shape == 'T'):
                triangle = np.array([[ [Startx+150,0], [Startx,Endy], [Endx,Endy]]], dtype = 'int32')
                cv2.fillPoly(self.img, triangle,(blue,green,red))
            elif(Shape =='C'):
                cv2.circle(self.img,(Startx+150,150),150,(blue,green,red),-1)
            else:
                cv2.rectangle(self.img,(Startx,Starty),(Endx,Endy),(blue,green,red),-1)
            cv2.imshow("Packages on the Robot",self.img)
            time.sleep(1)
            cv2.waitKey(1)
            
        elif(fill == '0'):
            self.token[section-1][0] = 'E'
            self.token[section-1][1] = 'E'
            count = 0
            while count < 2 :
                cv2.rectangle(self.img,(Startx,Starty),(Endx,Endy),(255,255,255),-1)
                cv2.imshow("Packages on the Robot",self.img)
                time.sleep(1)
                cv2.waitKey(1)

                if(Shape == 'T'):
                    triangle = np.array([[ [Startx+150,0], [Startx,Endy], [Endx,Endy]]], dtype = 'int32')
                    cv2.fillPoly(self.img, triangle,(blue,green,red))
                elif(Shape == 'C'):
                    cv2.circle(self.img,(Startx+150,150),150,(blue,green,red),-1)
                else:
                    cv2.rectangle(self.img,(Startx,Starty),(Endx,Endy),(blue,green,red),-1)
                cv2.imshow("Packages on the Robot",self.img)
                time.sleep(1)
                cv2.waitKey(1)
                count += 1
            cv2.rectangle(self.img,(Startx,Starty),(Endx,Endy),(255,255,255),-1)
            cv2.imshow("Packages on the Robot",self.img)
            time.sleep(1)
            cv2.waitKey(1)
        elif(fill == '-1'):
            img1 = self.img.copy()
            cv2.rectangle(img1,(0,0),(1200,300),(0,0,255),-1)
            cv2.imshow("Packages on the Robot",img1)
            time.sleep(2)
            cv2.waitKey(2)
            cv2.imshow("Packages on the Robot",self.img)
            time.sleep(1)
            cv2.waitKey(1)
        elif(fill == '-2'):
            img1 = self.img.copy()
            cv2.rectangle(img1,(0,0),(1200,300),(255,0,0),-1)
            cv2.imshow("Packages on the Robot",img1)
            time.sleep(2)
            cv2.waitKey(2)
            cv2.imshow("Packages on the Robot",self.img)
            time.sleep(1)
            cv2.waitKey(1)


