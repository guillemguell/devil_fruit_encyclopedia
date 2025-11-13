#!/usr/bin/env python3
import csv
import json
import os
from pathlib import Path
import re

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parent
csv_path = ROOT / "data" / "devil_fruits_raw.csv"
out_dir = ROOT / "docs"
out_dir.mkdir(parents=True, exist_ok=True)
out_index = out_dir / "index.html"
out_css = out_dir / "styles.css"
out_js = out_dir / "script.js"
img_base = ROOT / "data" / "devil_fruits_imgs"
mp3_path = ROOT / "assets" / "turn_a_page.mp3"


def main():
    entries = []
    excluded_fruits = ['Artificial Devil Fruit']

    if not csv_path.exists():
        print(f"⚠️ Warning: CSV file {csv_path} not found. Producing an HTML with no entries.")
    else:
        with csv_path.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            def parse_bool(val):
                if val is None:
                    return False
                s = str(val).strip().lower()
                return s in ("1", "true", "t", "yes", "y", "on")
            def get_field(r, names):
                for n in names:
                    if n in r and r[n] is not None:
                        return r[n].strip()
                for k, v in r.items():
                    if k and k.lower() in [n.lower() for n in names] and v is not None:
                        return v.strip()
                return ""
            for row in reader:
                name = get_field(row, ["name", "Name", "NAME"])
                typ = get_field(row, ["type", "Type", "TYPE"])
                abilities = get_field(row, ["abilities", "Abilities", "ABILITIES", "ability"])
                is_canon_field = get_field(row, ["is_canon", "isCanon", "iscanon", "canon", "is-canon"])
                if name and parse_bool(is_canon_field) and name not in excluded_fruits:
                    entries.append({
                        "name": name,
                        "type": typ,
                        "abilities": abilities
                    })

    entries.sort(key=lambda e: e["name"].lower())

    for entry in entries:
        safe_name = re.sub(r"[^A-Za-z0-9]+", "_", entry["name"]).strip("_")
        img_file = img_base / f"{safe_name}.png"
        if not img_file.exists():
            alt_png = img_base / f"{safe_name.lower()}.png"
            alt_jpg = img_base / f"{safe_name}.jpg"
            alt_jpeg = img_base / f"{safe_name}.jpeg"
            for alt in [alt_png, alt_jpg, alt_jpeg]:
                if alt.exists():
                    img_file = alt
                    break
        if img_file.exists():
            rel = Path(os.path.relpath(img_file, start=out_dir))
            entry["image"] = rel.as_posix()
        else:
            entry["image"] = None

    entries_json = json.dumps(entries, ensure_ascii=False, indent=2)

    css_content = """* {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      display: flex;
      height: 100dvh;
      perspective: 900px;
      font: 16px/1.4 sans-serif;
      overflow: hidden;
      background-color: #232425;
    }

    .book {
      position: relative;
      display: flex;
      width: 375px;
      height: 500px;
      left: 50%;
      margin-top: auto;
      margin-bottom: auto;
      pointer-events: none;
      transform-style: preserve-3d;
      transition: transform 0.3s ease;
      rotate: 1 0 0 30deg;
      transform: rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
    }


    .page {
      --thickness: 2px;
      flex: none;
      display: flex;
      width: 100%;
      height: 100%;
      pointer-events: all;
      user-select: none;
      transform-style: preserve-3d;
      border: 1px solid #0008;
      transform-origin: left center;
      transition: transform 1s,
        rotate 1s ease-in
          calc((min(var(--i), var(--c)) - max(var(--i), var(--c))) * 50ms);
      translate: calc(var(--i) * -100%) 0px 0px;
      transform: translateZ(calc(var(--i) * var(--thickness)))
        translateZ(calc((var(--c) - var(--i) - 0.5) * 5px));
      rotate: 0 1 0 calc(clamp(0, var(--c) - var(--i), 1) * -180deg);
      position: relative;
      background: linear-gradient(
        180deg,
        #fff7df 0%,
        #f1dfb3 60%,
        #e9d5a0 100%
      );
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
      padding: 0.6rem;
      overflow: visible;
    }

    .front,
    .back {
      flex: none;
      width: 100%;
      height: 100%;
      padding: 0.6rem;
      backface-visibility: hidden;
      background-color: #fff;
      translate: 0px;
      box-shadow: inset 0 0 3px #0002;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .back {
      background-image: linear-gradient(to right, #fff 80%, #eee 100%);
      translate: -100% 0;
      rotate: 0 1 0 180deg;
    }

    .page::before {
      content: "";
      position: absolute;
      top: 0;
      right: -1px;
      width: var(--thickness);
      height: 100%;
      background: linear-gradient(to right, #ccc, #999);
      transform: rotateY(90deg) translateX(calc(var(--thickness) / 2));
      transform-origin: left;
    }

    .page .page-content {
      height: 100%;
      display: grid;
      grid-template-columns: 1fr;
      grid-template-rows: repeat(4, 1fr);
      gap: 0.5rem;
      align-content: start;
      padding: 0;
    }

    .entry {
      display: flex;
      flex-direction: row;
      gap: 0.6rem;
      align-items: stretch;
      background: linear-gradient(
        180deg,
        rgba(255, 255, 245, 0.96),
        rgba(255, 250, 230, 0.96)
      );
      border-radius: 8px;
      padding: 0.45rem;
      box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.6);
      min-height: 0;
      border: 1px solid #b9924a;
      position: relative;
      overflow: hidden;
    }

    .entry::after {
      content: "";
      position: absolute;
      inset: 6px;
      border-radius: 6px;
      pointer-events: none;
      box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.04);
    }

    .entry-image {
      flex: 0 0 25%;
      max-width: 25%;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 64px;
    }

    .entry-image img {
      width: 100%;
      height: auto;
      max-height: 90px;
      object-fit: contain;
      border: 1px solid #e6d6b0;
      background: #fffdf6;
      padding: 4px;
      border-radius: 4px;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }

    .no-img {
      width: 100%;
      height: 100%;
      min-height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px dashed #c9bfae;
      background: linear-gradient(180deg, #fbf6eb, #f3ead1);
      font-family: "IM Fell English SC", "IM Fell English", Georgia, serif;
      color: #3a2f21;
      padding: 0.25rem;
      text-align: center;
      font-size: 0.6rem;
      border-radius: 4px;
    }

    .entry-text {
      flex: 1 1 67%;
      min-width: 0;
      display: flex;
      flex-direction: column;
      justify-content: start;
      gap: 0.125rem;
      padding-left: 0.15rem;
    }

    .devil-title {
      font-family: "IM Fell English SC", "IM Fell English", Georgia,
        "Times New Roman", serif;
      font-size: 0.75rem;
      margin: 0;
      color: #21160d;
    }

    .devil-meta {
      font-family: "EB Garamond", Georgia, "Times New Roman", serif;
      font-size: 0.6rem;
      margin: 0;
      color: #3b2e25;
    }

    .devil-abilities {
      font-family: "EB Garamond", Georgia, "Times New Roman", serif;
      font-size: 0.6rem;
      color: #2e2a23;
      line-height: 1.2;
      white-space: pre-wrap;
    }

    .cover {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.25rem;
      text-align: center;
      background-color: #7A5A3A;
      padding: 2rem;
    }
    .cover h1 {
      margin: 0;
      font-family: "IM Fell English SC", "Cinzel", Georgia, serif;
      font-size: 1.35rem;
      font-variant: small-caps;
      letter-spacing: 1.5px;
    }
    .cover h3 {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 0.85rem;
      color: #4a3b2e;
    }

    .backcover .back {
      background-color: #7A5A3A;
      background-image: none;
      color: #F6E9D7;
    }

    @media (max-width: 420px) {
      .page .page-content {
        grid-template-rows: repeat(4, auto);
      }
      .entry {
        flex-direction: column;
        padding: 0.5rem;
      }
      .entry-image {
        flex: 0 0 auto;
        width: 100%;
        max-width: 100%;
        min-height: 100px;
      }
      .entry-image img {
        height: 100%;
        width: auto;
        max-height: 160px;
      }
      .entry-text {
        padding-left: 0;
      }
    }

    .page .tab {
      right: -33px;
      width: 34px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 2px;
      background: linear-gradient(180deg,#fff7df,#f1dfb3);
      font-size: 0.65rem;
      color: #23160d;
      cursor: pointer;
      z-index: 9999;
      box-sizing: border-box;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      transition: opacity 0.2s ease;
    }

    .book .tab {
      position: absolute;
      right: -33px;
      pointer-events: auto;
    }

    .page .tab._auto {
      pointer-events: auto;
    }
    .page .tab.disabled {
      opacity: 0.45;
      cursor: default;
      pointer-events: none;
    }
    .page .tab:hover:not(.disabled) {
      opacity: 0.8;
    }

    @media (max-width: 420px) {
      .page .tab { right: -28px; width: 26px; font-size: 0.6rem; }
      .book .tab { right: -28px; width: 26px; font-size: 0.6rem; }
    }
    """

    js_template = """const entries = <<ENTRIES>>;

    const book = document.getElementById("devil-book");

    function playPageFlip() {
      const sound = document.getElementById("pageFlipSound");
      if (sound) {
        sound.currentTime = 0;
        sound.play().catch(() => {});
      }
    }

    function chunkArray(array, size) {
      const chunks = [];
      for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size));
      }
      return chunks;
    }

    function createEntryHTML(entry, globalIndex) {
      return `
        <div class="entry" data-entry-index="${globalIndex}">
          <div class="entry-image">
            ${
              entry.image
                ? `<img src="${entry.image}" alt="${entry.name}">`
                : `<div class="no-img">No image<br>available</div>`
            }
          </div>
          <div class="entry-text">
            <div class="devil-title">${entry.name}</div>
            <div class="devil-meta">Type: ${entry.type}</div>
            <div class="devil-abilities">${entry.abilities}</div>
          </div>
        </div>`;
    }

    function createPage(frontEntries = [], backEntries = [], index, globalStartIndex) {
      const page = document.createElement("div");
      page.className = "page";
      page.style.setProperty("--i", index + 1);

      const front = document.createElement("div");
      front.className = "front";
      front.innerHTML = `<div class="page-content">${frontEntries
        .map((e, idx) => createEntryHTML(e, globalStartIndex + idx))
        .join("")}</div>`;

      const back = document.createElement("div");
      back.className = "back";
      back.innerHTML = `<div class="page-content">${backEntries
        .map((e, idx) => createEntryHTML(e, globalStartIndex + frontEntries.length + idx))
        .join("")}</div>`;

      page.appendChild(front);
      page.appendChild(back);
      return page;
    }

    const groups = chunkArray(entries, 8);
    groups.forEach((group, i) => {
      const frontEntries = group.slice(0, 4);
      const backEntries = group.slice(4);
      const globalStart = i * 8;
      const page = createPage(frontEntries, backEntries, i, globalStart);
      book.appendChild(page);
    });

    const backCoverPage = document.createElement("div");
    backCoverPage.className = "page backcover";
    backCoverPage.style.setProperty("--i", groups.length);
    const backFront = document.createElement("div");
    backFront.className = "front";
    backFront.innerHTML = `<div class="page-content"></div>`;
    const backBack = document.createElement("div");
    backBack.className = "back";
    backCoverPage.appendChild(backFront);
    backCoverPage.appendChild(backBack);
    book.appendChild(backCoverPage);

    const flipBook = (elBook) => {
      elBook.style.setProperty("--c", 0);
      const pages = elBook.querySelectorAll(".page");
      const lastIndex = pages.length - 1;
      const maxC = pages.length;

      pages.forEach((page, i) => {
        page.style.setProperty("--i", i);
        page.addEventListener("click", (evt) => {
          const onBack = !!evt.target.closest(".back");
          let c = onBack ? i : i + 1;
          c = Math.max(0, Math.min(c, maxC));
          elBook.style.setProperty("--c", c);
          playPageFlip();
        });
      });
    };
    flipBook(book);

    const enableRotation = (elBook) => {
      let rotating = false,
        sx = 0,
        sy = 0,
        rx = 0,
        ry = 0;
      document.addEventListener("contextmenu", (e) => e.preventDefault());
      document.addEventListener("mousedown", (e) => {
        if (e.button !== 2) return;
        rotating = true;
        sx = e.clientX;
        sy = e.clientY;
      });
      document.addEventListener("mousemove", (e) => {
        if (!rotating) return;
        ry += (e.clientX - sx) * 0.4;
        rx -= (e.clientY - sy) * 0.4;
        sx = e.clientX;
        sy = e.clientY;
        elBook.style.setProperty("--rx", `${rx}deg`);
        elBook.style.setProperty("--ry", `${ry}deg`);
      });
      document.addEventListener("mouseup", () => (rotating = false));
    };
    enableRotation(book);

    (function placeLetterTabsExactly() {
      const pages = Array.from(book.querySelectorAll(".page"));
      if (pages.length === 0) return;

      const letterFirstPage = {};
      pages.forEach((pageEl, pageIdx) => {
        const titles = pageEl.querySelectorAll(".devil-title");
        titles.forEach((titleEl) => {
          const txt = (titleEl.textContent || "").trim();
          if (!txt) return;
          const ch = txt.charAt(0).toUpperCase();
          if (ch >= "A" && ch <= "Z" && !(ch in letterFirstPage)) {
            letterFirstPage[ch] = { pageEl, pageIdx, titleEl };
          }
        });
      });

      const letters = Object.keys(letterFirstPage).sort();
      const M = letters.length;
      if (M === 0) return;

      function clearOldTabs() {
        pages.forEach((p) => {
          p.querySelectorAll(".tab._auto").forEach((el) => el.remove());
        });
      }

      function computeAndPlace() {
        clearOldTabs();

        const bookRect = book.getBoundingClientRect();
        if (!bookRect.height) return;
        const bandHeight = bookRect.height / M;

        letters.forEach((L, idx) => {
          const info = letterFirstPage[L];
          if (!info) return;
          const targetPage = info.pageEl;

          const bandTopInBook = bookRect.top + idx * bandHeight;
          const bandHeightInBook = bandHeight;

          const pageRect = targetPage.getBoundingClientRect();

          let topPercent, heightPercent;
          if (pageRect.height > 0) {
            topPercent = ((bandTopInBook - pageRect.top) / pageRect.height) * 100;
            heightPercent = (bandHeightInBook / pageRect.height) * 100;
          } else {
            topPercent = (idx * (100 / M));
            heightPercent = (100 / M);
          }

          if (idx === 0) {
            topPercent = Math.max(topPercent, 0);
          }

          if (topPercent < -60) topPercent = -60;
          if (topPercent > 160) topPercent = 160;

          if (idx === M - 1) {
            const bottom = topPercent + heightPercent;
            if (bottom < 100) {
              const needed = 100 - topPercent + 0.5;
              heightPercent = Math.min(needed, 110);
            }
          }

          const tab = document.createElement("div");
          tab.className = "tab _auto";
          tab.textContent = L;

          tab.style.position = "absolute";
          tab.style.top = `${topPercent}%`;
          tab.style.height = `${heightPercent}%`;
          tab.style.right = "-33px";
          tab.style.visibility = "visible";
          tab.style.pointerEvents = "auto";

          targetPage.appendChild(tab);

          tab.addEventListener("click", (evt) => {
            evt.stopImmediatePropagation();
            evt.preventDefault();

            const titleEl = info.titleEl;
            let entryEl = titleEl && titleEl.closest && titleEl.closest(".entry");
            let globalIndex = null;
            if (entryEl && entryEl.dataset && entryEl.dataset.entryIndex != null) {
              globalIndex = parseInt(entryEl.dataset.entryIndex, 10);
            }

            const pagesAll = Array.from(book.querySelectorAll(".page"));
            const maxC = pagesAll.length;

            if (globalIndex == null || Number.isNaN(globalIndex)) {
              const domIndex = pagesAll.indexOf(info.pageEl);
              const target = Math.max(0, Math.min(maxC, domIndex + 1));
              book.style.setProperty("--c", target);
              playPageFlip();
              tab.animate([{ transform: "scale(1)" }, { transform: "scale(1.06)" }, { transform: "scale(1)" }], { duration: 220 });
              return;
            }

            const sheetIndex = Math.floor(globalIndex / 8);
            const posInSheet = globalIndex % 8;
            const domPageIndex = pagesAll.indexOf(info.pageEl);
            const desiredC = posInSheet < 4 ? domPageIndex  : domPageIndex + 1;
            const clamped = Math.max(0, Math.min(maxC, desiredC));
            book.style.setProperty("--c", clamped);
            playPageFlip();
            tab.animate([{ transform: "scale(1)" }, { transform: "scale(1.06)" }, { transform: "scale(1)" }], { duration: 220 });
          });

        });
      }

      setTimeout(computeAndPlace, 40);
      setTimeout(computeAndPlace, 260);
      setTimeout(computeAndPlace, 800);
      window.addEventListener("resize", () => {
        clearTimeout(window._tabs_place_timer);
        window._tabs_place_timer = setTimeout(computeAndPlace, 120);
      });
    })();
    """

    js_content = js_template.replace("<<ENTRIES>>", entries_json)

    mp3_rel = Path(os.path.relpath(mp3_path, start=out_dir)).as_posix()

    index_html = f"""<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>DEVIL FRUIT ENCYCLOPEDIA</title>
        <link href="https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap" rel="stylesheet" />
        <link rel="stylesheet" href="styles.css" />
        <audio id="pageFlipSound" preload="auto">
          <source src="{mp3_rel}" type="audio/mpeg">
        </audio>
      </head>
      <body>
        <div class="book" id="devil-book">
          <div class="page">
            <div class="front cover">
              <h1>DEVIL FRUIT ENCYCLOPEDIA</h1>
            </div>
            <div class="back">
              <div style="text-align: center"></div>
            </div>
          </div>
        </div>
        <script src="script.js"></script>
      </body>
    </html>
    """

    out_css.write_text(css_content, encoding="utf-8")
    out_js.write_text(js_content, encoding="utf-8")
    out_index.write_text(index_html, encoding="utf-8")
    print(f"Wrote index to {out_index.resolve()} css to {out_css.resolve()} js to {out_js.resolve()} (entries: {len(entries)})")


if __name__ == '__main__':
    main()
