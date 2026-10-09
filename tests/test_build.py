import copy,importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build',ROOT/'scripts/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class BuildTests(unittest.TestCase):
 def setUp(self):self.data=json.loads((ROOT/'content/guide.json').read_text())
 def test_valid(self):b.validate(self.data)
 def test_duplicate_ids(self):
  d=copy.deepcopy(self.data);d['checklist'][1]['id']=d['checklist'][0]['id']
  with self.assertRaises(ValueError):b.validate(d)
 def test_unsafe_source(self):
  d=copy.deepcopy(self.data);d['sources'][0]['url']='javascript:alert(1)'
  with self.assertRaises(ValueError):b.validate(d)
 def test_private_public_input(self):
  d=copy.deepcopy(self.data);d['subtitle']='/Users/private/example'
  with self.assertRaises(ValueError):b.validate(d)
if __name__=='__main__':unittest.main()
