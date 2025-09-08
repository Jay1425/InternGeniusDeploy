// Accessibility Features
document.addEventListener('DOMContentLoaded', function() {
    // Font size controls
    document.getElementById('increaseText')?.addEventListener('click', function(e) {
        e.preventDefault();
        document.body.classList.add('large-text');
    });
    
    document.getElementById('decreaseText')?.addEventListener('click', function(e) {
        e.preventDefault();
        document.body.classList.remove('large-text');
    });
    
    // High contrast toggle
    document.getElementById('toggleContrast')?.addEventListener('click', function(e) {
        e.preventDefault();
        document.body.classList.toggle('high-contrast');
    });
    
    // Animation for statistics when they come into view
    const statsElements = document.querySelectorAll('.govt-stat-card-number, .govt-stat-number');
    
    if (statsElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateStats();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        // Observe the first stats element
        observer.observe(statsElements[0]);
        
        function animateStats() {
            statsElements.forEach(element => {
                // Get the target value from the HTML
                const value = element.textContent;
                const hasPlus = value.includes('+');
                
                // Extract the numeric part
                const targetValue = parseInt(value.replace(/[^0-9]/g, ''));
                
                // Animation parameters
                let startValue = 0;
                const duration = 2000; // 2 seconds
                const increment = Math.ceil(targetValue / (duration / 50)); // Update every 50ms
                
                // Reset to 0
                element.textContent = hasPlus ? '0+' : '0';
                
                // Start the animation
                const interval = setInterval(() => {
                    startValue += increment;
                    if (startValue >= targetValue) {
                        startValue = targetValue;
                        clearInterval(interval);
                    }
                    element.textContent = hasPlus ? startValue + '+' : startValue;
                }, 50);
            });
        }
    }
});
