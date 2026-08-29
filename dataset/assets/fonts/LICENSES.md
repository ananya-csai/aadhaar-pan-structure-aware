# Bundled font files

These font binaries are committed to the repository so that a render is
byte-identical on any platform: font rasterisation depends on the exact font
file, and relying on whatever the operating system happens to provide would
make the "reproducible from code" claim of Section IV-I false on Windows and
macOS. All four families are freely redistributable.

| files | family | licence |
|---|---|---|
| `Liberation*.ttf` | Liberation Sans / Serif / Mono (Red Hat) | SIL Open Font License 1.1 |
| `DejaVu*.ttf` | DejaVu Sans / Sans Mono | Bitstream Vera Fonts Copyright (permissive, MIT-like) |
| `Carlito*.ttf` | Carlito (Łukasz Dziedzic) | SIL Open Font License 1.1 |
| `FreeSerif.ttf`, `FreeSerifBold.ttf`, `FreeSans.ttf` | GNU FreeFont | GNU GPL v3 with the GPL font exception |

The GNU FreeFont files are used because they are the Devanagari-capable faces
available under a redistributable licence; the GPL font exception explicitly
allows documents (here, rendered images) produced with them to carry any
licence.

Full licence texts ship with the upstream packages; see
https://github.com/liberationfonts, https://dejavu-fonts.github.io,
https://fonts.google.com/specimen/Carlito and https://www.gnu.org/software/freefont/.
