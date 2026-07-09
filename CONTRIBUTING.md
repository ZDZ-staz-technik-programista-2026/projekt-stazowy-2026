# Jak pracujemy w tym repozytorium

Dokument obowiązuje cały zespół. Jeśli coś jest niejasne — pytaj **wcześnie**, nie blokuj się dłużej
niż 30 minut.

---

## 1. Zasada podstawowa

**Nigdy nie commitujemy bezpośrednio na `main`.**

Gałąź `main` jest chroniona — próba wypchnięcia zmian wprost na nią zostanie odrzucona przez GitHub.
Każda zmiana wchodzi do `main` przez **Pull Request** zatwierdzony przez kolegę z zespołu.

---

## 2. Zaczynamy pracę

```bash
# jednorazowo
git clone https://github.com/ZDZ-staz-technik-programista-2026/projekt-stazowy-2026.git
cd projekt-stazowy-2026

# przed każdym nowym zadaniem
git checkout main
git pull                              # pobierz najnowszy stan
git checkout -b feature/entry-form    # nowa gałąź na zadanie
```

### Nazewnictwo gałęzi

Gałęzie nazywamy **po angielsku**, w formacie `typ/krotki-opis`:

| Typ | Kiedy | Przykład |
|---|---|---|
| `feature/` | nowa funkcjonalność | `feature/entry-form` |
| `fix/` | poprawka błędu | `fix/hours-validation` |
| `docs/` | dokumentacja | `docs/readme-setup` |
| `refactor/` | porządkowanie kodu bez zmiany działania | `refactor/entry-service` |
| `test/` | testy | `test/status-transitions` |

Jedna gałąź = jedno zadanie z Jiry.

---

## 3. Commity

- Piszemy **po angielsku**, w trybie rozkazującym: `add entry form validation`
- Krótko i konkretnie — commit ma mówić **co** się zmieniło
- Commitujemy **małymi porcjami**, nie raz na trzy dni
- **Codzienny push** to dowód pracy (wymóg stażu)

```bash
git add .
git commit -m "add entry status transitions"
git push -u origin feature/entry-form
```

**Dobre komunikaty:**

```
add entry form validation
fix hours calculation for overnight entries
update readme with setup instructions
```

**Złe komunikaty:**

```
poprawki          ← co poprawione?
zmiany            ← jakie?
asdf              ← nie
fix               ← czego?
```

---

## 4. Pull Request

1. Wypchnij gałąź na GitHub (`git push`)
2. Otwórz **Pull Request** do `main`
3. Wypełnij szablon (pojawi się automatycznie) — **po polsku**
4. Poproś kolegę o przegląd (**Reviewers**)
5. Odpowiedz na komentarze i popraw kod
6. Po zatwierdzeniu: **Squash and merge** → gałąź kasuje się automatycznie

### Zasady

- **1 zatwierdzenie** od kolegi z zespołu jest wymagane przed scaleniem
- Nie zatwierdzamy własnych Pull Requestów
- Wszystkie komentarze muszą być **rozwiązane** (resolved) przed scaleniem
- PR powinien być **mały** — łatwiej go przejrzeć. Jeśli zmienia 30 plików, prawdopodobnie
  powinien być podzielony na kilka

---

## 5. Przegląd kodu (code review)

Przegląd cudzego kodu to **osobna umiejętność zawodowa** — ćwiczymy ją celowo (dzień 9).

**Jako recenzent:**

- czytaj kod i **pytaj**, jeśli czegoś nie rozumiesz — pytanie nie jest atakiem
- komentuj kod, nie osobę: „ta funkcja robi dwie rzeczy" zamiast „źle to napisałeś"
- doceniaj dobre rozwiązania — nie tylko wytykaj błędy
- jeśli wszystko gra: **Approve**. Jeśli nie: **Request changes** z konkretnym uzasadnieniem

**Jako autor:**

- nie broń się — przegląd dotyczy kodu, nie Ciebie
- jeśli się nie zgadzasz, wyjaśnij dlaczego; można się różnić
- odpowiedz na **każdy** komentarz (nawet krótkim „poprawione")

---

## 6. Definicja ukończenia (Definition of Done)

Zadanie jest skończone, gdy **wszystkie** punkty są spełnione:

- [ ] kod działa lokalnie (frontend i backend uruchamiają się bez błędów)
- [ ] Pull Request przejrzany i zatwierdzony przez kolegę
- [ ] wszystkie komentarze w PR rozwiązane
- [ ] zadanie w Jirze przeniesione do **Done**
- [ ] *(od dnia 14)* testy `pytest` przechodzą

---

## 7. Czego nie commitujemy

Sprawdź `.gitignore`, ale pamiętaj — najważniejsze:

- **plik bazy danych** (`*.db`, `*.sqlite3`) — każdy ma swoją lokalną bazę
- `node_modules/`, `venv/`, `__pycache__/`
- pliki konfiguracyjne edytora, pliki systemowe (`.DS_Store`)
- **jakiekolwiek prawdziwe dane osobowe** — pracujemy wyłącznie na danych fikcyjnych

> Jeśli przypadkiem wypchniesz coś wrażliwego — **powiedz od razu opiekunowi**.
> Historia Gita jest publiczna i sam commit „usuwający" plik nie usuwa go z historii.

---

## 8. Języki

| Element | Język |
|---|---|
| Kod, nazwy zmiennych, funkcji, plików | angielski |
| Nazwy gałęzi | angielski |
| Komunikaty commitów | angielski |
| Opisy Pull Requestów, komentarze w przeglądzie | polski |
| README i dokumentacja | polski |

---

## 9. Narzędzia AI

Korzystamy z **darmowych czatów** (ChatGPT, Gemini, Claude) jako pomocy przy nauce i pisaniu kodu.
Nie używamy płatnych ani agentowych narzędzi (Copilot, Codex, Claude Code) — nie są wymagane.

**Zasady (regulamin stażu § 9):**

- kod wygenerowany z pomocą AI musisz **zrozumieć**, samodzielnie **zweryfikować** i **przetestować**
- odpowiedzialność za kod w Pull Requeście ponosi **jego autor**, nie czat
- **zakaz wklejania** do narzędzi AI danych poufnych, danych klientów i danych osobowych
- jeśli nie potrafisz wyjaśnić, jak działa Twój kod na przeglądzie — nie jest gotowy do scalenia

AI **nie jest funkcją naszej aplikacji** — to wyłącznie narzędzie pracy.

---

## 10. Charakter projektu

Projekt ma charakter **wyłącznie edukacyjny/symulacyjny**. Pracujemy na **danych testowych
i fikcyjnych uczniach**. Aplikacja nie zastępuje formalnego dzienniczka stażu prowadzonego dla ZDZ.

Obowiązuje regulamin stażu (§ 2–3, § 8, § 9, § 10).
