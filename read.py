from paramiko import SSHClient
import math as mt
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.signal.signaltools import correlate
import numpy as np

BETA = 0.25

ssh = SSHClient()
ssh.load_system_host_keys()

ssh.connect('192.168.1.1', username='root', password='root')

print('started...')
stdin, stdout, stderr = ssh.exec_command('/bin/recvCSI', get_pty=True)

ready = False
theta = None
samples = []

for line in iter(stdout.readline, ""):
    # print(line, end='')
    if line.find("F") != -1:
        # Process the new dataset
        # print(data)

        # Convert data from cartesian to polar

        polarData = [[[], []], [[], []]]

        for x in [0,1]:
            for y in [0,1]:
                lastTheta = None
                for val in data[x][y]:
                    theta = mt.atan(val[1]/val[0]) if val[0] != 0 else (mt.pi/2 if val[1] > 0 else 1.5*mt.pi)
                    if lastTheta is not None and abs(theta - lastTheta) > 1:
                        theta = theta + mt.pi
                    lastTheta = theta
                    polarData[x][y].append([mt.sqrt(val[0]**2 + val[1]**2), theta])
        
        # print(polarData)
        plt.clf()
        wave1 = fft([theta[1] for theta in polarData[0][0]])
        wave2 = fft([theta[1] for theta in polarData[0][1]])
        wave1 = wave1[3:len(wave1)-2]
        wave2 = wave2[3:len(wave2)-2]
        plt.plot(wave1)
        plt.plot(wave2)
        xcor = np.argmax(correlate(wave1, wave2))
        theta = theta*(1-BETA) + xcor*BETA
        print(theta)
        # plt.polar(0, 500)
        # plt.polar(theta, np.mean([dat[0] for dat in polarData[0][0]]), marker='o')
        # plt.plot([theta[1] for theta in polarData[1][0]])
        # plt.plot([theta[1] for theta in polarData[1][1]])
        plt.draw()
        plt.pause(0.0001)
        # Reset
        data = [[[], []], [[], []]]
    elif line.find("#Receiving") != -1:
        # This is the beginning, let's set defaults
        ready = True
        data = [[[], []], [[], []]] # [Antenna0rx, Antenna1rx] each with [Antenna0tx, Antenna1tx]
        plt.ion()
    else:
        if not ready:
            continue
        
        # Process the inputs
        if line.find('~') != -1:
            info = line.replace('~', '').replace('\r\n', '')
            pos = [int(val) for val in info.split('.')]
        else:
            data[pos[0]][pos[1]].append([int(val) for val in line.replace('\r\n', '').split(',')])
