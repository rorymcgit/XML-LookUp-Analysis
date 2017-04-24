# iTunes XML Metadata LookUp Analysis Tool
OS X/Windows desktop app for analysing iTunes XML metadata lookups.

Instructions for use:
- Use iTunes Transporter to download desired Film lookup metadata XML.
- Drag 'n' drop .iTMSP folder containing XML onto application's GUI and hit submit.
- TXT document will output to source .iTMSP folder with the following information, along with the total count of each type of asset:
    - FEATURE:
      - filename, audio locale
    - PREVIEW(S):
      - filename, audio locale, embedded subtitles locale (if present), territory
    - FULL SUBTITLES:
      - filename, subtitle locale
    - FORCED SUBTITLES:
      - filename, subtitle locale
    - CLOSED CAPTIONS (.SCC):
      - filename, subtitle locale
    - SUBTITLES FOR THE DEAF AND HARD OF HEARING:
      - filename, subtitle locale
    - ALTERNATE AUDIO:
      - filename, audio locale

---
I used:
- Python 2.7
- wxPython (a GUI framework)
- lxml (an XML parser)
- Beautiful Soup 4 (an HTML/XML parser)
