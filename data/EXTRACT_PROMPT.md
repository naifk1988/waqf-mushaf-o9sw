You are extracting Quranic pause (الوقف والابتداء) positions from ONE classical book in the "خزانة المعارف" library, for Surat al-Fatiha (1) and Surat al-Baqara (2) only.

## Tools
The Khizana tools are deferred. Load them first with ToolSearch, e.g.
ToolSearch(query="select:mcp__377d35d9-81e8-4ded-a6e5-08ddd728f637__book_toc,mcp__377d35d9-81e8-4ded-a6e5-08ddd728f637__read_pages,mcp__377d35d9-81e8-4ded-a6e5-08ddd728f637__search_text,mcp__377d35d9-81e8-4ded-a6e5-08ddd728f637__book_info,mcp__377d35d9-81e8-4ded-a6e5-08ddd728f637__search_toc", max_results=5)
Then: book_toc to find the start of al-Fatiha and the start of the surah after al-Baqara (Aal Imran) → read_pages (count up to 20, max_chars up to 50000) through every page from al-Fatiha to the end of al-Baqara. Use next_page_id to continue. Read EVERY page in that range — do not skip or sample.

## What to extract
Every place where the author gives a ruling on pausing (وقف) or starting (ابتداء) at a point in al-Fatiha or al-Baqara: e.g. «﴿لا ريب﴾ وقف تام», «(ج)», «كاف», «حسن», «ليس بوقف», «لا يوقف», «قبيح», «لازم», «مطلق», «جائز», «مجوز لوجه», «مرخص ضرورة», «صالح», «مفهوم», «ت/ك/ح/ص/ق/ن» letter codes, «الوقف على ... ثم يبتدئ ...», attributions like «قال نافع: تام», etc. Include positions at ayah ends too. If the author gives two opinions on one spot, make one entry per opinion.

## Output
Write a JSON array (UTF-8, pretty) with the Write tool to: {OUT}
Each entry:
{
  "s": 2,                       // surah number
  "a": 2,                       // ayah number (Kufan count, Madinah mushaf). Determine from the cue phrase.
  "cue": "لا ريب",              // the Quran words exactly as the author quotes them, ENDING at the pause point (the last word = the word paused on). Strip ﴿﴾ brackets and footnote marks. If the author does not quote words, write the 1–4 Quran words ending at the pause point.
  "type": "waqf",               // "waqf" (ruling on stopping here) or "ibtida" (ruling on starting at this word; then cue = the words starting from the start point)
  "ruling": "تام",              // the author's own term, normalized to a word (map letter/symbol codes to their meaning per the author's introduction, e.g. السجاوندي: م=لازم ط=مطلق ج=جائز ز=مجوز لوجه ص=مرخص ضرورة لا=لا يوقف)
  "raw": "تام",                 // the term/symbol exactly as printed
  "reason": "...",              // the author's justification/explanation, VERBATIM from the page, at most ~350 characters (cut with … if longer). "" if none.
  "who": "",                    // if the author attributes the ruling to someone (نافع، يعقوب، الأخفش، أبو حاتم…), their name; else ""
  "loc": "ص 75",                // printed location: "ج1/ص75" or "ص75" as read_pages reports it
  "page_id": 75                 // internal page_id
}

## Rules
- NEVER invent or complete text from memory. Every cue/ruling/reason must come from a page you actually read. Text inside the author's body only — not the editor's footnotes (you may use footnotes only to identify which ayah a cue belongs to, e.g. Qastallani's footnotes give verse numbers).
- Keep the author's wording in "reason"; do not paraphrase.
- Be exhaustive: a typical book has dozens to hundreds of positions in al-Baqara.
- Save progress: write the file after al-Fatiha and then every ~40 entries (overwrite with the full array so far), so nothing is lost.
- When done, reply with ONLY: the entry count, the page range read, and any problems (e.g. book has no al-Baqara section, garbled pages). No other commentary.

## Extra rules (apply always)
- If the cue words occur more than once in the same ayah, append the occurrence to the cue in parentheses: "أو دين (الثاني)". Use (الأول)/(الثاني)/(الثالث)/(الرابع). Never put this in "ruling".
- Assign "s" and "a" in the Kufan count (Madinah mushaf). Check each cue really exists in that ayah; ayah texts are in /home/claude/waqf-mushaf/data/text_preview.json (keys are surah numbers) once that surah has been added — use Python to check.
- Use your OWN scratch files (put your initials/book id in the filename); other jobs run in parallel in the same scratchpad.
