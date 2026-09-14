# Dots and Boxes (Punktid ja kastid)

Dots and Boxes on klassikaline kahe mängijaga strateegiamäng, mis on realiseeritud Pythonis ja kasutab graafilist kasutajaliidest (`tkinter`). Mängus saab inimene (Mängija A) mängida arvuti (Mängija B) vastu, kus arvuti kasutab kas **MINIMAX** algoritmi (sügavusega 4 ja heuristilise hindamisega) või **Greedy** (ahnet) strateegiat.

---

## Mängulaua kirjeldus ja reeglid

Mängulaud koosneb 6 punktist ja 7 joonest, mis moodustavad 2 kasti:

```text
(0,0) ------- 0 ------- (0,1) ------- 1 ------- (0,2)
  |                       |                       |
  2        KAST 0         3        KAST 1         4
  |                       |                       |
(1,0) ------- 5 ------- (1,1) ------- 6 ------- (1,2)
```

### Joonte ja kastide indeksid
- **Jooned (0..6):**
  - `0`: ülemine vasak horisontaalne
  - `1`: ülemine parem horisontaalne
  - `2`: vasakpoolne vertikaalne
  - `3`: keskmine vertikaalne *(Kasti 0 ja Kasti 1 ühine joon)*
  - `4`: parempoolne vertikaalne
  - `5`: alumine vasak horisontaalne
  - `6`: alumine parem horisontaalne
- **Kastid:**
  - **Kast 0:** jooned `(0, 2, 3, 5)`
  - **Kast 1:** jooned `(1, 3, 4, 6)`

### Seisu kodeering
Seis salvestatakse 9-sümbolilise stringina, näiteks `"0000000.A"`:
- Esimesed 7 sümbolit (`0` või `1`) näitavad vastava joone staatust (`0` = vaba, `1` = tõmmatud).
- Punkt `.` eraldab joonte seisu ja käigukorda.
- Viimane täht näitab, kelle käik on parajasti (`A` või `B`).

### Mängureeglid
1. Mängijad teevad kordamööda käike, tõmmates ühe vaba joone.
2. Kui mängija tõmmatud joon sulgeb kasti 4. külje, saab ta selle kasti endale (+1 punkt) ja **saab lisakäigu** (boonuskäik).
3. Mäng lõpeb, kui kõik 7 joont on tõmmatud. Võidab mängija, kes on kogunud enim kaste.

---

## Tehisintellekti (AI) algoritmid

1. **MINIMAX (Depth 4):**
   - Analüüsib mängupuud 4 käiku ette.
   - Arvestab boonuskäike (kasti sulgemisel jätkab sama mängija samas harus).
   - Kasutab lehttippude hindamiseks heuristilist funktsiooni `evaluate_state()`:
     - 3 tõmmatud joont kastil: `+5.0`
     - 2 tõmmatud joont kastil: `+2.0`
     - 1 tõmmatud joon kastil: `+0.5`
   - Algoritm on optimeeritud eelarvutatud üleminekutabeli (*lookup table*) abil, saavutades ~18-kordse kiirusekasvu ja külastades täpselt samad 8,660 sõlme sügavusel 6.

2. **Greedy (Ahne strateegia):**
   - Kui leidub käik, mis sulgeb koheselt kasti, valib selle.
   - Kui kasti sulgeda ei saa, valib ohutu käigu (väldib vastasele 3. joone tekitamist).
   - Kui ohutuid käike pole, teeb vaba käigu.

3. **Jõudlustest (`measure_performance`):**
   - Mõõdab Minimaxi arvutuskiirust sügavustel 1 kuni 6.
   - Väljastab tabeli, mis näitab läbitud sõlmede arvu (*Nodes*), aega sekundites ja arvutuskiirust (*Nodes/min*).

---

## Nõuded süsteemile

- Python 3.8 või uuem
- Ainult Pythoni standardteegid (`tkinter`, `time`, `unittest` jne). Väliseid lisateeke pole vaja paigaldada.

---

## Käivitamine

### Graafilise mängu käivitamine
Käivita mäng käsurealt:

```bash
python dots_and_boxes.py
```

Mängu aknas on võimalik:
- Klikkida vabadel joontel hiirega (Mängija A).
- Vahetada AI režiimi nuppudega **"AI: Minimax (Depth 4)"** ja **"AI: Greedy"**.
- Käivitada kiirustest nupuga **"Jõudlustest"** ning näha tulemuste tabelit.
- Alustada uut mängu nupuga **"Uus mäng"**.

### Automaattestide käivitamine
Projektiga on kaasas põhjalikud automaattestid failis `test_dots_and_boxes.py`. Testide käivitamiseks:

```bash
python -m unittest -v
```

---

## Failide struktuur

- `dots_and_boxes.py` – Kogu mängu loogika, Minimax, Greedy, jõudlustest ja Tkinter graafiline liides ühes failis.
- `test_dots_and_boxes.py` – Automaattestid (`apply_move`, `evaluate_state`, `minimax`, `computer_move_greedy`, `measure_performance`).
- `README.md` – Projekti dokumentatsioon ja kasutusjuhend.
