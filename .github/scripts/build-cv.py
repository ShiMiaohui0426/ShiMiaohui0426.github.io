"""Build the public bilingual CV PDFs. Requires reportlab and PyYAML."""
from pathlib import Path
from xml.sax.saxutils import escape
import re, shutil
import yaml
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

ROOT = Path(__file__).resolve().parents[2]
DATA = yaml.safe_load((ROOT/'_data/profile.yml').read_text())
PAPERS = yaml.safe_load((ROOT/'_data/papers.yml').read_text())
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
BASE = 'https://shimiaohui0426.github.io'
UPDATED = '2026-09-13'

COPY = {
'en': {
 'name':'Miaohui Shi / 施妙辉', 'role':'Algorithm Engineer | High-performance Computing & Robotics',
 'intro':'Algorithm engineer at Taizhou Optoelectronics Industry Innovation Center. M.S. in Mechanical Engineering, Waseda University, completed March 2024. Research and engineering in GDS rasterization, multi-robot interaction and vision-based tactile sensing.',
 'work':'PROFESSIONAL EXPERIENCE', 'education':'EDUCATION', 'skills':'TECHNICAL SKILLS', 'earlier':'EARLIER ACADEMIC EXPERIENCE',
 'jobs':[
  ('Sep 2024 - present','Algorithm Engineer','Taizhou Optoelectronics Industry Innovation Center / 台州光电产业创新中心',[
   'Develop EDA-related algorithms and software using C++ and Python. Ported GDS rasterization from Python to C++ and optimized computation, parallelism, memory access and compilation.',
   'Migrated the workload from a small PC to multi-node servers. Full progression: an initial estimate of tens of thousands of hours to a measured 24-minute six-node run. Measured 800 to 24 minutes gives 33.3× end-to-end acceleration, including hardware and deployment changes.',
   'Implemented partitioned reads so each node loads only its assigned data. On the same server configuration and node count, reduced processing from 92 to 44 minutes (2.09×). Minute-level comparisons use the same GDS input and 4-pass workload.',
   'Extended the pipeline with multi-node processing, CD bias and correction support; built software for local inspection of very large raster images and equipment control.'
  ]),
  ('Apr - Aug 2024','Algorithm Development','Hesai Technology / Sharpa-related R&D',[
   'Formal employer: Hesai Technology. Worked on LiDAR functional-degradation algorithms and noise-segmentation model training, alongside Sharpa-related tactile-sensor R&D.',
   'Designed and trained mechanical models for vision-based tactile sensors; developed and trained models on Ubuntu.'
  ])],
 'research':'SELECTED RESEARCH',
 'projects':[
  ('Multi-robot interaction, attention and automation | CASE 2024', 'Independently developed the experimental system (excluding the mechanical-head module), designed and conducted the experiments, and completed all data analysis. Adapted the PASAT auditory-addition task to a dual-task study involving three robotic arms, with NASA-TLX and user-experience measures.'),
  ('High-speed vision-based tactile sensing | ICAT-EGVE 2024', 'Independently developed algorithmic principles, implementation, performance tuning and the front-end UI. The method combines local sparse marker tracking with force estimation using an asymmetric stiffness-coefficient matrix. The paper reports 601.25 Hz sensor-system force acquisition; this is not a standalone algorithm benchmark.')],
 'papers':'PUBLICATIONS', 'patents':'PATENTS',
 'patent_text':'Eight distinct patent application records are listed on the website, covering visual inspection, material handling, subpixel image processing and vision-based tactile sensing. Publication and grant versions of the same application are counted once.',
 'interest':'RESEARCH DIRECTION', 'interest_text':'Future doctoral research interest: household service robots, tactile perception, human-robot collaboration and appropriate automation. Industry interests include EDA, computational lithography and high-performance algorithm engineering.',
 'foot':'Updated 13 Sep 2026 | Quantified project results through 2025',
},
'zh': {
 'name':'施妙辉 / Miaohui Shi', 'role':'算法工程师 | 高性能计算与机器人研究',
 'intro':'现任台州光电产业创新中心算法工程师。2024 年 3 月毕业于早稻田大学，获机械工程硕士学位。研究与工程方向涵盖 GDS 光栅化、多机器人人机交互及高速视触觉感知。',
 'work':'工作经历', 'education':'教育背景', 'skills':'技术能力', 'earlier':'早期学术经历',
 'jobs':[
  ('2024.09 - 至今','算法工程师','台州光电产业创新中心',[
   '使用 C++ 与 Python 开发 EDA 相关算法和软件。将 GDS 光栅化算法由 Python 移植至 C++，优化计算内核、并行执行、访存和编译设置。',
   '将工作负载由小型 PC 迁移至多节点服务器。完整演进从最初预计的数万小时，到六节点服务器实测 24 分钟；已实测阶段从 800 分钟降至 24 分钟，约 33.3 倍端到端加速，包含硬件与部署变化。',
   '设计按节点分块读取，每个节点只加载所需数据。同一服务器配置与节点数下，耗时由 92 分钟降至 44 分钟，约加速 2.09 倍。分钟级对比使用同一 GDS 输入与 4-pass 工作负载。',
   '集成多节点计算、CD bias 与校正功能，开发超大规模图像局部查看和设备控制配套软件。'
  ]),
  ('2024.04 - 2024.08','算法研发','禾赛科技 / Sharpa 相关研发',[
   '正式任职单位为禾赛科技，负责激光雷达功能降级算法、噪声分割模型训练，同时参与 Sharpa 相关视触觉传感器研发。',
   '设计与训练视触觉传感器力学模型，在 Ubuntu 下进行模型训练及软件开发。'
  ])],
 'research':'代表性研究',
 'projects':[
  ('多机器人人机交互、注意力与自动化 | CASE 2024','独立完成实验系统开发（机械头模块除外）、实验设计与实施及全部数据分析。将心理学中的 PASAT 听觉连续加法任务引入三台机械臂的双任务实验，结合 NASA-TLX 工作负荷和用户体验问卷评估不同自动化等级。'),
  ('高速视触觉感知算法与软件 | ICAT-EGVE 2024','独立完成算法原理设计、代码实现、性能调优及前端 UI。通过帧间局部稀疏标记点搜索与非对称刚度系数矩阵进行力估计。论文报告系统力信息采集速率为 601.25 Hz，此数值并非单独算法的性能基准。')],
 'papers':'发表论文', 'patents':'专利成果',
 'patent_text':'主页收录 8 条不同专利申请记录，涵盖视觉检测、自动上料、亚像素图像处理及视触觉传感器。同一申请的公开文本与授权文本不重复计数；完整题名、申请号和来源见专利页面。',
 'interest':'研究方向', 'interest_text':'未来博士研究兴趣：家庭服务机器人、触觉感知、人机协作与适度自动化。产业方向关注 EDA、计算光刻与高性能算法工程。',
 'foot':'更新于 2026-09-13 | 量化项目成果截至 2025 年',
}}

def build(lang):
 c=COPY[lang]; ui=DATA[lang]; stories=[]
 styles={
 'name':ParagraphStyle('name',fontName='Helvetica',fontSize=24,leading=29,textColor=HexColor('#153b57'),spaceAfter=5),
 'role':ParagraphStyle('role',fontName='Helvetica',fontSize=12,leading=17,spaceAfter=7),
 'body':ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=13.5,spaceAfter=5,wordWrap='CJK' if lang=='zh' else None),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=4,textColor=HexColor('#42566a')),
 'section':ParagraphStyle('section',fontName='Helvetica',fontSize=13,leading=18,textColor=HexColor('#153b57'),spaceBefore=8,spaceAfter=5,keepWithNext=True),
 'job':ParagraphStyle('job',fontName='Helvetica',fontSize=11.5,leading=16,spaceBefore=5,spaceAfter=3,keepWithNext=True),
 }
 def para(t,style='body',raw=False):
  text=t if raw else escape(t)
  text=re.sub(r'[\u2e80-\uffff]+',lambda m:'<font name="STSong-Light">'+m.group()+'</font>',text)
  return Paragraph(text,styles[style])
 def add(t,s='body',raw=False):stories.append(para(t,s,raw))
 def sect(t):add(t,'section')
 add(c['name'],'name');add(c['role'],'role')
 add(f'Taizhou, Zhejiang, China | <link href="{BASE}/cv/" color="#17608c">{BASE}/cv/</link>', 'small',True)
 add('<link href="https://github.com/ShiMiaohui0426" color="#17608c">GitHub: ShiMiaohui0426</link> | <link href="https://www.linkedin.com/in/miaohui-shi-721756195/" color="#17608c">LinkedIn: Miaohui Shi</link>', 'small',True)
 add(c['intro']);sect(c['work'])
 for period,title,org,bullets in c['jobs']:
  add(f'{title} | {period}','job');add(org,'small')
  for b in bullets:add('• '+b)
 sect(c['education'])
 for e in ui['education_entries']:
  add(e['title']+' | '+e['period'],'job');add(e['organization'],'body')
 sect(c['skills'])
 for e in ui['skills']:add(e['title']+': '+e['text'],'small')
 sect(c['earlier'])
 for e in ui['earlier_entries']:add(e['period']+' | '+e['title'],'small')
 stories.append(PageBreak())
 add(c['name'],'name');add(c['research'],'role')
 for title,desc in c['projects']:add(title,'job');add(desc)
 sect(c['papers'])
 for p in PAPERS:
  title=p['title'];authors=p['authors'].replace('**','')
  stories.append(KeepTogether([para(f"{p['year']} | {title}",'job'),para(authors,'small'),para(escape(p['venue'])+f' | <link href="https://doi.org/{p["doi"]}" color="#17608c">DOI: {p["doi"]}</link>','small',True)]))
 sect(c['patents']);add(c['patent_text']);add(f'<link href="{BASE}/patents/" color="#17608c">{BASE}/patents/</link>','small',True)
 sect(c['interest']);add(c['interest_text'])
 def footer(can,doc):
  can.setTitle('Miaohui Shi - Curriculum Vitae - '+lang.upper()+' - '+UPDATED)
  can.setAuthor('Miaohui Shi');can.setSubject('Current professional CV; updated '+UPDATED)
  can.setStrokeColor(HexColor('#d5dde4'));can.line(42,37,553,37)
  can.setFont('STSong-Light',8);can.setFillColor(HexColor('#526779'));can.drawString(42,24,c['foot']);can.drawRightString(553,24,str(doc.page))
 path=ROOT/'files'/f'Miaohui_Shi_CV_{lang.upper()}.pdf'
 SimpleDocTemplate(str(path),pagesize=(595.28,841.89),leftMargin=42,rightMargin=42,topMargin=34,bottomMargin=49).build(stories,onFirstPage=footer,onLaterPages=footer)
 print(path)
for lang in ('en','zh'):build(lang)
# Keep old bookmarks useful; the original PDF was in Chinese.
shutil.copyfile(ROOT/'files/Miaohui_Shi_CV_ZH.pdf',ROOT/'files/SMH_RESUME.pdf')
