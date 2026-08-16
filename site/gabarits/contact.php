<?php
declare(strict_types=1);
/* ===========================================================================
 * contact.php — le traitement du formulaire de contact de l'Observatoire
 * ===========================================================================
 * À déposer à côté de `contact.html`, à la racine du sous-domaine.
 *
 * PARTI PRIS : aucun service tiers, aucun captcha externe, aucun cookie.
 * Le site affiche « la recherche se fait dans votre navigateur : aucune
 * requête n'est envoyée ». Poser un reCAPTCHA sur la page de contact
 * contredirait cette phrase — et ce serait la seule page du site à déposer un
 * traceur. La protection est donc entièrement portée ici, par cinq barrières
 * qui se cumulent et dont aucune n'est visible pour un visiteur légitime :
 *
 *   1. le piège   — un champ que seul un robot remplit ;
 *   2. le temps   — un envoi arrivé en moins de 4 s n'est pas humain ;
 *   3. l'origine  — un POST qui ne vient pas d'une page de ce domaine ;
 *   4. le débit   — 3 messages par heure et par adresse, 40 par jour en tout ;
 *   5. le contenu — deux liens ou plus, ou un champ hors bornes.
 *
 * Une sixième barrière est passive et vaut les cinq autres : l'adresse de
 * destination n'apparaît nulle part dans le HTML servi. Les robots moissonnent
 * les pages, pas les scripts.
 *
 * RÉPONSE : jamais de page rendue ici. On renvoie (303) vers
 * `contact.html#envoye` ou `contact.html#refuse`, et la feuille de style
 * révèle le bloc correspondant par `:target`. C'est le motif Post/Redirect/Get :
 * un rechargement ne renvoie pas le message, et l'accusé de réception ne
 * dépend d'aucun JavaScript.
 *
 * SILENCE : un message rejeté par le piège ou par le débit repart avec le même
 * « envoyé » qu'un message accepté. Dire à un robot pourquoi il a échoué, c'est
 * lui donner le moyen de réessayer autrement.
 * ---------------------------------------------------------------------------
 */

/* ---------------------------------------------------------------------------
 * 1. RÉGLAGES — les seules lignes à toucher
 * ------------------------------------------------------------------------- */

/** Où arrivent les messages. */
const DESTINATAIRE = 'eau@mytae.fr';

/** L'expéditeur technique. DOIT appartenir à un domaine dont le SPF autorise
 *  le serveur qui envoie — ici Hostinger. Ce n'est jamais l'adresse du
 *  visiteur : elle va en `Reply-To`.
 *
 *  CORRIGÉ LE 16 AOÛT 2026, sur relevé DNS et non sur supposition. La valeur
 *  d'origine était `no-reply@mytae.fr`, et elle aurait envoyé chaque message
 *  en indésirable :
 *
 *    mytae.fr           SPF  include:_spf.protonmail.ch (+ autorépondeur)
 *                       MX   protonmail          DMARC  p=quarantine, pct=100
 *    yannick-mytae.fr   SPF  include:_spf.mail.hostinger.com
 *                       MX   hostinger           DMARC  p=none
 *
 *  La messagerie de `mytae.fr` est chez Proton, le site est chez Hostinger.
 *  Un envoi PHP depuis Hostinger au nom de `mytae.fr` échoue SPF, n'a aucun
 *  DKIM aligné, et tombe donc sous le `p=quarantine` que le domaine publie
 *  lui-même. Créer la boîte chez Proton n'y change rien : elle autorise à
 *  écrire DEPUIS Proton, pas depuis un serveur web tiers.
 *
 *  `yannick-mytae.fr` autorise déjà Hostinger — c'est le domaine du site.
 *  Le message part de là et arrive sur `eau@mytae.fr` chez Proton, qui le
 *  reçoit sans difficulté : recevoir n'a jamais demandé d'autorisation SPF.
 *
 *  À FAIRE CÔTÉ HÉBERGEUR : créer `no-reply@yannick-mytae.fr` dans hPanel,
 *  même sans boîte associée, pour que les rejets aient où retomber. */
const EXPEDITEUR     = 'no-reply@yannick-mytae.fr';
const EXPEDITEUR_NOM = 'Observatoire de la potabilite reglementaire';

/** Le domaine du site, sans barre finale. Sert au contrôle d'origine. */
const SITE = 'https://eau.yannick-mytae.fr';

/** La page à laquelle on renvoie. */
const RETOUR = '/contact.html';

/** Où le compteur de débit est tenu. Idéalement HORS du dossier web :
 *  sur hPanel, `public_html` est le dossier web, son parent ne l'est pas. */
const FICHIER_DEBIT = __DIR__ . '/../.contact-debit.json';

/** Les barrières, en clair. */
const DELAI_MINIMAL   = 4;     // secondes entre l'ouverture et l'envoi
const DELAI_MAXIMAL   = 7200;  // au-delà, la page traînait ouverte : on refuse
const MAX_PAR_IP_HEURE = 3;
const MAX_GLOBAL_JOUR  = 40;
const LIENS_MAXIMUM    = 1;    // au-delà, c'est de la publicité

/** Les motifs acceptés — la même liste que le `<select>` de la page. Un motif
 *  hors liste est un POST fabriqué à la main. */
const MOTIFS = [
    'erreur'      => 'Signalement d\'erreur',
    'source'      => 'Versement de source primaire',
    'departement' => 'Demande de collecte d\'un departement',
    'presse'      => 'Presse, elus, associations',
    'donnees'     => 'Question donnees ou methode',
    'autre'       => 'Autre',
];

/* ---------------------------------------------------------------------------
 * 2. OUTILS
 * ------------------------------------------------------------------------- */

/** Repart vers la page, sans jamais rendre de HTML ici. */
function repartir(string $ancre): never
{
    header('Location: ' . RETOUR . '#' . $ancre, true, 303);
    header('Cache-Control: no-store');
    exit;
}

/** Une valeur de formulaire, nettoyée : les retours à la ligne d'un champ
 *  d'une seule ligne sont le vecteur de l'injection d'en-tête SMTP. Un
 *  `\r\n` glissé dans le nom permettrait d'ajouter un `Bcc:`. */
function champ(string $cle, bool $multiligne = false): string
{
    $v = (string)($_POST[$cle] ?? '');
    $v = str_replace("\0", '', $v);
    if (!$multiligne) {
        $v = preg_replace('/[\r\n\t]+/u', ' ', $v) ?? '';
    } else {
        $v = str_replace("\r\n", "\n", $v);
        $v = preg_replace('/[^\P{C}\n]+/u', '', $v) ?? $v;
    }
    return trim($v);
}

/** Le sujet d'un courriel doit être encodé s'il porte des accents. */
function sujet_mime(string $s): string
{
    return '=?UTF-8?B?' . base64_encode($s) . '?=';
}

/** L'adresse du demandeur, telle que le serveur la voit. Derrière un
 *  répartiteur, `REMOTE_ADDR` est celle du répartiteur : on lit alors
 *  l'en-tête transmis, en ne gardant que le premier saut. */
function adresse(): string
{
    foreach (['HTTP_CF_CONNECTING_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'] as $c) {
        if (!empty($_SERVER[$c])) {
            $v = explode(',', (string)$_SERVER[$c])[0];
            $v = trim($v);
            if (filter_var($v, FILTER_VALIDATE_IP)) {
                return $v;
            }
        }
    }
    return '0.0.0.0';
}

/**
 * Le compteur de débit.
 *
 * Un fichier JSON, un verrou exclusif, et rien de plus : pas de base, pas de
 * session, pas de cookie. Les adresses n'y sont pas écrites en clair — un
 * condensat suffit à compter, et un fichier de journalisation d'adresses IP
 * serait une collecte de données personnelles que ce formulaire n'a aucune
 * raison de faire.
 *
 * Renvoie true si l'envoi est autorisé.
 */
function debit_autorise(string $ip): bool
{
    $maintenant = time();
    $cle = hash('sha256', $ip . '|' . EXPEDITEUR);   // sel constant, jamais l'IP en clair

    $f = @fopen(FICHIER_DEBIT, 'c+');
    if ($f === false) {
        return true;   // pas de compteur possible : on n'interdit pas d'écrire
    }
    if (!flock($f, LOCK_EX)) {
        fclose($f);
        return true;
    }
    $brut = stream_get_contents($f) ?: '';
    $etat = json_decode($brut, true);
    if (!is_array($etat)) {
        $etat = ['par_ip' => [], 'jour' => []];
    }

    // On oublie tout ce qui a plus d'une heure (par adresse) ou d'un jour (global).
    foreach ($etat['par_ip'] as $k => $liste) {
        $etat['par_ip'][$k] = array_values(array_filter(
            $liste,
            static fn($t) => $t > $maintenant - 3600
        ));
        if (!$etat['par_ip'][$k]) {
            unset($etat['par_ip'][$k]);
        }
    }
    $etat['jour'] = array_values(array_filter(
        $etat['jour'],
        static fn($t) => $t > $maintenant - 86400
    ));

    $ok = count($etat['par_ip'][$cle] ?? []) < MAX_PAR_IP_HEURE
       && count($etat['jour']) < MAX_GLOBAL_JOUR;

    if ($ok) {
        $etat['par_ip'][$cle][] = $maintenant;
        $etat['jour'][] = $maintenant;
    }

    ftruncate($f, 0);
    rewind($f);
    fwrite($f, json_encode($etat));
    fflush($f);
    flock($f, LOCK_UN);
    fclose($f);
    return $ok;
}

/* ---------------------------------------------------------------------------
 * 3. LES CINQ BARRIÈRES
 * ------------------------------------------------------------------------- */

// -- 0. la méthode ----------------------------------------------------------
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    repartir('refuse');
}

// -- 1. le piège ------------------------------------------------------------
// Ce champ est masqué et retiré du parcours clavier. Rempli = robot.
// On repart avec « envoyé » : lui dire non l'inviterait à recommencer.
if (champ('site_web') !== '') {
    repartir('envoye');
}

// -- 3. l'origine (contrôlée avant le temps : moins coûteuse) ---------------
// Un POST légitime vient d'une page de ce domaine. Les deux en-têtes sont
// falsifiables, mais la grande majorité des robots ne les posent pas du tout.
$origine = (string)($_SERVER['HTTP_ORIGIN'] ?? '');
$referent = (string)($_SERVER['HTTP_REFERER'] ?? '');
$provenance = $origine !== '' ? $origine : $referent;
if ($provenance === '' || !str_starts_with($provenance, SITE)) {
    repartir('envoye');
}

// -- 2. le temps ------------------------------------------------------------
// Posé par le navigateur à l'ouverture, en millisecondes. Absent = pas de
// JavaScript : on ne s'en sert pas, et le visiteur n'est jamais bloqué pour
// cette raison. Présent = il doit être cohérent.
$ouvert = (string)($_POST['ouvert_a'] ?? '');
if ($ouvert !== '' && ctype_digit($ouvert)) {
    $ecoule = time() - (int)((int)$ouvert / 1000);
    if ($ecoule < DELAI_MINIMAL || $ecoule > DELAI_MAXIMAL) {
        repartir('envoye');
    }
}

// -- les champs, et leurs bornes -------------------------------------------
$nom      = champ('nom');
$courriel = champ('courriel');
$objet    = champ('objet');
$page     = champ('page');
$message  = champ('message', true);
$accord   = (string)($_POST['accord'] ?? '');

$valide = $accord === '1'
    && mb_strlen($nom) >= 2      && mb_strlen($nom) <= 80
    && mb_strlen($courriel) <= 120
    && filter_var($courriel, FILTER_VALIDATE_EMAIL) !== false
    && isset(MOTIFS[$objet])
    && mb_strlen($page) <= 200
    && mb_strlen($message) >= 20 && mb_strlen($message) <= 4000;

if (!$valide) {
    // Ici, et ici seulement, on le dit : c'est presque toujours un humain qui
    // a oublié un champ, et le laisser dans le doute serait cruel.
    repartir('refuse');
}

// -- 5. le contenu ----------------------------------------------------------
// Deux liens ou plus dans le message, ou un lien dans le nom : c'est de la
// publicité. Un signalement d'erreur en porte un au plus — la page concernée,
// et elle a son propre champ.
$liens = preg_match_all('~\bhttps?://|\bwww\.~i', $message . ' ' . $nom);
if ($liens > LIENS_MAXIMUM || preg_match('~https?://|\[url~i', $nom)) {
    repartir('envoye');
}
// La page concernée, si elle est donnée, doit être une adresse de ce site.
if ($page !== '' && !preg_match('~^https?://~i', $page)) {
    $page = SITE . '/' . ltrim($page, '/');
}
if ($page !== '' && !str_starts_with($page, SITE)) {
    $page = '(hors du site) ' . $page;
}

// -- 4. le débit ------------------------------------------------------------
if (!debit_autorise(adresse())) {
    repartir('envoye');
}

/* ---------------------------------------------------------------------------
 * 4. L'ENVOI
 * ------------------------------------------------------------------------- */

$corps = implode("\n", [
    'Motif    : ' . MOTIFS[$objet],
    'Nom      : ' . $nom,
    'Courriel : ' . $courriel,
    'Page     : ' . ($page !== '' ? $page : '—'),
    'Reçu le  : ' . date('d/m/Y à H:i'),
    '',
    str_repeat('-', 60),
    '',
    $message,
    '',
    str_repeat('-', 60),
    'Envoyé depuis le formulaire de ' . SITE . RETOUR,
    'Répondre à ce message écrit directement à l\'expéditeur.',
]);

// `Reply-To` porte l'adresse du visiteur ; `From` reste le domaine du site.
// Inverser les deux ferait échouer SPF et enverrait tout en indésirable.
$entetes = implode("\r\n", [
    'From: ' . EXPEDITEUR_NOM . ' <' . EXPEDITEUR . '>',
    'Reply-To: ' . sujet_mime($nom) . ' <' . $courriel . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'Auto-Submitted: auto-generated',
    'X-Mailer: contact.php (Observatoire)',
]);

$envoye = @mail(
    DESTINATAIRE,
    sujet_mime('[Observatoire] ' . MOTIFS[$objet] . ' — ' . $nom),
    $corps,
    $entetes,
    '-f' . EXPEDITEUR
);

repartir($envoye ? 'envoye' : 'refuse');
