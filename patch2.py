"""Patch 2: Add JS for timer, calendar, exam countdown, sync, switchScreen sidebar update, dashboard zone detail"""

with open('/home/claude/revenge-note.html', 'r') as f:
    html = f.read()

# Add JS functions before the INIT section
new_js = """
// ================================================================
// TIMER (Pomodoro)
// ================================================================
let timerSec=25*60,timerRunning=false,timerInterval=null;
const timerModes=[{label:'25分',sec:25*60},{label:'5分休',sec:5*60},{label:'50分',sec:50*60},{label:'10分休',sec:10*60}];
let timerModeIdx=0;
function updateTimerDisplay(){const m=Math.floor(timerSec/60),s=timerSec%60;document.getElementById('timerDisplay').textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')}
function toggleTimer(){if(timerRunning){clearInterval(timerInterval);timerRunning=false;document.getElementById('timerStartBtn').textContent='▶'}else{timerRunning=true;document.getElementById('timerStartBtn').textContent='⏸';timerInterval=setInterval(function(){timerSec--;if(timerSec<=0){clearInterval(timerInterval);timerRunning=false;document.getElementById('timerStartBtn').textContent='▶';alert('⏰ タイマー終了！')}updateTimerDisplay()},1000)}}
function resetTimer(){clearInterval(timerInterval);timerRunning=false;timerSec=timerModes[timerModeIdx].sec;updateTimerDisplay();document.getElementById('timerStartBtn').textContent='▶'}
function cycleTimerMode(){timerModeIdx=(timerModeIdx+1)%timerModes.length;timerSec=timerModes[timerModeIdx].sec;document.getElementById('timerModeBtn').textContent=timerModes[timerModeIdx].label;updateTimerDisplay();if(timerRunning){clearInterval(timerInterval);timerRunning=false;document.getElementById('timerStartBtn').textContent='▶'}}

// ================================================================
// CALENDAR
// ================================================================
let calMonth=new Date().getMonth(),calYear=new Date().getFullYear();
function renderCalendar(){
  var el=document.getElementById('calTitle');if(!el)return;
  el.textContent=calYear+'年'+(calMonth+1)+'月';
  var grid=document.getElementById('calGrid');
  var headers=['日','月','火','水','木','金','土'];
  var h=headers.map(function(x){return'<div class="cal-header">'+x+'</div>'}).join('');
  var first=new Date(calYear,calMonth,1);var startDay=first.getDay();
  var daysInMonth=new Date(calYear,calMonth+1,0).getDate();
  var daysInPrev=new Date(calYear,calMonth,0).getDate();
  var dayCounts={};
  DATA.sessionLog.forEach(function(s){dayCounts[s.date]=(dayCounts[s.date]||0)+(s.correct||0)+(s.wrong||0)+(s.hard||0)});
  DATA.problems.forEach(function(p){(p.history||[]).forEach(function(x){dayCounts[x.date]=(dayCounts[x.date]||0)+1})});
  var todayStr=today();
  for(var i=0;i<startDay;i++){h+='<div class="cal-day other-month">'+(daysInPrev-startDay+i+1)+'</div>'}
  for(var d=1;d<=daysInMonth;d++){
    var ds=calYear+'-'+String(calMonth+1).padStart(2,'0')+'-'+String(d).padStart(2,'0');
    var cnt=dayCounts[ds]||0;var cls='cal-day';
    if(ds===todayStr)cls+=' today';
    if(cnt>=5)cls+=' has-data-many';else if(cnt>0)cls+=' has-data';
    h+='<div class="'+cls+'" title="'+cnt+'問">'+d+'</div>';
  }
  var remain=7-(startDay+daysInMonth)%7;
  if(remain<7)for(var j=1;j<=remain;j++)h+='<div class="cal-day other-month">'+j+'</div>';
  grid.innerHTML=h;
}
function calNav(dir){calMonth+=dir;if(calMonth<0){calMonth=11;calYear--}if(calMonth>11){calMonth=0;calYear++}renderCalendar()}

// ================================================================
// EXAM COUNTDOWN
// ================================================================
function renderExamCountdown(){
  var el=document.getElementById('examCountdown');
  var badge=document.getElementById('countdownBadge');
  if(!el)return;
  if(DATA.settings.examDate){
    var diff=Math.ceil((new Date(DATA.settings.examDate)-new Date())/864e5);
    if(diff>0){el.style.display='';
      document.getElementById('examLabel').textContent=(DATA.settings.examName||'入試')+'まで';
      document.getElementById('examDays').textContent=diff;
      if(badge)badge.textContent=(DATA.settings.examName||'入試')+' あと'+diff+'日';
    }else{el.style.display='none';if(badge)badge.textContent=''}
  }else{el.style.display='none';if(badge)badge.textContent=''}
}
function saveExamGoal(){
  DATA.settings.examDate=document.getElementById('settingExamDate').value;
  DATA.settings.examName=document.getElementById('settingExamName').value;
  saveData(DATA);renderExamCountdown();
}

// ================================================================
// SHARE LINK SYNC
// ================================================================
function generateShareLink(){
  try{var json=JSON.stringify({problems:DATA.problems,settings:DATA.settings});
    var compressed=btoa(unescape(encodeURIComponent(json)));
    var url=location.origin+location.pathname+'#sync='+compressed;
    document.getElementById('shareLinkArea').style.display='';
    document.getElementById('shareLinkText').value=url;
  }catch(e){alert('データが大きすぎます。JSONエクスポートをご利用ください。')}
}
function importFromURL(){var h=location.hash;if(!h.startsWith('#sync=')){alert('共有リンクを開いてからこのボタンを押してください');return}
  try{var d=JSON.parse(decodeURIComponent(escape(atob(h.slice(6)))));
    if(d.problems){var added=0;d.problems.forEach(function(p){if(!DATA.problems.find(function(x){return x.id===p.id})){DATA.problems.push(p);added++}});
      if(d.settings)Object.assign(DATA.settings,d.settings);saveData(DATA);location.hash='';
      alert(added+'問を取り込みました');switchScreen('Today')}
  }catch(e){alert('リンクの読み込みに失敗しました')}}

// ================================================================
// DASHBOARD ZONE DETAIL
// ================================================================
var _zoneProbs={};
function showZoneDetail(zone,title){
  var panel=document.getElementById('zoneDetailPanel');if(!panel)return;
  panel.style.display='';
  document.getElementById('zoneDetailTitle').textContent=title+' の問題';
  var probs=_zoneProbs[zone]||[];
  document.getElementById('zoneDetailList').innerHTML=probs.length?probs.map(function(p){
    return'<div class="zone-detail-item"><strong>'+p.subject+'</strong> '+p.topic+' <span style="color:var(--text2);font-size:10px">'+(p.source||'')+' ・ '+(p.interval||0)+'日間隔</span></div>'
  }).join(''):'<div style="color:var(--text2);font-size:12px">なし</div>';
}
"""

html = html.replace('// ================================================================\n// INIT', new_js + '// ================================================================\n// INIT')

# Update renderToday to call renderExamCountdown and renderCalendar
old_render_today_end = "renderFreezeAlerts();\n}"
new_render_today_end = "renderFreezeAlerts();\n  renderExamCountdown();\n  renderCalendar();\n}"
html = html.replace(old_render_today_end, new_render_today_end, 1)

# Update renderSettings to load exam date
old_render_settings = "function renderSettings() {"
new_render_settings = """function renderSettings() {
  if(document.getElementById('settingExamDate')){
    document.getElementById('settingExamDate').value=DATA.settings.examDate||'';
    document.getElementById('settingExamName').value=DATA.settings.examName||'';
  }"""
html = html.replace(old_render_settings, new_render_settings, 1)

# Update switchScreen to also update sidebar nav items
old_switch = "document.querySelectorAll('.nav-item').forEach("
# Add sidebar update
html = html.replace(
    "document.querySelectorAll('.nav-item').forEach(",
    "document.querySelectorAll('.nav-item,.s-item').forEach("
)

# Update renderDashboard to store zone problems and show zone detail panel
# Add zone detail panel HTML to dashboard screen
if 'zoneDetailPanel' not in html:
    html = html.replace(
        '<div class="subject-breakdown"',
        '<div id="zoneDetailPanel" class="card" style="display:none;margin-bottom:12px;background:var(--surface);border-radius:var(--radius);padding:16px;border:1px solid var(--border)"><h3 id="zoneDetailTitle" style="font-size:13px;font-weight:700;margin-bottom:8px"></h3><div class="zone-detail" id="zoneDetailList"></div></div>\n  <div class="subject-breakdown"'
    )

# Make zone cards clickable in renderDashboard
html = html.replace(
    """<div class="zone-card zone-priority"><div class="num">${zones.priority}</div><div class="label">🔴 最優先（できない×高頻出）</div></div>""",
    """<div class="zone-card zone-priority" onclick="showZoneDetail('priority','🔴 最優先')" style="cursor:pointer"><div class="num">${zones.priority}</div><div class="label">🔴 最優先</div></div>"""
)
html = html.replace(
    """<div class="zone-card zone-graduated"><div class="num">${zones.graduated}</div><div class="label">🟢 定着済み</div></div>""",
    """<div class="zone-card zone-graduated" onclick="showZoneDetail('graduated','🟢 定着済')" style="cursor:pointer"><div class="num">${zones.graduated}</div><div class="label">🟢 定着済み</div></div>"""
)
html = html.replace(
    """<div class="zone-card zone-frozen"><div class="num">${zones.frozen}</div><div class="label">❄️ 凍結中</div></div>""",
    """<div class="zone-card zone-frozen" onclick="showZoneDetail('frozen','❄️ 凍結')" style="cursor:pointer"><div class="num">${zones.frozen}</div><div class="label">❄️ 凍結中</div></div>"""
)
html = html.replace(
    """<div class="zone-card zone-review"><div class="num">${zones.review + zones.discard}</div><div class="label">🟡 復習待ち・後回し</div></div>""",
    """<div class="zone-card zone-review" onclick="showZoneDetail('review','🟡 復習待ち')" style="cursor:pointer"><div class="num">${zones.review + zones.discard}</div><div class="label">🟡 復習待ち</div></div>"""
)

# Store zone problems in renderDashboard
html = html.replace(
    "DATA.problems.forEach(p => { const z = classifyZone(p); zones[z] = (zones[z]||0) + 1; });",
    "_zoneProbs={priority:[],review:[],graduated:[],frozen:[],discard:[]};\n  DATA.problems.forEach(p => { const z = classifyZone(p); zones[z] = (zones[z]||0) + 1; (_zoneProbs[z]=_zoneProbs[z]||[]).push(p); });"
)

# Add subject filter dropdown to dashboard
if 'dashSubjectFilter' not in html:
    html = html.replace(
        '<div class="zone-grid" id="zoneGrid"></div>',
        """<div class="filter-row" style="margin-bottom:8px"><select class="form-select" id="dashSubjectFilter" onchange="renderDashboard()" style="width:auto;padding:6px 12px;font-size:12px"><option value="">全教科</option></select></div>
  <div class="zone-grid" id="zoneGrid"></div>"""
    )

# Add init timer display
html = html.replace('renderToday();\n</script>', 'updateTimerDisplay();\nif(location.hash.startsWith("#sync="))importFromURL();\nrenderToday();\n</script>')

with open('/home/claude/revenge-note.html', 'w') as f:
    f.write(html)
print("Patch 2 applied: JS for timer, calendar, exam, sync, zone detail")
