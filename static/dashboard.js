(() => {
    const toastStack = document.querySelector("[data-toast-stack]");

    const ui = {
        showToast(message, tone = "info", title = "Dashboard") {
            if (!toastStack) {
                return;
            }

            const toast = document.createElement("article");
            toast.className = "toast";
            toast.dataset.tone = tone;
            toast.innerHTML = `
                <div class="toast-title">${title}</div>
                <div class="toast-body">${message}</div>
            `;

            toastStack.appendChild(toast);
            requestAnimationFrame(() => toast.classList.add("is-visible"));

            window.setTimeout(() => {
                toast.classList.remove("is-visible");
                window.setTimeout(() => toast.remove(), 220);
            }, 3200);
        },
    };

    window.dashboardUI = ui;

    const initClock = () => {
        const clock = document.querySelector("[data-live-clock]");
        if (!clock) {
            return;
        }

        const render = () => {
            const formatter = new Intl.DateTimeFormat("de-DE", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
            });
            clock.textContent = formatter.format(new Date());
        };

        render();
        window.setInterval(render, 1000);
    };

    const initReveal = () => {
        const items = document.querySelectorAll(".reveal");
        if (!items.length) {
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.16 }
        );

        items.forEach((item) => observer.observe(item));
    };

    const initCopyButtons = () => {
        document.addEventListener("click", async (event) => {
            const trigger = event.target.closest("[data-copy]");
            if (!trigger) {
                return;
            }

            const value = trigger.dataset.copy || "";
            const label = trigger.dataset.copyLabel || "Wert";
            if (!value) {
                return;
            }

            try {
                await navigator.clipboard.writeText(value);
                ui.showToast(`${label} wurde in die Zwischenablage kopiert.`, "success", "Kopiert");
            } catch (error) {
                ui.showToast("Kopieren ist in diesem Browser gerade nicht verfuegbar.", "error", "Fehler");
            }
        });
    };

    const initTiltPanels = () => {
        const panels = document.querySelectorAll("[data-tilt]");
        panels.forEach((panel) => {
            panel.addEventListener("pointermove", (event) => {
                const rect = panel.getBoundingClientRect();
                const x = ((event.clientX - rect.left) / rect.width) * 100;
                const y = ((event.clientY - rect.top) / rect.height) * 100;
                panel.style.setProperty("--pointer-x", `${x}%`);
                panel.style.setProperty("--pointer-y", `${y}%`);
            });
        });
    };

    initClock();
    initReveal();
    initCopyButtons();
    initTiltPanels();
})();
