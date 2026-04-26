# NS Reisadvies — moved

This Home Assistant integration has moved to its own dedicated repository
so it can be installed and kept up to date via HACS.

**New location:** <https://github.com/Meppies/ha-ns-reisadvies>

## Why the move

HACS does not support installing integrations from sub-folders inside a
monorepo. To get into the standard HACS install flow — Custom repositories
today, the default HACS list later — the integration needs to live at the
root of its own repository, in the layout `custom_components/<domain>/`.
Splitting it out also gives it its own release history, an issue tracker
scoped to just this integration, and CI that runs on every commit.

## What is at the new repository

- HACS-compatible Home Assistant integration in
  `custom_components/ns_reisadvies/`.
- Companion Lovelace card, auto-registered by the integration.
- Tagged releases with changelog notes.
- GitHub Actions running Hassfest and the HACS validator on every push.

## Installing

In Home Assistant, open HACS → *Integrations → ⋮ → Custom repositories*.
Add the URL `https://github.com/Meppies/ha-ns-reisadvies` with category
*Integration*, then *Download*. Restart Home Assistant and add the
integration via *Settings → Devices & services → Add integration →
NS Reisadvies*.

## Issues and feature requests

Please open them at <https://github.com/Meppies/ha-ns-reisadvies/issues>
rather than here, so the discussion stays close to the code.
