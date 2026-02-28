#!/usr/bin/env python3
"""Phase 1 patch: Transform revnote from flashcard app to true revenge note app."""

with open('/home/claude/revenge-note.html') as f:
    html = f.read()

# ============================================================
# 1. Change sidebar "登録" to "間違い登録"
# ============================================================
html = html.replace(
    '<span>📸</span>登録',
    '<span>📸</span>間違い登録'
)

# ============================================================
# 2. Add parent/child mode toggle to timer bar area
# ============================================================
html = html.replace(
    '<div id="countdownBadge" class="countdown-badge"></div>\n</div>',
    '<div id="countdownBadge" class="countdown-badge"></div>\n'
    '<button id="modeToggleBtn" onclick="toggleParentChild()" style="font-size:10px;padding:3px 8px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text2);cursor:pointer;font-weight:600;white-space:nowrap">👦 子ども</button>\n'
    '</div>'
)

# ============================================================
# 3. Add Parent Dashboard screen to HTML (after screenDash)
# ============================================================
parent_dash_html = '''
<!-- PARENT DASHBOARD -->
<div class="screen" id="screenParent" style="display:none">
  <div style="padding:16px;max-width:800px;margin:0 auto">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div style="font-size:18px;font-weight:800">👨‍👩‍👧 保護者ダッシュボード</div>
      <button onclick="toggleParentChild()" style="font-size:12px;padding:6px 14px;border-radius:8px;background:var(--accent);color:#fff;border:none;font-weight:700;cursor:pointer">👦 子ども画面へ</button>
    </div>

    <!-- Today's Activity Timeline -->
    <div class="card" style="background:var(--surface);border-radius:var(--radius);padding:16px;border:1px solid var(--border);margin-bottom:14px">
      <div style="font-size:14px;font-weight:800;margin-bottom:12px">📋 今日の学習ログ</div>
      <div id="parentTimeline"></div>
    </div>

    <!-- Weakness Heatmap -->
    <div class="card" style="background:var(--surface);border-radius:var(--radius);padding:16px;border:1px solid var(--border);margin-bottom:14px">
      <div style="font-size:14px;font-weight:800;margin-bottom:12px">🎯 弱点分析（単元別）</div>
      <div id="parentWeakness"></div>
    </div>

    <!-- Mistake Pattern -->
    <div class="card" style="background:var(--surface);border-radius:var(--radius);padding:16px;border:1px solid var(--border);margin-bottom:14px">
      <div style="font-size:14px;font-weight:800;margin-bottom:12px">🔍 間違いパターン</div>
      <div id="parentMistakePattern"></div>
    </div>

    <!-- Repeat Offenders -->
    <div class="card" style="background:var(--surface);border-radius:var(--radius);padding:16px;border:1px solid var(--border);margin-bottom:14px">
      <div style="font-size:14px;font-weight:800;margin-bottom:12px">⚠️ 繰り返し間違える問題</div>
      <div id="parentRepeatErrors"></div>
    </div>

    <!-- Weekly Stats -->
    <div class="card" style="background:var(--surface);border-radius:var(--radius);padding:16px;border:1px solid var(--border);margin-bottom:14px">
      <div style="font-size:14px;font-weight:800;margin-bottom:12px">📊 週間サマリー</div>
      <div id="parentWeekly"></div>
    </div>
  </div>
</div>
'''

html = html.replace(
    '<!-- PARENT DASHBOARD -->',
    parent_dash_html
) if '<!-- PARENT DASHBOARD -->' in html else html.replace(
    '<div class="screen" id="screenSettings"',
    parent_dash_html + '\n<div class="screen" id="screenSettings"'
)

# ============================================================
# 4. Add mistake reason selector to review answer UI
#    (enhance existing mistakeReason)
# ============================================================
# Find the existing review answer buttons area and add mistake reason UI
old_mistake = '''  if (mistakeReason) entry.mistakeReason = mistakeReason;'''
new_mistake = '''  if (mistakeReason) entry.mistakeReason = mistakeReason;
  // Save timestamp for parent timeline
  entry.timestamp = new Date().toISOString();'''
html = html.replace(old_mistake, new_mistake)

# ============================================================
# 5. Save scratchpad strokes per problem
# ============================================================
# After answer submission, save strokes to problem
old_push = '''  real.history.push(entry);
  if (memo) real.lastMemo = memo;'''
new_push = '''  real.history.push(entry);
  if (memo) real.lastMemo = memo;
  // Save scratchpad drawing data for this problem
  if (window._spStrokes && window._spStrokes.length > 0) {
    real.lastDrawing = JSON.parse(JSON.stringify(window._spStrokes));
  }'''
html = html.replace(old_push, new_push)

# ============================================================
# 6. Add parent/child mode toggle + parent dashboard render functions
# ============================================================
# Insert before the calendar page section
calendar_marker = '// ================================================================\n// CALENDAR PAGE'
parent_functions = '''// ================================================================
// PARENT/CHILD MODE
// ================================================================
function toggleParentChild() {
  DATA.settings.mode = (DATA.settings.mode === 'parent') ? 'child' : 'parent';
  saveData(DATA);
  applyMode();
}

function applyMode() {
  var mode = DATA.settings.mode || 'child';
  var btn = document.getElementById('modeToggleBtn');
  if (btn) {
    if (mode === 'parent') {
      btn.innerHTML = '👨‍👩‍👧 保護者';
      btn.style.background = 'var(--accent)';
      btn.style.color = '#fff';
      btn.style.border = 'none';
    } else {
      btn.innerHTML = '👦 子ども';
      btn.style.background = 'var(--surface)';
      btn.style.color = 'var(--text2)';
      btn.style.border = '1px solid var(--border)';
    }
  }
  // Show/hide parent dashboard
  var parentScreen = document.getElementById('screenParent');
  if (mode === 'parent' && parentScreen) {
    switchScreen('Parent');
    renderParentDash();
  }
}

function renderParentDash() {
  renderParentTimeline();
  renderParentWeakness();
  renderParentMistakePattern();
  renderParentRepeatErrors();
  renderParentWeekly();
}

function renderParentTimeline() {
  var el = document.getElementById('parentTimeline');
  if (!el) return;
  var t = today();
  var entries = [];
  DATA.problems.forEach(function(p) {
    (p.history || []).forEach(function(h) {
      if (h.date === t) {
        entries.push({
          subject: p.subject,
          topic: p.topic,
          result: h.result,
          quality: h.quality,
          mistakeReason: h.mistakeReason,
          timeSpent: h.timeSpent,
          timestamp: h.timestamp || (t + 'T12:00:00'),
          memo: h.memo
        });
      }
    });
  });
  entries.sort(function(a, b) { return a.timestamp > b.timestamp ? 1 : -1; });

  if (entries.length === 0) {
    el.innerHTML = '<div style="color:var(--text2);font-size:13px;text-align:center;padding:20px">今日はまだ学習記録がありません</div>';
    return;
  }

  var html = '<div style="display:flex;flex-direction:column;gap:6px">';
  entries.forEach(function(e) {
    var icon = e.result === 'correct' ? '✅' : e.result === 'hard' ? '△' : '❌';
    var color = e.result === 'correct' ? 'var(--success)' : e.result === 'hard' ? 'var(--warning)' : 'var(--danger)';
    var time = e.timestamp ? new Date(e.timestamp).toLocaleTimeString('ja-JP', {hour:'2-digit',minute:'2-digit'}) : '';
    var spent = e.timeSpent ? Math.round(e.timeSpent / 60) + '分' : '';
    var reason = e.mistakeReason ? ' (' + e.mistakeReason + ')' : '';
    html += '<div style="display:flex;align-items:center;gap:8px;padding:6px 10px;background:var(--surface2);border-radius:8px;font-size:12px">';
    html += '<span style="color:var(--text2);min-width:40px">' + time + '</span>';
    html += '<span style="font-size:16px">' + icon + '</span>';
    html += '<span style="font-weight:600">' + (e.subject || '') + '</span>';
    html += '<span style="color:var(--text2);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + (e.topic || '') + '</span>';
    if (spent) html += '<span style="color:var(--accent);font-size:10px">' + spent + '</span>';
    if (reason) html += '<span style="color:var(--danger);font-size:10px">' + reason + '</span>';
    html += '</div>';
  });
  html += '</div>';
  html += '<div style="margin-top:8px;font-size:11px;color:var(--text2)">合計 ' + entries.length + '問 / ';
  var correct = entries.filter(function(e){return e.result==='correct'}).length;
  html += '正解 ' + correct + '問 (' + (entries.length > 0 ? Math.round(correct/entries.length*100) : 0) + '%)</div>';
  el.innerHTML = html;
}

function renderParentWeakness() {
  var el = document.getElementById('parentWeakness');
  if (!el) return;
  // Group by subject + topic
  var topics = {};
  DATA.problems.forEach(function(p) {
    var key = (p.subject || '?') + '：' + (p.topic || '未分類');
    if (!topics[key]) topics[key] = { total: 0, correct: 0, subject: p.subject };
    (p.history || []).forEach(function(h) {
      topics[key].total++;
      if (h.result === 'correct') topics[key].correct++;
    });
  });

  var sorted = Object.entries(topics)
    .filter(function(e) { return e[1].total >= 2; })
    .sort(function(a, b) {
      var rateA = a[1].total > 0 ? a[1].correct / a[1].total : 1;
      var rateB = b[1].total > 0 ? b[1].correct / b[1].total : 1;
      return rateA - rateB;
    });

  if (sorted.length === 0) {
    el.innerHTML = '<div style="color:var(--text2);font-size:13px;text-align:center;padding:20px">学習データが蓄積されると弱点が表示されます</div>';
    return;
  }

  var html = '<div style="display:flex;flex-direction:column;gap:4px">';
  sorted.slice(0, 15).forEach(function(item) {
    var name = item[0];
    var d = item[1];
    var rate = d.total > 0 ? Math.round(d.correct / d.total * 100) : 0;
    var color = rate >= 70 ? 'var(--success)' : rate >= 40 ? 'var(--warning)' : 'var(--danger)';
    html += '<div style="display:flex;align-items:center;gap:6px;font-size:12px">';
    html += '<span style="min-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + name + '</span>';
    html += '<div style="flex:1;height:14px;background:var(--surface2);border-radius:4px;overflow:hidden;position:relative">';
    html += '<div style="height:100%;width:' + rate + '%;background:' + color + ';border-radius:4px;transition:width .3s"></div>';
    html += '</div>';
    html += '<span style="min-width:55px;text-align:right;font-weight:600;color:' + color + '">' + rate + '% <span style="color:var(--text2);font-weight:400">(' + d.correct + '/' + d.total + ')</span></span>';
    html += '</div>';
  });
  html += '</div>';
  el.innerHTML = html;
}

function renderParentMistakePattern() {
  var el = document.getElementById('parentMistakePattern');
  if (!el) return;
  var reasons = {};
  DATA.problems.forEach(function(p) {
    (p.history || []).forEach(function(h) {
      if (h.result === 'incorrect' && h.mistakeReason) {
        reasons[h.mistakeReason] = (reasons[h.mistakeReason] || 0) + 1;
      }
    });
  });

  var total = Object.values(reasons).reduce(function(s, v) { return s + v; }, 0);
  if (total === 0) {
    el.innerHTML = '<div style="color:var(--text2);font-size:13px;text-align:center;padding:20px">間違い理由が記録されると分析が表示されます</div>';
    return;
  }

  var sorted = Object.entries(reasons).sort(function(a, b) { return b[1] - a[1]; });
  var colors = {'ケアレスミス':'#f39c12','知識不足':'#e74c3c','時間切れ':'#3498db','解法わからず':'#9b59b6','問題の読み違い':'#e67e22'};
  var html = '<div style="display:flex;flex-wrap:wrap;gap:8px">';
  sorted.forEach(function(item) {
    var pct = Math.round(item[1] / total * 100);
    var c = colors[item[0]] || 'var(--text2)';
    html += '<div style="background:' + c + '22;border:1px solid ' + c + '44;border-radius:8px;padding:8px 12px;text-align:center;min-width:80px">';
    html += '<div style="font-size:20px;font-weight:900;color:' + c + '">' + pct + '%</div>';
    html += '<div style="font-size:10px;color:var(--text1);font-weight:600">' + item[0] + '</div>';
    html += '<div style="font-size:9px;color:var(--text2)">' + item[1] + '回</div>';
    html += '</div>';
  });
  html += '</div>';
  el.innerHTML = html;
}

function renderParentRepeatErrors() {
  var el = document.getElementById('parentRepeatErrors');
  if (!el) return;
  var repeats = DATA.problems.filter(function(p) {
    var fails = (p.history || []).filter(function(h) { return h.result === 'incorrect'; }).length;
    return fails >= 2;
  }).sort(function(a, b) {
    var af = (a.history || []).filter(function(h) { return h.result === 'incorrect'; }).length;
    var bf = (b.history || []).filter(function(h) { return h.result === 'incorrect'; }).length;
    return bf - af;
  });

  if (repeats.length === 0) {
    el.innerHTML = '<div style="color:var(--text2);font-size:13px;text-align:center;padding:20px">繰り返し間違える問題はまだありません 👍</div>';
    return;
  }

  var html = '<div style="display:flex;flex-direction:column;gap:4px">';
  repeats.slice(0, 10).forEach(function(p) {
    var fails = (p.history || []).filter(function(h) { return h.result === 'incorrect'; }).length;
    var total = (p.history || []).length;
    html += '<div style="display:flex;align-items:center;gap:6px;padding:6px 10px;background:rgba(231,76,60,.08);border-radius:8px;font-size:12px">';
    html += '<span style="color:var(--danger);font-weight:800;min-width:28px">×' + fails + '</span>';
    html += '<span style="font-weight:600">' + (p.subject || '') + '</span>';
    html += '<span style="color:var(--text2);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + (p.topic || '') + '</span>';
    html += '<span style="font-size:10px;color:var(--text2)">' + total + '回中</span>';
    html += '</div>';
  });
  html += '</div>';
  el.innerHTML = html;
}

function renderParentWeekly() {
  var el = document.getElementById('parentWeekly');
  if (!el) return;
  // Last 7 days
  var days = [];
  for (var i = 6; i >= 0; i--) {
    var d = new Date(); d.setDate(d.getDate() - i);
    var ds = d.toISOString().split('T')[0];
    var count = 0, correct = 0, totalTime = 0;
    DATA.problems.forEach(function(p) {
      (p.history || []).forEach(function(h) {
        if (h.date === ds) {
          count++;
          if (h.result === 'correct') correct++;
          if (h.timeSpent) totalTime += h.timeSpent;
        }
      });
    });
    days.push({
      label: (d.getMonth()+1) + '/' + d.getDate(),
      dow: ['日','月','火','水','木','金','土'][d.getDay()],
      count: count,
      correct: correct,
      minutes: Math.round(totalTime / 60)
    });
  }

  var html = '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;text-align:center">';
  days.forEach(function(d) {
    var bg = d.count === 0 ? 'var(--surface2)' : d.count >= 10 ? 'rgba(108,99,255,.2)' : 'rgba(108,99,255,.08)';
    var rate = d.count > 0 ? Math.round(d.correct / d.count * 100) : 0;
    var rateColor = rate >= 70 ? 'var(--success)' : rate >= 40 ? 'var(--warning)' : d.count > 0 ? 'var(--danger)' : 'var(--text2)';
    html += '<div style="background:' + bg + ';border-radius:8px;padding:8px 4px">';
    html += '<div style="font-size:9px;color:var(--text2)">' + d.label + '(' + d.dow + ')</div>';
    html += '<div style="font-size:18px;font-weight:900;color:var(--text1)">' + d.count + '</div>';
    html += '<div style="font-size:9px;color:var(--text2)">問</div>';
    if (d.count > 0) {
      html += '<div style="font-size:10px;font-weight:700;color:' + rateColor + '">' + rate + '%</div>';
      if (d.minutes > 0) html += '<div style="font-size:8px;color:var(--text2)">' + d.minutes + '分</div>';
    }
    html += '</div>';
  });
  html += '</div>';

  // Weekly total
  var wTotal = days.reduce(function(s,d){return s+d.count},0);
  var wCorrect = days.reduce(function(s,d){return s+d.correct},0);
  var wMin = days.reduce(function(s,d){return s+d.minutes},0);
  html += '<div style="margin-top:8px;font-size:12px;color:var(--text2);text-align:center">';
  html += '週計: ' + wTotal + '問 / 正答率 ' + (wTotal>0?Math.round(wCorrect/wTotal*100):0) + '% / 学習時間 ' + wMin + '分';
  html += '</div>';
  el.innerHTML = html;
}

// ================================================================
// RESTORE DRAWING on card show
// ================================================================
function restoreProblemDrawing(problem) {
  if (problem && problem.lastDrawing && problem.lastDrawing.length > 0) {
    window._spStrokes = JSON.parse(JSON.stringify(problem.lastDrawing));
    var c = document.getElementById('scratchpadCanvas');
    if (c && c.getContext) {
      var ctx = c.getContext('2d');
      ctx.globalCompositeOperation = 'source-over';
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--canvas-bg').trim() || '#f5f5f5';
      ctx.fillRect(0, 0, c.width, c.height);
      drawProblemImageOnCanvas();
      _spStrokes.forEach(function(stroke) {
        ctx.globalCompositeOperation = stroke.erasing ? 'destination-out' : 'source-over';
        ctx.strokeStyle = stroke.erasing ? 'rgba(0,0,0,1)' : stroke.color;
        ctx.lineWidth = stroke.erasing ? stroke.width * 3 : stroke.width;
        ctx.lineCap = 'round'; ctx.lineJoin = 'round';
        ctx.beginPath();
        stroke.points.forEach(function(p, i) { if (i === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y); });
        ctx.stroke();
      });
      ctx.globalCompositeOperation = 'source-over';
    }
  }
}

''' + calendar_marker

html = html.replace(calendar_marker, parent_functions)

# ============================================================
# 7. Add 'Parent' to screen list
# ============================================================
html = html.replace(
    "var screens = ['Today','Add','List','Calendar','Dash','Settings'];",
    "var screens = ['Today','Add','List','Calendar','Dash','Parent','Settings'];"
)

# ============================================================
# 8. Add mistake reason dropdown to Add screen
# ============================================================
# Add source presets and mistake reason to add form
old_source = '''source: document.getElementById('addSource').value.trim(),'''
new_source = '''source: (document.getElementById('addSourcePreset').value || '') + ' ' + document.getElementById('addSource').value.trim(),'''
html = html.replace(old_source, new_source) if 'addSourcePreset' not in html else html

# ============================================================
# 9. Enhanced hand-feel review display showing past attempts
# ============================================================
# Add to showCard to display history dots
old_showcard_memo = '''  // Review memo'''
new_showcard_memo = '''  // Show past attempt history as dots
  var pHist = p.history || [];
  if (pHist.length > 0) {
    var dots = pHist.slice(-8).map(function(h) {
      if (h.result === 'correct') return '<span style="color:var(--success)">◎</span>';
      if (h.result === 'hard') return '<span style="color:var(--warning)">△</span>';
      return '<span style="color:var(--danger)">×</span>';
    }).join(' ');
    document.getElementById('answerZone').insertAdjacentHTML('beforeend',
      '<div style="font-size:12px;margin-top:8px;color:var(--text2)">過去の結果: ' + dots + ' (' + pHist.length + '回目)</div>');
  }

  // Review memo'''
html = html.replace(old_showcard_memo, new_showcard_memo)

# ============================================================
# 10. Call applyMode on init
# ============================================================
old_init_end = '''renderExamCountdown();'''
new_init_end = '''renderExamCountdown();
applyMode();'''
html = html.replace(old_init_end, new_init_end, 1)

# ============================================================
# 11. Update version
# ============================================================
html = html.replace('v3.8', 'v4.0')

with open('/home/claude/revenge-note.html', 'w') as f:
    f.write(html)

print(f"Phase 1 patch applied. {html.count(chr(10))} lines")
