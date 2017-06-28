# -*- coding:utf-8 -*-
__author__ = 'xuyunnan'

import os
import sys
from numpy import *
from matplotlib import pyplot as plt

main_pid = 0
tot_info = []

TimeStart = {}
TimeEach = {}
RelyOn = {}
IOWaitTime = {}
energyEvent = {}


threadNumber = []


def analysis_energy():
    network_status = 0
    timeList = []
    energyList = []
    number = 0
    lastScreenEnergy = 0.0

    the_end_energy = 0.0

    for k in energyEvent:

        if energyEvent[k]['Screen'] < 10:
            energyEvent[k]['tot_energy'] += lastScreenEnergy
        else:
            global lastScreenEnergy
            energyEvent[k]['tot_energy'] += energyEvent[k]['Screen'] * 0.02
            lastScreenEnergy = energyEvent[k]['Screen'] * 0.02

        energyEvent[k]['tot_energy'] += energyEvent[k]['CPU'] * 0.001 * 0.001 * 0.001
        energyEvent[k]['tot_energy'] += energyEvent[k]['DMA'] * 0.001 * 0.001 * 0.001
        energyEvent[k]['tot_energy'] += 0.104 * 0.02
        energyEvent[k]['tot_energy'] += energyEvent[k]['GPU']
        energyEvent[k]['tot_energy'] += energyEvent[k]['NAND']

        if energyEvent[k]['status']['NetworkData'] == 0:
            if network_status == 0:
                continue
            else:
                network_status -= 1
        else:
            network_status = 24
            energyEvent[k]['tot_energy'] += 0.46 * 0.02 + energyEvent[k]['status']['NetworkData'] * 0.001 * 0.11

        timeList.append(number)

        '''
        if number > 75 and number < 130:
            energyList.append((energyEvent[k]['tot_energy'] - 0.5) * 2.5 * 1.5 - 1)
        elif number < 300:
            energyList.append((energyEvent[k]['tot_energy'] - 0.5) * 2.5 - 1)
        else:
            energyList.append(energyEvent[k]['tot_energy'] - 0.3)
        '''
        
        the_end_energy += 0.02 * energyEvent[k]['tot_energy']
        number += 1
        #if number > 500:
        #    break


    plt.figure(figsize=(80, 16), dpi = 120)



    file = open("/Users/xuyunnan/develop/bishe/data/energy/open_hupu.txt")
    all_the_text = file.read()
    intList = all_the_text.split(',')
    number = 0
    start = 0
    for i in intList:
        if len(i) > 0:
            k = int(i)
            start = start + 1
            if k > 10000:
                break

    end = len(intList)

    currentList2 = []
    timeList2 = []
    j = 0
    for i in intList:
        if i == '':
            continue
        currentList2.append(float(i) * 0.001 * 0.001 * 4.2)
        timeList2.append(j - 75)
        j += 1


    plt.plot(timeList, energyList, label="Energy by Emulator", linestyle="-")
    plt.plot(timeList2, currentList2, label="Energy by Test", linestyle=":")

    plt.title('HupuGames App Energy on Emulator')
    plt.xlabel('Time')
    plt.ylabel('Power')
    plt.legend(loc='upper right', shadow=True, fontsize=12)
    plt.show()

    print "the_end_energy : " , the_end_energy


def analysis_time(start, end):

    # init data structure
    for i in range(start, end + 1):
        TimeStartInit = {}
        for j in tot_info[i]['thread_info']:
            TimeStartInit[j] = 0.0

        TimeStart[i] = TimeStartInit

        TimeEachInit = {}
        for j in tot_info[i]['thread_info']:
            TimeEachInit[j] = float(tot_info[i]['thread_info'][j]['time']) / 200000000

        TimeEach[i] = TimeEachInit

        RelyOnInit = {}
        for j in tot_info[i]['thread_info']:
            RelyOnInit[j] = []

        RelyOn[i] = RelyOnInit

        IOWaitTimeInit = {}
        for j in tot_info[i]['thread_info']:
            IOWaitTimeInit[j] = 0.0

        IOWaitTime[i] = IOWaitTimeInit

    energy_time = 0.0
    ttt = 0
    while ttt < 3000:
        energyEvent[energy_time] = {'CPU':0.0, "Screen" : 0.0, "Network":0.0, "NAND":0.0, "DMA":0.0, "GPU":0.0, "status": {"NetworkData": 0}, "tot_energy" : 0.0}
        # CPU Screen Network NAND DMA GPU
        energy_time = float(ttt) * 0.02
        ttt += 1

    # fill RelyOn
    threadLastCPU = {}
    for t in threadNumber:
        threadLastCPU[t] = -1

    for i in range(start, end+1):
        for t in tot_info[i]['thread_info']:
            if tot_info[i]['thread_info'][t]['time'] > 0:
                if threadLastCPU[t] != -1:
                    RelyOn[i][t].append([threadLastCPU[t], t])
                else:
                    RelyOn[i][t].append([i,tot_info[i]['thread_info'][t]['father']])

                threadLastCPU[t] = i


    threadLastFutexWake = {}
    for t in threadNumber:
        threadLastFutexWake[t] = -1

    for i in range(start, end + 1):
        for t in tot_info[i]['thread_info']:
            if tot_info[i]['thread_info'][t]['futex_wake_times'] != 0:
                threadLastFutexWake[t] = i

        if i > start:
            for t in tot_info[i]['thread_info']:
                if tot_info[i]['thread_info'][t]['time'] != 0 and (t in tot_info[i-1]['thread_info']) and tot_info[i-1]['thread_info'][t]['time'] == 0:
                    wakeby = tot_info[i]['thread_info'][t]['futex_wake_by']
                    if wakeby in threadNumber:
                        if threadLastFutexWake[wakeby] != -1:
                            RelyOn[i][t].append([threadLastFutexWake[wakeby], wakeby])
                        else :
                            RelyOn[i][t].append([i, wakeby])

    threadLastWaitWake = {}
    for t in threadNumber:
        threadLastWaitWake[t] = -1

    for i in range(start, end + 1):
        for t in tot_info[i]['thread_info']:
            if tot_info[i]['thread_info'][t]['waitqueue_wake_times'] != 0:
                threadLastWaitWake[t] = i

        if i > start:
            for t in tot_info[i]['thread_info']:
                if tot_info[i]['thread_info'][t]['time'] != 0 and (t in tot_info[i-1]['thread_info']) and tot_info[i-1]['thread_info'][t]['time'] == 0:
                    wakeby = tot_info[i]['thread_info'][t]['waitqueue_wake_by']
                    if wakeby in threadNumber:
                        if threadLastWaitWake[wakeby] != -1:
                            RelyOn[i][t].append([threadLastWaitWake[wakeby], wakeby])
                        else :
                            RelyOn[i][t].append([i, wakeby])


    for i in range(start, end+1):
        for t in tot_info[i]['thread_info']:
            if tot_info[i]['thread_info'][t]['file_read_times'] != 0 and tot_info[i]['hardware_info']['bio']['read_times'] != 0:
                IOWaitTime[i][t] = 0.00030 * (1 + int(tot_info[i]['hardware_info']['bio']['count']) / 4096)
                tot_info[i]['hardware_info']['bio']['count'] = 0
            elif tot_info[i]['thread_info'][t]['network_recv_times'] != 0:
                IOWaitTime[i][t] = 0.01


    '''
    total_cycle = 0.0
    for i in range(start, end + 1):
        for j in tot_info[i]['thread_info']:
            total_cycle += tot_info[i]['thread_info'][j]['time']

    print "total_cycle = ", total_cycle
    '''

    '''
    for i in range(start, end + 1):
        print i, ":"
        for t in RelyOn[i]:
            print t,":",RelyOn[i][t], ",",

        print ""
    '''

    # start anslysis

    cpu_next_aviliable = [0.0, 0.0, 0.0, 0.0]
    now_time = 0.0

    for i in range(start+1, end + 1):
        for j in tot_info[i]['thread_info']:
            maxTimeSlice = 0
            maxPid = 0
            maxTime = 0.0
            for relyList in RelyOn[i][j]:
                timeSlice = relyList[0]
                pid = relyList[1]
                if pid not in TimeStart[timeSlice]:
                    continue
                timeEnd = TimeStart[timeSlice][pid] + TimeEach[timeSlice][pid] + IOWaitTime[timeSlice][pid]
                if timeEnd > maxTime:
                    maxTime = timeEnd
                    maxTimeSlice = timeSlice
                    maxPid = pid

            now_time = maxTime
            findCPU = 0
            CPUId = -1
            '''
            if now_time >= cpu_next_aviliable[0]:
                TimeStart[i][j] = now_time
                cpu_next_aviliable[0] = TimeStart[i][j] + TimeEach[i][j]
                continue

            if now_time >= cpu_next_aviliable[1]:
                TimeStart[i][j] = now_time
                cpu_next_aviliable[1] = TimeStart[i][j] + TimeEach[i][j]
                continue

            if now_time >= cpu_next_aviliable[2]:
                TimeStart[i][j] = now_time
                cpu_next_aviliable[2] = TimeStart[i][j] + TimeEach[i][j]
                continue

            if now_time >= cpu_next_aviliable[3]:
                TimeStart[i][j] = now_time
                cpu_next_aviliable[3] = TimeStart[i][j] + TimeEach[i][j]
                continue
            '''
            for c in range(0,4):
                if now_time >= cpu_next_aviliable[c]:
                    TimeStart[i][j] = now_time
                    cpu_next_aviliable[c] = TimeStart[i][j] + TimeEach[i][j]

                    num = float (int(now_time / 0.02)) * 0.02
                    energyEvent[num]['CPU'] = float(tot_info[i]['thread_info'][j]['energy'])

                    energyEvent[num]['status']['NetworkData'] += tot_info[i]['thread_info'][j]['network_data_count']


                    if j == main_pid:
                        energyEvent[num]['NAND'] += tot_info[i]['hardware_info']['bio']['count'] * 0.00043 / 4096.0
                        energyEvent[num]['CPU'] += tot_info[i]['hardware_info']['system_service']['time'] * 100.0
                        energyEvent[num]['CPU'] += tot_info[i]['hardware_info']['surfaceflinger']['time'] * 100.0
                        energyEvent[num]['Screen'] = 0.41 + tot_info[i]['hardware_info']['screen']['R'] * 0.00028 * 256 \
                                                          + tot_info[i]['hardware_info']['screen']['G'] * 0.00039 * 256 \
                                                          + tot_info[i]['hardware_info']['screen']['B'] * 0.00048 * 256

                        energyEvent[num]['GPU'] = 0.0034 * tot_info[i]['hardware_info']['gpu']['image_draw_times'] + \
                                                  0.0023 * tot_info[i]['hardware_info']['gpu']['draw_element_times']

                        energyEvent[num]['DMA'] = 6.5 * tot_info[i]['hardware_info']['dma']['count']

                    findCPU += 1
                    break

            if findCPU == 1:
                continue

            near = 9999999.999
            near_id = -1
            for cpuid in range(0,3):
                if cpu_next_aviliable[cpuid] < near:
                    near = cpu_next_aviliable[cpuid]
                    near_id = cpuid

            now_time = near
            TimeStart[i][j] = now_time
            num = float (int(now_time / 0.02)) * 0.02
            energyEvent[num]['CPU'] = float(tot_info[i]['thread_info'][j]['energy'])

            energyEvent[num]['status']['NetworkData'] += tot_info[i]['thread_info'][j]['network_data_count']


            if j == main_pid:
                energyEvent[num]['NAND'] += tot_info[i]['hardware_info']['bio']['count'] * 0.00043 / 4096.0
                energyEvent[num]['CPU'] += tot_info[i]['hardware_info']['system_service']['time'] * 100.0
                energyEvent[num]['CPU'] += tot_info[i]['hardware_info']['surfaceflinger']['time'] * 100.0
                energyEvent[num]['Screen'] = 0.41 + tot_info[i]['hardware_info']['screen']['R'] * 0.00028 * 256 \
                                                          + tot_info[i]['hardware_info']['screen']['G'] * 0.00039 * 256 \
                                                          + tot_info[i]['hardware_info']['screen']['B'] * 0.00048 * 256

                energyEvent[num]['GPU'] = 0.0034 * tot_info[i]['hardware_info']['gpu']['image_draw_times'] + \
                                                  0.0023 * tot_info[i]['hardware_info']['gpu']['draw_element_times']

                energyEvent[num]['DMA'] = 6.5 * tot_info[i]['hardware_info']['dma']['count']


    print "!!!!!! ToT time  = " ,TimeStart[end][main_pid]
    pass

def drawHardwareInfoPic(start, end):

    plt.figure(figsize=(100, 50), dpi = 80)
    axes = plt.subplot(111)

    axes.set_yticks([0,1,2,3,4,5])
    yticks_label = ['Screen Post', 'DMA', 'BIO', 'GPU', 'System Service', 'Surfaceflinger']
    axes.set_yticklabels(yticks_label,rotation='horizontal', fontsize=16)

    system_service_CPU_x = []
    system_service_CPU_y = []
    surfaceflinger_CPU_x = []
    surfaceflinger_CPU_y = []
    screen_post_x = []
    screen_post_y = []
    dma_x = []
    dma_y = []
    bio_x = []
    bio_y = []
    gpu_element_x = []
    gpu_element_y = []
    gpu_image_x = []
    gpu_image_y = []


    for j in range(start, end + 1):
        h = tot_info[j]['hardware_info']
        if h['screen']['post_number'] > 0:
            screen_post_x.append(j)
            screen_post_y.append(0)

        if h['dma']['times'] > 0:
            dma_x.append(j)
            dma_y.append(1)

        if h['bio']['count'] > 0:
            bio_x.append(j)
            bio_y.append(2)

        if h['gpu']['draw_element_times'] > 0:
            gpu_element_x.append(j)
            gpu_element_y.append(3)

        if h['gpu']['image_draw_times'] > 0:
            gpu_image_x.append(j)
            gpu_image_y.append(3)

        if h['system_service']['time'] > 0:
            system_service_CPU_x.append(j)
            system_service_CPU_y.append(4)

        if h['system_service']['time'] > 0:
            surfaceflinger_CPU_x.append(j)
            surfaceflinger_CPU_y.append(5)

    axes.scatter(screen_post_x, screen_post_y,  c='red', marker = 'x',s = 20, edgecolors = None, label="Screen Post")
    axes.scatter(dma_x, dma_y,  c='blue', marker = 'x',s = 20, edgecolors = None, label="DMA")
    axes.scatter(bio_x, bio_y,  c='black', marker = 'x',s = 20, edgecolors = None, label="BIO")
    axes.scatter(gpu_element_x, gpu_element_y,  c='green', marker = 'x',s = 20, edgecolors = None, label="GPU element")
    axes.scatter(gpu_image_x, gpu_image_y,  c='green', marker = '+',s = 20, edgecolors = None, label="GPU 2D image")
    axes.scatter(system_service_CPU_x, system_service_CPU_y,  c='red', marker = '+',s = 20, edgecolors = None, label="System Service")
    axes.scatter(surfaceflinger_CPU_x, surfaceflinger_CPU_y,  c='red', marker = '+',s = 20, edgecolors = None, label="Surfaceflinger")


    plt.legend(loc='upper right', shadow=True, fontsize=18)

    plt.grid(True)

    plt.show()

    pass

def drawThreadInfoPic(start, end):

    plt.figure(figsize=(100, 200), dpi = 40)
    axes = plt.subplot(111)

    plt.rc('font', size=8)
    plt.legend(loc=0, numpoints=1)

    cpu_x_small = []
    cpu_y_small = []
    cpu_x_mid = []
    cpu_y_mid = []
    cpu_x_big = []
    cpu_y_big = []

    lockwake_x_small = []
    lockwake_y_small = []
    lockwake_x_mid = []
    lockwake_y_mid = []
    lockwake_x_big = []
    lockwake_y_big = []


    lockwait_x_small = []
    lockwait_y_small = []
    lockwait_x_mid = []
    lockwait_y_mid = []
    lockwait_x_big = []
    lockwait_y_big = []


    fileIO_x_small = []
    fileIO_y_small = []
    fileIO_x_mid = []
    fileIO_y_mid = []
    fileIO_x_big = []
    fileIO_y_big = []

    network_x_small = []
    network_y_small = []
    network_x_mid = []
    network_y_mid = []
    network_x_big = []
    network_y_big = []

    for t in tot_info[end]['thread_info']:
        threadNumber.append(t)

    for i in range(start, end + 1):

        for tid in tot_info[i]['thread_info']:

            threadInfo = tot_info[i]['thread_info'][tid]

            if threadInfo['time'] > 0:
                if threadInfo['time'] < 4096:
                    cpu_x_small.append(i)
                    cpu_y_small.append(threadInfo['pid'])
                elif threadInfo['time'] < 4096 * 64:
                    cpu_x_mid.append(i)
                    cpu_y_mid.append(threadInfo['pid'])
                else:
                    cpu_x_big.append(i)
                    cpu_y_big.append(threadInfo['pid'])

            if threadInfo['futex_wake_times'] + threadInfo['waitqueue_wake_times'] > 0:
                if threadInfo['futex_wake_times'] + threadInfo['waitqueue_wake_times'] == 1:
                    lockwake_x_small.append(i)
                    lockwake_y_small.append(threadInfo['pid'])
                elif threadInfo['futex_wake_times'] + threadInfo['waitqueue_wake_times'] < 10 :
                    lockwake_x_mid.append(i)
                    lockwake_y_mid.append(threadInfo['pid'])
                else :
                    lockwake_x_big.append(i)
                    lockwake_y_big.append(threadInfo['pid'])

            if threadInfo['futex_wait_times'] + threadInfo['waitqueue_wait_times'] > 0:
                if threadInfo['futex_wait_times'] + threadInfo['waitqueue_wait_times'] == 1:
                    lockwait_x_small.append(i)
                    lockwait_y_small.append(threadInfo['pid'])
                elif threadInfo['futex_wait_times'] + threadInfo['waitqueue_wait_times'] < 10 :
                    lockwait_x_mid.append(i)
                    lockwait_y_mid.append(threadInfo['pid'])
                else :
                    lockwait_x_big.append(i)
                    lockwait_y_big.append(threadInfo['pid'])


            if threadInfo['file_read_count'] > 0:
                if threadInfo['file_read_count'] < 4096:
                    fileIO_x_small.append(i)
                    fileIO_y_small.append(float(threadInfo['pid']) + 0.4)
                elif threadInfo['file_read_count'] < 4096 * 64:
                    fileIO_x_mid.append(i)
                    fileIO_y_mid.append(float(threadInfo['pid']) + 0.4)
                else:
                    fileIO_x_big.append(i)
                    fileIO_y_big.append(float(threadInfo['pid']) + 0.4)

            if threadInfo['network_data_count'] > 0:
                if threadInfo['network_data_count'] < 64:
                    network_x_small.append(i)
                    network_y_small.append(float(threadInfo['pid']) - 0.4)
                elif threadInfo['network_data_count'] < 1024:
                    network_x_mid.append(i)
                    network_y_mid.append(float(threadInfo['pid']) - 0.4)
                else :
                    network_x_big.append(i)
                    network_y_big.append(float(threadInfo['pid']) - 0.4)

    typeCPU_1 = axes.scatter(cpu_x_small, cpu_y_small,  c='red', marker = 'x',s = 5, edgecolors = None)
    typeCPU_2 = axes.scatter(cpu_x_mid, cpu_y_mid,  c='red', marker = 'x',s = 20, edgecolors = None)
    typeCPU_3 = axes.scatter(cpu_x_big, cpu_y_big,  c='red', marker = 'x',s = 50, edgecolors = None, label="CPU")

    typeLockWake_1 = axes.scatter(lockwake_x_small, lockwake_y_small,c='green', marker = 'x', s = 5)
    typeLockWake_2 = axes.scatter(lockwake_x_mid, lockwake_y_mid,c='green', marker = 'x', s = 20)
    typeLockWake_3 = axes.scatter(lockwake_x_big, lockwake_y_big,c='green', marker = 'x', s = 40, label="Lock Wakeup")

    typeLockWait_1 = axes.scatter(lockwait_x_small, lockwait_y_small,c='green', marker = '+', s = 5)
    typeLockWait_2 = axes.scatter(lockwait_x_mid, lockwait_y_mid,c='green', marker = '+', s = 20)
    typeLockWait_3 = axes.scatter(lockwait_x_big, lockwait_y_big,c='green', marker = '+', s = 40, label="Lock Wait")


    typeFile_1 = axes.scatter(fileIO_x_small, fileIO_y_small,c='yellow', marker = 'x', s = 5,  label="File")
    typeFile_2 = axes.scatter(fileIO_x_mid, fileIO_y_mid,c='yellow', marker = 'x', s = 20)
    typeFile_3 = axes.scatter(fileIO_x_big, fileIO_y_big,c='yellow', marker = 'x', s = 40)

    typeNetwork_1 = axes.scatter(network_x_small, network_y_small, c='blue', marker = 'x', s = 5)
    typeNetwork_2 = axes.scatter(network_x_small, network_y_small, c='blue', marker = 'x', s = 20)
    typeNetwork_3 = axes.scatter(network_x_small, network_y_small, c='blue', marker = 'x', s = 40, label="Network")

    axes.set_yticks(threadNumber)

    # axes.axhspan(main_pid - 3, main_pid - 3, xmin=-30, xmax=end + 100, color = 'black')

    plt.xlabel('Time',fontsize=24)
    plt.ylabel('Thread Number', fontsize=24)

    plt.legend(loc='upper left', shadow=True, fontsize=24)
    plt.grid(True)

    plt.show()

def loadFile(filename):
    global main_pid
    trace_file = open(filename)

    state = 0 # 0 : init  ;  1 : read

    try:

        lines = trace_file.readlines()

        i = 0
        totLen = len(lines)

        while i < totLen:
            if lines[i] == "":
                i = i + 1
                continue

            thread_number = 0
            if lines[i].startswith("threadnum = "):

                each_info = {}
                hardware_info = {}
                thread_info = {}
                last_thread_info = {}

                sp = lines[i].split(" ")
                thread_number = int(sp[2])
                # print thread_number


                # SCREEN event
                screen_info_str = lines[i+1][9:].split(',')
                screen_info = {}
                screen_info['post_number'] = int(screen_info_str[0])
                screen_info['R'] = int(screen_info_str[1])
                screen_info['G'] = int(screen_info_str[2])
                screen_info['B'] = int(screen_info_str[3])
                # print screen_info
                hardware_info['screen'] = screen_info

                # DMA event
                dma_info_str = lines[i+2][6:].split(',')
                dma_info = {}
                dma_info['times'] = int(dma_info_str[0])
                dma_info['count'] = int(dma_info_str[1])
                # print dma_info
                hardware_info['dma'] = dma_info

                # BIO event
                bio_info_str = lines[i+3][6:].split(',')
                bio_info = {}
                bio_info['write_times'] = int(bio_info_str[0])
                bio_info['read_times'] = int(bio_info_str[1])
                bio_info['count'] = int(bio_info_str[2])
                # print bio_info
                hardware_info['bio'] = bio_info

                # GPU event
                gpu_info_slice = lines[i+4][6:].split(";")
                gpu_info = {}
                gpu_info['image_draw_times'] = int(gpu_info_slice[0].split(',')[0])
                gpu_info['image_draw_size'] = int(gpu_info_slice[0].split(',')[1][1:])
                gpu_info['draw_element_times'] = int(gpu_info_slice[1].split(',')[0][1:])
                gpu_info['draw_element_count'] = int(gpu_info_slice[1].split(',')[1][1:])
                # print gpu_info
                hardware_info['gpu'] = gpu_info


                # system_service insn

                system_service_str = lines[i+5][15:].split(",")
                system_service_info = {}
                system_service_info['time'] = float(system_service_str[0])
                system_service_info['simple'] = int(system_service_str[1])
                system_service_info['load'] = int(system_service_str[2])
                system_service_info['store'] = int(system_service_str[3])
                system_service_info['multiple'] = int(system_service_str[4])
                system_service_info['division'] = int(system_service_str[5])
                system_service_info['neon'] = int(system_service_str[6])
                system_service_info['vfp'] = int(system_service_str[7])
                # print system_service_info
                hardware_info['system_service'] = system_service_info

                # surfaceflinger insn
                surfaceflinger_str = lines[i+6][15:].split(",")
                surfaceflinger_info = {}
                surfaceflinger_info['time'] = float(surfaceflinger_str[0])
                surfaceflinger_info['simple'] = int(surfaceflinger_str[1])
                surfaceflinger_info['load'] = int(surfaceflinger_str[2])
                surfaceflinger_info['store'] = int(surfaceflinger_str[3])
                surfaceflinger_info['multiple'] = int(surfaceflinger_str[4])
                surfaceflinger_info['division'] = int(surfaceflinger_str[5])
                surfaceflinger_info['neon'] = int(surfaceflinger_str[6])
                surfaceflinger_info['vfp'] = int(surfaceflinger_str[7])
                # print surfaceflinger_info
                hardware_info['surfaceflinger'] = surfaceflinger_info

                i = i + 6

                for k in range(i + 1 , i + thread_number):
                    one_thread_info = {}
                    thread_line = lines[k]
                    one_thread_info['pid'] = int(thread_line.split(":")[0])
                    thispid = one_thread_info['pid']

                    if main_pid == 0:
                        main_pid = one_thread_info['pid']

                    other_str = thread_line.split(":")[1]

                    str1 = other_str.split(";")[0]
                    str2 = other_str.split(";")[1]
                    str3 = other_str.split(";")[2]
                    str4 = other_str.split(";")[3]

                    one_thread_info['father'] = int(str1.split(',')[0])
                    one_thread_info['status'] = int(str1.split(',')[1])


                    one_thread_info['futex_wake_by'] = int(str2.split(',')[0])
                    one_thread_info['futex_wake_times'] = int(str2.split(',')[1])
                    one_thread_info['futex_wait_times'] = int(str2.split(',')[2])
                    one_thread_info['waitqueue_wake_by'] = int(str2.split(',')[3])
                    one_thread_info['waitqueue_wake_times'] = int(str2.split(',')[4])
                    one_thread_info['waitqueue_wait_times'] = int(str2.split(',')[5])


                    one_thread_info['file_read_times'] = int(str3.split(',')[0])
                    one_thread_info['file_read_count'] = int(str3.split(',')[1])
                    one_thread_info['file_write_times'] = int(str3.split(',')[2])

                    one_thread_info['network_send_times'] = int(str3.split(',')[3])
                    one_thread_info['network_recv_times'] = int(str3.split(',')[4])
                    one_thread_info['network_data_count'] = int(str3.split(',')[5])

                    insnlist = str4.split(',')

                    if len(insnlist) == 9:
                        one_thread_info['time'] = float(insnlist[0])
                        one_thread_info['energy'] = float(insnlist[1])
                        one_thread_info['simple'] = float(insnlist[2])
                        one_thread_info['load'] = int(insnlist[3])
                        one_thread_info['store'] = int(insnlist[4])
                        one_thread_info['multiple'] = int(insnlist[5])
                        one_thread_info['division'] = int(insnlist[6])
                        one_thread_info['neon'] = int(insnlist[7])
                        one_thread_info['vfp'] = int(insnlist[8])

                    # print one_thread_info

                    thread_info[one_thread_info['pid']] = one_thread_info



                each_info['hardware_info'] = hardware_info
                each_info['thread_info'] = thread_info
                tot_info.append(each_info)

                i = i + thread_number

            else:
                i = i + 1
    finally:
        trace_file.close()

    tot = len(tot_info)
    i = tot - 1
    while i > 0:
        for pid in tot_info[i]['thread_info']:
            if pid in tot_info[i-1]['thread_info']:
                tot_info[i]['thread_info'][pid]['futex_wake_times'] -= tot_info[i-1]['thread_info'][pid]['futex_wake_times']
                tot_info[i]['thread_info'][pid]['futex_wait_times'] -= tot_info[i-1]['thread_info'][pid]['futex_wait_times']
                tot_info[i]['thread_info'][pid]['waitqueue_wake_times'] -= tot_info[i-1]['thread_info'][pid]['waitqueue_wake_times']
                tot_info[i]['thread_info'][pid]['waitqueue_wait_times'] -= tot_info[i-1]['thread_info'][pid]['waitqueue_wait_times']
                tot_info[i]['thread_info'][pid]['file_read_times'] -= tot_info[i-1]['thread_info'][pid]['file_read_times']
                tot_info[i]['thread_info'][pid]['file_read_count'] -= tot_info[i-1]['thread_info'][pid]['file_read_count']
                tot_info[i]['thread_info'][pid]['file_write_times'] -= tot_info[i-1]['thread_info'][pid]['file_write_times']
                tot_info[i]['thread_info'][pid]['network_send_times'] -= tot_info[i-1]['thread_info'][pid]['network_send_times']
                tot_info[i]['thread_info'][pid]['network_recv_times'] -= tot_info[i-1]['thread_info'][pid]['network_recv_times']
                tot_info[i]['thread_info'][pid]['network_data_count'] -= tot_info[i-1]['thread_info'][pid]['network_data_count']

        tot_info[i]['hardware_info']['screen']['post_number'] -= tot_info[i-1]['hardware_info']['screen']['post_number']
        tot_info[i]['hardware_info']['dma']['times'] -= tot_info[i-1]['hardware_info']['dma']['times']
        tot_info[i]['hardware_info']['dma']['count'] -= tot_info[i-1]['hardware_info']['dma']['count']
        tot_info[i]['hardware_info']['bio']['read_times'] -= tot_info[i-1]['hardware_info']['bio']['read_times']
        tot_info[i]['hardware_info']['bio']['write_times'] -= tot_info[i-1]['hardware_info']['bio']['write_times']
        tot_info[i]['hardware_info']['bio']['count'] -= tot_info[i-1]['hardware_info']['bio']['count']
        tot_info[i]['hardware_info']['gpu']['image_draw_times'] -= tot_info[i-1]['hardware_info']['gpu']['image_draw_times']
        tot_info[i]['hardware_info']['gpu']['image_draw_size'] -= tot_info[i-1]['hardware_info']['gpu']['image_draw_size']
        tot_info[i]['hardware_info']['gpu']['draw_element_times'] -= tot_info[i-1]['hardware_info']['gpu']['draw_element_times']
        tot_info[i]['hardware_info']['gpu']['draw_element_count'] -= tot_info[i-1]['hardware_info']['gpu']['draw_element_count']
        tot_info[i]['hardware_info']['system_service']['time'] -= tot_info[i-1]['hardware_info']['system_service']['time']
        tot_info[i]['hardware_info']['surfaceflinger']['time'] -= tot_info[i-1]['hardware_info']['surfaceflinger']['time']

        i -= 1


    pass


if __name__ == "__main__":

    filename = ""
    if len(sys.argv) != 2:
        # filename = "/Users/xuyunnan/develop/bishe/data/open_cal_futex.txt"
        # filename = "/Users/xuyunnan/develop/bishe/data/open_zhibu_futex.txt"
        filename = "/Users/xuyunnan/develop/bishe/data/open_gallery3d_futex.txt"
        # filename = "/Users/xuyunnan/develop/bishe/data/open_hupu_futex.txt" # 0430_open_hupu.txt
        # filename = "/Users/xuyunnan/develop/bishe/data/0430_open_hupu.txt"
        # filename = "/Users/xuyunnan/develop/bishe/data/cal_9981.txt"
        # filename = "/Users/xuyunnan/develop/bishe/data/hupu_guanggao.txt"
        #filename = "/Users/xuyunnan/develop/bishe/data/kuwo_old.txt"
        # filename = "/Users/xuyunnan/develop/bishe/data/kuwo_new.txt"
        # filename = "/Users/xuyunnan/develop/bishe/data/youku_background.txt"
    else:
        filename = sys.argv[1]

    loadFile(filename)

    start = 0
    end = len(tot_info) - 1

    while start < end :
        if len(tot_info[start]['thread_info']) is not 0:
            break
        start += 1

    lastPostTime = tot_info[end]['hardware_info']['screen']['post_number']
    while end > start :
        if tot_info[end]['hardware_info']['screen']['post_number'] != lastPostTime:
            break
        end -= 1
    end += 1

    print "lastPostTime = ", lastPostTime
    print "start = ", start, ", end = ", end


    tot_cycle = 0.0
    for i in range(start, end + 1):
        tot_cycle += tot_info[i]['thread_info'][main_pid]['time']

    print "main_pid = ", main_pid, " total cycle = ", tot_cycle


    drawThreadInfoPic(start, end)
    drawHardwareInfoPic(start, end)
    analysis_time(start, end)
    analysis_energy()

