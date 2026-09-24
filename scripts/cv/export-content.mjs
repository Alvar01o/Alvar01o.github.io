// Exporta el contenido bilingüe de la web (src/i18n/content.ts) a JSON para generar los PDF del CV.
import { content, site } from '../../src/i18n/content.ts';
process.stdout.write(JSON.stringify({ content, site }));
