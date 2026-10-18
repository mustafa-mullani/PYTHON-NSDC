/* Free multilingual voice helper for the Hotel Event Management System.
   Uses browser SpeechRecognition and SpeechSynthesis; no API key or server service. */
(() => {
  'use strict';
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const LANGS = {en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN'};
  let recognition = null;
  let listening = false;
  let selectedLang = 'en';
  let lastTranscript = '';

  const norm = value => String(value || '').toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[’']/g, '').replace(/[^\p{L}\p{N}:.-]+/gu, ' ').trim();
  const say = (message) => {
    const output = document.getElementById('va-response');
    if (output) output.textContent = message;
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.lang = LANGS[selectedLang] || 'en-IN';
      utterance.rate = 0.92;
      const voices = window.speechSynthesis.getVoices();
      const preferred = voices.find(v => v.lang.toLowerCase() === utterance.lang.toLowerCase()) || voices.find(v => v.lang.toLowerCase().startsWith(utterance.lang.slice(0,2)));
      if (preferred) utterance.voice = preferred;
      window.speechSynthesis.speak(utterance);
    }
  };
  const setStatus = text => { const s = document.getElementById('va-status'); if (s) s.textContent = text; };
  const setValue = (field, value) => {
    if (!field || value === undefined || value === null || value === '') return false;
    field.value = value;
    field.dispatchEvent(new Event('input', {bubbles:true}));
    field.dispatchEvent(new Event('change', {bubbles:true}));
    field.style.outline = '2px solid #0d9488';
    setTimeout(() => { field.style.outline = ''; }, 1300);
    return true;
  };
  const fieldByName = name => document.querySelector(`[name="${name}"]`);

  function parseDate(text) {
    const s = norm(text);
    let m = s.match(/\b(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\b/);
    if (m) return `${m[1]}-${m[2].padStart(2,'0')}-${m[3].padStart(2,'0')}`;
    m = s.match(/\b(\d{1,2})[-/.](\d{1,2})[-/.](20\d{2})\b/);
    if (m) return `${m[3]}-${m[2].padStart(2,'0')}-${m[1].padStart(2,'0')}`;
    const months = {january:1,jan:1,february:2,feb:2,march:3,mar:3,april:4,apr:4,may:5,june:6,jun:6,july:7,jul:7,august:8,aug:8,september:9,sep:9,sept:9,october:10,oct:10,november:11,nov:11,december:12,dec:12,
      जनवरी:1,फरवरी:2,मार्च:3,अप्रैल:4,मई:5,जून:6,जुलाई:7,अगस्त:8,सितंबर:9,अक्टूबर:10,नवंबर:11,दिसंबर:12,
      जानेवारी:1,फेब्रुवारी:2,मार्च:3,एप्रिल:4,मे:5,जून:6,जुलै:7,ऑगस्ट:8,सप्टेंबर:9,ऑक्टोबर:10,नोव्हेंबर:11,डिसेंबर:12};
    const monthPattern = Object.keys(months).sort((a,b)=>b.length-a.length).join('|');
    m = text.match(new RegExp(`(\\d{1,2})\\s*(${monthPattern})[\\s,.-]*(20\\d{2})?`, 'i'));
    if (m) {
      const monthKey = m[2].toLocaleLowerCase(); const month = months[monthKey];
      const year = Number(m[3] || new Date().getFullYear());
      if (month) return `${year}-${String(month).padStart(2,'0')}-${String(Number(m[1])).padStart(2,'0')}`;
    }
    return '';
  }
  function parseTime(text, keyword) {
    const s = norm(text);
    const re = keyword === 'start' ? /(?:start(?:ing)? time|from|शुरू|सुरु|वेळ|वाजता)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/i : /(?:end time|until|to|तक|पर्यंत|समाप्त)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/i;
    let m = s.match(re);
    if (!m) {
      const all = [...s.matchAll(/\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b/gi)];
      m = all[keyword === 'start' ? 0 : 1];
    }
    if (!m) return '';
    let h = Number(m[1]), min = Number(m[2] || 0), ap = (m[3] || '').toLowerCase();
    if (ap === 'pm' && h < 12) h += 12;
    if (ap === 'am' && h === 12) h = 0;
    if (h > 23 || min > 59) return '';
    return `${String(h).padStart(2,'0')}:${String(min).padStart(2,'0')}`;
  }
  function fillBooking(text) {
    let changed = [];
    const eventTypes = [
      ['Conference', /conference|meeting|सम्मेलन|बैठक|परिषद/i],
      ['Workshop', /workshop|कार्यशाळा|कार्यशाला/i],
      ['Birthday', /birthday|जन्मदिन|वाढदिवस|बर्थडे/i],
      ['Marriage', /marriage|wedding|लग्न|शादी|विवाह/i],
      ['Other', /other|अन्य|इतर/i]
    ];
    const type = eventTypes.find(x => x[1].test(text));
    if (type && setValue(fieldByName('event_type'), type[0])) changed.push('event type');

    const dateValue = parseDate(text);
    if (dateValue && setValue(fieldByName('date'), dateValue)) changed.push('date');

    const capMatch = text.match(/(?:capacity|guests?|people|persons?|attendees?|लोग|मेहमान|व्यक्ति|लोक|पाहुणे|माणसं)\D{0,18}(\d{1,4})/i) || text.match(/\b(\d{1,4})\s*(?:guests?|people|persons?|attendees?|लोग|मेहमान|लोक|पाहुणे)\b/i);
    if (capMatch && setValue(fieldByName('capacity'), capMatch[1] || capMatch[2])) changed.push('guest capacity');

    const start = parseTime(text, 'start');
    const end = parseTime(text, 'end');
    if (start && setValue(fieldByName('s_time'), start)) changed.push('start time');
    if (end && setValue(fieldByName('e_time'), end)) changed.push('end time');

    const eventName = fieldByName('event_name');
    if (eventName && !eventName.value) {
      const named = text.match(/(?:event name is|event is|event name|कार्यक्रम का नाम|कार्यक्रमाचे नाव)\s+([\p{L} ]{2,40})/iu);
      if (named && setValue(eventName, named[1].trim())) changed.push('event name');
      else if (type) setValue(eventName, type[0] + ' Event');
    }
    const description = fieldByName('description');
    if (description && /description|details|विवरण|तपशील/i.test(text)) {
      const detail = text.replace(/.*?(?:description|details|विवरण|तपशील)\s*/i, '').trim();
      if (detail && setValue(description, detail)) changed.push('description');
    }
    if (changed.length) {
      const msg = 'I filled: ' + changed.join(', ') + '. Please check the values and complete anything missing.';
      say(msg);
    } else {
      say('I could not identify a booking field in that sentence. Try saying the event type, date, guest capacity, or start and end time.');
    }
  }

  function selectMenuOption(text) {
    const wanted = norm(text).replace(/^(please )?(select|choose|add|i want|मुझे|मला|निवडा|चुनें)\s+/, '');
    const radios = [...document.querySelectorAll('input[type="radio"]')];
    if (!radios.length) return false;
    let best = null, bestScore = 0;
    for (const radio of radios) {
      const label = radio.closest('label') || document.querySelector(`label[for="${radio.id}"]`);
      const labelText = norm(label ? label.innerText : radio.value);
      const value = norm(radio.value);
      if (!labelText) continue;
      let score = 0;
      if (wanted.includes(value) && value.length > 2) score = value.length + 10;
      else if (labelText.includes(wanted) && wanted.length > 2) score = wanted.length + 5;
      else if (wanted.includes(labelText) && labelText.length > 2) score = labelText.length;
      if (score > bestScore) { bestScore = score; best = radio; }
    }
    if (best && bestScore >= 4) {
      best.checked = true;
      best.dispatchEvent(new Event('change', {bubbles:true}));
      best.scrollIntoView({behavior:'smooth', block:'center'});
      best.closest('label')?.classList.add('va-selected');
      say('Selected ' + (best.closest('label')?.innerText.trim() || best.value) + '. You can choose another item or submit the menu when ready.');
      return true;
    }
    return false;
  }
  function chooseMenuType(text) {
    const s = norm(text);
    const type = /\b(veg|vegetarian|शाकाहारी|शाकाहार|शाकाहारी भोजन)\b/i.test(s) ? 'veg' :
      /\b(chicken|चिकन|कोंबडी)\b/i.test(s) ? 'chicken' :
      /\b(mutton|मटण|मटन)\b/i.test(s) ? 'mutton' : '';
    if (!type) return false;
    const links = [...document.querySelectorAll('a')];
    const link = links.find(a => norm(a.innerText + ' ' + a.href).includes(type));
    if (link) { say('Opening the ' + type + ' menu.'); window.location.href = link.href; return true; }
    return false;
  }
  function handleTranscript(text) {
    lastTranscript = text;
    const transcript = document.getElementById('va-transcript');
    if (transcript) transcript.textContent = 'Heard: ' + text;
    if (document.querySelector('[name="event_name"]') && document.querySelector('[name="date"]')) {
      fillBooking(text);
      return;
    }
    if (chooseMenuType(text)) return;
    if (selectMenuOption(text)) return;
    const selects = [...document.querySelectorAll('select')];
    for (const select of selects) {
      const option = [...select.options].find(o => norm(o.text + ' ' + o.value) && (norm(text).includes(norm(o.text)) || norm(o.text).includes(norm(text))));
      if (option) { select.value = option.value; select.dispatchEvent(new Event('change',{bubbles:true})); say('Selected ' + option.text + '.'); return; }
    }
    say('I heard you, but could not match that to an option. Please say the option name more clearly or select it manually.');
  }
  function startListening() {
    if (!SpeechRecognition) {
      say('Voice recognition is not supported by this browser. Please use the latest Google Chrome or Microsoft Edge.');
      return;
    }
    if (listening && recognition) { recognition.stop(); return; }
    selectedLang = document.getElementById('va-language')?.value || 'en';
    recognition = new SpeechRecognition();
    recognition.lang = LANGS[selectedLang] || 'en-IN';
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.maxAlternatives = 3;
    recognition.onstart = () => { listening = true; setStatus('Listening… speak now'); document.getElementById('va-mic')?.classList.add('va-listening'); };
    recognition.onresult = event => {
      const result = event.results[event.results.length - 1];
      handleTranscript(result[0].transcript);
    };
    recognition.onerror = event => { setStatus('Voice input: ' + (event.error || 'error')); if (event.error === 'not-allowed') say('Microphone permission was blocked. Allow microphone access in your browser settings.'); };
    recognition.onend = () => { listening = false; setStatus('Ready'); document.getElementById('va-mic')?.classList.remove('va-listening'); };
    try { recognition.start(); } catch (e) { setStatus('Please wait and try again.'); }
  }
  function init() {
    if (document.getElementById('voice-assistant')) return;
    const panel = document.createElement('section');
    panel.id = 'voice-assistant';
    panel.innerHTML = `
      <button type="button" id="va-toggle" aria-expanded="false" aria-controls="va-panel">🎙️ Voice Assistant</button>
      <div id="va-panel" hidden>
        <div class="va-heading"><strong>Hotel Voice Assistant</strong><button type="button" id="va-close" aria-label="Close voice assistant">×</button></div>
        <label for="va-language">Speak in / भाषा / भाषा निवडा</label>
        <select id="va-language"><option value="en">English (India)</option><option value="hi">हिन्दी (Hindi)</option><option value="mr">मराठी (Marathi)</option></select>
        <button type="button" id="va-mic">🎤 Tap to speak</button>
        <p id="va-status" role="status">Ready</p><p id="va-transcript">Your spoken words will appear here.</p>
        <p id="va-response" aria-live="polite">Tell me what you want to fill or select.</p>
        <small>Tip: speak one instruction at a time. Check all selections before submitting.</small>
      </div>`;
    document.body.appendChild(panel);
    document.getElementById('va-toggle').addEventListener('click', () => {
      const p = document.getElementById('va-panel'); p.hidden = !p.hidden;
      document.getElementById('va-toggle').setAttribute('aria-expanded', String(!p.hidden));
      if (!p.hidden) say('Hello. Choose your language and tap the microphone.');
    });
    document.getElementById('va-close').addEventListener('click', () => { document.getElementById('va-panel').hidden = true; });
    document.getElementById('va-mic').addEventListener('click', startListening);
    document.getElementById('va-language').addEventListener('change', e => { selectedLang = e.target.value; });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
