/* ============================================================
   ChicShop — home.js
   Spécifique à la page d'accueil :
   - Timer vente flash
   - Rotation des prénoms dans le hero
   ============================================================ */

'use strict';

/* ===== FLASH SALE TIMER ===== */
(function() {
    // Fin de la vente flash : +6h à partir du chargement (peut être dynamisé via data-attr)
    const endTs = Date.now() + (5 * 3600 + 47 * 60 + 23) * 1000;

    function tick() {
        const diff = Math.max(0, Math.floor((endTs - Date.now()) / 1000));
        const h = Math.floor(diff / 3600);
        const m = Math.floor((diff % 3600) / 60);
        const s = diff % 60;
        const pad = n => String(n).padStart(2, '0');
        const elH = document.getElementById('fh');
        const elM = document.getElementById('fm');
        const elS = document.getElementById('fs');
        if (elH) elH.textContent = pad(h);
        if (elM) elM.textContent = pad(m);
        if (elS) elS.textContent = pad(s);
        if (diff === 0) clearInterval(timer);
    }
    tick();
    const timer = setInterval(tick, 1000);
})();

/* ===== ROTATION PRÉNOMS HERO ===== */
(function() {
    const heroNames = ['Fatima', 'Ibrahim', 'Maïssa', 'Aminata', 'Mohamed', 'Aïcha', 'Kadiatou', 'Alpha'];
    let idx = 0;

    setInterval(() => {
        idx = (idx + 1) % heroNames.length;
        const el = document.getElementById('heroName');
        if (!el) return;
        el.style.opacity = '0';
        el.style.transform = 'translateY(-6px)';
        setTimeout(() => {
            el.textContent = heroNames[idx];
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 400);
    }, 3000);
})();

document.addEventListener('DOMContentLoaded', () => {
    const track = document.querySelector('.carousel-track');
    if (!track) return; // Pas de carrousel sur cette page
    const slides = Array.from(track.children);
    const nextButton = document.querySelector('.next-btn');
    const prevButton = document.querySelector('.prev-btn');
    const dotsNav = document.querySelector('.carousel-nav');
    if (!nextButton || !prevButton || !dotsNav) return; //elements manquants
    const dots = Array.from(dotsNav.children);

    let currentIndex = 0;

    // Fonction pour obtenir le nombre de slides visibles selon l'écran
    const getVisibleSlidesCount = () => {
        if (window.innerWidth >= 1024) return 4;
        if (window.innerWidth >= 600) return 2;
        return 1;
    };

    // Déplace le carrousel à la bonne position
    const moveToSlide = (index) => {
        const slideWidth = slides[0].getBoundingClientRect().width;
        track.style.transform = `translateX(-${index * slideWidth}px)`;

        // Mise à jour des classes actives pour les dots
        dots.forEach(dot => dot.classList.remove('active'));
        if (dots[index]) dots[index].classList.add('active');

        currentIndex = index;
    };

    // Gestion du clic sur le bouton Suivant
    nextButton.addEventListener('click', () => {
        const visibleSlides = getVisibleSlidesCount();
        const maxIndex = slides.length - visibleSlides;

        if (currentIndex < maxIndex) {
            moveToSlide(currentIndex + 1);
        } else {
            moveToSlide(0); // Boucle et revient au début
        }
    });

    // Gestion du clic sur le bouton Précédent
    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            moveToSlide(currentIndex - 1);
        } else {
            const visibleSlides = getVisibleSlidesCount();
            moveToSlide(slides.length - visibleSlides); // Va à la fin
        }
    });

    // Navigation via les points (dots)
    dotsNav.addEventListener('click', e => {
        const targetDot = e.target.closest('button');
        if (!targetDot) return;

        const targetIndex = dots.indexOf(targetDot);
        const visibleSlides = getVisibleSlidesCount();

        // Empêche de scroller dans le vide sur desktop
        if (targetIndex <= slides.length - visibleSlides) {
            moveToSlide(targetIndex);
        }
    });

    // Ajustement de la position lors du redimensionnement de la fenêtre
    window.addEventListener('resize', () => {
        moveToSlide(0);
    });
});