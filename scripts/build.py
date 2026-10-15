#!/usr/bin/env python3
"""Build public artifacts from one reviewed content source."""
import argparse,datetime,hashlib,html,json,pathlib,re,tempfile
from urllib.parse import urlparse
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Image as RLImage,SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Flowable
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from PIL import Image,ImageDraw
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAP='https://robbagley-afk.github.io/model-value-map/'
TEAM='https://your-portable-ai-team.airy-emu-9499.chatgpt.site/'
def validate(d):
 datetime.date.fromisoformat(d['reviewed'])
 assert len(d['pages'])==4
 text=json.dumps(d)
 if re.search(r'/Users/|OneDrive|mem\.ai/|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?i:api[_-]?key|access[_-]?token)',text):raise ValueError('Private content in public input')
 ids=[x['id'] for x in d['checklist']]
 if len(ids)!=len(set(ids)) or any(not re.fullmatch(r'[a-z][a-z0-9-]*',x) for x in ids):raise ValueError('Invalid checklist IDs')
 for s in d['sources']+[x['link'] for pg in d['pages'] for x in pg['sections'] if x.get('link')]:
  u=urlparse(s['url'])
  if u.scheme!='https' or not u.netloc:raise ValueError('Sources require HTTPS')
def esc(t):return html.escape(t,quote=True)
def section(s):
 out=f'<section class="topic" id="{esc(s["id"])}"><div class="topic-head"><div class="rp-kicker">{esc(s["kicker"])}</div><h3>{esc(s["title"])}</h3></div><div class="topic-body">'
 if s.get('intro'):out+=f'<p class="intro">{esc(s["intro"])}</p>'
 if s.get('date'):out+=f'<p class="intro"><strong>{esc(s["date"]["text"])}</strong></p>'
 if s.get('cards'):out+='<div class="rp-grid rp-boxed cards">'+''.join(f'<div class="rp-tinted">'+(f'<p class="rp-label">{esc(c["label"])}</p>' if c.get('label') else '')+f'<h4>{esc(c["title"])}</h4><p>{esc(c["text"])}</p></div>' for c in s['cards'])+'</div>'
 if s.get('image'):im=s['image'];out+=f'<figure class="shot"><img src="../assets/{esc(im["src"])}" alt="{esc(im["alt"])}" loading="lazy"><figcaption class="rp-note">{esc(im["caption"])}</figcaption></figure>'
 if s.get('table'):
  t=s['table'];out+='<div class="rp-table-wrap"><table class="rp-table"><thead><tr>'+''.join(f'<th scope="col">{esc(x)}</th>' for x in t['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join((f'<th scope="row">{esc(x)}</th>' if i==0 else f'<td>{esc(x)}</td>') for i,x in enumerate(r))+'</tr>' for r in t['rows'])+'</tbody></table></div>'
 if s.get('steps'):out+='<ol class="rp-steps">'+''.join(f'<li>{esc(x)}</li>' for x in s['steps'])+'</ol>'
 if s.get('bullets'):out+='<ul class="bullets">'+''.join(f'<li>{esc(x)}</li>' for x in s['bullets'])+'</ul>'
 if s.get('notice'):out+=f'<p class="rp-note">{esc(s["notice"])}</p>'
 if s.get('try'):out+=f'<p class="rp-note"><strong>Quick win:</strong> {esc(s["try"])}</p>'
 if s.get('link'):out+=f'<p><a class="rp-btn rp-btn-primary" href="{esc(s["link"]["url"])}">{esc(s["link"]["text"])}<span aria-hidden="true">→</span></a></p>'
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
 rows=[('Learn Projects, models, scheduled tasks and plugins','ChatGPT Quick Start Guide','A practical guide to Projects, models, scheduled tasks, skills and plugins. Read online or download the printable four-page guide.','Web guide · 4-page PDF','Open ChatGPT Guide','chatgpt-quick-start-guide/','Download PDF','ChatGPT-Quick-Start-Guide.pdf'),
  ('Pick the right model for a task','Model Value Map','Compare model capability and cost using the current public map and its maintained guidance.','Interactive map · Ensign Career Services guidance','Open Model Value Map',MAP,'Ensign Career Services guidance',MAP+'team/'),
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
class Box(Flowable):
 # Filled square or empty tick box drawn as vector art, so it prints crisply and stays findable in grayscale.
 def __init__(self,size,fill,stroke=None,dy=0,h=None):Flowable.__init__(self);self.size,self.fill,self.stroke,self.dy=size,fill,stroke,dy;self.width=size;self.height=h or size
 def draw(self):
  c=self.canv;c.setFillColor(colors.HexColor(self.fill))
  if self.stroke:c.setStrokeColor(colors.HexColor(self.stroke));c.setLineWidth(1.5)
  c.rect(0,self.dy,self.size,self.size,fill=1,stroke=1 if self.stroke else 0)
def pdf(path,d,rev):
 # Layout follows the Design canvas "ChatGPT Quick Start Handout Redesign" (three Letter artboards).
 fonts()
 W=528;ink,acc,acct,mut,sur,soft=(colors.HexColor(x) for x in (INK,ACCENT,ACCENT_TEXT,MUTED,SURFACE,SOFT))
 S=lambda name,font='Archivo',size=9.4,lead=13.2,color=INK,**kw:ParagraphStyle(name=name,fontName=font,fontSize=size,leading=lead,textColor=colors.HexColor(color),**kw)
 st={'body':S('body',size=8.9,lead=11.9),'intro':S('intro',size=9.8,lead=13.4),'note':S('note',size=8.6,lead=11.4,color=MUTED),'kick':S('kick','Archivo-SemiBold',9,11,ACCENT_TEXT),
  'lab':S('lab','Archivo-SemiBold',7.8,10,MUTED),'ct':S('ct','Archivo-ExtraBold',10,12),'title':S('title','Archivo-ExtraBold',15,17),'num':S('num','Archivo-ExtraBold',27,25,ACCENT),
  'stepn':S('stepn','Archivo-ExtraBold',10,12,ACCENT),'white':S('white',size=9.2,lead=12.4,color='#ffffff'),'whiteb':S('whiteb','Archivo-ExtraBold',9,11,'#ffffff'),
  'h1':S('h1','Archivo-ExtraBold',31,30),'sub':S('sub',size=11,lead=15),'panel':S('panel',size=9,lead=12,color='#f3f2f2'),'panelh':S('panelh','Archivo-ExtraBold',9,11,'#f3f2f2'),
  'th':S('th','Archivo-ExtraBold',9.4,12),'src':S('src',size=8.4,lead=10.8,color=ACCENT_TEXT)}
 P=lambda t,k='body':Paragraph(t,st[k]);E=lambda t,k='body':P(esc(t),k)
 up=lambda t:esc(t.upper())
 n=[0]
 def head(s):
  n[0]+=1
  t=Table([[P(f'{n[0]:02d}','num'),[P(up(s['kicker']),'kick'),E(s['title'],'title')]]],colWidths=[38,W-38])
  t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'BOTTOM'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),4),('LINEBELOW',(0,0),(-1,0),1.5,ink)]));return t
 def grid(cells,widths=None,fill=True):
  t=Table([cells],colWidths=widths or [W/len(cells)]*len(cells))
  t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOX',(0,0),(-1,-1),1.5,ink),('INNERGRID',(0,0),(-1,-1),1.5,ink),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6)]+([('BACKGROUND',(0,0),(-1,-1),sur)] if fill else [])));return t
 def card(c):return ([E(c['label'].upper(),'lab')] if c.get('label') else [])+[E(c['title'],'ct'),E(c['text'])]
 def flat(t,style):t.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]+style));return t
 def note(text):return flat(Table([[Box(5,ACCENT,dy=4.6,h=11.4),E(text,'note')]],colWidths=[12,W-12]),[('VALIGN',(0,0),(-1,-1),'TOP')])
 def steps(items):
  t=Table([[[P(f'{i+1:02d}','stepn'),E(x)] for i,x in enumerate(items)]],colWidths=[W/len(items)]*len(items))
  return flat(t,[('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,0),(-1,0),.75,soft),('TOPPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),10)])
 def band(label,text):
  t=Table([[P(up(label),'whiteb'),E(text,'white')]],colWidths=[78,W-78])
  t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),acc),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6)]));return t
 gap=lambda h=5:Spacer(1,h)
 story=[]
 for i,page in enumerate(d['pages']):
  if i:story.append(PageBreak())
  if i==0:
   c=d['checklist']
   panel=Table([[E('YOUR FIRST WEEK','panelh')]]+[[P(f'<font name="Archivo-ExtraBold" color="#7fa8ec">Day {k+1}</font>  '+esc(c[k]['text']),'panel')] for k in range(3)]+[[E(f'Full checklist on page {len(d["pages"])}.','note')]],colWidths=[186])
   panel.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),ink),('LEFTPADDING',(0,0),(-1,-1),11),('RIGHTPADDING',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,0),9),('BOTTOMPADDING',(0,-1),(-1,-1),8),('TEXTCOLOR',(0,-1),(-1,-1),colors.HexColor('#b8b4b4'))]))
   hero=Table([[[P(esc(d['title'])+f'<font color="{ACCENT}">.</font>','h1'),gap(5),E(d['subtitle'],'sub')],panel]],colWidths=[W-204,204])
   story+= [flat(hero,[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(1,0),(1,0),18)]),gap(6)]
  for s in page['sections']:
   story+=[head(s),gap(5)]
   if s.get('intro'):story+=[E(s['intro'],'intro'),gap(6)]
   if s.get('table'):
    t=s['table'];rows=[[E(x,'th') for x in t['headers']]]+[[E(r[0].upper(),'lab')]+[E(x) for x in r[1:]] for r in t['rows']]
    story+=[flat(Table(rows,colWidths=[78,150,150,150]),[('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),1.5,ink),('LINEBELOW',(0,1),(-1,-1),.75,soft),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),8)]),gap()]
   if s.get('cards'):
    cs=s['cards']
    if all(c['title'].endswith('day') for c in cs):
     cells=[flat(Table([[band_tag(c['title'][:3].upper()),E(c['text'])]],colWidths=[38,W/len(cs)-56]),[('VALIGN',(0,0),(-1,-1),'TOP')]) for c in cs]
     story+=[grid(cells,fill=False),gap()]
    elif s.get('image'):
     im=s['image'];iw=300;w0,h0=Image.open(ROOT/'content'/im['src']).size
     pic=[RLImage(str(ROOT/'content'/im['src']),width=iw,height=iw*h0/w0),gap(3),E(im['caption'],'note')]
     cw=W-iw-14;stack=Table([[card(c)] for c in cs],colWidths=[cw]);stack.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOX',(0,0),(-1,-1),1.5,ink),('INNERGRID',(0,0),(-1,-1),1.5,ink),('BACKGROUND',(0,0),(-1,-1),sur),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
     story+=[flat(Table([[pic,stack]],colWidths=[iw+14,cw]),[('VALIGN',(0,0),(-1,-1),'TOP')]),gap()]
    elif s.get('date'):
     dt=s['date'];tile=[E(dt['label'].upper(),'whiteb'),Paragraph(esc(dt['big']),S('big','Archivo-ExtraBold',23,25,'#ffffff')),E(dt['small'],'whiteb')]
     inner=grid([card(c) for c in cs],[(W-112)/3]*3)
     t=Table([[tile,inner]],colWidths=[112,W-112]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(0,0),acc),('VALIGN',(0,0),(0,0),'MIDDLE'),('LEFTPADDING',(0,0),(0,0),10),('LEFTPADDING',(1,0),(1,0),0),('RIGHTPADDING',(1,0),(1,0),0),('TOPPADDING',(1,0),(1,0),0),('BOTTOMPADDING',(1,0),(1,0),0),('BOX',(0,0),(-1,-1),1.5,ink)]))
     story+=[t,gap()]
    else:story+=[grid([card(c) for c in cs]),gap()]
   if s.get('link'):
    l=s['link'];btn=Table([[P(f'<link href="{esc(l["url"])}" color="#ffffff">{esc(l["text"])}</link>','whiteb')]],rowHeights=[26]);btn.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),acc),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12)]))
    side=E(s['notice'],'note') if s.get('notice') else ''
    story+=[flat(Table([[btn,side]],colWidths=[176,W-176]),[('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(1,0),(1,0),12)]),gap()]
   if s.get('steps'):story+=[steps(s['steps']),gap()]
   if s.get('bullets'):
    b=s['bullets'];cols=3;rows=[[[P(f'<font name="Archivo-ExtraBold" color="{ACCENT}">{r*cols+k+1}</font>  '+esc(b[r*cols+k]))] for k in range(cols)] for r in range(len(b)//cols)]
    story+=[flat(Table(rows,colWidths=[W/cols]*cols),[('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,0),(-1,0),1.5,ink),('LINEBELOW',(0,0),(-1,-1),.75,soft),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),10)]),gap()]
   if s.get('try'):story+=[band('Quick win',s['try']),gap()]
   if s.get('notice') and not s.get('link'):story+=[note(s['notice']),gap()]  # a link row carries its notice beside the button
   story.append(gap(4))
  if i==len(d['pages'])-1:
   items=[flat(Table([[Box(10,'#ffffff',INK),E(c['text'])]],colWidths=[18,(W-40)/2-18]),[('VALIGN',(0,0),(-1,-1),'MIDDLE')]) for c in d['checklist']]
   rows=[[items[j],items[j+1]] for j in range(0,len(items),2)]
   chk=flat(Table(rows,colWidths=[(W-40)/2+10,(W-40)/2+10]),[('LINEBELOW',(0,0),(-1,-1),.75,soft),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(0,-1),12)])
   ttl=flat(Table([[P('Try these next'+f'<font color="{ACCENT}">.</font>','title'),E('ONE A DAY. TICK AS YOU GO.','lab')]],colWidths=[260,W-28-260]),[('VALIGN',(0,0),(-1,-1),'BOTTOM'),('ALIGN',(1,0),(1,0),'RIGHT')])
   wrap=Table([[ttl],[chk]],colWidths=[W]);wrap.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),sur),('BOX',(0,0),(-1,-1),1.5,ink),('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),('TOPPADDING',(0,0),(0,0),8),('BOTTOMPADDING',(0,-1),(-1,-1),8)]))
   story+=[wrap,gap(8),E('SOURCES AND CURRENT GUIDANCE','lab'),gap(4)]
   src=[P(f'<link href="{esc(x["url"])}" color="{ACCENT_TEXT}">{esc(x["title"])}</link>','src') for x in d['sources']]
   src+=['']*(-len(src)%3)
   story.append(flat(Table([src[j:j+3] for j in range(0,len(src),3)],colWidths=[W/3]*3),[('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),10)]))
 def decorate(c,doc):
  k=doc.page;N=len(d['pages']);pt=d['pages'][min(k-1,N-1)]['title']
  kick='AI QUICK START · RESOURCE 01' if k==1 else f'{d["title"].upper()}. · {pt.upper()}'
  c.setFillColor(acct);c.setFont('Archivo-SemiBold',9);c.drawString(42,750,kick)
  c.setFillColor(acc);c.setFont('Archivo-ExtraBold',13.5);c.drawRightString(570,750,f'{k:02d} / {N:02d}')
  c.setStrokeColor(ink);c.setLineWidth(1.5);c.line(42,742,570,742);c.line(42,42,570,42)
  c.setFillColor(mut);c.setFont('Archivo',8.25);c.drawString(42,30,f'Rob Bagley · Reviewed {d["reviewed"]} · Revision {rev[:12]} · Verify important results and follow your campus policies.');c.drawRightString(570,30,f'{k} / {N}')
 SimpleDocTemplate(str(path),pagesize=(612,792),leftMargin=42,rightMargin=42,topMargin=58,bottomMargin=48,title=d['title'],author='Rob Bagley').build(story,onFirstPage=decorate,onLaterPages=decorate,canvasmaker=lambda *a,**kw: Canvas(*a,**dict(kw,invariant=1)))
 if len(PdfReader(path).pages)!=len(d['pages']):raise ValueError('Guide exceeds its page layout. Shorten or reflow content before publishing.')
def band_tag(day):
 t=Table([[Paragraph(esc(day),ParagraphStyle(name='tag',fontName='Archivo-ExtraBold',fontSize=9,leading=11,textColor=colors.white))]],colWidths=[32])
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor(ACCENT)),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),3)]));return t
def generate(out):
 d=json.loads((ROOT/'content/guide.json').read_text());validate(d);rev=hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 out.mkdir(parents=True,exist_ok=True);(out/'assets').mkdir();(out/'chatgpt-quick-start-guide').mkdir()
 (out/'index.html').write_text(home_page(d,rev))
 body=f'<div class="rp-page"><section class="rp-hero"><div class="rp-hero-title"><div class="rp-kicker">Resource 01</div><h1 class="rp-display">{esc(d["title"])}<span class="rp-dot">.</span></h1></div><div class="guide-lede"><p class="rp-lede">{esc(d["subtitle"])}</p><a class="rp-btn rp-btn-primary no-print" href="../ChatGPT-Quick-Start-Guide.pdf">Download printable PDF<span aria-hidden="true">↓</span></a><p class="rp-label">Reviewed {d["reviewed"]} · Revision {rev[:12]}</p></div></section>'
 parts=[(f'part-{i+1}',f'{i+1:02d}',pg['title']) for i,pg in enumerate(d['pages'])]+[('checklist',f'{len(d["pages"])+1:02d}','Try these next')]
 body+='<nav class="rp-grid rp-boxed toc" aria-label="In this guide" style="--rp-cell:200px">'+''.join(f'<a href="#{a}"><span class="toc-num">{n}</span>{esc(t)}</a>' for a,n,t in parts)+'</nav>'
 for i,page in enumerate(d['pages']):body+=f'<article class="rp-section chapter" id="part-{i+1}"><div class="rp-section-head"><span class="rp-num">{i+1:02d}</span><h2>{esc(page["title"])}</h2></div>'+''.join(section(s) for s in page['sections'])+'</article>'
 body+=f'</div><section class="rp-band" id="checklist"><div class="rp-band-inner"><span class="rp-band-big" aria-hidden="true">{len(d["pages"])+1:02d}</span><h2 class="rp-band-big">Try these next.</h2></div></section><div class="rp-page after-band"><p class="rp-kicker progress" data-progress aria-live="polite">0 of 8 complete</p><ul class="checks">'+''.join(f'<li><label class="rp-check"><input type="checkbox" data-check="{esc(c["id"])}"><span>{esc(c["text"])}</span></label></li>' for c in d['checklist'])+'</ul><p class="meta">Checklist progress is saved in this browser when local storage is available.</p><section class="sources"><h2 class="rp-label">Sources and current guidance</h2><ul class="source-list">'+''.join(f'<li><a href="{esc(s["url"])}">{esc(s["title"])}</a></li>' for s in d['sources'])+'</ul></section></div>'
 (out/'chatgpt-quick-start-guide/index.html').write_text(shell(d['title'],body,d,rev,True))
 for name in ('site.css','guide.js'):(out/'assets'/name).write_bytes((ROOT/'templates'/name).read_bytes())
 # The shared style sheet ships unchanged from style-guide/, so every personal site gets the same file.
 (out/'assets'/'fonts').mkdir()
 for name in ('rob-personal.css','fonts/archivo.woff2','fonts/archivo-italic.woff2','fonts/OFL.txt'):(out/'assets'/name).write_bytes((ROOT/'style-guide'/name).read_bytes())
 for sec in (x for pg in d['pages'] for x in pg['sections'] if x.get('image')):
  dst=out/'assets'/sec['image']['src'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((ROOT/'content'/sec['image']['src']).read_bytes())
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
