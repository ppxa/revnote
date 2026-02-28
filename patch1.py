"""Patch 1: Add timer bar, exam countdown, calendar, sidebar nav, landscape layout"""
import re

with open('/home/claude/revenge-note.html', 'r') as f:
    html = f.read()

# 1. Add timer bar CSS after --shadow line
timer_css = """
/* TIMER BAR */
.timer-bar{position:fixed;top:0;left:0;right:0;height:44px;background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 16px;z-index:150;gap:8px}
.timer-display{font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:700;min-width:72px;text-align:center}
.timer-btn{padding:4px 12px;border-radius:6px;font-size:11px;border:1px solid var(--border);background:var(--surface2);color:var(--text2);cursor:pointer;font-family:inherit}
.timer-btn.active{border-color:var(--accent);color:var(--accent)}
.countdown-badge{font-size:11px;color:var(--warning);font-weight:700;white-space:nowrap}
/* SIDEBAR NAV */
.nav-side{display:none;position:fixed;top:0;left:0;bottom:0;width:72px;background:var(--surface);border-right:1px solid var(--border);flex-direction:column;align-items:center;padding:12px 0;gap:4px;z-index:200;overflow-y:auto}
.nav-side .s-item{display:flex;flex-direction:column;align-items:center;padding:10px 4px;gap:2px;color:var(--text2);font-size:9px;font-weight:500;cursor:pointer;border:none;background:none;border-radius:10px;width:64px}
.nav-side .s-item.active{color:var(--accent);background:rgba(108,99,255,.1)}
.nav-side .s-item span{font-size:20px}
.nav-side .s-logo{font-size:14px;font-weight:900;color:var(--accent);margin-bottom:8px;padding:8px 0}
/* CALENDAR */
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;text-align:center}
.cal-header{font-size:10px;color:var(--text2);padding:4px}
.cal-day{font-size:11px;padding:6px 2px;border-radius:6px;position:relative}
.cal-day.today{font-weight:900;color:var(--accent)}
.cal-day.has-data::after{content:'';position:absolute;bottom:2px;left:50%;transform:translateX(-50%);width:4px;height:4px;border-radius:50%;background:var(--success)}
.cal-day.has-data-many::after{background:var(--accent);width:6px;height:6px}
.cal-day.other-month{opacity:.3}
/* Zone detail */
.zone-detail{max-height:200px;overflow-y:auto;margin-top:8px}
.zone-detail-item{font-size:12px;padding:4px 0;border-bottom:1px solid var(--border);color:var(--text2)}
"""
html = html.replace('--shadow: 0 4px 24px rgba(0,0,0,0.3);\n}', '--shadow: 0 4px 24px rgba(0,0,0,0.3);\n}' + timer_css)

# 2. Fix landscape media query to include sidebar 
old_landscape = """@media(min-width:900px){
  :root{--nav-w:72px}"""
new_landscape_start = """@media(min-width:1024px){"""
# Replace the existing landscape query
html = re.sub(r'@media\s*\(min-width:\s*900px\s*\)', '@media(min-width:1024px)', html)

# Add sidebar display and margin in landscape
old_landscape_block = """@media(min-width:1024px) {
  .screen { max-width: 1200px; padding-left: 24px; padding-right: 24px; }"""
new_landscape_block = """@media(min-width:1024px) {
  .nav-bottom{display:none!important}
  .nav-side{display:flex!important}
  .timer-bar{left:72px}
  .screen { max-width: 1200px; padding-left: 24px; padding-right: 24px; margin-left:72px; padding-top:56px; }"""
html = html.replace(old_landscape_block, new_landscape_block)

# 3. Adjust screen padding for timer bar
html = html.replace('.screen { padding-top: env(safe-area-inset-top, 16px); }', '.screen { padding-top: max(env(safe-area-inset-top, 16px), 52px); }')

# 4. Add timer bar HTML before body content
timer_html = """
<!-- TIMER BAR -->
<div class="timer-bar">
  <div style="display:flex;align-items:center;gap:8px">
    <div class="timer-display" id="timerDisplay">25:00</div>
    <button class="timer-btn" id="timerStartBtn" onclick="toggleTimer()">▶</button>
    <button class="timer-btn" onclick="resetTimer()">↺</button>
    <button class="timer-btn" id="timerModeBtn" onclick="cycleTimerMode()">25分</button>
  </div>
  <div id="countdownBadge" class="countdown-badge"></div>
</div>

<!-- SIDEBAR NAV (landscape) -->
<nav class="nav-side" id="navSide">
  <div class="s-logo">rn</div>
  <button class="s-item active" data-screen="Today" onclick="switchScreen('Today')"><span>⚔️</span>今日</button>
  <button class="s-item" data-screen="Add" onclick="switchScreen('Add')"><span>📸</span>登録</button>
  <button class="s-item" data-screen="List" onclick="switchScreen('List')"><span>📚</span>一覧</button>
  <button class="s-item" data-screen="Dash" onclick="switchScreen('Dash')"><span>📊</span>分析</button>
  <button class="s-item" data-screen="Settings" onclick="switchScreen('Settings')"><span>⚙️</span>設定</button>
</nav>
"""
html = html.replace('<body>\n', '<body>\n' + timer_html)

# 5. Add exam countdown + calendar to Today screen (before streak bar)
exam_html = """  <!-- Exam Countdown -->
  <div id="examCountdown" class="card" style="display:none;text-align:center;background:linear-gradient(135deg,rgba(108,99,255,.08),rgba(78,205,196,.08));margin-bottom:12px;border-radius:var(--radius);padding:16px;border:1px solid var(--border)">
    <div style="font-size:11px;color:var(--text2)" id="examLabel"></div>
    <div style="font-size:36px;font-weight:900;background:var(--grad1);-webkit-background-clip:text;-webkit-text-fill-color:transparent" id="examDays"></div>
    <div style="font-size:12px;color:var(--text2)">日</div>
  </div>
"""
html = html.replace('  <div class="streak-bar">', exam_html + '  <div class="streak-bar">')

# 6. Add calendar after completionView
calendar_html = """
  <!-- Calendar -->
  <div class="card" style="margin-top:12px;background:var(--surface);border-radius:var(--radius);padding:16px;border:1px solid var(--border)">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
      <button class="sp-btn" onclick="calNav(-1)">◀</button>
      <h3 id="calTitle" style="font-size:13px;font-weight:700"></h3>
      <button class="sp-btn" onclick="calNav(1)">▶</button>
    </div>
    <div class="cal-grid" id="calGrid"></div>
  </div>
"""
html = html.replace('</div>\n\n<!-- === SCREEN: ADD === -->', calendar_html + '</div>\n\n<!-- === SCREEN: ADD === -->')

# 7. Add exam goal settings 
exam_settings = """  <div class="setting-card"><h3>🎯 入試目標</h3>
    <div class="setting-row"><span class="setting-label">入試日</span><input type="date" class="form-input" id="settingExamDate" onchange="saveExamGoal()" style="width:auto"></div>
    <div class="setting-row" style="margin-top:8px"><span class="setting-label">目標校</span><input class="form-input" id="settingExamName" onchange="saveExamGoal()" placeholder="例: 開成中学" style="width:180px"></div>
  </div>
"""
html = html.replace('  <div class="setting-card">\n    <h3>学校段階</h3>', exam_settings + '  <div class="setting-card">\n    <h3>学校段階</h3>')

# 8. Add sync section to settings
sync_html = """  <div class="setting-card"><h3>🔄 親子同期</h3>
    <div style="font-size:12px;color:var(--text2);line-height:1.7;margin-bottom:10px">
      親のiPadで登録 → エクスポート → 子のiPadでインポート<br>
      <strong style="color:var(--accent)">共有リンク:</strong> URLにデータを埋め込み。サーバー不要で同期。
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
      <button class="btn-export" onclick="generateShareLink()" style="border-color:var(--accent);color:var(--accent)">🔗 共有リンク生成</button>
      <button class="btn-export" onclick="importFromURL()">📲 リンクから取込</button>
    </div>
    <div id="shareLinkArea" style="display:none;margin-top:8px">
      <textarea id="shareLinkText" class="form-textarea" style="min-height:40px;font-size:10px" readonly></textarea>
      <button class="sp-btn" onclick="navigator.clipboard.writeText(document.getElementById('shareLinkText').value);alert('コピーしました')" style="margin-top:4px">コピー</button>
    </div>
  </div>
"""
html = html.replace('  <div class="setting-card">\n    <h3>データ管理</h3>', sync_html + '  <div class="setting-card">\n    <h3>データ管理</h3>')

with open('/home/claude/revenge-note.html', 'w') as f:
    f.write(html)
print("Patch 1 applied: timer, sidebar, calendar, exam countdown, sync settings")
