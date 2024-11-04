from playwright.sync_api import sync_playwright
import random
import time

# Générateur d'agent utilisateur aléatoire
def user_agent_aleatoire():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, comme Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, comme Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, comme Gecko) Chrome/91.0.4472.101 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, comme Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36'
    ]
    return random.choice(user_agents)

# Fonction pour configurer le navigateur
def configurer_navigateur(playwright, proxy=None, user_agent=None):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent=user_agent if user_agent else user_agent_aleatoire(),
        proxy={"server": proxy} if proxy else None,
    )
    page = context.new_page()

    # Masquer différentes empreintes
    masquer_webgl(page)
    masquer_canvas(page)
    masquer_audiocontext(page)
    masquer_battery(page)
    masquer_webrtc(page)
    masquer_timezone(page)
    masquer_language(page, 'fr-FR')

    return browser, context, page

# Masquage des empreintes digitales WebGL
def masquer_webgl(page):
    page.add_init_script("""
        Object.defineProperty(WebGLRenderingContext.prototype, 'getParameter', {
            value: function(param) {
                if (param === 37445) return 'Intel Inc.';  // WEBGL_VENDOR
                if (param === 37446) return 'Intel Iris OpenGL Engine';  // WEBGL_RENDERER
                return WebGLRenderingContext.prototype.getParameter.call(this, param);
            }
        });
    """)

# Masquage des empreintes digitales Canvas
def masquer_canvas(page):
    page.add_init_script("""
        const toDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(...args) {
            return toDataURL.apply(this, args).replace("data:image/png;base64,", "data:image/jpeg;base64,");
        };

        const getImageData = CanvasRenderingContext2D.prototype.getImageData;
        CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {
            const data = getImageData.call(this, x, y, w, h);
            for (let i = 0; i < data.data.length; i += 4) {
                data.data[i] += Math.floor(Math.random() * 10);  // Modification légère des pixels
            }
            return data;
        };
    """)

# Masquage des empreintes AudioContext
def masquer_audiocontext(page):
    page.add_init_script("""
        const contextPrototype = AudioContext.prototype;
        const originalGetChannelData = contextPrototype.getChannelData;
        contextPrototype.getChannelData = function(...args) {
            const results = originalGetChannelData.apply(this, args);
            for (let i = 0; i < results.length; i++) {
                results[i] = results[i] + (Math.random() * 0.0000001);  // Légère modification des données audio
            }
            return results;
        };
    """)

# Masquage des empreintes Battery
def masquer_battery(page):
    page.add_init_script("""
        navigator.getBattery = async function() {
            return {
                charging: true,
                chargingTime: 0,
                dischargingTime: Infinity,
                level: 1.0
            };
        };
    """)

# Masquage des empreintes WebRTC
def masquer_webrtc(page):
    page.add_init_script("""
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                type: 'wifi',
                effectiveType: '4g',
                downlink: 10,
                rtt: 50
            })
        });

        const originalRTCPeerConnection = window.RTCPeerConnection;
        window.RTCPeerConnection = function(config) {
            config.iceServers = [];  // Empêche les serveurs STUN d'exposer l'IP locale
            return new originalRTCPeerConnection(config);
        };
    """)

# Masquage des empreintes de fuseau horaire
def masquer_timezone(page):
    page.add_init_script("""
        const timezoneOffset = new Date().getTimezoneOffset();
        Date.prototype.getTimezoneOffset = function() {
            return timezoneOffset + Math.floor(Math.random() * 60);  // Modification légère du décalage horaire
        };
    """)

# Masquage de la langue
def masquer_language(page, langue):
    page.add_init_script(f"""
        Object.defineProperty(navigator, 'language', {{
            get: () => '{langue}'
        }});

        Object.defineProperty(navigator, 'languages', {{
            get: () => ['{langue}', 'en-US']
        }});
    """)

# Fonction pour fermer la popup de consentement aux cookies et autres dialogues
def fermer_popup_si_presente(page):
    try:
        # Sélection pour les popups courantes liées aux cookies ou consentements
        popup_selectors = [
            'button[aria-label="Accepter tout"]',  # Bouton pour consentir aux cookies
            'button[aria-label="Refuser tout"]',   # Bouton pour refuser les cookies
            'button:has-text("Je refuse")',        # Refuser cookies selon d'autres variantes
            'button:has-text("Tout accepter")'     # Autre variante d'accepter
        ]
        for selector in popup_selectors:
            if page.locator(selector).count() > 0:
                print(f"Popup détectée avec le sélecteur {selector}. Tentative de fermeture...")
                page.locator(selector).click()
                page.wait_for_timeout(1000)  # Attendre un peu après avoir fermé la popup
                print("Popup fermée avec succès.")
                break
        else:
            print("Aucune popup détectée.")
    except Exception as e:
        print(f"Erreur lors de la tentative de fermeture de la popup : {e}")

# Fonction de défilement aléatoire
def defilement_aleatoire(page):
    for _ in range(random.randint(5, 10)):  # Nombre de scrolls aléatoire
        scroll_position = random.randint(100, 800)
        page.evaluate(f"window.scrollBy(0, {scroll_position})")
        page.wait_for_timeout(random.uniform(1000, 3000))  # Pause aléatoire entre les défilements

# Fonction pour cliquer sur plusieurs pages internes du site avec un temps aléatoire entre chaque
def navigation_sur_site(page, nombre_pages):
    for i in range(nombre_pages):
        page.wait_for_load_state('networkidle')  # Attendre que la page soit complètement chargée

        # Sélectionner un lien aléatoire à partir des liens internes disponibles sur la page
        liens = page.locator('a[href^="/"], a[href^="http"]')  # Amélioration du sélecteur pour capturer des liens internes et externes
        if liens.count() > 0:
            lien_choisi = liens.nth(random.randint(0, liens.count() - 1))
            url_lien = lien_choisi.get_attribute("href")
            
            if url_lien and "http" in url_lien:  # Vérifier que le lien est valide
                print(f"Visiter la page {i+1}: {url_lien}")
                lien_choisi.click()
                
                # Temps de pause aléatoire entre 1 minute et 2 minutes 30 secondes
                temps_pause = random.uniform(60, 150)  # Temps entre 60 et 150 secondes
                print(f"Attente pendant {temps_pause / 60:.2f} minutes...")
                time.sleep(temps_pause)  # Pause humaine entre les pages visitées

                # Simuler un défilement humain
                defilement_aleatoire(page)
        else:
            print("Aucun lien trouvé sur cette page.")
            break  # Si aucun lien n'est trouvé, arrêter la navigation

# Fonction pour rechercher "presse à gaufrer" et cliquer sur "popstamp.fr" avec pagination
def recherche_google_avec_pagination(page, mot_cle, url_cible, max_pages=10, nombre_pages_visiter=3):
    page.goto(f"https://www.google.fr/search?q={mot_cle}")
    current_page = 1
    
    while current_page <= max_pages:
        fermer_popup_si_presente(page)  # Fermer la popup si présente
        page.wait_for_timeout(random.uniform(2000, 4000))  # Attente aléatoire pour simuler un comportement humain

        # Défilement aléatoire dans la SERP
        defilement_aleatoire(page)

        # Chercher les résultats organiques sans paramètres dans l'URL (éviter les annonces et les URLs avec paramètres de suivi)
        liens = page.locator(f'a[href*="{url_cible}"]:not(:has-text("Annonce")):not(:has-text("Ad"))')

        if liens.count() > 0:
            # Vérification supplémentaire pour s'assurer que l'URL ne contient aucun paramètre comme "?"
            for i in range(liens.count()):
                lien = liens.nth(i).get_attribute("href")
                if lien and "?" not in lien and "gclid" not in lien and "gad_source" not in lien and "gbraid" not in lien:
                    print(f"Lien trouvé : {lien}")  # Afficher l'URL trouvée
                    liens.nth(i).click()
                    print(f"Cliqué sur {lien}")
                    
                    # Navigation sur le site une fois que le lien est cliqué
                    navigation_sur_site(page, nombre_pages_visiter)  # Visiter plusieurs pages internes
                    return  # Lien trouvé et cliqué, sortir de la fonction

        # Si le lien n'est pas trouvé, aller à la page suivante
        next_button = page.locator('a[aria-label="Page suivante"], a[aria-label="Next"]')
        if next_button.count() > 0:
            next_button.first.click()
            current_page += 1
            print(f"Passage à la page {current_page}")
        else:
            print("Le bouton 'Page suivante' n'est pas disponible.")
            break
    
    print(f"Le lien {url_cible} n'a pas été trouvé après {current_page} pages.")

# Exemple d'utilisation pour rechercher "presse à gaufrer" et cliquer sur le lien "popstamp.fr"
def main():
    with sync_playwright() as p:
        # Configuration du navigateur
        browser, context, page = configurer_navigateur(p)
        
        # Recherche "presse à gaufrer" et clique sur le lien "popstamp.fr" en paginant jusqu'à 10 pages
        recherche_google_avec_pagination(page, "presse à gaufrer popstamp", "popstamp.fr", max_pages=10, nombre_pages_visiter=5)

        # Fermer la session
        context.close()
        browser.close()

if __name__ == "__main__":
    main()
