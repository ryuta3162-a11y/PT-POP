import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");
const bothPath = path.join(root, "pt-pop-a4-both.html");
const s = fs.readFileSync(bothPath, "utf8");

function campaignStart(html) {
  const crlf = html.indexOf("\r\n  <article class=\"sheet sheet--campaign\">");
  if (crlf !== -1) return crlf;
  return html.indexOf("\n  <article class=\"sheet sheet--campaign\">");
}

function scriptAfter(html, from) {
  const crlf = html.indexOf("\r\n  <script>", from);
  if (crlf !== -1) return crlf;
  return html.indexOf("\n  <script>", from);
}

const start2 = campaignStart(s);
const scriptIdx = scriptAfter(s, start2);
if (start2 === -1 || scriptIdx === -1) {
  console.error("kitei markers not found", { start2, scriptIdx });
  process.exit(1);
}
let kitei = s.slice(0, start2) + s.slice(scriptIdx);

function firstTrainerArticleStart(html) {
  const tagged = html.indexOf('<article class="sheet sheet--kitei-pop">');
  if (tagged !== -1) return tagged;
  return html.indexOf('<article class="sheet">');
}

const gStart = firstTrainerArticleStart(s);
const gEnd = campaignStart(s);
if (gStart === -1 || gEnd === -1) {
  console.error("gentei markers not found", { gStart, gEnd });
  process.exit(1);
}
let gentei = s.slice(0, gStart) + s.slice(gEnd);

function setTitle(html, title) {
  return html.replace(/<title>[^<]*<\/title>/, `<title>${title}</title>`);
}

function setPdfButton(html, label) {
  return html.replace(
    /<button type="button" class="pdf-btn" id="btn-save-pdf">[^<]*<\/button>/,
    `<button type="button" class="pdf-btn" id="btn-save-pdf">${label}</button>`
  );
}

function setPdfHint(html, inner) {
  return html.replace(
    /<p class="pdf-hint">[\s\S]*?<\/p>/,
    `<p class="pdf-hint">\n      ${inner}\n    </p>`
  );
}

const kiteiHint =
  "このファイルは<strong>規定POP（トレーナー紹介）1枚のみ</strong>です。<strong>「PDFに保存」</strong>を選び、<strong>余白なし・背景のグラフィックをオン</strong>にしてください。限定POPは <code>pt-pop-a4-gentei-pop.html</code> を別途開いて印刷してください。レイアウトがずれるときは<strong>拡大／縮小を「既定」または 100%</strong>にしてください。";

const genteiHint =
  "このファイルは<strong>限定POP（キャンペーン面）1枚のみ</strong>です。<strong>「PDFに保存」</strong>を選び、<strong>余白なし・背景のグラフィックをオン</strong>にしてください。規定POPは <code>pt-pop-a4-kitei-pop.html</code> を別途開いて印刷してください。レイアウトがずれるときは<strong>拡大／縮小を「既定」または 100%</strong>にしてください。";

kitei = setTitle(kitei, "規定POP（トレーナー紹介）A4・1枚印刷用");
kitei = setPdfButton(kitei, "規定POPをPDFで保存");
kitei = setPdfHint(kitei, kiteiHint);

gentei = setTitle(gentei, "限定POP（初回キャンペーン）A4・1枚印刷用");
gentei = setPdfButton(gentei, "限定POPをPDFで保存");
gentei = setPdfHint(gentei, genteiHint);

fs.writeFileSync(path.join(root, "pt-pop-a4-kitei-pop.html"), kitei);
fs.writeFileSync(path.join(root, "pt-pop-a4-gentei-pop.html"), gentei);

const count = (t) => (t.match(/<article/g) || []).length;
console.log("kitei bytes", kitei.length, "articles", count(kitei));
console.log("gentei bytes", gentei.length, "articles", count(gentei));
