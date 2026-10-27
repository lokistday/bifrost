/* Meta-compatible CSP for static hosting. Header-only protections are documented. */
const policy = "default-src 'self'; script-src 'self'; script-src-attr 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-src 'self'";
function protect(html) {
  const tags = `<meta http-equiv="Content-Security-Policy" content="${policy}">\n<meta name="referrer" content="no-referrer">`;
  if (!/<meta charset="utf-8">/i.test(html)) throw new Error('Charset required before security metadata');
  return html.replace(/<meta charset="utf-8">/i, '<meta charset="utf-8">\n' + tags);
}
module.exports = { policy, protect };
