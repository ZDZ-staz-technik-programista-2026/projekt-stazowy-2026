# Dzienniczek stażu online

> ## ⚠️ PROJEKT DEMONSTRACYJNY — DANE TESTOWE
>
> Ta aplikacja **nie zastępuje** formalnego dzienniczka stażu prowadzonego dla ZDZ.
> Powstaje jako **projekt edukacyjny/symulacyjny** i działa **wyłącznie na fikcyjnych danych**
> („Uczeń Testowy 1", „Uczeń Testowy 2"). Nie wprowadzamy do niej prawdziwych danych
> osobowych ani realnych godzin stażu.

Aplikacja webowa do prowadzenia dziennych wpisów stażowych: uczeń dodaje wpis (data, godziny,
opis pracy, blokery), a opiekun zatwierdza go lub zwraca do poprawki.

---

## Spis treści

- [O projekcie](#o-projekcie)
- [Stos technologiczny](#stos-technologiczny)
- [Zespół i role](#zespół-i-role)
- [Uruchomienie lokalne](#uruchomienie-lokalne)
- [Struktura repozytorium](#struktura-repozytorium)
- [Statusy wpisu](#statusy-wpisu)
- [Zakres MVP](#zakres-mvp)
- [Praca z repozytorium](#praca-z-repozytorium)
- [Licencja](#licencja)

---

## O projekcie

Projekt realizowany w ramach **stażu uczniowskiego** w zawodzie technik programista (351406),
kwalifikacje INF.03 i INF.04.

| | |
|---|---|
| Termin | 08.07.2026 – 04.08.2026 (20 dni roboczych) |
| Zakład pracy | PAWEŁ SZMIDT |
| Opiekun stażu / „klient" | Paweł Szmidt |
| Organizator | Zakład Doskonalenia Zawodowego w Białymstoku (ZDZ) |
| Projekt UE | „Kształcenie zawodowe na potrzeby Gospodarki 4.0 i GOZ", nr FEPD.08.02-IZ.00-0005/24 |

---

## Stos technologiczny

| Warstwa | Technologia |
|---|---|
| Frontend | React + Vite |
| Backend | Python + FastAPI |
| Baza danych | SQLite (docelowo opcjonalnie MySQL) |
| ORM | SQLAlchemy |
| Testy | pytest |
| Wdrożenie demo | Render / Vercel |

---

## Zespół i role

| Osoba | Odpowiedzialność |
|---|---|
| Jakub Lewkowicz | Frontend (React), widoki ucznia i opiekuna, stylowanie |
| Kacper Musiaka | Baza danych, API wpisów (FastAPI + SQLAlchemy), eksport CSV |
| Michał Misiewicz | Logika statusów, walidacja limitów godzin, testy, wdrożenie |

---

## Uruchomienie lokalne

> 🔧 **TODO (dzień 17):** uzupełnić po zbudowaniu aplikacji.
> Każdy krok musi dać się wykonać na czystym komputerze — sprawdźcie to nawzajem.

### Wymagania

- Python 3.11+
- Node.js 20+

### Backend

```bash
# TODO: uzupełnić
```

### Frontend

```bash
# TODO: uzupełnić
```

Po uruchomieniu backendu automatyczna dokumentacja API dostępna jest pod `/docs`.

---

## Struktura repozytorium

```
projekt-stazowy-2026/
├── backend/          # FastAPI + SQLAlchemy
│   ├── app/
│   ├── tests/        # pytest
│   └── requirements.txt
└── frontend/         # React + Vite
    ├── src/
    └── package.json
```

> 🔧 **TODO (dzień 6):** utworzyć katalogi `backend/` i `frontend/` przy konfiguracji projektu.

---

## Statusy wpisu

Wpis w dzienniczku przechodzi przez zdefiniowane stany. **Tylko poniższe przejścia są dozwolone** —
każde inne backend odrzuca.

| Status początkowy | Akcja | Status końcowy | Kto wykonuje |
|---|---|---|---|
| `roboczy` | wyślij do zatwierdzenia | `wysłany` | uczeń |
| `wysłany` | zatwierdź | `zatwierdzony` | opiekun |
| `wysłany` | zwróć z komentarzem | `do poprawki` | opiekun |
| `do poprawki` | popraw i wyślij ponownie | `wysłany` | uczeń |
| `zatwierdzony` | — | — | stan końcowy |

---

## Zakres MVP

Minimum, które musi działać na **Demo Day (04.08)**:

- [ ] CRUD wpisu: data, godziny od–do, opis pracy, blokery
- [ ] Automatyczne liczenie godzin z zakresu „od–do"
- [ ] Workflow statusów (tabela powyżej)
- [ ] Zwrot wpisu z komentarzem (widok opiekuna)
- [ ] Widok ucznia (swoje wpisy) i widok opiekuna (lista do zatwierdzenia)
- [ ] Wybór ucznia z listy (bez logowania)
- [ ] Stały baner „DEMO — dane testowe" w interfejsie

### Funkcjonalności dodatkowe (tylko z zapasem czasu, w tej kolejności)

1. Walidacja limitów godzin (6 h / 8 h wg kategorii wieku; brak nakładania się wpisów)
2. Statystyki tygodniowe (suma godzin, liczba wpisów, % zatwierdzonych)
3. Eksport CSV / widok do druku
4. Logowanie i role
5. Widok kalendarza, filtrowanie, Docker

---

## Praca z repozytorium

Zasady pracy z Git, nazewnictwo gałęzi, proces Pull Request i definicja ukończenia:
**[CONTRIBUTING.md](CONTRIBUTING.md)**

Najważniejsze w skrócie:

- nie commitujemy bezpośrednio na `main` — ochrona gałęzi odrzuci taki push,
- każda zmiana wchodzi przez Pull Request,
- PR wymaga **1 zatwierdzenia** od kolegi z zespołu.

---

## Licencja

> 🔧 **TODO (dzień 18):** wybór licencji projektu jest zadaniem stażowym
> (obszar 15: prawo autorskie i licencjonowanie oprogramowania).
> Do tego czasu repozytorium nie ma przypisanej licencji.

---

## Dokumentacja i języki

- Dokumentacja, README i opisy Pull Requestów: **po polsku**
- Kod, nazwy plików, gałęzi, zmiennych i commity: **po angielsku**
