"""Minimal in-process i18n.

A flat catalog maps a semantic key to its translations. `t(key, **kwargs)`
returns the string for the active language (falling back to English, then to the
key itself) and applies `str.format(**kwargs)` for interpolated values.

The language switch is applied live by rebuilding the UI (see App.apply_language),
so widgets simply call `t(...)` at construction time and always read the current
language — no per-widget retranslate bookkeeping needed.
"""

DEFAULT_LANGUAGE = "en"

# Display name -> language code, for the Settings language selector.
LANGUAGES = {"English": "en", "Italiano": "it"}

_TRANSLATIONS = {
    # ── Menu bar ────────────────────────────────────────────────────────────
    "menu.file": {"en": "File", "it": "File"},
    "menu.create_credential": {"en": "Create Credential", "it": "Crea credenziale"},
    "menu.settings": {"en": "Settings", "it": "Impostazioni"},
    "menu.exit": {"en": "Exit", "it": "Esci"},
    "menu.help": {"en": "Help", "it": "Help"},
    "menu.check_updates": {"en": "Check for Updates", "it": "Controlla aggiornamenti"},
    "menu.donate": {"en": "♥ Donate (PayPal)", "it": "♥ Dona (PayPal)"},
    "menu.about": {"en": "About", "it": "Informazioni"},

    # ── Update checker ────────────────────────────────────────────────────────
    "update.available_title": {"en": "Update available", "it": "Aggiornamento disponibile"},
    "update.available_msg": {
        "en": "Version {version} is available.\n\nOpen the download page?",
        "it": "È disponibile la versione {version}.\n\nVuoi aprire la pagina di download?",
    },
    "update.uptodate_title": {"en": "Up to date", "it": "Aggiornato"},
    "update.uptodate_msg": {
        "en": "You are running the latest version.",
        "it": "Stai usando l'ultima versione.",
    },
    "update.failed_title": {"en": "Update check failed", "it": "Controllo non riuscito"},
    "update.failed_msg": {
        "en": "Could not check for updates.",
        "it": "Impossibile controllare gli aggiornamenti.",
    },

    # ── Common ──────────────────────────────────────────────────────────────
    "common.back": {"en": "← Back", "it": "← Indietro"},
    "common.save": {"en": "Save", "it": "Salva"},
    "common.ok": {"en": "OK", "it": "OK"},
    "common.yes": {"en": "Yes", "it": "Sì"},
    "common.no": {"en": "No", "it": "No"},

    # ── Toast titles ──────────────────────────────────────────────────────────
    "toast.error": {"en": "Error", "it": "Errore"},
    "toast.settings": {"en": "Settings", "it": "Impostazioni"},
    "toast.saved": {"en": "Saved", "it": "Salvato"},
    "toast.created": {"en": "Created", "it": "Creato"},
    "toast.deleted": {"en": "Deleted", "it": "Eliminato"},
    "toast.test": {"en": "Test", "it": "Test"},
    "toast.not_found": {"en": "Not Found", "it": "Nessun risultato"},

    # ── Search ──────────────────────────────────────────────────────────────
    "search.placeholder": {"en": "Insert credential ID", "it": "Inserisci ID credenziale"},
    "search.missing_settings": {
        "en": "Missing server, username and/or password",
        "it": "Server, username e/o password mancanti",
    },
    "search.wrong_auth": {
        "en": "Wrong server, username and/or password",
        "it": "Server, username e/o password errati",
    },
    "search.not_found": {
        "en": "No credentials found for: {term}",
        "it": "Nessuna credenziale trovata per: {term}",
    },

    # ── Result / credential details ───────────────────────────────────────────
    "result.id": {"en": "ID", "it": "ID"},
    "result.deleted": {"en": "'{id}' deleted", "it": "'{id}' eliminata"},
    "tooltip.copy_id": {"en": "Copy ID", "it": "Copia ID"},
    "tooltip.delete_credential": {"en": "Delete credential", "it": "Elimina credenziale"},
    "tooltip.edit": {"en": "Edit", "it": "Modifica"},
    "tooltip.save_changes": {"en": "Save changes", "it": "Salva modifiche"},
    "tooltip.copy_secret": {"en": "Copy secret", "it": "Copia Secret"},
    "tooltip.copy_username": {"en": "Copy username", "it": "Copia username"},
    "tooltip.copy_password": {"en": "Copy password", "it": "Copia password"},
    "tooltip.show_hide_secret": {"en": "Show / hide secret", "it": "Mostra / nascondi Secret"},
    "tooltip.show_hide_password": {"en": "Show / hide password", "it": "Mostra / nascondi password"},
    "contextmenu.download": {"en": "download", "it": "scarica"},
    "dialog.save_file": {"en": "Save file", "it": "Salva file"},
    "credential.updated": {"en": "'{id}' updated", "it": "'{id}' aggiornata"},
    "field.secret": {"en": "Secret", "it": "Secret"},
    "field.username": {"en": "Username", "it": "Username"},
    "field.password": {"en": "Password", "it": "Password"},

    # ── Create credential ─────────────────────────────────────────────────────
    "create.title": {"en": "Create Credential", "it": "Crea credenziale"},
    "create.type": {"en": "Credential Type", "it": "Tipo di credenziale"},
    "create.id": {"en": "Credential ID", "it": "ID credenziale"},
    "create.secret": {"en": "Secret:", "it": "Secret:"},
    "create.username": {"en": "Username:", "it": "Username:"},
    "create.password": {"en": "Password:", "it": "Password:"},
    "create.button": {"en": "Create", "it": "Crea"},
    "create.err_id": {"en": "Please enter a credential ID.", "it": "Inserisci un ID credenziale."},
    "create.err_secret": {"en": "Please enter a secret.", "it": "Inserisci un Secret."},
    "create.err_username": {"en": "Please enter a username.", "it": "Inserisci un username."},
    "create.err_password": {"en": "Please enter a password.", "it": "Inserisci una password."},
    "create.created": {"en": "'{id}' created", "it": "'{id}' creata"},

    # ── Settings ──────────────────────────────────────────────────────────────
    "settings.connection": {"en": "Jenkins connection", "it": "Connessione Jenkins"},
    "settings.server": {"en": "Server address", "it": "Indirizzo server"},
    "settings.server_hint": {
        "en": "e.g. https://jenkins.company.com",
        "it": "es. https://jenkins.azienda.com",
    },
    "settings.username": {"en": "Username", "it": "Username"},
    "settings.token": {"en": "API token", "it": "Token API"},
    "settings.test_button": {"en": "Test connection", "it": "Prova connessione"},
    "settings.appearance": {"en": "Appearance", "it": "Aspetto"},
    "settings.theme": {"en": "Theme", "it": "Tema"},
    "settings.light": {"en": "Light", "it": "Chiaro"},
    "settings.dark": {"en": "Dark", "it": "Scuro"},
    "settings.language": {"en": "Language", "it": "Lingua"},
    "settings.test_ok": {"en": "Connection successful", "it": "Connessione riuscita"},
    "settings.test_fail": {"en": "Could not connect to Jenkins", "it": "Impossibile connettersi a Jenkins"},
    "settings.save_untested": {
        "en": "You have not tested the connection to the server.\nDo you want to continue?",
        "it": "Non hai provato la connessione al server.\nVuoi continuare?",
    },
    "settings.keyring_unavailable": {
        "en": "OS keyring unavailable: token stored in config file",
        "it": "Keyring di sistema non disponibile: token salvato nel file di configurazione",
    },
    "settings.saved": {"en": "Settings saved", "it": "Impostazioni salvate"},

    # ── Delete confirmation ───────────────────────────────────────────────────
    "delete.confirm_title": {"en": "Confirm Delete", "it": "Conferma eliminazione"},
    "delete.confirm_msg": {
        "en": "Are you sure you want to permanently delete:\n\n    \"{id}\"\n\nThis action cannot be undone.",
        "it": "Vuoi davvero eliminare definitivamente:\n\n    \"{id}\"\n\nL'operazione non può essere annullata.",
    },
    "delete.type_prompt": {
        "en": "Type \"delete\" to permanently delete \"{id}\":",
        "it": "Scrivi \"delete\" per eliminare definitivamente \"{id}\":",
    },

    # ── About ─────────────────────────────────────────────────────────────────
    "about.title": {"en": "About", "it": "Informazioni"},
    "about.version": {"en": "Version {version}", "it": "Versione {version}"},
    "about.description": {
        "en": "Search and decrypt Jenkins credentials.",
        "it": "Cerca e decifra credenziali Jenkins.",
    },
    "about.github": {"en": "GitHub repository", "it": "Repository GitHub"},
    "about.support": {"en": "♥ Support", "it": "♥ Supporta"},
}

_language = DEFAULT_LANGUAGE


def set_language(lang):
    """Set the active language code ('en' / 'it'). Unknown codes fall back to
    the default."""
    global _language
    _language = lang if lang in ("en", "it") else DEFAULT_LANGUAGE


def get_language():
    return _language


def t(key, **kwargs):
    entry = _TRANSLATIONS.get(key)
    if entry is None:
        text = key  # missing key: surface it instead of crashing
    else:
        text = entry.get(_language) or entry.get(DEFAULT_LANGUAGE) or key
    return text.format(**kwargs) if kwargs else text
