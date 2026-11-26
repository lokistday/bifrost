/* Hash text consistently across Git checkouts. Binary assets retain their exact bytes. */
const { createHash } = require('node:crypto');
module.exports = function fingerprint(...parts) {
  const hash = createHash('sha256');
  for (const part of parts) hash.update(typeof part === 'string' ? part.replace(/\r\n/g, '\n') : part);
  return hash.digest('hex').slice(0, 12);
};
