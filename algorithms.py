import random
import json
from numpy.random import choice
from sortedcollections import SortedDict
from clTask import Task
from clJob import Job
from clItinerary import  Itinerary
from clMachine import Machine


# =========================================================================================

def prepareJobs(machinesList, itinerariesList):
    """Converts available data to list of jobs on which is calculations and graphs made"""
    jobsList = []
    itineraryColors = []

    pastelFactor = random.uniform(0, 1)
    # 从工艺路径任务中解析出每一个工序任务
    for idItinerary, itineraryObj in enumerate(itinerariesList):
    # 为每一条工艺路线创建不同的颜色
        itineraryColors.append(
            generate_new_color(itineraryColors, pastelFactor))
    #实例化每一个工序任务，创建工序任务列表
        for idTask, taskObj in enumerate(itineraryObj.tasksList):
            if itineraryObj.name == "Itinerary 0":
                jobsList.append(Job(itineraryObj.name, itineraryColors[idItinerary], idTask + 1, 0,
                                   taskObj.machine, taskObj.duration))
            else:
                jobsList.append(Job(itineraryObj.name, itineraryColors[idItinerary], idTask + 1, idItinerary + 1,
                                taskObj.machine, taskObj.duration))
    return jobsList


def algorithmMOPSO(aJobsList, machinesList):
    """
    Modified Shortest Processing Time (MOPSO) algorithm for job shop scheduling problem.
    """
    time = {} 
    jobsListToExport = []
    waitingOperations = {}
    currentTimeOnMachines = {}

    # Initialize machines times and get
    # first waiting operations for each machine
    for machine in machinesList:
        currentTimeOnMachines[machine.name] = 0
    
    for machine in machinesList:
        waitingOperations[machine.name] = []
        for job in aJobsList:
            if job.idOperation == 1 and machine.name in job.machine:
                if len(job.machine) == 1:
                    waitingOperations[machine.name].append(job)
                else:
                    minTimeMachine = machine.name
                    for mac in job.machine:
                        if currentTimeOnMachines[mac] <  currentTimeOnMachines[minTimeMachine]:
                            minTimeMachine = mac
                    if minTimeMachine == machine.name:
                        waitingOperations[machine.name].append(job)

        waitingOperations[machine.name].sort(key=lambda j: j.duration)

    time[0] = waitingOperations

    while len(jobsListToExport) != len(aJobsList):
        # Check if time dictionary is empty
        if not time:
            break

        # Get the next time step
        t = min(time.keys())
        operations = time[t]

        for keyMach, tasks in operations.items():
            if len(tasks):
                if t < currentTimeOnMachines[keyMach]:
                    continue

                tasks[0].startTime = t
                tasks[0].completed = True
                tasks[0].assignedMachine = keyMach

                jobsListToExport.append(tasks[0])

                currentTimeOnMachines[keyMach] = tasks[0].getEndTime()
                time[currentTimeOnMachines[keyMach]] = getWaitingOperationsMOPSO(aJobsList, machinesList, currentTimeOnMachines)

        del time[t]

        print("Jobs exported:", len(jobsListToExport))  # Print length of exported jobs list

    # Check if all jobs are completed
    if len(jobsListToExport) != len(aJobsList):
        print("Algorithm did not finish correctly!")
    else:
        print("Algorithm finished successfully!")

    # Check if all jobs from input list are in the exported list
    if all(job in jobsListToExport for job in aJobsList):
        print("All jobs from input list are exported.")
    else:
        print("Not all jobs from input list are exported.")

    return jobsListToExport

def getWaitingOperationsMOPSO(aJobsList, machinesList, currentTimeOnMachines):
    """Get waiting jobs at current time based on MOPSO"""

    incomingOperations = {}

    for mach in machinesList:
        assignedJobsForMachine = []
        # Dictionary to track current job on each machine
        currentJobs = {machine.name: None for machine in machinesList}

        for job in aJobsList:
            if job.completed == False and mach.name in job.machine:
                if len(job.machine) == 1:
                    assignedJobsForMachine.append(job)
                else:
                    minTimeMachine = mach.name
                    for mac in job.machine:
                        if currentTimeOnMachines[mac] <  currentTimeOnMachines[minTimeMachine]:
                            minTimeMachine = mac
                    if minTimeMachine == mach.name:
                        assignedJobsForMachine.append(job)
        incomingOperations[mach.name] = []

        for j in assignedJobsForMachine:
            # Check if any other job on the machine is from the same itinerary
            if not any(job.assignedMachine == m.name for m in machinesList if m.name != mach.name and job.itinerary == currentJobs[m.name]):
                if j.idOperation == 1:
                    incomingOperations[mach.name].append(j)
                else:
                    previousTask = [job for job in aJobsList if
                                    job.itinerary == j.itinerary and job.idOperation == j.idOperation - 1 and job.endTime <= currentTimeOnMachines[mach.name]]
                    if len(previousTask):
                        if previousTask[0].completed:
                            incomingOperations[mach.name].append(j)
        incomingOperations[mach.name].sort(key=lambda j: j.duration)
        
        # Debugging prints
        print("Machine:", mach.name)
        print("Incoming operations:", incomingOperations[mach.name])

    return incomingOperations

def color_distance(c1,c2):
    return sum([abs(x[0] - x[1]) for x in zip(c1,c2)])
def get_random_color(pastel_factor=0.5):
    return [(x + pastel_factor) / (1.0 + pastel_factor) for x in [random.uniform(0,1.0) for i in [1,2,3]]]
def generate_new_color(existing_colors, pastel_factor=0.5):
    """Generate new color if not exist in existing array of colors"""
    max_distance = None
    best_color = None
    for i in range(0, 100):
        color = get_random_color(pastel_factor=pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color, c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color



