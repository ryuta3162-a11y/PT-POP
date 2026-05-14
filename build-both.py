# -*- coding: utf-8 -*-
import re
from pathlib import Path

base = Path(__file__).resolve().parent
a4 = (base / "pt-pop-a4.html").read_text(encoding="utf-8")
camp = (base / "pt-pop-a4-campaign.html").read_text(encoding="utf-8")
style = re.search(r"<style>([\s\S]*?)</style>", camp).group(1)
art1 = re.search(r'<article class="sheet">[\s\S]*?</article>', a4).group(0)
art2 = re.search(r'<article class="sheet sheet--campaign">[\s\S]*?</article>', camp).group(0)
art1 = art1.replace('id="qr-slot"', "", 1)
art2 = art2.replace('id="qr-slot"', "", 1)
extra = ""
hint = (
    "押すと印刷画面が開きます<strong>プリンターで「PDFに保存」</strong>を選ぶと"
    "<strong>1枚目：トレーナー紹介 → 2枚目：初回キャンペーン</strong>の順で2ページのPDFになります"
    "<strong>余白なし</strong>・<strong>背景のグラフィック</strong>をオンにしてください"
)
png_sub = (
    "PNGは最大4倍の解像度で書き出します（失敗時は自動で下げます） fileを直接開いたままだとQRなどの画像取得がブロックされ失敗することがあります "
    "このフォルダで python -m http.server 8765 を実行し http://localhost:8765 からこのHTMLを開いてください"
)
out = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>POP A4 2枚まとめ（トレーナー紹介＋初回キャンペーン）</title>
  <style>{style}{extra}
  </style>
</head>
<body>
  <div class="pdf-toolbar" role="region" aria-label="PDF・PNG保存">
    <div class="pdf-btn-row">
      <button type="button" class="pdf-btn" id="btn-save-pdf">2枚まとめてPDF保存</button>
      <button type="button" class="pdf-btn pdf-btn--png" id="btn-save-png">高画質PNG保存</button>
    </div>
    <p class="pdf-hint">
      {hint}
    </p>
    <p class="pdf-hint pdf-hint--sub">{png_sub}</p>
  </div>
{art1}
{art2}
  <script>
    (function () {{
      var PDF_ID = "btn-save-pdf";
      var PNG_ID = "btn-save-png";

      function bindPdf() {{
        var btn = document.getElementById(PDF_ID);
        if (btn) btn.addEventListener("click", function () {{ window.print(); }});
      }}

      function fileNamesForSheets(sheets) {{
        var n = sheets.length;
        if (n === 2) return ["pt-pop-01-trainer.png", "pt-pop-02-campaign.png"];
        if (n === 1 && sheets[0].classList.contains("sheet--campaign")) return ["pt-pop-campaign.png"];
        return ["pt-pop-trainer.png"];
      }}

      function pngFailMessage() {{
        if (/^file:/i.test(location.protocol || "")) {{
          return "PNGの保存に失敗しました\\n\\nこのHTMLを file で開いたままだと QR やロゴ画像の読み込みがブラウザにブロックされることがあります\\n\\nこのフォルダで次を実行し ブラウザから http://localhost:8765/ でこのファイルを開いてください\\n\\npython -m http.server 8765\\n\\nまたは PDF 保存をお試しください";
        }}
        return "PNGの保存に失敗しました ページを更新するか PDF 保存をお試しください（原因は開発者ツールのコンソールに出ます）";
      }}

      function bindPng() {{
        var btn = document.getElementById(PNG_ID);
        if (!btn) return;
        btn.addEventListener("click", function () {{
          var sheets = document.querySelectorAll(".sheet");
          if (!sheets.length) return;
          var labels = ["高画質PNG保存", "PNG作成中…"];
          btn.disabled = true;
          btn.textContent = labels[1];
          var libUrl = new URL("./html-to-image.esm.mjs", document.baseURI).href;
          import(libUrl)
            .then(function (mod) {{
              var toPng = mod.toPng;
              var baseOpts = {{
                backgroundColor: "#ffffff",
                cacheBust: true,
                skipFonts: true,
                style: {{ margin: "0", boxShadow: "none" }},
              }};
              var ratios = [4, 2, 1];
              function toPngBest(el) {{
                var ri = 0;
                function tryNext(err) {{
                  if (ri >= ratios.length) return Promise.reject(err || new Error("PNG failed"));
                  var r = ratios[ri++];
                  return toPng(el, Object.assign({{ pixelRatio: r }}, baseOpts)).catch(function (e) {{
                    return tryNext(e);
                  }});
                }}
                return tryNext(null);
              }}
              var names = fileNamesForSheets(sheets);
              var i = 0;
              function delay(ms) {{
                return new Promise(function (r) {{ setTimeout(r, ms); }});
              }}
              function next() {{
                if (i >= sheets.length) {{
                  btn.disabled = false;
                  btn.textContent = labels[0];
                  return Promise.resolve();
                }}
                var idx = i;
                i += 1;
                return toPngBest(sheets[idx])
                  .then(function (dataUrl) {{
                    var a = document.createElement("a");
                    a.href = dataUrl;
                    a.download = names[idx] || "pt-pop-" + (idx + 1) + ".png";
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    return delay(400);
                  }})
                  .then(next);
              }}
              return next();
            }})
            .catch(function (err) {{
              console.error(err);
              alert(pngFailMessage());
              btn.disabled = false;
              btn.textContent = labels[0];
            }});
        }});
      }}

      bindPdf();
      bindPng();
    }})();
  </script>
</body>
</html>
"""
(base / "pt-pop-a4-both.html").write_text(out, encoding="utf-8")
print("ok")
