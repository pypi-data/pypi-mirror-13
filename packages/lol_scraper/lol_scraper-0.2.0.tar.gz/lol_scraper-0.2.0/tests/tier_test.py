import unittest
import os
from lol_scraper.summoners_api import summoner_names_to_id, _slice, leagues_by_summoner_ids, Tier
from cassiopeia import baseriotapi



class TierTest(unittest.TestCase):

    api_key = None
    def setUp(self):
        if not self.api_key:
            with open(os.path.join(os.path.dirname(__file__), '../../api-key'),'rt') as f:
                self.api_key = f.read()[:36]
        baseriotapi.print_calls(False)
        baseriotapi.set_region('euw')
        baseriotapi.set_api_key(self.api_key)

    def list_to_tier_initializer(self, list):
        initializer = {}
        for tier in Tier:
            if list[tier.value]:
                initializer[tier] = set(list[tier.value])
        return initializer

    def test_slice_empty_list(self):
        for _ in _slice(0,0, 1):
            self.fail()

    def test_slice_middle_values(self):
        source = [x for x in range(50)]
        lst = [(x, x+1) for x in range(50)]
        for (b1,e1), (b2,e2) in zip(lst, _slice(0,50,1)):
            self.assertEqual(source[b1:e1], source[b2:e2])

    def test_slice_end_value(self):
        step = 3
        lst = [ x for x in range(20)]
        begin = [0, 3, 6, 9,12,15,18]
        end =   [3, 6, 9,12,15,18,20]
        generator = _slice(0,20,step)
        for (b1,e1), (b2,e2) in zip(zip(begin, end), generator):
            self.assertEqual(lst[b1:e1], lst[b2:e2])
        try:
            next(generator)
            self.fail()
        except StopIteration:
            self.assertTrue(True)

    def test_leagues_by_summoner(self):
        summoners = [44256841, 21653685, 22447540, 22281234, 29378330, 23836705, 23746128, 23742827, 35473944,
                     56067323, 29600081, 26191711]
        leagues = {
                    Tier.challenger : {44256841, 21653685, 22447540},
                    Tier.master : {22281234},
                    Tier.diamond : {29378330, 23746128, 23742827, 23836705, 23836705},
                    Tier.platinum : {29600081},
                    Tier.gold : {35473944},
                    Tier.silver :{56067323},
                    Tier.bronze : {26191711}
                }
        result = leagues_by_summoner_ids(summoners)
        for tier in Tier:
            self.assertEqual(leagues[tier], result.get(tier, set()), tier.name)

    def test_names_to_id(self):
        names = ['cwfreeze', 'makersf', 'zoffo', 'w4sh', "sirnukesalot", "exngodzukee",
                 "lamept", "hiddenlaw", "dijio", "zockchock", "sirkillerlord"]

        ids = {'cwfreeze':44256841, 'makersf':45248415, 'zoffo':46677170,
               'w4sh':23367874, 'exngodzukee': 22447540, 'sirnukesalot': 21653685, 'dijio': 23742827,
               'hiddenlaw': 23746128,'lamept': 23836705,'sirkillerlord': 26191711,'zockchock': 56067323}
        result = summoner_names_to_id(names)
        self.assertEqual(ids, result)

if __name__ == '__main__':
    unittest.main()
