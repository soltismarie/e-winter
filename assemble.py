import re

with open("welcome.html", encoding="utf-8") as f:
    html = f.read()

with open("hromada_embedded.json", encoding="utf-8") as f:
    embedded_json = f.read()

# 1. wire the "Розпочати" button to the new input screen instead of the toast
html = html.replace('onclick="notReady()"', 'onclick="showInput()"')

# 2. remove the now-unused notReady() function
html = re.sub(
    r"\n  function notReady\(\)\{.*?\n  \}\n",
    "\n",
    html,
    flags=re.DOTALL,
)

NEW_CSS = """
  /* ---------- Screen 3: search ---------- */
  .search-wrap{position:relative;}
  .search-input{width:100%;font-size:17px;font-family:'IBM Plex Sans',sans-serif;padding:14px 16px;border-radius:12px;border:1px solid var(--border);background:var(--surface);color:var(--ink);}
  .search-input:focus{outline:2px solid var(--brand);outline-offset:2px;}
  .search-results{margin-top:10px;display:flex;flex-direction:column;gap:2px;}
  .result-row{padding:11px 14px;border-radius:9px;cursor:pointer;display:flex;justify-content:space-between;gap:10px;align-items:center;}
  .result-row:hover{background:var(--surface-2);}
  .result-name{font-weight:600;font-size:14.5px;}
  .result-meta{font-size:12px;color:var(--ink-muted);white-space:nowrap;}
  .result-empty{font-size:13.5px;color:var(--ink-muted);padding:10px 4px;}

  /* ---------- Screen 4: dashboard ---------- */
  .tag{display:inline-block;font-size:12px;font-weight:600;padding:5px 12px;border-radius:999px;font-family:'IBM Plex Mono',monospace;}
  .tag-safe{background:var(--safe-soft);color:var(--safe);}
  .tag-mid{background:var(--mid-soft);color:var(--mid);}
  .tag-bad{background:var(--bad-soft);color:var(--bad);}

  .dash-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;border-bottom:1px solid var(--border);padding-bottom:20px;margin-bottom:6px;}
  .dash-score{text-align:right;}
  .dash-score-num{font-family:'IBM Plex Mono',monospace;font-size:34px;font-weight:600;font-variant-numeric:tabular-nums;line-height:1;margin-bottom:8px;}
  .dash-score-num.tier-safe{color:var(--safe);}
  .dash-score-num.tier-mid{color:var(--mid);}
  .dash-score-num.tier-bad{color:var(--bad);}

  .meters{background:var(--surface);border:1px solid var(--border);border-radius:14px;box-shadow:var(--shadow);padding:18px 22px;margin:24px 0;}
  .meter-row{display:grid;grid-template-columns:160px 1fr 130px;align-items:center;gap:14px;padding:9px 0;}
  .meter-label{font-size:13px;color:var(--ink-muted);}
  .meter-track{height:8px;border-radius:5px;background:var(--surface-2);overflow:hidden;}
  .meter-fill{height:100%;border-radius:5px;background:var(--brand);}
  .meter-val{font-family:'IBM Plex Mono',monospace;font-size:12px;text-align:right;font-variant-numeric:tabular-nums;color:var(--ink-muted);}

  .fac-note{font-size:13px;color:var(--ink-muted);background:var(--surface-2);border-radius:10px;padding:12px 16px;margin:18px 0;}

  .advice-box{border-radius:14px;padding:18px 22px;font-size:14.5px;margin:20px 0;border:1px solid;}
  .advice-box.tier-safe-box{background:var(--safe-soft);border-color:var(--safe);}
  .advice-box.tier-mid-box{background:var(--mid-soft);border-color:var(--mid);}
  .advice-box.tier-bad-box{background:var(--bad-soft);border-color:var(--bad);}
  .advice-box p{margin:0;}

  .reco-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-bottom:10px;}
  .reco-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:14px 16px;box-shadow:var(--shadow);}
  .reco-name{font-family:'Spectral',Georgia,serif;font-weight:600;font-size:15px;margin-bottom:4px;}
  .reco-meta{font-size:12px;color:var(--ink-muted);margin-bottom:8px;}
  .reco-score{font-family:'IBM Plex Mono',monospace;font-size:13px;color:var(--safe);font-weight:600;}

  .next-caveat{font-size:12.5px;color:var(--ink-muted);border-top:1px solid var(--border);padding-top:16px;margin-top:30px;}

  @media (max-width:700px){
    .meter-row{grid-template-columns:120px 1fr 80px;gap:8px;}
    .reco-list{grid-template-columns:1fr;}
    .dash-head{flex-direction:column;align-items:flex-start;}
    .dash-score{text-align:left;}
  }
</style>"""

html = html.replace("</style>", NEW_CSS, 1)

NEW_SECTIONS = """
<section id="screen-input" hidden>
  <div class="narrator-bar">
    <div class="avatar" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none"><circle cx="8.5" cy="10.5" r="1.3" fill="#fff"/><circle cx="15.5" cy="10.5" r="1.3" fill="#fff"/><path d="M8 15c1.2 1.1 2.6 1.6 4 1.6s2.8-.5 4-1.6" stroke="#fff" stroke-width="1.4" stroke-linecap="round" fill="none"/></svg>
    </div>
    <div class="narrator-line"><b>Маруся:</b> напишіть назву вашого міста, села чи громади.</div>
  </div>
  <div class="wrap" style="max-width:640px;">
    <h2 class="section">Де ви зараз?</h2>
    <p class="section-sub">Ми оцінюємо ситуацію на рівні громади (об’єднаної територіальної громади) &mdash; введіть назву вашого міста, найближчого районного центру або громади. У базі 1 469 громад, а не всі ~30 000 населених пунктів окремо.</p>
    <div class="search-wrap">
      <input type="text" id="search-input" class="search-input" placeholder="Наприклад: Харків, Буча, Ізюм..." autocomplete="off" oninput="onSearchInput()">
      <div id="search-results" class="search-results"></div>
    </div>
  </div>
</section>

<section id="screen-dashboard" hidden>
  <div class="narrator-bar">
    <div class="avatar" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none"><circle cx="8.5" cy="10.5" r="1.3" fill="#fff"/><circle cx="15.5" cy="10.5" r="1.3" fill="#fff"/><path d="M8 15c1.2 1.1 2.6 1.6 4 1.6s2.8-.5 4-1.6" stroke="#fff" stroke-width="1.4" stroke-linecap="round" fill="none"/></svg>
    </div>
    <div class="narrator-line" id="dash-narrator"><b>Маруся:</b> &hellip;</div>
  </div>
  <div class="wrap">
    <button class="btn btn-ghost" onclick="showInput()" style="margin-bottom:22px;">&larr; Змінити громаду</button>
    <div id="dash-content"></div>
  </div>
</section>

<script type="application/json" id="hromada-data">__HROMADA_JSON__</script>
"""

NEW_JS = """
  var HD = null;
  var IDX = {n:0,o:1,r:2,lat:3,lon:4,pop:5,urb:6,occ:7,fl:8,x1:9,x2:10,x3:11,x4:12,ov:13,fac:14};

  function loadData(){
    if(!HD){ HD = JSON.parse(document.getElementById('hromada-data').textContent); }
    return HD;
  }

  function showInput(){
    document.getElementById('screen-clusters').hidden = true;
    document.getElementById('screen-dashboard').hidden = true;
    document.getElementById('screen-input').hidden = false;
    window.scrollTo(0,0);
    var inp = document.getElementById('search-input');
    inp.value = '';
    document.getElementById('search-results').innerHTML = '';
    inp.focus();
  }

  function normalizeStr(s){
    return s.toLowerCase().replace(/['’ʼ]/g,'').trim();
  }

  function onSearchInput(){
    var q = normalizeStr(document.getElementById('search-input').value);
    var box = document.getElementById('search-results');
    box.innerHTML = '';
    if(q.length < 2){ return; }
    var data = loadData();
    var matches = [];
    for(var i=0;i<data.rows.length;i++){
      var name = normalizeStr(data.rows[i][IDX.n]);
      if(name.indexOf(q) !== -1){ matches.push(i); if(matches.length>=8) break; }
    }
    if(matches.length===0){
      box.innerHTML = '<div class="result-empty">Нічого не знайдено. Спробуйте назву районного або обласного центру поруч.</div>';
      return;
    }
    matches.forEach(function(i){
      var r = data.rows[i];
      var div = document.createElement('div');
      div.className = 'result-row';
      div.innerHTML = '<span class="result-name">'+r[IDX.n]+'</span><span class="result-meta">'+r[IDX.o]+' область &middot; '+r[IDX.r]+' район</span>';
      div.onclick = (function(idx){ return function(){ selectHromada(idx); }; })(i);
      box.appendChild(div);
    });
  }

  function haversineKm(lat1,lon1,lat2,lon2){
    var R = 6371.0088;
    var p1 = lat1*Math.PI/180, p2 = lat2*Math.PI/180;
    var dphi = (lat2-lat1)*Math.PI/180, dl = (lon2-lon1)*Math.PI/180;
    var a = Math.sin(dphi/2)*Math.sin(dphi/2) + Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)*Math.sin(dl/2);
    return 2*R*Math.asin(Math.sqrt(a));
  }

  function tierOf(ov){
    if(ov < 0.10) return {key:'safe', label:'Безпечно'};
    if(ov < 0.30) return {key:'mid', label:'Помірний ризик'};
    return {key:'bad', label:'Високий ризик'};
  }

  function pctStr(v){ return (Math.round(v*1000)/10) + '%'; }

  function meterRow(label, display, val){
    var w = Math.max(2, Math.min(100, val*100));
    return '<div class="meter-row"><div class="meter-label">'+label+'</div>'+
           '<div class="meter-track"><div class="meter-fill" style="width:'+w+'%;"></div></div>'+
           '<div class="meter-val">'+display+'</div></div>';
  }

  function findSafeAlternatives(current){
    var data = loadData();
    var lat1 = current[IDX.lat], lon1 = current[IDX.lon];
    var cands = [];
    for(var i=0;i<data.rows.length;i++){
      var r = data.rows[i];
      if(r === current) continue;
      if(r[IDX.ov] >= 0.10) continue;
      if(r[IDX.pop] < 15000) continue;
      var d = haversineKm(lat1, lon1, r[IDX.lat], r[IDX.lon]);
      cands.push({name:r[IDX.n], oblast:r[IDX.o], pop:r[IDX.pop], ov:r[IDX.ov], dist:d});
    }
    cands.sort(function(a,b){ return a.dist - b.dist; });
    return cands.slice(0,3);
  }

  function selectHromada(i){
    var data = loadData();
    var r = data.rows[i];
    renderDashboard(r);
    document.getElementById('screen-input').hidden = true;
    document.getElementById('screen-dashboard').hidden = false;
    window.scrollTo(0,0);
  }

  function renderDashboard(r){
    var name=r[IDX.n], oblast=r[IDX.o], raion=r[IDX.r], pop=r[IDX.pop], occ=r[IDX.occ];
    var fl=r[IDX.fl], x1=r[IDX.x1], x2=r[IDX.x2], x3=r[IDX.x3], x4=r[IDX.x4], ov=r[IDX.ov], fac=r[IDX.fac];
    var tier = tierOf(ov);

    var narr = '<b>Маруся:</b> ';
    if(occ){
      narr += 'Громада «'+name+'» перебуває під окупацією &mdash; це найвищий рівень ризику в нашій моделі.';
    } else if(tier.key==='safe'){
      narr += 'Громада «'+name+'» ('+oblast+' область) &mdash; один із відносно спокійних районів за нашими даними.';
    } else if(tier.key==='mid'){
      narr += 'У громаді «'+name+'» ('+oblast+' область) помірний рівень ризику &mdash; варто стежити за ситуацією.';
    } else {
      narr += 'Громада «'+name+'» ('+oblast+' область) має високий рівень ризику за нашими даними.';
    }
    document.getElementById('dash-narrator').innerHTML = narr;

    var html = '';
    html += '<div class="dash-head">';
    html += '<div><h2 class="section" style="font-size:26px;">'+name+'</h2>';
    html += '<div class="section-sub" style="margin-bottom:0;">'+oblast+' область &middot; '+raion+' район &middot; '+pop.toLocaleString('uk-UA')+' осіб</div></div>';
    html += '<div class="dash-score"><div class="dash-score-num tier-'+tier.key+'">'+ov.toFixed(3)+'</div><span class="tag tag-'+tier.key+'">'+tier.label+'</span></div>';
    html += '</div>';

    if(occ){
      html += '<div class="exclusion-note" style="margin-top:18px;"><span class="dot"></span>'+
              '<div><b>Ця громада окупована.</b> Порівняння ризиків нижче має обмежену практичну цінність &mdash; '+
              'пріоритет тут безпека евакуації, а не вибір між регіонами.</div></div>';
    }

    html += '<div class="meters">';
    html += meterRow('Ризик атак', pctStr(x1), x1);
    html += meterRow('Ризик відключень', x2.toFixed(3), x2);
    html += meterRow('Ризик лінії фронту', x3.toFixed(3)+' &middot; '+fl+' км до лінії', x3);
    html += meterRow('Логістичний ризик', x4===null ? 'немає даних' : x4.toFixed(3), x4===null ? 0 : x4);
    html += '</div>';

    if(fac){
      html += '<div class="fac-note"><b>Задокументовані об’єкти поруч:</b> '+fac+'</div>';
    }

    html += '<div class="advice-box tier-'+tier.key+'-box">';
    if(tier.key==='safe'){
      html += '<p><b>Порада Марусі:</b> Термінової потреби переїжджати немає &mdash; ситуація тут відносно спокійна порівняно з рештою країни. Продовжуйте стежити за офіційними попередженнями та маршрутами укриттів.</p>';
    } else if(tier.key==='mid'){
      html += '<p><b>Порада Марусі:</b> Ризик помірний. Якщо у вас є діти, літні родичі або особливі медичні потреби &mdash; варто заздалегідь розглянути безпечніші варіанти нижче, навіть якщо не переїжджати прямо зараз.</p>';
    } else {
      html += '<p><b>Порада Марусі:</b> Це один із районів із найвищим рівнем ризику за нашими даними. Варто серйозно розглянути переїзд, особливо якщо у вас є діти чи вразливі члени родини. Нижче &mdash; найближчі відносно безпечні громади зі значним населенням.</p>';
    }
    html += '</div>';

    if(tier.key !== 'safe'){
      html += '<h2 class="section" style="margin-top:34px;">Найближчі безпечніші громади</h2>';
      html += '<p class="section-sub">Відсортовано за відстанню по прямій, серед громад із загальним балом ризику нижче 0.10 і населенням понад 15 000.</p>';
      var recos = findSafeAlternatives(r);
      if(recos.length){
        html += '<div class="reco-list">';
        recos.forEach(function(rec){
          html += '<div class="reco-card"><div class="reco-name">'+rec.name+'</div>'+
                  '<div class="reco-meta">'+rec.oblast+' область &middot; ~'+Math.round(rec.dist)+' км &middot; '+rec.pop.toLocaleString('uk-UA')+' осіб</div>'+
                  '<div class="reco-score">бал '+rec.ov.toFixed(3)+'</div></div>';
        });
        html += '</div>';
      }
    }

    html += '<div class="next-caveat">Це орієнтовна оцінка на основі задокументованих даних (атаки, пошкодження інфраструктури, лінія фронту, логістика) &mdash; ще не персоналізована рекомендація. Підбір за родинною ситуацією, професією, житлом, школами та вартістю переїзду ще в розробці.</div>';

    document.getElementById('dash-content').innerHTML = html;
  }
"""

# at this point there is still exactly one <script> block (the main one),
# so this targets it unambiguously
assert html.count("<script>") == 1 and html.count("</script>") == 1
html = html.replace("</script>", NEW_JS + "</script>", 1)

# now add the new sections (including the separate JSON data script tag)
html = html.replace(
    '<div id="toast" class="toast" role="status"></div>',
    NEW_SECTIONS.replace("__HROMADA_JSON__", "PLACEHOLDER_JSON_TOKEN") +
    '\n<div id="toast" class="toast" role="status"></div>'
)

# finally swap in the real JSON payload (unique token, no ambiguity)
assert html.count("PLACEHOLDER_JSON_TOKEN") == 1
html = html.replace("PLACEHOLDER_JSON_TOKEN", embedded_json)

with open("welcome.html", "w", encoding="utf-8") as f:
    f.write(html)

print("done, new size:", len(html)/1024, "KB")
