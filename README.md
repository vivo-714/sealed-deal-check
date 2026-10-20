# Flipr

The live TCG price index, from MSRP to market.

A small phone app for checking Pokémon sealed product prices (ETB, Pokémon Center ETB, Booster Bundle, Booster Box) against MSRP, current online price (TCGplayer) and market price (PriceCharting recent sold average).

- `index.html` – the app
- `prices.json` – the price list. Update the numbers and `asOf` date here to refresh prices for every device.
- `sw.js`, `manifest.webmanifest`, `icon-*.png` – home-screen install and offline support

Price edits made inside the app are saved only on that device.
