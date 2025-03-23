// src/lib/utils/animations.js
// مكتبة الرسوم المتحركة - Animation Utilities

import { browser } from '$app/environment';
import { language } from '$lib/i18n';
import { get } from 'svelte/store';

/**
 * التحقق مما إذا كان المستخدم يفضل تقليل الحركة
 * Check if user prefers reduced motion
 * 
 * @returns {boolean} تفضيل تقليل الحركة
 */
export function prefersReducedMotion() {
    if (!browser) return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * حساب القيمة مع التخميد (إيزنج)
 * Calculate eased value
 * 
 * @param {number} t - الوقت/التقدم (0-1)
 * @param {string} easingType - نوع الإيزنج
 * @returns {number} القيمة بعد تطبيق الإيزنج
 */
export function applyEasing(t, easingType = 'easeOutCubic') {
    const easingFunctions = {
        // Linear (no easing)
        linear: t => t,
        
        // Quad
        easeInQuad: t => t * t,
        easeOutQuad: t => t * (2 - t),
        easeInOutQuad: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
        
        // Cubic
        easeInCubic: t => t * t * t,
        easeOutCubic: t => (--t) * t * t + 1,
        easeInOutCubic: t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
        
        // Quart
        easeInQuart: t => t * t * t * t,
        easeOutQuart: t => 1 - (--t) * t * t * t,
        easeInOutQuart: t => t < 0.5 ? 8 * t * t * t * t : 1 - 8 * (--t) * t * t * t,
        
        // Elastic
        easeInElastic: t => t === 0 ? 0 : t === 1 ? 1 : -Math.pow(2, 10 * (t - 1)) * Math.sin((t - 1.1) * 5 * Math.PI),
        easeOutElastic: t => t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t - 0.1) * 5 * Math.PI) + 1,
        
        // Bounce
        easeOutBounce: t => {
            if (t < 1/2.75) return 7.5625 * t * t;
            if (t < 2/2.75) return 7.5625 * (t -= 1.5/2.75) * t + 0.75;
            if (t < 2.5/2.75) return 7.5625 * (t -= 2.25/2.75) * t + 0.9375;
            return 7.5625 * (t -= 2.625/2.75) * t + 0.984375;
        }
    };
    
    return (easingFunctions[easingType] || easingFunctions.easeOutCubic)(t);
}

/**
 * إنشاء رسم متحرك من البداية إلى النهاية باستخدام requestAnimationFrame
 * Create an animation from start to end using requestAnimationFrame
 * 
 * @param {Object} options - خيارات الرسم المتحرك
 * @param {number} options.duration - مدة الرسم المتحرك بالمللي ثانية
 * @param {number} options.from - قيمة البداية
 * @param {number} options.to - قيمة النهاية
 * @param {string} options.easing - نوع الإيزنج
 * @param {Function} options.onUpdate - دالة تنفذ في كل إطار مع القيمة الحالية
 * @param {Function} options.onComplete - دالة تنفذ عند اكتمال الرسم المتحرك
 * @returns {Function} دالة لإيقاف الرسم المتحرك
 */
export function animate({
    duration = 300,
    from = 0,
    to = 1,
    easing = 'easeOutCubic',
    onUpdate,
    onComplete
}) {
    // Skip animation if user prefers reduced motion
    if (prefersReducedMotion()) {
        if (onUpdate) onUpdate(to);
        if (onComplete) onComplete();
        return () => {};
    }
    
    const startTime = performance.now();
    let animationFrame;
    
    const animateFrame = (currentTime) => {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        const easedProgress = applyEasing(progress, easing);
        const currentValue = from + (to - from) * easedProgress;
        
        if (onUpdate) onUpdate(currentValue);
        
        if (progress < 1) {
            animationFrame = requestAnimationFrame(animateFrame);
        } else {
            if (onComplete) onComplete();
        }
    };
    
    animationFrame = requestAnimationFrame(animateFrame);
    
    // Return a cancel function
    return () => {
        if (animationFrame) {
            cancelAnimationFrame(animationFrame);
        }
    };
}

/**
 * إنشاء رسم متحرك متتابع لعدة عناصر
 * Create a sequential animation for multiple elements
 * 
 * @param {Array<Element|string>} elements - عناصر DOM أو محددات CSS
 * @param {Object} options - خيارات الرسم المتحرك
 * @param {string} options.animation - نوع الرسم المتحرك (fadeIn, slideIn, etc.)
 * @param {number} options.duration - مدة الرسم المتحرك لكل عنصر
 * @param {number} options.delay - التأخير الأولي قبل بدء الرسم المتحرك
 * @param {number} options.stagger - التأخير بين كل عنصر
 * @param {string} options.easing - نوع الإيزنج
 * @param {boolean} options.reverse - عكس ترتيب العناصر
 * @returns {Promise<void>} وعد يكتمل عند انتهاء جميع الرسوم المتحركة
 */
export function animateSequence(elements, {
    animation = 'fadeIn',
    duration = 500,
    delay = 0,
    stagger = 100,
    easing = 'easeOutCubic',
    reverse = false
}) {
    if (!browser) return Promise.resolve();
    
    // Handle reduced motion preference
    if (prefersReducedMotion()) {
        // Just show the elements without animation
        const resolvedElements = resolveElements(elements);
        resolvedElements.forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'none';
        });
        return Promise.resolve();
    }
    
    return new Promise(resolve => {
        // Resolve element references if they're selector strings
        const resolvedElements = resolveElements(elements);
        if (reverse) resolvedElements.reverse();
        
        if (resolvedElements.length === 0) {
            resolve();
            return;
        }
        
        let completed = 0;
        
        // Animation configurations
        const animations = {
            fadeIn: {
                from: { opacity: 0 },
                to: { opacity: 1 }
            },
            fadeInUp: {
                from: { opacity: 0, transform: 'translateY(20px)' },
                to: { opacity: 1, transform: 'translateY(0)' }
            },
            fadeInDown: {
                from: { opacity: 0, transform: 'translateY(-20px)' },
                to: { opacity: 1, transform: 'translateY(0)' }
            },
            fadeInLeft: {
                from: { opacity: 0, transform: 'translateX(-20px)' },
                to: { opacity: 1, transform: 'translateX(0)' }
            },
            fadeInRight: {
                from: { opacity: 0, transform: 'translateX(20px)' },
                to: { opacity: 1, transform: 'translateX(0)' }
            },
            zoomIn: {
                from: { opacity: 0, transform: 'scale(0.9)' },
                to: { opacity: 1, transform: 'scale(1)' }
            },
            zoomOut: {
                from: { opacity: 0, transform: 'scale(1.1)' },
                to: { opacity: 1, transform: 'scale(1)' }
            },
            flipIn: {
                from: { opacity: 0, transform: 'perspective(400px) rotateX(90deg)' },
                to: { opacity: 1, transform: 'perspective(400px) rotateX(0deg)' }
            }
        };
        
        // Handle RTL layout for directional animations
        if (get(language) === 'ar') {
            animations.fadeInLeft = animations.fadeInRight;
            animations.fadeInRight = {
                from: { opacity: 0, transform: 'translateX(-20px)' },
                to: { opacity: 1, transform: 'translateX(0)' }
            };
        }
        
        const selectedAnimation = animations[animation] || animations.fadeIn;
        
        // Set initial styles
        resolvedElements.forEach(el => {
            Object.entries(selectedAnimation.from).forEach(([property, value]) => {
                el.style[property] = value;
            });
        });
        
        // Animate each element with staggered delay
        resolvedElements.forEach((el, index) => {
            const elementDelay = delay + (index * stagger);
            
            setTimeout(() => {
                // Using CSS Transitions for better performance
                el.style.transition = `all ${duration}ms ${easing}`;
                
                Object.entries(selectedAnimation.to).forEach(([property, value]) => {
                    el.style[property] = value;
                });
                
                // When all animations complete
                el.addEventListener('transitionend', function transitionHandler(e) {
                    if (e.target === el) {
                        el.removeEventListener('transitionend', transitionHandler);
                        el.style.transition = '';
                        
                        completed++;
                        if (completed === resolvedElements.length) {
                            resolve();
                        }
                    }
                });
            }, elementDelay);
        });
    });
}

/**
 * إنشاء رسم متحرك للعناصر عند دخولها منطقة العرض
 * Create animation for elements when they enter the viewport
 * 
 * @param {Element|string} element - عنصر DOM أو محدد CSS
 * @param {Object} options - خيارات الرسم المتحرك
 * @param {string} options.animation - نوع الرسم المتحرك
 * @param {number} options.threshold - نسبة العنصر الذي يجب أن يكون مرئيًا
 * @param {number} options.duration - مدة الرسم المتحرك
 * @param {string} options.easing - نوع الإيزنج
 * @param {boolean} options.once - تنفيذ الرسم المتحرك مرة واحدة فقط
 * @returns {Function} دالة لإزالة المراقب
 */
export function animateOnScroll(element, {
    animation = 'fadeInUp',
    threshold = 0.2,
    duration = 500,
    easing = 'easeOutCubic',
    once = true
}) {
    if (!browser) return () => {};
    
    // Handle reduced motion preference
    if (prefersReducedMotion()) {
        const el = resolveElements([element])[0];
        if (el) el.style.opacity = '1';
        return () => {};
    }
    
    const el = resolveElements([element])[0];
    if (!el) return () => {};
    
    // Animation configurations
    const animations = {
        fadeIn: {
            initial: { opacity: '0' },
            animate: { opacity: '1' }
        },
        fadeInUp: {
            initial: { opacity: '0', transform: 'translateY(30px)' },
            animate: { opacity: '1', transform: 'translateY(0)' }
        },
        fadeInDown: {
            initial: { opacity: '0', transform: 'translateY(-30px)' },
            animate: { opacity: '1', transform: 'translateY(0)' }
        },
        fadeInLeft: {
            initial: { opacity: '0', transform: 'translateX(-30px)' },
            animate: { opacity: '1', transform: 'translateX(0)' }
        },
        fadeInRight: {
            initial: { opacity: '0', transform: 'translateX(30px)' },
            animate: { opacity: '1', transform: 'translateX(0)' }
        },
        scaleIn: {
            initial: { opacity: '0', transform: 'scale(0.9)' },
            animate: { opacity: '1', transform: 'scale(1)' }
        }
    };
    
    // Handle RTL layout for directional animations
    if (get(language) === 'ar') {
        animations.fadeInLeft = animations.fadeInRight;
        animations.fadeInRight = {
            initial: { opacity: '0', transform: 'translateX(-30px)' },
            animate: { opacity: '1', transform: 'translateX(0)' }
        };
    }
    
    const selectedAnimation = animations[animation] || animations.fadeIn;
    
    // Set initial styles
    Object.entries(selectedAnimation.initial).forEach(([property, value]) => {
        el.style[property] = value;
    });
    
    // Create intersection observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // When element enters viewport
                el.style.transition = `all ${duration}ms ${easing}`;
                
                Object.entries(selectedAnimation.animate).forEach(([property, value]) => {
                    el.style[property] = value;
                });
                
                // If once is true, unobserve after animation
                if (once) {
                    observer.unobserve(el);
                }
            } else if (!once) {
                // Reset animation if not once
                Object.entries(selectedAnimation.initial).forEach(([property, value]) => {
                    el.style[property] = value;
                });
            }
        });
    }, {
        threshold: threshold
    });
    
    // Start observing
    observer.observe(el);
    
    // Return unobserve function
    return () => observer.unobserve(el);
}

/**
 * إنشاء رسم متحرك للتلاشي عند التمرير
 * Create a parallax scroll effect
 * 
 * @param {Element|string} element - عنصر DOM أو محدد CSS
 * @param {Object} options - خيارات الرسم المتحرك
 * @param {number} options.speed - سرعة التأثير (1 = عادي، أكبر = أسرع)
 * @param {string} options.direction - اتجاه التأثير (up, down, left, right)
 * @param {boolean} options.reverse - عكس الاتجاه
 * @returns {Function} دالة لإزالة تأثير التلاشي
 */
export function createParallax(element, {
    speed = 0.3,
    direction = 'up',
    reverse = false
}) {
    if (!browser) return () => {};
    
    // Handle reduced motion preference
    if (prefersReducedMotion()) {
        return () => {};
    }
    
    const el = resolveElements([element])[0];
    if (!el) return () => {};
    
    if (reverse) {
        speed = -speed;
    }
    
    const handleScroll = () => {
        const scrollY = window.scrollY || window.pageYOffset;
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        
        // Check if element is in viewport
        if (rect.top < windowHeight && rect.bottom > 0) {
            // Calculate position
            const elCenterY = rect.top + rect.height / 2;
            const distanceFromCenter = elCenterY - windowHeight / 2;
            
            let translateX = 0;
            let translateY = 0;
            
            switch (direction) {
                case 'up':
                case 'down':
                    translateY = distanceFromCenter * speed;
                    break;
                case 'left':
                case 'right':
                    translateX = distanceFromCenter * speed;
                    break;
            }
            
            // Apply parallax effect
            el.style.transform = `translate3d(${translateX}px, ${translateY}px, 0)`;
        }
    };
    
    // Set initial styles
    el.style.willChange = 'transform';
    
    // Add scroll event listener
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial positioning
    
    // Return cleanup function
    return () => {
        window.removeEventListener('scroll', handleScroll);
        el.style.willChange = '';
        el.style.transform = '';
    };
}

/**
 * إنشاء رسم متحرك للتحرك من خلال المراحل المختلفة
 * Create a morphing animation through different stages
 * 
 * @param {Element|string} element - عنصر DOM أو محدد CSS
 * @param {Array<Object>} stages - مراحل الرسم المتحرك
 * @param {Object} options - خيارات الرسم المتحرك
 * @param {number} options.duration - مدة الرسم المتحرك لكل مرحلة
 * @param {number} options.delay - التأخير بين المراحل
 * @param {string} options.easing - نوع الإيزنج
 * @returns {Promise<void>} وعد يكتمل عند انتهاء جميع المراحل
 */
export function animateMorph(element, stages, {
    duration = 500,
    delay = 0,
    easing = 'easeInOutCubic'
}) {
    if (!browser) return Promise.resolve();
    
    // Handle reduced motion preference
    if (prefersReducedMotion()) {
        const el = resolveElements([element])[0];
        if (el && stages.length > 0) {
            const finalStage = stages[stages.length - 1];
            Object.entries(finalStage).forEach(([property, value]) => {
                el.style[property] = value;
            });
        }
        return Promise.resolve();
    }
    
    return new Promise(resolve => {
        const el = resolveElements([element])[0];
        if (!el || stages.length === 0) {
            resolve();
            return;
        }
        
        let currentStage = 0;
        
        function animateNextStage() {
            if (currentStage >= stages.length) {
                resolve();
                return;
            }
            
            const targetStyles = stages[currentStage];
            const currentStyles = {};
            
            // Get current computed styles as starting point
            Object.keys(targetStyles).forEach(property => {
                currentStyles[property] = window.getComputedStyle(el)[property];
            });
            
            // Animate to target styles
            el.style.transition = `all ${duration}ms ${easing}`;
            
            Object.entries(targetStyles).forEach(([property, value]) => {
                el.style[property] = value;
            });
            
            // Wait for transition to complete before moving to next stage
            setTimeout(() => {
                currentStage++;
                animateNextStage();
            }, duration + delay);
        }
        
        // Start animation
        animateNextStage();
    });
}

/**
 * إنشاء تأثير كتابة للنص
 * Create a typing effect for text
 * 
 * @param {Element|string} element - عنصر DOM أو محدد CSS
 * @param {string} text - النص المراد كتابته
 * @param {Object} options - خيارات الرسم المتحرك
 * @param {number} options.speed - سرعة الكتابة (مللي ثانية لكل حرف)
 * @param {number} options.initialDelay - تأخير قبل بدء الكتابة
 * @param {number} options.deleteSpeed - سرعة حذف النص (اختياري)
 * @param {boolean} options.loop - إعادة الكتابة بعد الانتهاء
 * @returns {Function} دالة لإيقاف تأثير الكتابة
 */
export function typeText(element, text, {
    speed = 50,
    initialDelay = 0,
    deleteSpeed = null,
    loop = false
}) {
    if (!browser) return () => {};
    
    // Handle reduced motion preference
    if (prefersReducedMotion()) {
        const el = resolveElements([element])[0];
        if (el) el.textContent = text;
        return () => {};
    }
    
    const el = resolveElements([element])[0];
    if (!el) return () => {};
    
    let currentIndex = 0;
    let currentText = '';
    let isDeleting = false;
    let timeoutId;
    
    function type() {
        // If deleting
        if (isDeleting) {
            currentText = text.substring(0, currentIndex - 1);
            currentIndex--;
            
            if (currentIndex === 0) {
                isDeleting = false;
                
                if (loop) {
                    timeoutId = setTimeout(type, initialDelay);
                }
                return;
            }
        } 
        // If typing
        else {
            currentText = text.substring(0, currentIndex + 1);
            currentIndex++;
            
            if (currentIndex === text.length) {
                if (loop) {
                    isDeleting = true;
                    timeoutId = setTimeout(type, 1000); // Pause before deleting
                    return;
                }
                return; // Stop if not looping
            }
        }
        
        // Update element
        el.textContent = currentText;
        
        // Calculate next delay
        const delay = isDeleting 
            ? (deleteSpeed || speed / 2)
            : speed;
        
        // Continue typing/deleting
        timeoutId = setTimeout(type, delay);
    }
    
    // Start typing after initial delay
    timeoutId = setTimeout(type, initialDelay);
    
    // Return cleanup function
    return () => {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        // Show full text when stopped
        el.textContent = text;
    };
}

/**
 * إنشاء تأثير عداد للأرقام
 * Create a number counter effect
 * 
 * @param {Element|string} element - عنصر DOM أو محدد CSS
 * @param {number} targetNumber - الرقم المستهدف
 * @param {Object} options - خيارات الرسم المتحرك
 * @param {number} options.duration - مدة الرسم المتحرك
 * @param {string} options.easing - نوع الإيزنج
 * @param {number} options.startNumber - رقم البداية
 * @param {string} options.prefix - بادئة قبل الرقم
 * @param {string} options.suffix - لاحقة بعد الرقم
 * @param {number} options.decimals - عدد الأرقام العشرية
 * @returns {Promise<void>} وعد يكتمل عند انتهاء العداد
 */
export function countNumber(element, targetNumber, {
    duration = 1500,
    easing = 'easeOutExpo',
    startNumber = 0,
    prefix = '',
    suffix = '',
    decimals = 0
}) {
    if (!browser) return Promise.resolve();
    
    // Handle reduced motion preference
    if (prefersReducedMotion()) {
        const el = resolveElements([element])[0];
        if (el) {
            const formattedNumber = Number(targetNumber).toLocaleString(undefined, {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            });
            el.textContent = `${prefix}${formattedNumber}${suffix}`;
        }
        return Promise.resolve();
    }
    
    return new Promise(resolve => {
        const el = resolveElements([element])[0];
        if (!el) {
            resolve();
            return;
        }
        
        // Ensure numbers
        targetNumber = Number(targetNumber);
        startNumber = Number(startNumber);
        
        animate({
            duration,
            from: startNumber,
            to: targetNumber,
            easing,
            onUpdate: (value) => {
                const formattedNumber = Number(value).toLocaleString(undefined, {
                    minimumFractionDigits: decimals,
                    maximumFractionDigits: decimals
                });
                el.textContent = `${prefix}${formattedNumber}${suffix}`;
            },
            onComplete: resolve
        });
    });
}

/**
 * تطبيق رسم متحرك يعتمد على تحرك المؤشر
 * Apply a hover animation to an element
 * 
 * @param {Element|string} element - عنصر DOM أو محدد CSS
 * @param {Object} hoverStyles - الأنماط عند تحرك المؤشر فوق العنصر
 * @param {Object} options - خيارات الرسم المتحرك
 * @param {number} options.duration - مدة الرسم المتحرك
 * @param {string} options.easing - نوع الإيزنج
 * @returns {Function} دالة لإزالة تأثير التحرك
 */
export function createHoverEffect(element, hoverStyles, {
    duration = 300,
    easing = 'easeOutCubic'
}) {
    if (!browser) return () => {};
    
    const el = resolveElements([element])[0];
    if (!el) return () => {};
    
    // Store original styles
    const originalStyles = {};
    
    Object.keys(hoverStyles).forEach(property => {
        originalStyles[property] = el.style[property] || '';
    });
    
    // Set transition
    el.style.transition = `all ${duration}ms ${easing}`;
    
    // Event handlers
    function handleMouseEnter() {
        Object.entries(hoverStyles).forEach(([property, value]) => {
            el.style[property] = value;
        });
    }
    
    function handleMouseLeave() {
        Object.entries(originalStyles).forEach(([property, value]) => {
            el.style[property] = value;
        });
    }
    
    // Add event listeners
    el.addEventListener('mouseenter', handleMouseEnter);
    el.addEventListener('mouseleave', handleMouseLeave);
    
    // Return cleanup function
    return () => {
        el.removeEventListener('mouseenter', handleMouseEnter);
        el.removeEventListener('mouseleave', handleMouseLeave);
        el.style.transition = '';
        
        Object.entries(originalStyles).forEach(([property, value]) => {
            el.style[property] = value;
        });
    };
}

/**
 * تحويل محددات CSS إلى عناصر DOM
 * Resolve selectors to DOM elements
 * 
 * @param {Array<Element|string>} elements - عناصر DOM أو محددات CSS
 * @returns {Array<Element>} مصفوفة من عناصر DOM
 */
function resolveElements(elements) {
    if (!browser) return [];
    
    return elements.map(element => {
        if (typeof element === 'string') {
            return document.querySelector(element);
        }
        return element;
    }).filter(Boolean);
}