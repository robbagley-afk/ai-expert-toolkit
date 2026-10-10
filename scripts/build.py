#!/usr/bin/env python3
"""Build public artifacts from one reviewed content source."""
import argparse,datetime,hashlib,html,json,pathlib,re,tempfile
from urllib.parse import urlparse
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from PIL import Image,ImageDraw
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAP='https://robbagley-afk.github.io/model-value-map/'
TEAM='https://your-portable-ai-team.airy-emu-9499.chatgpt.site/'
def validate(d):
 datetime.date.fromisoformat(d['reviewed'])
 assert len(d['pages'])==3
 text=json.dumps(d)
 if re.search(r'/Users/|OneDrive|mem\.ai/|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?i:api[_-]?key|access[_-]?token)',text):raise ValueError('Private content in public input')
 ids=[x['id'] for x in d['checklist']]
 if len(ids)!=len(set(ids)) or any(not re.fullmatch(r'[a-z][a-z0-9-]*',x) for x in ids):raise ValueError('Invalid checklist IDs')
 for s in d['sources']:
  u=urlparse(s['url'])
  if u.scheme!='https' or not u.netloc:raise ValueError('Sources require HTTPS')
def esc(t):return html.escape(t,quote=True)
def section(s):
 out=f'<section id="{esc(s["id"])}"><div class="kicker">{esc(s["kicker"])}</div><h3>{esc(s["title"])}</h3>'
 if s.get('intro'):out+=f'<p>{esc(s["intro"])}</p>'
 if s.get('cards'):out+='<div class="cards">'+''.join(f'<div class="card"><h4>{esc(c["title"])}</h4><p>{esc(c["text"])}</p></div>' for c in s['cards'])+'</div>'
 if s.get('table'):
  t=s['table'];out+='<div class="table-wrap"><table><thead><tr>'+''.join(f'<th scope="col">{esc(x)}</th>' for x in t['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{esc(x)}</td>' for x in r)+'</tr>' for r in t['rows'])+'</tbody></table></div>'
 for key,tag in [('steps','ol'),('bullets','ul')]:
  if s.get(key):out+=f'<{tag}>'+''.join(f'<li>{esc(x)}</li>' for x in s[key])+f'</{tag}>'
 if s.get('notice'):out+=f'<p class="notice">{esc(s["notice"])}</p>'
 return out+'</section>'
def shell(title,body,d,rev,child=False):
 prefix='../' if child else ''
 return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(d["subtitle"])}"><link rel="icon" href="{prefix}favicon.ico"><link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg"><link rel="stylesheet" href="{prefix}assets/site.css">'+ ('<script defer src="../assets/guide.js"></script>' if child else '')+f'</head><body><a class="skip" href="#main">Skip to content</a><header><nav aria-label="Main"><a class="brand" href="{prefix}index.html">Rob’s Everyday AI Guide</a><a href="{prefix}chatgpt-quick-start-guide/">ChatGPT Guide</a><a href="{MAP}">Model Value Map</a><a href="{TEAM}">Portable AI Team</a></nav></header><main id="main">{body}</main><footer>Created by {esc(d["author"]["name"])}. <a href="{esc(d["author"]["linkedin"])}">LinkedIn profile</a>. Reviewed {d["reviewed"]}. Revision {rev[:12]}.<br>Verify important results and follow your campus policies.</footer></body></html>'
def pdf(path,d,rev):
 styles=getSampleStyleSheet()
 styles.add(ParagraphStyle(name='BodySmall',fontName='Helvetica',fontSize=8.8,leading=11.4,spaceAfter=4,textColor=colors.HexColor('#172441')))
 styles.add(ParagraphStyle(name='SectionSmall',fontName='Helvetica-Bold',fontSize=12,leading=14,spaceBefore=6,spaceAfter=5,textColor=colors.HexColor('#205bb6')))
 styles.add(ParagraphStyle(name='CardSmall',parent=styles['BodySmall'],fontSize=8,leading=10))
 p=lambda t,sty='BodySmall':Paragraph(esc(t),styles[sty])
 story=[]
 for i,page in enumerate(d['pages']):
  if i:story.append(PageBreak())
  for s in page['sections']:
   story.append(p(s['title'],'SectionSmall'))
   if s.get('intro'):story.append(p(s['intro']))
   if s.get('cards'):
    row=[Paragraph('<b>'+esc(c['title'])+'</b><br/>'+esc(c['text']),styles['CardSmall']) for c in s['cards']]
    t=Table([row],colWidths=[524/len(row)]*len(row));t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#edf3fd')),('BOX',(0,0),(-1,-1),.4,colors.HexColor('#d4deed')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]));story.extend([t,Spacer(1,5)])
   if s.get('table'):
    data=[s['table']['headers']]+s['table']['rows'];t=Table([[p(c,'CardSmall') for c in r] for r in data],colWidths=[72,150,150,152]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf3fd')),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#d4deed'))]));story.extend([t,Spacer(1,5)])
   for key in ('steps','bullets'):
    for n,item in enumerate(s.get(key,[])):story.append(p((f'{n+1}. ' if key=='steps' else '• ')+item))
   if s.get('notice'):story.append(p(s['notice']))
  if i==2:
   story.append(p('Try these next','SectionSmall'))
   checks=[p('[ ] '+c['text'],'CardSmall') for c in d['checklist']]
   t=Table([[checks[j],checks[j+1]] for j in range(0,len(checks),2)],colWidths=[262,262]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]));story.append(t)
   links=' · '.join(f'<link href="{esc(s["url"])}">{esc(s["title"])}</link>' for s in d['sources'])
   story.append(Paragraph('<b>Sources:</b> '+links,styles['CardSmall']))
 def decorate(c,doc):
  c.setFillColor(colors.HexColor('#172441'));c.roundRect(44,723,524,44,8,fill=1,stroke=0);c.setFillColor(colors.white);c.setFont('Helvetica-Bold',17);c.drawString(56,747,d['title']);c.setFont('Helvetica',9);c.drawString(56,732,d['pages'][min(doc.page-1,2)]['title']);c.setFillColor(colors.HexColor('#516079'));c.setFont('Helvetica',7);c.drawString(44,28,f'Rob Bagley | Reviewed {d["reviewed"]} | Revision {rev[:12]}');c.drawRightString(568,28,f'{doc.page} / 3')
 SimpleDocTemplate(str(path),pagesize=(612,792),leftMargin=44,rightMargin=44,topMargin=81,bottomMargin=45,title=d['title'],author='Rob Bagley').build(story,onFirstPage=decorate,onLaterPages=decorate,canvasmaker=lambda *a,**kw: Canvas(*a,**dict(kw,invariant=1)))
 if len(PdfReader(path).pages)!=3:raise ValueError('Guide exceeds three-page layout. Shorten or reflow content before publishing.')
def generate(out):
 d=json.loads((ROOT/'content/guide.json').read_text());validate(d);rev=hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 out.mkdir(parents=True,exist_ok=True);(out/'assets').mkdir();(out/'chatgpt-quick-start-guide').mkdir()
 home='<div class="hero"><div class="eyebrow">Practical tools. Useful habits.</div><h1>Rob’s Everyday AI Guide</h1><p>Start with one useful task. Build a repeatable workflow, check the result and choose the right model for the job.</p></div><div class="resources"><article class="resource"><span class="number">Resource 1</span><h2>ChatGPT Quick Start Guide</h2><p>A practical guide to plugins, skills, models and scheduled tasks. Read online or download the printable three-page guide.</p><a class="button" href="chatgpt-quick-start-guide/">Open ChatGPT Guide</a><a class="secondary" href="ChatGPT-Quick-Start-Guide.pdf">Download PDF</a></article><article class="resource"><span class="number">Resource 2</span><h2>Model Value Map</h2><p>Compare model capability and cost using the current public map and its maintained guidance.</p><a class="button" href="'+MAP+'">Open Model Value Map</a><a class="secondary" href="'+MAP+'team/">Open team guidance</a></article></div>'
 team=d['portable_team']
 card='<article class="resource"><span class="number">Resource 3</span><h2>'+esc(team['title'])+'</h2><p>'+esc(team['description'])+'</p><a class="button" href="'+esc(team['url'])+'">Open Portable AI Team</a><a class="secondary" href="'+esc(team['url'])+'roles-and-skills.html#add-specialists">Explore specialist starters</a></article>'
 home=home[:-6]+card+'</div>'
 (out/'index.html').write_text(shell('Rob’s Everyday AI Guide',home,d,rev))
 body=f'<div class="hero"><div class="eyebrow">Resource 1</div><h1>{esc(d["title"])}</h1><p>{esc(d["subtitle"])}</p><p class="meta">Reviewed {d["reviewed"]} · Revision {rev[:12]}</p><a class="button no-print" href="../ChatGPT-Quick-Start-Guide.pdf">Download printable PDF</a></div>'
 for page in d['pages']:body+=f'<article class="chapter"><h2>{esc(page["title"])}</h2>'+''.join(section(s) for s in page['sections'])+'</article>'
 body+='<article class="chapter"><h2>Try these next</h2><p class="progress" data-progress aria-live="polite">0 of 8 complete</p><ul class="checks">'+''.join(f'<li><label><input type="checkbox" data-check="{esc(c["id"])}"><span>{esc(c["text"])}</span></label></li>' for c in d['checklist'])+'</ul><p class="meta">Checklist progress is saved in this browser when local storage is available.</p></article><section class="chapter sources"><h2>Sources and current guidance</h2><ul class="source-list">'+''.join(f'<li><a href="{esc(s["url"])}">{esc(s["title"])}</a></li>' for s in d['sources'])+'</ul></section>'
 (out/'chatgpt-quick-start-guide/index.html').write_text(shell(d['title'],body,d,rev,True))
 for name in ('site.css','guide.js'):(out/'assets'/name).write_bytes((ROOT/'templates'/name).read_bytes())
 (out/'.nojekyll').write_text('')
 (out/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#172441"/><path d="M12 16h17l3 5 3-5h17v33H35l-3 5-3-5H12z" fill="#fff"/><path d="M32 23v24" stroke="#205bb6" stroke-width="3"/></svg>')
 im=Image.new('RGB',(64,64),'#172441');draw=ImageDraw.Draw(im);draw.rounded_rectangle((10,14,54,49),4,fill='white');draw.line((32,17,32,49),fill='#205bb6',width=3);im.save(out/'favicon.ico',sizes=[(16,16),(32,32),(64,64)])
 pdf(out/'ChatGPT-Quick-Start-Guide.pdf',d,rev)
 files={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file()}
 (out/'release.json').write_text(json.dumps({'reviewed':d['reviewed'],'revision':rev,'files':files},indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
 with tempfile.TemporaryDirectory() as td:
  out=pathlib.Path(td)/'docs';generate(out);dest=ROOT/'docs';want={str(p.relative_to(out)):p.read_bytes() for p in out.rglob('*') if p.is_file()}
  if args.check:
   got={str(p.relative_to(dest)):p.read_bytes() for p in dest.rglob('*') if p.is_file()};bad=sorted(k for k in set(want)|set(got) if want.get(k)!=got.get(k))
   if bad:raise SystemExit('Stale output: '+', '.join(bad))
   print('Generated outputs are current')
  else:
   for k,v in want.items():p=dest/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
   print('Built '+str(len(want))+' public artifacts')
if __name__=='__main__':main()
