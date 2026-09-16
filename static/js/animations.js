(function () {
  'use strict';

  // SERVER CONFIG
  const CONFIG = {
    serverName: 'LAST TOWN',
    primaryColor: '#b19b55'
  };

  // REVEAL ANIMATIONS ON SCROLL
  var els = document.querySelectorAll('[data-reveal]');
  
  if (!('IntersectionObserver' in window) || els.length === 0) {
    els.forEach(function (el) { 
      el.classList.add('in-view'); 
    });
  } else {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('in-view');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
    );

    els.forEach(function (el) {
      if (!el.style.getPropertyValue('--reveal-delay')) {
        var group = el.closest('[data-reveal-group]');
        var delay = group ? Array.prototype.indexOf.call(group.children, el) * 70 : 0;
        el.style.setProperty('--reveal-delay', Math.min(delay, 420) + 'ms');
      }
      io.observe(el);
    });
  }
})();
