// Extra JavaScript functionality for Obelisk

document.addEventListener('DOMContentLoaded', function() {
  // Add smooth scroll behavior
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Add version text to footer
  const footer = document.querySelector('.md-footer-meta');
  if (footer) {
    const versionDiv = document.createElement('div');
    versionDiv.className = 'md-footer-version';
    versionDiv.innerHTML = '<span>Obelisk v0.1.0</span>';
    footer.querySelector('.md-footer-meta__inner').appendChild(versionDiv);
  }
  
  // Accept cookie consent by default in development
  const acceptButtons = document.querySelectorAll('.md-dialog__accept');
  if (acceptButtons.length > 0) {
    setTimeout(() => {
      acceptButtons[0].click();
    }, 500);
  }
});