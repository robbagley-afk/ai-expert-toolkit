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
 out=f'<section class="topic" id="{esc(s["id"])}"><div class="topic-head"><div class="rp-kicker">{esc(s["kicker"])}</div><h3>{esc(s["title"])}</h3></div><div class="topic-body">'
 if s.get('intro'):out+=f'<p class="intro">{esc(s["intro"])}</p>'
 if s.get('cards'):out+='<div class="rp-grid rp-boxed cards">'+''.join(f'<div class="rp-tinted"><h4>{esc(c["title"])}</h4><p>{esc(c["text"])}</p></div>' for c in s['cards'])+'</div>'
 if s.get('table'):
  t=s['table'];out+='<div class="rp-table-wrap"><table class="rp-table"><thead><tr>'+''.join(f'<th scope="col">{esc(x)}</th>' for x in t['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join((f'<th scope="row">{esc(x)}</th>' if i==0 else f'<td>{esc(x)}</td>') for i,x in enumerate(r))+'</tr>' for r in t['rows'])+'</tbody></table></div>'
 if s.get('steps'):out+='<ol class="rp-steps">'+''.join(f'<li>{esc(x)}</li>' for x in s['steps'])+'</ol>'
 if s.get('bullets'):out+='<ul class="bullets">'+''.join(f'<li>{esc(x)}</li>' for x in s['bullets'])+'</ul>'
 if s.get('notice'):out+=f'<p class="rp-note">{esc(s["notice"])}</p>'
 return out+'</div></section>'
def head(title,d,prefix,extra=''):
 return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(d["subtitle"])}"><link rel="icon" href="{prefix}favicon.ico"><link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg"><link rel="preload" href="{prefix}assets/fonts/archivo.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{prefix}assets/rob-personal.css"><link rel="stylesheet" href="{prefix}assets/site.css">{extra}</head>'
def nav(d,prefix,current):
 links=[('index.html',d['site_title'],'home'),('chatgpt-quick-start-guide/','ChatGPT Guide','guide'),(MAP,'Model Value Map',''),(TEAM,'Portable AI Team','')]
 out='<nav class="rp-nav" aria-label="Main">'
 for href,label,key in links:
  h=href if href.startswith('https') else prefix+href
  cls=' class="rp-brand"' if key=='home' else ''
  cur=' aria-current="page"' if key==current else ''
  out+=f'<a{cls} href="{h}"{cur}>{esc(label)}</a>'
 return out+'</nav>'
def footer(d,rev):
 return f'<footer class="rp-footer">Created by {esc(d["author"]["name"])}. <a href="{esc(d["author"]["linkedin"])}">LinkedIn profile</a>. Reviewed {d["reviewed"]}. Revision {rev[:12]}. Verify important results and follow your campus policies.</footer>'
def shell(title,body,d,rev,child=False):
 prefix='../' if child else ''
 return head(title,d,prefix,'<script defer src="../assets/guide.js"></script>' if child else '')+f'<body><a class="rp-skip" href="#main">Skip to content</a>{nav(d,prefix,"guide" if child else "home")}<main id="main">{body}</main>{footer(d,rev)}</body></html>'
def home_page(d,rev):
 team=d['portable_team']
 rows=[('Learn plugins, skills, models and scheduled tasks','ChatGPT Quick Start Guide','A practical guide to plugins, skills, models and scheduled tasks. Read online or download the printable three-page guide.','Web guide · 3-page PDF','Open ChatGPT Guide','chatgpt-quick-start-guide/','Download PDF','ChatGPT-Quick-Start-Guide.pdf'),
  ('Pick the right model for a task','Model Value Map','Compare model capability and cost using the current public map and its maintained guidance.','Interactive map · ChatGPT Edu guidance','Open Model Value Map',MAP,'Open ChatGPT Edu guidance',MAP+'chatgpt-edu/'),
  ('Set up a reusable team of AI specialists',team['title'],team['description'],'Setup prompts · specialist starters','Open Portable AI Team',team['url'],'Explore specialist starters',team['url']+'roles-and-skills.html#add-specialists')]
 cells=''.join(f'<article class="resource"><div class="rp-num">{n:02d}</div><div class="rp-label">I want to</div><h2>{esc(need)}</h2><div class="what"><div class="name">{esc(name)}</div><p>{esc(value)}</p><div class="rp-label">{esc(fmt)}</div></div><a class="rp-btn rp-btn-primary rp-btn-block" href="{esc(href)}">{esc(cta)}<span aria-hidden="true">→</span></a><a class="rp-link" href="{esc(href2)}">{esc(cta2)}</a></article>' for n,(need,name,value,fmt,cta,href,cta2,href2) in enumerate(rows,1))
 title=esc(d['site_title']).rsplit(' ',1)
 body=f'<div class="rp-page"><section class="rp-hero"><h1 class="rp-display"><span class="rp-line">{title[0]}</span><span class="rp-line">{title[1]}<span class="rp-dot">.</span></span></h1><div class="rp-hero-title"><div class="rp-kicker">Practical tools. Useful habits.</div><p class="rp-lede">Start with one useful task. Build a repeatable workflow, check the result and choose the right model for the job.</p><p class="rp-byline">Created by <strong>Rob Bagley</strong></p></div></section><div class="rp-bar"><h2 class="bar-title">What do you need today?</h2><span class="muted">3 resources</span></div><div class="rp-grid resources" style="--rp-cell:300px">{cells}</div></div>'
 return head(d['site_title'],d,'')+f'<body class="home"><a class="rp-skip" href="#main">Skip to content</a>{nav(d,"","home")}<main id="main">{body}</main>{footer(d,rev)}</body></html>'
INK,ACCENT,ACCENT_TEXT,MUTED,SURFACE,SOFT='#201e1d','#205bb6','#174a94','#605d5d','#eae9e9','#9b9797'
def fonts():
 # Archivo static instances (OFL) so the PDF matches style-guide/ on every machine.
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 from reportlab.lib.fonts import addMapping
 if 'Archivo' in pdfmetrics.getRegisteredFontNames():return
 for n in ('Regular','SemiBold','ExtraBold'):pdfmetrics.registerFont(TTFont('Archivo' if n=='Regular' else 'Archivo-'+n,str(ROOT/'templates/pdf-fonts'/f'Archivo-{n}.ttf')))
 addMapping('Archivo',0,0,'Archivo');addMapping('Archivo',1,0,'Archivo-ExtraBold');addMapping('Archivo',0,1,'Archivo');addMapping('Archivo',1,1,'Archivo-ExtraBold')
def pdf(path,d,rev):
 fonts()
 styles=getSampleStyleSheet()
 styles.add(ParagraphStyle(name='BodySmall',fontName='Archivo',fontSize=8.8,leading=11.6,spaceAfter=4,textColor=colors.HexColor(INK)))
 styles.add(ParagraphStyle(name='Kicker',fontName='Archivo-SemiBold',fontSize=6.8,leading=8,spaceBefore=8,spaceAfter=1,textColor=colors.HexColor(ACCENT_TEXT)))
 styles.add(ParagraphStyle(name='SectionSmall',fontName='Archivo-ExtraBold',fontSize=12.5,leading=14.5,spaceAfter=5,textColor=colors.HexColor(INK)))
 styles.add(ParagraphStyle(name='CardSmall',parent=styles['BodySmall'],fontSize=8,leading=10.2,spaceAfter=0))
 p=lambda t,sty='BodySmall':Paragraph(esc(t),styles[sty])
 rule=lambda w=1.4,c=INK:Table([['']],colWidths=[524],rowHeights=[2],style=TableStyle([('LINEABOVE',(0,0),(-1,0),w,colors.HexColor(c))]))
 story=[]
 for i,page in enumerate(d['pages']):
  if i:story.append(PageBreak())
  for s in page['sections']:
   story.append(p(s['kicker'].upper(),'Kicker'));story.append(p(s['title'],'SectionSmall'))
   if s.get('intro'):story.append(p(s['intro']))
   if s.get('cards'):
    row=[Paragraph('<font name="Archivo-ExtraBold">'+esc(c['title'])+'</font><br/>'+esc(c['text']),styles['CardSmall']) for c in s['cards']]
    t=Table([row],colWidths=[524/len(row)]*len(row));t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,-1),colors.HexColor(SURFACE)),('BOX',(0,0),(-1,-1),1.4,colors.HexColor(INK)),('INNERGRID',(0,0),(-1,-1),1.4,colors.HexColor(INK)),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.extend([t,Spacer(1,5)])
   if s.get('table'):
    data=[s['table']['headers']]+s['table']['rows'];t=Table([[p(c,'CardSmall') for c in r] for r in data],colWidths=[72,150,150,152]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,0),(-1,0),1.4,colors.HexColor(INK)),('LINEBELOW',(0,0),(-1,0),1.4,colors.HexColor(INK)),('LINEBELOW',(0,1),(-1,-1),.5,colors.HexColor(SOFT)),('LEFTPADDING',(0,0),(0,-1),0)]));story.extend([t,Spacer(1,5)])
   for key in ('steps','bullets'):
    for n,item in enumerate(s.get(key,[])):story.append(Paragraph((f'<font name="Archivo-ExtraBold" color="{ACCENT_TEXT}">{n+1:02d}</font>  ' if key=='steps' else f'<font name="ZapfDingbats" size="6" color="{ACCENT}">n</font>  ')+esc(item),styles['BodySmall']))
   if s.get('notice'):story.append(Paragraph(f'<font name="ZapfDingbats" size="6" color="{ACCENT}">n</font>  '+esc(s['notice']),styles['BodySmall']))
   story.append(rule(.5,SOFT))
  if i==2:
   story.append(p('CHECKLIST','Kicker'));story.append(p('Try these next','SectionSmall'))
   checks=[p('[ ] '+c['text'],'CardSmall') for c in d['checklist']]
   t=Table([[checks[j],checks[j+1]] for j in range(0,len(checks),2)],colWidths=[262,262]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.5,colors.HexColor(SOFT)),('LEFTPADDING',(0,0),(0,-1),0)]));story.append(t)
   links=' · '.join(f'<link href="{esc(s["url"])}" color="{ACCENT_TEXT}">{esc(s["title"])}</link>' for s in d['sources'])
   story.append(Spacer(1,4));story.append(Paragraph('<font name="Archivo-ExtraBold">Sources:</font> '+links,styles['CardSmall']))
 def decorate(c,doc):
  n=min(doc.page-1,2)
  c.setFillColor(colors.HexColor(INK));c.setFont('Archivo-ExtraBold',18);c.drawString(44,748,d['title']);w=c.stringWidth(d['title'],'Archivo-ExtraBold',18)
  c.setFillColor(colors.HexColor(ACCENT));c.drawString(44+w,748,'.')
  c.setFillColor(colors.HexColor(ACCENT));c.setFont('Archivo-ExtraBold',18);c.drawRightString(568,748,f'{doc.page:02d}')
  c.setFillColor(colors.HexColor(INK));c.setFont('Archivo-SemiBold',8);c.drawString(44,734,d['pages'][n]['title'].upper())
  c.setStrokeColor(colors.HexColor(INK));c.setLineWidth(1.4);c.line(44,726,568,726)
  c.setLineWidth(1.4);c.line(44,40,568,40)
  c.setFillColor(colors.HexColor(MUTED));c.setFont('Archivo',7);c.drawString(44,28,f'Rob Bagley · Reviewed {d["reviewed"]} · Revision {rev[:12]}');c.drawRightString(568,28,f'{doc.page} / 3')
 SimpleDocTemplate(str(path),pagesize=(612,792),leftMargin=44,rightMargin=44,topMargin=76,bottomMargin=48,title=d['title'],author='Rob Bagley').build(story,onFirstPage=decorate,onLaterPages=decorate,canvasmaker=lambda *a,**kw: Canvas(*a,**dict(kw,invariant=1)))
 if len(PdfReader(path).pages)!=3:raise ValueError('Guide exceeds three-page layout. Shorten or reflow content before publishing.')
def generate(out):
 d=json.loads((ROOT/'content/guide.json').read_text());validate(d);rev=hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 out.mkdir(parents=True,exist_ok=True);(out/'assets').mkdir();(out/'chatgpt-quick-start-guide').mkdir()
 (out/'index.html').write_text(home_page(d,rev))
 body=f'<div class="rp-page"><section class="rp-hero"><div class="rp-hero-title"><div class="rp-kicker">Resource 01</div><h1 class="rp-display">{esc(d["title"])}<span class="rp-dot">.</span></h1></div><div class="guide-lede"><p class="rp-lede">{esc(d["subtitle"])}</p><a class="rp-btn rp-btn-primary no-print" href="../ChatGPT-Quick-Start-Guide.pdf">Download printable PDF<span aria-hidden="true">↓</span></a><p class="rp-label">Reviewed {d["reviewed"]} · Revision {rev[:12]}</p></div></section>'
 parts=[(f'part-{i+1}',f'{i+1:02d}',pg['title']) for i,pg in enumerate(d['pages'])]+[('checklist','04','Try these next')]
 body+='<nav class="rp-grid rp-boxed toc" aria-label="In this guide" style="--rp-cell:200px">'+''.join(f'<a href="#{a}"><span class="toc-num">{n}</span>{esc(t)}</a>' for a,n,t in parts)+'</nav>'
 for i,page in enumerate(d['pages']):body+=f'<article class="rp-section chapter" id="part-{i+1}"><div class="rp-section-head"><span class="rp-num">{i+1:02d}</span><h2>{esc(page["title"])}</h2></div>'+''.join(section(s) for s in page['sections'])+'</article>'
 body+='</div><section class="rp-band" id="checklist"><div class="rp-band-inner"><span class="rp-band-big" aria-hidden="true">04</span><h2 class="rp-band-big">Try these next.</h2></div></section><div class="rp-page after-band"><p class="rp-kicker progress" data-progress aria-live="polite">0 of 8 complete</p><ul class="checks">'+''.join(f'<li><label class="rp-check"><input type="checkbox" data-check="{esc(c["id"])}"><span>{esc(c["text"])}</span></label></li>' for c in d['checklist'])+'</ul><p class="meta">Checklist progress is saved in this browser when local storage is available.</p><section class="sources"><h2 class="rp-label">Sources and current guidance</h2><ul class="source-list">'+''.join(f'<li><a href="{esc(s["url"])}">{esc(s["title"])}</a></li>' for s in d['sources'])+'</ul></section></div>'
 (out/'chatgpt-quick-start-guide/index.html').write_text(shell(d['title'],body,d,rev,True))
 for name in ('site.css','guide.js'):(out/'assets'/name).write_bytes((ROOT/'templates'/name).read_bytes())
 # The shared style sheet ships unchanged from style-guide/, so every personal site gets the same file.
 (out/'assets'/'fonts').mkdir()
 for name in ('rob-personal.css','fonts/archivo.woff2','fonts/archivo-italic.woff2','fonts/OFL.txt'):(out/'assets'/name).write_bytes((ROOT/'style-guide'/name).read_bytes())
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
