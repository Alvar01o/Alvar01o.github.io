import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const site = 'https://alvar01o.github.io';

// Sitio 100% estático. Cambia `site` por tu dominio final (sitemap, canonical, OG).
export default defineConfig({
  site,
  output: 'static',
  trailingSlash: 'always',
  integrations: [
    sitemap({
      filter: (page) => page !== `${site}/`, // la raíz solo redirige a /es/ o /en/
      i18n: { defaultLocale: 'es', locales: { es: 'es-PY', en: 'en-US' } },
    }),
  ],
  build: {
    inlineStylesheets: 'always', // el CSS va en el HTML: cero peticiones bloqueantes
  },
});
