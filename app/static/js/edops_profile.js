/* Stored environmental profile, drawn into a container (Dashboard Profile tab).
   Rendering is the /profiles page's own (filled text with ecoregion links, monthly climate figure), without its
   template view, draft captions and portal buttons. Usage: EdopsProfile.draw(record, containerElement). */
(function () {
  const mk = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };

  // Filled text as the record's runs; an ecoregion name carries its OneEarth page.
  function filledBody(sec) {
    const p = mk('p');
    sec.runs.forEach(r => {
      if (!r.href) return p.append(r.t);
      const a = mk('a', null, r.t); a.href = r.href; a.target = '_blank'; a.rel = 'noopener'; p.append(a);
    });
    return p;
  }

  // A round tick step (1, 2, 2.5, 5 or 10 times a power of ten) at or above raw.
  function niceStep(raw) {
    const pow = Math.pow(10, Math.floor(Math.log10(raw)));
    return pow * [1, 2, 2.5, 5, 10].find(f => f * pow >= raw - 1e-9);
  }

  // Monthly precipitation (bars) and temperature (line), after the Sandbox's Walter-Lieth chart.
  function climateFigure(m) {
    const pre = m.precip_mm, tmp = m.temp_c, months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const W = 460, H = 240, PAD = { t: 16, r: 50, b: 36, l: 50 }, iW = W - PAD.l - PAD.r, iH = H - PAD.t - PAD.b;
    const tmpMin = Math.min(...tmp), tmpMax = Math.max(...tmp), barW = iW / 12;
    const pStep = niceStep(Math.max(...pre) / 3), pTop = Math.ceil(Math.max(...pre) / pStep) * pStep;   // precipitation axis ends on a round tick
    const tLo = tmpMin - 3, tHi = tmpMax + 3, tStep = niceStep((tHi - tLo) / 4);
    const pY = v => iH - (v / pTop) * iH, tY = v => iH - ((v - tLo) / (tHi - tLo)) * iH;
    let bars = '', pts = '', xl = '', yp = '', yt = '';
    for (let i = 0; i < 12; i++) {
      const x = PAD.l + i * barW, tx = (PAD.l + (i + 0.5) * barW).toFixed(1);
      bars += `<rect x="${(x + 1.5).toFixed(1)}" y="${(PAD.t + pY(pre[i])).toFixed(1)}" width="${(barW - 3).toFixed(1)}" height="${(iH - pY(pre[i])).toFixed(1)}" fill="#5b8dc4" opacity="0.65"/>`;
      pts += `${tx},${(PAD.t + tY(tmp[i])).toFixed(1)} `;
      xl += `<text x="${tx}" y="${H - 8}" font-size="11" text-anchor="middle">${months[i]}</text>`;
    }
    for (let v = 0; v <= pTop + 1e-9; v += pStep) {
      const y = (PAD.t + pY(v)).toFixed(1);
      yp += `<text x="${PAD.l - 5}" y="${y}" font-size="11" text-anchor="end" fill="#5b8dc4" dominant-baseline="middle">${+v.toFixed(2)}</text><line x1="${PAD.l}" y1="${y}" x2="${PAD.l + iW}" y2="${y}" stroke="#ddd" stroke-width="0.6"/>`;
    }
    for (let v = Math.ceil(tLo / tStep) * tStep; v <= tHi + 1e-9; v += tStep) {
      yt += `<text x="${PAD.l + iW + 5}" y="${(PAD.t + tY(v)).toFixed(1)}" font-size="11" fill="#c0392b" dominant-baseline="middle">${+v.toFixed(2)}°</text>`;
    }
    const lx = PAD.l / 2, rx = W - PAD.r / 2 + 8, cy = PAD.t + iH / 2;
    const fig = mk('figure', 'pf-fig');
    fig.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Monthly precipitation and temperature of the basin" style="width:100%;max-width:${W}px;overflow:visible">
      <rect x="${PAD.l}" y="${PAD.t}" width="${iW}" height="${iH}" fill="#f8f9fa" rx="2"/>${yp}${bars}
      <polyline points="${pts.trim()}" fill="none" stroke="#c0392b" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>${yt}${xl}
      <text x="${lx}" y="${cy}" font-size="11" fill="#5b8dc4" text-anchor="middle" transform="rotate(-90,${lx},${cy})">Precip (mm)</text>
      <text x="${rx}" y="${cy}" font-size="11" fill="#c0392b" text-anchor="middle" transform="rotate(90,${rx},${cy})">Temp (°C)</text></svg>`;
    fig.append(mk('figcaption', null, 'Monthly precipitation and temperature of the basin, not the point (' + m.source + ').'));
    return fig;
  }

  function draw(rec, box) {
    const nodes = [];
    if (rec.no_basin) {
      nodes.push(mk('h3', 'pf-nobasin', rec.message));
    } else {
      rec.sections.forEach(sec => {
        nodes.push(mk('h5', 'pf-sec', sec.title), filledBody(sec));
        if (sec.id === 'S2' && rec.monthly) nodes.push(climateFigure(rec.monthly));
      });
    }
    box.replaceChildren(...nodes);
  }

  window.EdopsProfile = { draw };
})();
