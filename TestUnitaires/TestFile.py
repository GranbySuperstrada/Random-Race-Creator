import unittest


class TestOnRacer(unittest.TestCase):

    def test_overlap_fake_file_9(self):
        self.assertTrue(check_no_overlap_in_heats("./data/random/7 pilotes - 3 heat - 3 voies.txt"))

"""
    def test_racers_overlap(self):
        self.assertTrue(check_no_overlap_in_heats("./data/random/10 pilotes - 1 heat - 3 voies.txt"))
"""

def check_no_overlap_between_lists(list1, list2):
    for num in list1:
        if num in list2:
            return False
    return True


def load_data_from_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
        start_index = content.find('{')
        end_index = content.rfind('}') + 1
        data = eval(content[start_index:end_index])
    return data


def check_no_overlap_in_heats(filename):
    data = load_data_from_file(filename)
    for i in range(len(data['Heats']) - 1):
        current_heat = data['Heats'][i]
        next_heat = data['Heats'][i + 1]
        current_drivers = current_heat['Drivers']
        next_drivers = next_heat['Drivers']
        if not check_no_overlap_between_lists(current_drivers, next_drivers):
            return False
    return True
