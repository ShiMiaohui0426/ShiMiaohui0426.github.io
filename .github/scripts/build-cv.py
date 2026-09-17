"""Build the two-page bilingual CVs with embedded, locally bundled fonts.

Run: python3 .github/scripts/build-cv.py
Dependencies: reportlab, PyYAML. See .github/fonts/README.md for font coverage.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import re
import shutil
import yaml
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[2]
DATA = yaml.safe_load((ROOT / '_data/profile.yml').read_text(encoding='utf-8'))
PAPERS = yaml.safe_load((ROOT / '_data/papers.yml').read_text(encoding='utf-8'))
BASE = 'https://shimiaohui0426.github.io'
UPDATED = '2026-09-17'
FONT_DIR = ROOT / '.github/fonts'
for weight in ('Regular', 'Bold'):
    pdfmetrics.registerFont(TTFont('CV-' + weight, str(FONT_DIR / f'NotoSansSC-CV-{weight}.ttf')))
pdfmetrics.registerFontFamily('CV-Regular', normal='CV-Regular', bold='CV-Bold', italic='CV-Regular', boldItalic='CV-Bold')

COPY = {
'en': {
 'name':'Miaohui Shi', 'role':'Algorithm Engineer | High-performance Computing & Robotics',
 'intro':'Algorithm engineer developing C++ / Python software for computational lithography, with experience in performance optimization, distributed data pipelines and equipment diagnostics. M.S. from Waseda University; research in HRI and tactile sensing.',
 'work':'PROFESSIONAL EXPERIENCE', 'education':'EDUCATION', 'skills':'TECHNICAL SKILLS', 'earlier':'EARLIER ACADEMIC EXPERIENCE',
 'research':'SELECTED RESEARCH',
 'projects':[
  ('Multi-robot interaction, attention and automation | CASE 2024', 'Independently developed the experimental system (excluding the mechanical-head module), designed and conducted the experiments, and completed all data analysis. Adapted the PASAT auditory-addition task to a dual-task study involving three robotic arms, with NASA-TLX and user-experience measures.'),
  ('High-speed vision-based tactile sensing | ICAT-EGVE 2024', 'Independently developed algorithmic principles, implementation, performance tuning and the front-end UI. The method combines local sparse marker tracking with force estimation using an asymmetric stiffness-coefficient matrix. The paper reports 601.25 Hz sensor-system force acquisition; this is not a standalone algorithm benchmark.')],
 'papers':'PUBLICATIONS', 'patents':'PATENTS',
 'interest':'RESEARCH DIRECTION', 'interest_text':'Future doctoral research interest: household service robots, tactile perception, human-robot collaboration and appropriate automation. Industry interests include EDA, computational lithography and high-performance algorithm engineering.',
 'foot':'Updated 17 Sep 2026 | Runtime benchmarks recorded in 2024-2025',
},
'zh': {
 'name':'施妙辉', 'role':'算法工程师 | 高性能计算与机器人研究',
 'intro':'现任台州光电产业创新中心算法工程师，开发计算光刻 C++ / Python 软件，关注计算性能、分布式数据流水线与设备诊断。早稻田大学机械工程硕士，具有多机器人人机交互与视触觉研究经历。',
 'work':'工作经历', 'education':'教育背景', 'skills':'技术能力', 'earlier':'早期学术经历',
 'research':'代表性研究',
 'projects':[
  ('多机器人人机交互、注意力与自动化 | CASE 2024','独立完成实验系统开发（机械头模块除外）、实验设计与实施及全部数据分析。将心理学中的 PASAT 听觉连续加法任务引入三台机械臂的双任务实验，结合 NASA-TLX 工作负荷和用户体验问卷评估不同自动化等级。'),
  ('高速视触觉感知算法与软件 | ICAT-EGVE 2024','独立完成算法原理设计、代码实现、性能调优及前端 UI。通过帧间局部稀疏标记点搜索与非对称刚度系数矩阵进行力估计。论文报告系统力信息采集速率为 601.25 Hz，此数值并非单独算法的性能基准。')],
 'papers':'发表论文', 'patents':'专利成果',
 'interest':'研究方向', 'interest_text':'未来博士研究兴趣：家庭服务机器人、触觉感知、人机协作与适度自动化。产业方向关注 EDA、计算光刻与高性能算法工程。',
 'foot':'更新于 2026-09-17 | 耗时基准记录于 2024-2025 年',
}}

# A4, generous outer margins, one reading column and restrained teal accents.
W, H, M = 595.276, 841.89, 42
CW = W - 2 * M
INK, MUTED, TEAL, RULE, PALE = map(HexColor, ('#172B39', '#52636C', '#176B71', '#D5E0E3', '#F1F7F7'))


def clean(text):
    return str(text).replace('–', '-').replace('—', '-').replace('\u2011', '-')


class Resume:
    def __init__(self, lang):
        self.lang = lang
        self.c = COPY[lang]
        self.ui = DATA[lang]
        self.path = ROOT / 'files' / f'Miaohui_Shi_CV_{lang.upper()}.pdf'
        self.pdf = canvas.Canvas(str(self.path), pagesize=(W, H), pageCompression=1, invariant=1,
                                 initialFontName='CV-Regular', lang='zh-CN' if lang == 'zh' else 'en')
        self.pdf.setTitle(f'Miaohui Shi | Curriculum Vitae | {lang.upper()} | {UPDATED}')
        self.pdf.setAuthor('Miaohui Shi')
        self.pdf.setSubject('Algorithm engineering, high-performance computing and robotics')
        self.pdf.setCreator('Miaohui Shi CV / ReportLab')
        self.body_size = 10.0 if lang == 'zh' else 9.3
        self.leading = 15.0 if lang == 'zh' else 13.5
        self.page = 1
        self.y = 38

    def text(self, text, x=M, top=None, width=CW, size=None, leading=None,
             bold=False, color=INK, raw=False, measure=False):
        top = self.y if top is None else top
        text = clean(text)
        markup = text if raw else escape(text)
        visible = re.sub('<[^>]*>', '', markup)
        # Never silently emit missing-glyph squares after a content update.
        cmap = pdfmetrics.getFont('CV-Regular').face.charToGlyph
        missing = sorted({c for c in visible if not c.isspace() and ord(c) not in cmap})
        if missing:
            raise ValueError('Missing font glyphs; regenerate CV fonts: ' + ''.join(missing))
        size = size or self.body_size
        st = ParagraphStyle('cv', fontName='CV-Bold' if bold else 'CV-Regular',
                            fontSize=size, leading=leading or self.leading,
                            textColor=color, wordWrap='CJK' if self.lang == 'zh' else None,
                            splitLongWords=False, allowWidows=0, allowOrphans=0)
        p = Paragraph(markup, st)
        _, height = p.wrap(width, H)
        if not measure:
            if top + height > H - 48:
                raise ValueError(f'Page {self.page} overflows at {text[:70]!r}: {top + height:.1f}')
            p.drawOn(self.pdf, x, H - top - height)
        return height

    def add(self, text, gap=5, **kw):
        self.y += self.text(text, **kw) + gap

    def link(self, label, url):
        return f'<link href="{escape(url)}" color="#176B71">{escape(label)}</link>'

    def line(self, top, x=M, width=CW, color=RULE, weight=.6):
        self.pdf.setStrokeColor(color)
        self.pdf.setLineWidth(weight)
        self.pdf.line(x, H-top, x+width, H-top)

    def header(self, compact=False):
        self.pdf.setFillColor(TEAL)
        self.pdf.rect(M, H-29, 30, 3, fill=1, stroke=0)
        if compact:
            self.add(self.c['name'], size=21, leading=26, bold=True, gap=2)
            self.text('研究与成果' if self.lang == 'zh' else 'RESEARCH & PUBLICATIONS',
                      top=43, x=310, width=CW-268, size=9, leading=13, color=TEAL)
            self.line(self.y+6)
            self.y += 20
            return
        self.add(self.c['name'], size=31, leading=38, bold=True, gap=3)
        self.text('Miaohui Shi' if self.lang == 'zh' else '施妙辉',
                  x=424 if self.lang == 'en' else 397, top=47, width=155, size=13, leading=19, color=MUTED)
        self.add(self.c['role'], size=11, leading=16, color=TEAL, gap=7)
        loc = '中国 · 浙江台州' if self.lang == 'zh' else 'Taizhou, Zhejiang, China'
        self.add(escape(loc)+'  |  '+self.link('shimiaohui0426.github.io', BASE+('/zh/cv/' if self.lang=='zh' else '/cv/')),
                 size=8.4, leading=12, color=MUTED, raw=True, gap=2)
        self.add(self.link('GitHub / ShiMiaohui0426', 'https://github.com/ShiMiaohui0426')+'  ·  '+
                 self.link('LinkedIn / Miaohui Shi', 'https://www.linkedin.com/in/miaohui-shi-721756195/'),
                 size=8.4, leading=12, color=MUTED, raw=True, gap=9)
        self.line(self.y)
        self.y += 12
        self.add(self.c['intro'], size=self.body_size, leading=self.leading, gap=12)

    def section(self, label):
        self.y += 6
        self.text(label, size=10.3, leading=15, bold=True, color=TEAL)
        length = pdfmetrics.stringWidth(label, 'CV-Bold', 10.3)
        self.line(self.y+9, M+length+12, CW-length-12)
        self.y += 23

    def metrics(self):
        items = [
            ('800 → 24 min', 'GDS 端到端耗时' if self.lang=='zh' else 'GDS end-to-end runtime',
             '约 33.3× · 含硬件与部署变化' if self.lang=='zh' else '33.3× incl. platform changes'),
            ('< 120 GB', '单节点峰值内存' if self.lang=='zh' else 'Peak memory per node',
             '分块与复用 · 解决 256 GB OOM' if self.lang=='zh' else 'Resolved OOM on 256 GB nodes'),
            ('4 / 4', '整机子系统日志接入' if self.lang=='zh' else 'Subsystems with unified logs',
             'FastAPI · 任务日志持久化' if self.lang=='zh' else 'FastAPI · persistent task logs'),
        ]
        gap=10
        col=(CW-2*gap)/3
        top=self.y
        for i,(value,label,note) in enumerate(items):
            x=M+i*(col+gap)
            self.pdf.setFillColor(PALE)
            self.pdf.roundRect(x, H-top-70, col, 70, 4, fill=1, stroke=0)
            self.text(value, x+10, top+7, col-20, size=17.5, leading=24, bold=True, color=TEAL)
            self.text(label, x+10, top+34, col-20, size=8.3, leading=12, bold=True)
            self.text(note, x+10, top+49, col-20, size=7.2, leading=10, color=MUTED)
        self.y += 73

    def job(self, period, title, org, bullets):
        period_w = 113
        heading = org if self.lang=='zh' else org.split(' / ')[0]
        if self.lang == 'en' and 'Hesai' in org:
            heading = 'Hesai Technology / Sharpa-related R&D'
        self.add(heading, width=CW-period_w-8, size=11.2 if self.lang=='zh' else 10.3,
                 leading=16, bold=True, gap=1)
        # Dates align to the same right-hand column for every employer.
        self.text(period, M+CW-period_w, self.y-17, period_w, size=8.0, leading=13, color=MUTED)
        self.add(title, size=8.7, leading=13, color=MUTED, gap=4)
        for bullet in bullets:
            self.pdf.setFillColor(TEAL)
            self.pdf.circle(M+2, H-self.y-6.7, 1.35, fill=1, stroke=0)
            self.add(bullet, x=M+11, width=CW-11, gap=3)
        self.y += 6

    def education(self):
        self.section(self.c['education'])
        top=self.y
        gap=24
        width=(CW-gap)/2
        ends=[]
        for i,e in enumerate(self.ui['education_entries']):
            x=M+i*(width+gap)
            y=top
            org, country = e['organization'].split(' · ')
            y += self.text(org,x,y,width,size=10.2,leading=15,bold=True)+2
            y += self.text(e['title'],x,y,width,size=9,leading=13)+2
            y += self.text(e['period']+'  ·  '+country,x,y,width,size=8.3,leading=12,color=MUTED)
            ends.append(y)
        self.y=max(ends)+4

    def skills(self):
        self.section(self.c['skills'])
        gap=24
        width=(CW-gap)/2
        for row in range(2):
            top=self.y
            ends=[]
            for col,e in enumerate(self.ui['skills'][2*row:2*row+2]):
                x=M+col*(width+gap)
                y=top+self.text(e['title'],x,top,width,size=8.8,leading=13,bold=True)+2
                y+=self.text(e.get('cv_text', e['text']),x,y,width,size=8.2,leading=12,color=MUTED)
                ends.append(y)
            self.y=max(ends)+8

    def research(self):
        self.section(self.c['research'])
        for title, desc in self.c['projects']:
            self.add(title,size=10.1,leading=15,bold=True,gap=4)
            self.add(desc, size=self.body_size,leading=self.leading,gap=9)

    def papers(self):
        self.section(self.c['papers'])
        for p in PAPERS:
            top=self.y
            self.text(str(p['year']),M,top,35,size=8.5,leading=14,color=TEAL,bold=True)
            x=M+44
            width=CW-44
            title=self.link(p['title'], 'https://doi.org/'+p['doi'])
            self.y += self.text(title,x,top,width,size=9.0,leading=12.6,bold=True,raw=True)+2
            authors = escape(p['authors'].replace('**',''))
            for name in ('Miaohui Shi','施妙辉'):
                authors=authors.replace(name,f'<b>{name}</b>')
            self.y += self.text(authors,x,self.y,width,size=7.8,leading=11.3,color=MUTED,raw=True)+1
            self.y += self.text(p['venue'],x,self.y,width,size=8.0,leading=11.3,color=MUTED)+8

    def closing(self):
        self.section(self.c['patents'])
        patent_title = ('CN119987127B | 一种基于掩模版网格化区域的亚像素图像处理方法及系统'
                        if self.lang == 'zh' else
                        'CN119987127B | Subpixel image processing based on grid-partitioned mask regions')
        self.add(self.link(patent_title, 'https://patents.google.com/patent/CN119987127B/zh'),
                 raw=True,size=9.0,leading=13,bold=True,gap=3)
        self.add('共同发明人 | 2026-03-20 授权' if self.lang == 'zh' else
                 'Co-inventor | Granted 20 March 2026',size=8.2,leading=12,color=MUTED,gap=4)
        self.add(self.link('完整专利记录 / 8 项申请' if self.lang=='zh' else 'Full patent record / 8 applications',
                           BASE+('/zh/patents/' if self.lang=='zh' else '/patents/')),
                 raw=True,size=8.2,leading=12,gap=6)
        self.section(self.c['earlier'])
        for e in self.ui['earlier_entries']:
            self.add(e['period']+'  |  '+e['title'],size=8.2,leading=12,gap=3)
        self.section(self.c['interest'])
        self.add(self.c['interest_text'],size=8.8,leading=13,gap=0)

    def footer(self):
        print(f'{self.lang.upper()} page {self.page}: content bottom {self.y:.1f} pt / {H-48:.1f} pt')
        if self.y > H-48:
            raise ValueError('Page content collides with footer')
        self.line(H-36)
        self.text(self.c['foot'], top=H-30, size=7.0, leading=10, color=MUTED, measure=True)
        self.pdf.setFont('CV-Regular',7)
        self.pdf.setFillColor(MUTED)
        self.pdf.drawString(M, 21, clean(self.c['foot']))
        self.pdf.drawRightString(W-M, 21, f'0{self.page} / 02')

    def build(self):
        self.header()
        self.metrics()
        self.section(self.c['work'])
        for job in self.ui['employment_entries']:
            title = job['title'] + (' | ' + job['cv_role'] if job.get('cv_role') else '')
            self.job(job['period'], title, job.get('cv_organization', job['organization']),
                     job.get('cv_details', job['details']))
        self.education()
        self.skills()
        self.footer()
        self.pdf.showPage()
        self.page=2
        self.y=38
        self.header(compact=True)
        self.research()
        self.papers()
        self.closing()
        self.footer()
        self.pdf.save()
        print(self.path)


if __name__ == '__main__':
    for language in ('en','zh'):
        Resume(language).build()
    # Keep existing bookmarks and the legacy Chinese download valid.
    shutil.copyfile(ROOT/'files/Miaohui_Shi_CV_ZH.pdf', ROOT/'files/SMH_RESUME.pdf')
