(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* Surat time in the header */
  const clock = $('[data-clock]');
  if (clock) {
    const fmt = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Kolkata' });
    const tick = () => { clock.textContent = fmt.format(new Date()); };
    tick();
    setInterval(tick, 20000);
  }

  /* Header switches between light and dark text depending on the section under it */
  const header = $('[data-header]');
  const themed = $$('[data-theme]');
  const setTone = () => {
    if (!header) return;
    let theme = 'dark';
    for (const s of themed) {
      const r = s.getBoundingClientRect();
      if (r.top <= 34 && r.bottom > 34) theme = s.dataset.theme;
    }
    header.dataset.tone = theme === 'light' ? 'light' : 'dark';
  };

  /* Hero reel: each project arrives through an arch */
  const hero = $('.hero');
  if (hero) {
    const SLIDE_MS = 4700;
    const ARCH_MS = 1700;
    const slides = $$('.hero__slide', hero);
    const ticks = $$('[data-reel-ticks] i', hero);
    const idxEl = $('[data-reel-index]', hero);
    const titleEl = $('[data-reel-title]', hero);
    const metaEl = $('[data-reel-meta]', hero);
    const caption = $('.hero__caption', hero);
    const saveData = navigator.connection && navigator.connection.saveData;
    const useVideo = !reduceMotion && !saveData;
    let current = 0;
    let timer = null;
    let inView = true;

    const prepare = (slide) => {
      const v = $('video', slide);
      if (!v || !useVideo) return null;
      if (!v.src && v.dataset.src) {
        v.preload = 'auto';
        v.src = v.dataset.src;
        v.addEventListener('playing', () => v.classList.add('is-playing'));
      }
      return v;
    };
    const play = (slide) => {
      const v = prepare(slide);
      if (!v) return;
      try { v.currentTime = 0; } catch (e) { /* not seekable yet */ }
      const p = v.play();
      if (p) p.catch(() => {});
    };
    const stop = (slide) => {
      const v = $('video', slide);
      if (!v) return;
      v.pause();
      v.classList.remove('is-playing');
    };
    const paint = (n) => {
      const s = slides[n];
      idxEl.textContent = String(n + 1).padStart(2, '0');
      titleEl.innerHTML = s.dataset.title;
      metaEl.textContent = s.dataset.meta;
      caption.classList.remove('is-swapping');
      void caption.offsetWidth;
      caption.classList.add('is-swapping');
      ticks.forEach((t, i) => {
        t.classList.toggle('is-done', i < n);
        t.classList.remove('is-on');
        if (i === n) { t.style.setProperty('--tick', `${SLIDE_MS}ms`); void t.offsetWidth; t.classList.add('is-on'); }
      });
    };
    const queue = () => {
      clearTimeout(timer);
      if (reduceMotion || !inView || document.hidden) return;
      timer = setTimeout(() => go((current + 1) % slides.length), SLIDE_MS);
    };
    const go = (n) => {
      const prev = slides[current];
      const next = slides[n];
      if (prev === next) return;
      next.classList.add('is-entering');
      play(next);
      paint(n);
      current = n;
      setTimeout(() => {
        prev.classList.remove('is-active');
        stop(prev);
        next.classList.remove('is-entering');
        next.classList.add('is-active');
        prepare(slides[(n + 1) % slides.length]);
      }, ARCH_MS);
      queue();
    };

    // start once the opening curtain has lifted
    setTimeout(() => {
      play(slides[0]);
      paint(0);
      prepare(slides[1]);
      queue();
    }, reduceMotion ? 0 : 1700);

    new IntersectionObserver(([e]) => {
      inView = e.isIntersecting;
      if (inView) { play(slides[current]); queue(); } else { clearTimeout(timer); stop(slides[current]); }
    }, { threshold: 0.15 }).observe(hero);
    document.addEventListener('visibilitychange', queue);

    // slight 3D lean toward the pointer
    const stage = $('[data-tilt]', hero);
    if (stage && finePointer && !reduceMotion) {
      hero.addEventListener('pointermove', (e) => {
        const r = hero.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        stage.style.setProperty('--ry', `${(x * 3.2).toFixed(2)}deg`);
        stage.style.setProperty('--rx', `${(-y * 2.4).toFixed(2)}deg`);
      });
      hero.addEventListener('pointerleave', () => {
        stage.style.setProperty('--ry', '0deg');
        stage.style.setProperty('--rx', '0deg');
      });
    }
  }

  /* Reveal on scroll, staggered among siblings */
  const reveals = $$('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach((el) => {
      const sibs = [...el.parentElement.children].filter((c) => c.classList.contains('reveal'));
      el.style.setProperty('--d', `${Math.min(sibs.indexOf(el), 6) * 0.09}s`);
      io.observe(el);
    });
  } else {
    reveals.forEach((el) => el.classList.add('is-in'));
  }

  /* Projects: each panel dims and settles back as the next slides over it */
  const panels = $$('.project');
  const setPanels = () => {
    const vh = innerHeight;
    panels.forEach((p, i) => {
      const r = p.getBoundingClientRect();
      p.style.setProperty('--enter', clamp(1 - r.top / vh).toFixed(3));
      const next = panels[i + 1];
      if (next) p.style.setProperty('--cover', clamp(1 - next.getBoundingClientRect().top / vh).toFixed(3));
    });
  };

  /* Services: an arched preview follows the pointer */
  const preview = $('[data-service-preview]');
  const list = $('.services__list');
  if (preview && list && finePointer) {
    const img = $('img', preview);
    $$('.service', list).forEach((row) => {
      row.addEventListener('pointerenter', () => { img.src = row.dataset.preview; preview.classList.add('is-on'); });
    });
    list.addEventListener('pointerleave', () => preview.classList.remove('is-on'));
    list.addEventListener('pointermove', (e) => {
      preview.style.setProperty('--x', `${e.clientX + 26}px`);
      preview.style.setProperty('--y', `${e.clientY - 200}px`);
    });
  }

  /* Client wall: loop each column by doubling its tiles */
  $$('[data-logo-wall] .logo-col').forEach((col) => {
    if (reduceMotion) return;
    const track = document.createElement('div');
    track.className = 'logo-track';
    const tiles = [...col.children];
    tiles.forEach((t) => track.appendChild(t));
    tiles.forEach((t) => { const c = t.cloneNode(true); c.setAttribute('aria-hidden', 'true'); track.appendChild(c); });
    track.style.setProperty('--dur', `${col.dataset.speed || 40}s`);
    col.appendChild(track);
  });

  /* Footer: how far you have scrolled, in metres */
  const meter = $('[data-scroll-m]');
  const note = $('[data-scroll-note]');
  const NOTES = [
    [2.2, 'About the height of a doorway.'],
    [3.2, 'About the height of a ceiling.'],
    [6.5, 'About two storeys.'],
    [10, 'About a three-storey villa.'],
    [Infinity, 'Taller than most homes we design.'],
  ];
  const setMeter = () => {
    if (!meter) return;
    const m = (scrollY / 96) * 0.0254;
    meter.textContent = m.toFixed(1);
    if (note) note.textContent = NOTES.find(([max]) => m < max)[1];
  };

  /* WhatsApp button appears after the hero and steps aside for the contact card */
  const wa = $('[data-wa-float]');
  const cta = $('.cta__card');
  let ctaInView = false;
  if (wa && cta && 'IntersectionObserver' in window) {
    new IntersectionObserver(([e]) => { ctaInView = e.isIntersecting; setWa(); }, { threshold: 0.3 }).observe(cta);
  }
  function setWa() {
    if (!wa) return;
    wa.classList.toggle('is-visible', scrollY > innerHeight * 0.55 && !ctaInView);
  }

  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      setTone();
      setPanels();
      setMeter();
      setWa();
      ticking = false;
    });
  };
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();
})();
