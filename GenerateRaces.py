import os
import random
import configparser
import time

"""

    Author Maxence LEVESQUE @waylow1 on github

"""


class GenerateRaces:
    def __init__(self, num_lanes, num_heats, num_racers):
        """
            GenerateRaces Constructor

            Parameters:\n
            -num_lanes (int): The number of lanes of your track. \n
            -num_heats (int): The number of rounds you want to do.\n
            -num_racers (int): The number of racers.\n

            Returns:\n
            Create a Races object.

        """
        self.time = time.time()
        self.num_lanes = num_lanes
        self.num_heats = num_heats
        self.num_racers = num_racers
        self.lanes = [[] for _ in range(self.num_lanes)]
        self.coupleDictionary = {}
        self.historic = []
        self.possible = num_lanes * 2 + 1 <= num_racers
        self.nbInstructionsPerInsertion = ((num_lanes - 1) * num_lanes) / 2
        self.tolerance = ((num_lanes * (num_lanes - 1) * num_heats) / num_racers) * self.nbInstructionsPerInsertion
        self.value = 0
        self.text_file_content = ""

    def resetLanes(self):
        """
                Reset Lanes. Used to reset all the lanes data when errors or finishing one race.

                Returns:\n
                It clears the self.lanes properties.
        """

        self.lanes = [[] for _ in range(self.num_lanes)]
        for lane in self.lanes:
            for j in range(self.num_racers):
                lane.append(j)

    def chooseARacerForALane(self, laneNum):
        """
                Choose a Racer For A Lane. Used to choose in the list of available racers in a given lane.

                Parameters:\n
                -laneNum (int): The index of the lane you are working on.\n

                Returns:\n
                It returns the chosen Racer.
        """
        racer = random.choice(self.lanes[laneNum])
        return racer

    def checkIfRaceIsEnded(self, heats, index):
        """
                Check If Race Is Ended. Used to check if we complete a part of the race.

                Parameters:\n
                -heats (dict): The result of the computing function.\n
                -index (int): The index to get the part of race you are working on.\n

                Returns:\n
                It returns a boolean that says if the part of the race you are working on is ended.
        """
        limit = self.num_racers * index
        if len(heats) == 0 or len(heats) != limit:
            return False
        i = 0
        while i < limit:
            if len(heats[i]['Drivers']) != self.num_lanes:
                return False
            i += 1
        return True

    def dictionaryUpdate(self, couple):
        """
                Dictionary Update. Used to constantly the dictionary containing all the couples.

                Parameters:\n
                -couple (tuple): The combination of racers (tuple of racer's id).\n

                Returns:\n
                It returns a boolean that says if we can update the dictionary.
        """
        sorted_couple = tuple(sorted(couple))
        if sorted_couple not in self.coupleDictionary:
            self.coupleDictionary[sorted_couple] = 1
            self.historic.append(sorted_couple)
            return True

        if self.coupleDictionary[sorted_couple] + 1 <= self.tolerance + 1:

            self.coupleDictionary[sorted_couple] += 1
            self.historic.append(sorted_couple)
            return True
        else:
            if sum(self.coupleDictionary.values()) > self.num_racers*self.num_heats:
                self.tolerance = 50
            print("Couple not updated due to tolerance limit:", sorted_couple)
            return False

    def popLatestActionsInDictionary(self, index):
        """
                Pop Latest Actions In Dictionary. Used to undo latest actions when error happens.

                Parameters:\n
                -index (int): The number of values you need to pop.

        """
        temp = list(reversed(self.historic))
        for i in range(index):
            couple = temp[i]
            self.coupleDictionary[couple] -= 1

    def buildTextFile(self):
        """
                Build Text File. The main function where everything is created and where the algorithm takes place.

                Returns:\n
                It returns the content of the text file.
        """
        heats = []
        infiniteLoop = False
        racer_from_last_run = set()
        for index in range(self.num_heats):
            race_ended = False
            while not race_ended:
                self.resetLanes()
                if infiniteLoop:
                    loopCount = 0
                    for i in range(index * self.num_racers, len(heats)):
                        heats.pop()
                        loopCount += 1
                    actions = int(loopCount * self.nbInstructionsPerInsertion)
                    self.popLatestActionsInDictionary(actions)
                    for j in range(actions):
                        self.historic.pop()
                    infiniteLoop = False

                for howMuchRaces in range(self.num_racers): # Creating the text for each Rounds and running the program.
                    heat = {'Group': 0, 'Drivers': []}
                    used_racers_this_heat = set()
                    reset_and_restart = False
                    for lanesIndex in range(self.num_lanes): # Choosing the best choice for each Lanes.
                        count = 0
                        racer_num_in_the_lane = self.chooseARacerForALane(lanesIndex)
                        while racer_num_in_the_lane in used_racers_this_heat or (
                                self.possible and racer_num_in_the_lane in racer_from_last_run):
                            count += 1
                            racer_num_in_the_lane = self.chooseARacerForALane(lanesIndex)
                            if sum(bool(lane) for lane in self.lanes) == 1 or any(
                                    set(lane) <= used_racers_this_heat for lane in
                                    self.lanes) or count > self.num_racers * self.num_lanes:
                                reset_and_restart = True
                                break
                        if reset_and_restart:
                            break

                        used_racers_this_heat.add(racer_num_in_the_lane) # Adding racers to check that they are not already running in another lane
                        self.lanes[lanesIndex].remove(racer_num_in_the_lane) # Removing from the racer from the list which checks available runners.
                        heat['Drivers'].append(racer_num_in_the_lane)

                    if len(heat['Drivers']) == self.num_lanes: # If we completed a round
                        for i in range(len(heat['Drivers'])):
                            for j in range(i + 1, len(heat['Drivers'])):
                                drivers_tuple = (heat['Drivers'][i], heat['Drivers'][j])
                                if not self.dictionaryUpdate(drivers_tuple):
                                    infiniteLoop = True
                                    break
                        if not infiniteLoop: #If there is no problem we add the heat in the list of all runs
                            heats.append(heat)
                            racer_from_last_run = used_racers_this_heat
                    else: # Going here mean that we will pop the last actions we did to get a better result
                        elapsed_time = time.time() - self.time
                        if elapsed_time > 2:# Change this value if you have a lot of lanes
                            print("Timer exceeded. Returning None.")
                            return False
                        infiniteLoop = True

                if not infiniteLoop: # If we did great we check if we ended the race
                    race_ended = self.checkIfRaceIsEnded(heats, index + 1)

        self.value = (sum(self.coupleDictionary.values()))/3
        self.text_file_content = {'NumDrivers': self.num_racers, 'NumLanes': self.num_lanes, 'Heats': heats}
        return True

    def writeRaceFile(self, text_file_content):
        """
                Write Race File. The function that create the text file in a given place in the config file or in the local directory if none.

                Parameters:\n
                -text_file_content (dict): The result of the computing.\n

                Returns:\n
                Create the text file.
        """

        config = configparser.ConfigParser()
        config.read('config.ini')
        folder_path = ""

        try:
            folder_path = config['DEFAULT']['FOLDER_PATH']
        except Exception as e:
            print("No config file found")

        if not os.path.exists(folder_path):
            folder_path = "data/random"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        file_path = os.path.join(folder_path,
                                 f"{self.num_racers} pilotes - {self.num_heats} heat - {self.num_lanes} voies.txt")
        with open(file_path, "w") as file:
            file.write(str(text_file_content).replace(", ", ",").replace(": ", ":"))
        file.close()
