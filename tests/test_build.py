import copy,importlib.util,json,pathlib,tempfile,unittest
from pypdf import PdfReader
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
 def test_inline_markdown_emphasis_and_safe_links(self):
  text='Use **GPT-6.1 Sol** at **Medium** and [the guide](https://example.org/a?x=1&y=2).'
  self.assertEqual(b.inline_markdown(text), 'Use <strong>GPT-6.1 Sol</strong> at <strong>Medium</strong> and <a href="https://example.org/a?x=1&amp;y=2">the guide</a>.')
  self.assertEqual(b.inline_markdown(text, target='pdf'), 'Use <b>GPT-6.1 Sol</b> at <b>Medium</b> and <link href="https://example.org/a?x=1&amp;y=2" color="#174a94">the guide</link>.')
 def test_model_guidance_emphasizes_model_names_and_effort(self):
  sec=next(s for p in self.data['pages'] for s in p['sections'] if s['id']=='models')
  self.assertEqual(sec.get('format'),'markdown')
  self.assertIn('**GPT-6 Luna**',sec['cards'][0]['text'])
  self.assertIn('**Low**',sec['cards'][0]['text'])
  self.assertIn('**GPT-6.1 Sol**',sec['cards'][1]['text'])
  self.assertIn('**Medium**',sec['cards'][1]['text'])
  rendered=b.section(sec)
  self.assertIn('<strong>GPT-6 Luna</strong>',rendered)
  self.assertIn('<strong>GPT-6.1 Sol</strong>',rendered)
 def test_plugin_navigation_analogy_and_example_are_in_guide(self):
  sections={s['id']:s for p in self.data['pages'] for s in p['sections']}
  self.assertIn('Customize',sections['find-plugins']['intro'])
  self.assertIn('**Plugins**',sections['find-plugins']['intro'])
  self.assertIn('<strong>Customize</strong>',b.section(sections['find-plugins']))
  self.assertNotIn('**Plugins**',b.section(sections['find-plugins']))
  self.assertIn('toolbox',sections['ces-plugins']['notice'])
  self.assertIn('workbench',sections['ces-plugins']['notice'])
  self.assertIn('Outlook Calendar',sections['ces-plugins']['example'])
  self.assertIn('SharePoint',sections['ces-plugins']['example'])
  self.assertIn('iPhones',self.data['pages'][2]['sections'][0]['title'])
 def test_ces_workspace_verification_shows_logo_in_web_and_pdf(self):
  sec=next(s for p in self.data['pages'] for s in p['sections'] if s['id']=='app')
  check=sec['verification']
  self.assertIn('data privacy',sec['notice'])
  self.assertNotIn('data rules',sec['notice'])
  self.assertEqual(check['src'],'img/ces-logo.jpeg')
  self.assertIn('profile menu',check['text'])
  self.assertIn('lower-left',check['text'])
  rendered=b.section(sec)
  self.assertIn('class="rp-note rp-ces-check"',rendered)
  self.assertIn('src="../assets/img/ces-logo.jpeg"',rendered)
  self.assertIn('alt="CES logo"',rendered)
  with tempfile.TemporaryDirectory() as td:
   out=pathlib.Path(td)/'docs';b.generate(out)
   self.assertEqual((out/'assets/img/ces-logo.jpeg').read_bytes(),(ROOT/'content/img/ces-logo.jpeg').read_bytes())
   pages=PdfReader(out/'ChatGPT-Quick-Start-Guide.pdf').pages
   self.assertIn('CES workspace',pages[0].extract_text())
   self.assertIn('lower-left',pages[0].extract_text())
 def test_desktop_app_agent_features_are_explained_with_current_openai_source(self):
  sec=next(s for p in self.data['pages'] for s in p['sections'] if s['id']=='app')
  self.assertEqual(sec.get('format'),'markdown')
  self.assertIn('broadest agent features',sec['intro'])
  self.assertIn('supported multi-step tasks in a browser',sec['intro'])
  self.assertIn('desktop-only',sec['intro'])
  rendered=b.section(sec)
  self.assertIn('<a href="https://help.openai.com/en/articles/20001276-moving-to-the-new-chatgpt-desktop-app">OpenAI app guide</a>',rendered)
  with tempfile.TemporaryDirectory() as td:
   out=pathlib.Path(td)/'docs';b.generate(out)
   pages=PdfReader(out/'ChatGPT-Quick-Start-Guide.pdf').pages
   self.assertIn('broadest agent features',pages[0].extract_text())
   uris=[]
   for ref in pages[0].get('/Annots',[]):
    action=ref.get_object().get('/A',{})
    if action.get('/URI'):uris.append(str(action['/URI']))
   self.assertIn('https://help.openai.com/en/articles/20001276-moving-to-the-new-chatgpt-desktop-app',uris)
 def test_inline_markdown_rejects_unsafe_links(self):
  d=copy.deepcopy(self.data)
  next(s for p in d['pages'] for s in p['sections'] if s['id']=='iphone-chip-analogy')['paragraphs'][0]='[unsafe](javascript:alert(1))'
  with self.assertRaises(ValueError):b.validate(d)
 def test_analogy_and_plugin_example_render_in_printable_pdf(self):
  with tempfile.TemporaryDirectory() as td:
   path=pathlib.Path(td)/'guide.pdf';b.pdf(path,self.data,'test')
   pages=PdfReader(path).pages
   self.assertEqual(len(pages),7)
   analogy=' '.join(pages[2].extract_text().split())
   self.assertIn('AI models are like the chips inside iPhones',analogy)
   self.assertIn('GPT-6 Luna',analogy)
   self.assertIn('Low, Medium, or High effort',analogy)
   self.assertIn('reasoning tokens',analogy)
   uris=[]
   for ref in pages[2].get('/Annots',[]):
    action=ref.get_object().get('/A',{})
    if action.get('/URI'):uris.append(str(action['/URI']))
   self.assertIn('https://www.apple.com/newsroom/2024/09/apple-debuts-iphone-16-pro-and-iphone-16-pro-max/',uris)
   self.assertIn('https://developers.openai.com/api/docs/guides/reasoning',uris)
   plugins=' '.join(pages[4].extract_text().split())
   self.assertIn('toolbox',plugins)
   self.assertIn('workbench',plugins)
   self.assertIn('Outlook Calendar',plugins)
   self.assertIn('SharePoint',plugins)
 def test_private_public_input(self):
  d=copy.deepcopy(self.data);d['subtitle']='/Users/private/example'
  with self.assertRaises(ValueError):b.validate(d)
 def test_long_pdf_blocks_publication(self):
  d=copy.deepcopy(self.data);d['pages'][0]['sections'][0]['intro'] *= 25
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):b.pdf(pathlib.Path(td)/'guide.pdf',d,'test')
 def test_printable_empty_checkboxes(self):
  with tempfile.TemporaryDirectory() as td:
   path=pathlib.Path(td)/'guide.pdf';b.pdf(path,self.data,'test')
   # Tick boxes are drawn vector squares; every checklist item must print on the last page in order.
   text=' '.join(PdfReader(path).pages[-1].extract_text().split())
   pos=[text.find(' '.join(c['text'].split())) for c in self.data['checklist']]
   self.assertTrue(all(p>=0 for p in pos),pos);self.assertEqual(pos,sorted(pos))
if __name__=='__main__':unittest.main()
