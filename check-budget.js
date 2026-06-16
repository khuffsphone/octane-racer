#!/usr/bin/env node
// Asset budget check for the single-file build. Measures the SHIPPED footprint =
// inlined base64 bytes in index.html + any referenced on-disk assets/ files, and
// fails (exit 1) if it exceeds the 3 MB budget. Usage: node check-budget.js index.html
const fs = require('fs');
const path = process.argv[2] || 'index.html';
const LIMIT = 3 * 1024 * 1024;
const h = fs.readFileSync(path, 'utf8');

// inlined base64 payloads (data URIs)
let inlined = 0;
for (const chunk of h.split('base64,').slice(1)) {
  const m = chunk.match(/^[A-Za-z0-9+/=]+/);
  if (m) inlined += Math.floor(m[0].length * 3 / 4); // decoded byte estimate
}
// referenced asset files that actually exist on disk
let referenced = 0; const refFiles = new Set();
for (const m of h.matchAll(/['"](assets\/[^'"]+\.(?:png|jpe?g|webp))['"]/g)) refFiles.add(m[1]);
for (const f of refFiles) { try { referenced += fs.statSync(f).size; } catch (e) {} }

const total = inlined + referenced;
const mb = b => (b / 1048576).toFixed(2);
console.log(`Budget: inlined(decoded) ${mb(inlined)} MB + referenced ${mb(referenced)} MB = ${mb(total)} MB / 3.00 MB`);
if (total > LIMIT) { console.error(`OVER BUDGET by ${mb(total - LIMIT)} MB`); process.exit(1); }
if (total > LIMIT * 0.9) console.warn(`WARNING: within 10% of the 3 MB budget`);
console.log('budget OK');
