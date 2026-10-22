Task: list every Habti pause mark «صه» in a scanned Mushaf (رواية قالون، مصحف الجماهيرية) for a given page range.

The PDF (image-only, no text layer): /mnt/user-data/uploads/مصحف_الهبطي.pdf  (read-only)
Work dir: /tmp/claude-0/-home-claude/dafd93b9-d5a9-5716-9227-dc7dbcac64b8/scratchpad/hb/{CHUNK}/  (create it)

For each page N in your range:
1. Render: pdftoppm -r 150 -png -f N -l N "/mnt/user-data/uploads/مصحف_الهبطي.pdf" <workdir>/p
2. Split into top half and bottom half with a tiny python/PIL script (slight overlap of ~40px is fine), then view both halves with the Read tool.
3. Read line by line, right to left. The Habti mark is a small «صه» (looks like a little ص with a stroke) written ABOVE the last letter of a word. Record every word that carries it, including words at ayah ends. Do NOT record ayah-number circles, ruku/hizb stars, or other marks.

Stop at the end of Surat al-Baqara (if the header of سورة آل عمران appears on a page, stop there; record nothing after it). If your range starts in al-Fatiha, also record al-Fatiha's marks with "surah":1.

Output: write with the Write tool a JSON array to /home/claude/waqf-mushaf/data/raw/habti_{CHUNK}.json, in reading order:
{"surah":2,"pdf_page":4,"line":2,"word":"يومنون","context":"ام لم تنذرهم لا يومنون","ayah_madani":5}
- word: the marked word, written plainly without diacritics as it appears.
- context: the marked word preceded by the 2–4 words before it (plain letters), so it can be located unambiguously.
- ayah_madani: the number of the ayah the word belongs to, from the nearest ayah circle (the ayah ending AFTER the word; if the word itself ends the ayah, that ayah's number). Numbers here follow the Madani count and differ from the Kufan count — record what is printed.
Save the file after every page (overwrite with the full array so far).

Be exhaustive and careful: a page has roughly 15–30 marks. Never invent; if a mark is unclear, include it with "unsure":true.
When done reply ONLY with: pages covered, total marks, count of unsure, and whether you reached the start of Aal Imran.

Extra rules:
- Use your OWN helper scripts and image folder named after your CHUNK; other chunks run in parallel and must not share files.
- Set "surah" from the surah headers you see, using the standard surah number (العنكبوت=29، الروم=30 … الحديد=57، المجادلة=58 … الناس=114). The task message tells you which surahs are in scope and where to stop.
