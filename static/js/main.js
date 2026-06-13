/* ============================================================
   RESTRO — Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

    // ---- Theme Toggle (Dark/Light) ----
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const html = document.documentElement;

    // Load saved theme
    const savedTheme = localStorage.getItem('restro-theme') || 'dark';
    html.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const currentTheme = html.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('restro-theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
        }
    }

    // ---- Navbar Scroll Effect ----
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // ---- Active Nav Link ----
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar .nav-link').forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && currentPath === href) {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });

    // ---- Auto-dismiss alerts after 5 seconds ----
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // ---- Scroll Reveal Animation ----
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px',
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal-on-scroll').forEach(function (el) {
        el.style.opacity = '0';
        observer.observe(el);
    });

    // ---- Add to Cart (AJAX) ----
    document.querySelectorAll('.btn-add-cart-ajax').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.dataset.url;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
                || getCookie('csrftoken');

            // Button animation
            const originalContent = this.innerHTML;
            this.innerHTML = '<i class="bi bi-check-lg"></i>';
            this.classList.add('bg-success', 'border-success');
            this.style.color = 'white';

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.success) {
                    // Update cart badge
                    updateCartBadge(data.cart_count);
                    showToast(data.message, 'success');
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
                showToast('Failed to add item to cart.', 'error');
            })
            .finally(function () {
                setTimeout(function () {
                    btn.innerHTML = originalContent;
                    btn.classList.remove('bg-success', 'border-success');
                    btn.style.color = '';
                }, 1000);
            });
        });
    });

    // ---- Cart Quantity Update (AJAX) ----
    document.querySelectorAll('.cart-qty-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const form = this.closest('form');
            const url = form.action;
            const formData = new FormData(form);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData,
            })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.success) {
                    // Reload the page to update quantities and totals
                    location.reload();
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
            });
        });
    });

    // ---- Toast Notification ----
    function showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            animation: fadeInUp 0.3s ease;
            backdrop-filter: blur(20px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            max-width: 350px;
        `;

        if (type === 'success') {
            toast.style.background = 'rgba(34, 197, 94, 0.9)';
            toast.innerHTML = '<i class="bi bi-check-circle-fill"></i> ' + message;
        } else if (type === 'error') {
            toast.style.background = 'rgba(239, 68, 68, 0.9)';
            toast.innerHTML = '<i class="bi bi-exclamation-circle-fill"></i> ' + message;
        } else {
            toast.style.background = 'rgba(59, 130, 246, 0.9)';
            toast.innerHTML = '<i class="bi bi-info-circle-fill"></i> ' + message;
        }

        document.body.appendChild(toast);

        setTimeout(function () {
            toast.style.animation = 'fadeInUp 0.3s ease reverse';
            setTimeout(function () {
                toast.remove();
            }, 300);
        }, 3000);
    }

    // ---- Update Cart Badge ----
    function updateCartBadge(count) {
        const badges = document.querySelectorAll('.cart-badge');
        if (count > 0) {
            badges.forEach(function (badge) {
                badge.textContent = count;
                badge.style.display = 'flex';
            });
            // If no badge exists, create one
            if (badges.length === 0) {
                const cartLink = document.querySelector('.cart-link');
                if (cartLink) {
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-gradient-primary rounded-pill cart-badge';
                    badge.textContent = count;
                    cartLink.appendChild(badge);
                }
            }
        } else {
            badges.forEach(function (badge) {
                badge.style.display = 'none';
            });
        }
    }

    // ---- Get CSRF Cookie ----
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // ---- Smooth Scroll for anchor links ----
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ---- Counter Animation ----
    function animateCounters() {
        document.querySelectorAll('.counter').forEach(function (counter) {
            const target = parseInt(counter.dataset.target);
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;

            const timer = setInterval(function () {
                current += step;
                if (current >= target) {
                    counter.textContent = target.toLocaleString();
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.floor(current).toLocaleString();
                }
            }, 16);
        });
    }

    // Trigger counter animation when in viewport
    const counterSection = document.querySelector('.hero-stats');
    if (counterSection) {
        const counterObserver = new IntersectionObserver(function (entries) {
            if (entries[0].isIntersecting) {
                animateCounters();
                counterObserver.unobserve(counterSection);
            }
        });
        counterObserver.observe(counterSection);
    }

});
