# gnucash-web-companion (RU)

> Статус: pre-alpha / MVP in progress. Английская документация в `README.md` остаётся канонической; этот русский файл синхронизирует публичный статус, но не является полным переводом.

`gnucash-web-companion` — self-hosted web companion для существующих GnuCash SQL books. Цель текущего MVP — безопасный read-only просмотр в браузере/на мобильном устройстве, пока GnuCash Desktop остаётся главным редактором.

## Что это

- Read-only-first веб-приложение для существующих GnuCash SQL books через `piecash`.
- Self-hosted приложение для своей инфраструктуры.
- Companion, а не замена GnuCash: GnuCash Desktop остаётся источником правды для редактирования.
- Single-book by default, с read-only foundation для будущих независимых книг и scoped access.

## Что это не

- Не GnuCash replacement.
- Не hosted personal-finance SaaS.
- Не collaborative multi-user accounting.
- Не family-wallet baseline.
- Не production-ready и не security-audited accounting software.
- Не безопасный write mode для единственной реальной книги.

## Текущий публичный статус

- Завершены Phase 0–159.
- MVP v0.1 остаётся **read-only by default**.
- `GNUCASH_WRITES_ENABLED=false` — безопасный дефолт.
- Controlled-write код, если присутствует, является experimental post-MVP/write-alpha, отключён по умолчанию и дополнительно ограничен backend `APP_ENV=test` gate при явном включении.
- Текущий публичный read-only pre-alpha release: [`v0.1.5-readonly`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.5-readonly).
- Опубликованный write-alpha pre-release: `v0.2.0-writealpha`; он pre-alpha/experimental, disabled by default, не production-ready, не security-audited и не заявляет безопасность записей в real/private books.
- Compatibility matrix: [docs/gnucash-compatibility.md](docs/gnucash-compatibility.md). Текущие evidence boundaries — synthetic/disposable fixtures only; broad real GnuCash Desktop version support не заявлен.

## Последние post-release фазы

- Phase 143 — добавлен app-shell read-only/current-book status banner.
- Phase 144 — добавлен локальный read-only фильтр дерева счетов.
- Phase 145 — добавлена сводка текущего вида транзакций с filter/export parity и CSV cap.
- Phase 146 — улучшена читаемость transaction detail/split rows на mobile/desktop.
- Phase 147 — уточнены dashboard/reporting ограничения: base-currency-only, no conversion, mixed-currency/`XXX` edge cases.
- Phase 148 — улучшена `/books` self-hosting readiness без upload/delete/default-changing/registry-edit действий.
- Phase 149 — расширено Russian localization coverage для нового read-only UX через существующий catalog; перевод остаётся частичным, English остаётся canonical.
- Phase 150 — повторно пройден synthetic/disposable Docker/Caddy read-only API и headless browser dogfood с `GNUCASH_WRITES_ENABLED=false` после последних UX/localization изменений.
- Phase 159 — расширен release-critical Russian localization slice: dashboard report cards/drilldowns, recent/expense/cashflow widgets, `/scheduled` filters/metadata/empty states, and landing-page sign-in copy now use the English/Russian catalog; перевод всё ещё частичный, English остаётся canonical.

## Как пробовать безопасно

- Сначала используйте test copy или synthetic/disposable fixture, а не единственную реальную книгу.
- Держите регулярные tested backups GnuCash files и `data/app/app.db`.
- Не коммитьте `.env`, app DB, GnuCash books, backups, private screenshots/exports, tokens, keys, certs или реальные финансовые данные.
- Не публикуйте early build напрямую в интернет; используйте local/LAN/VPN-only testing.
- Держите `GNUCASH_WRITES_ENABLED=false`, если только вы явно не тестируете post-MVP write-alpha на disposable fixture.

## Ограниченный русский UI

Русский язык включается вручную через переключатель языка в UI. Английский остаётся дефолтом и каноническим источником для safety/release wording.

Сейчас переведён только небольшой проверенный срез:

- экран входа;
- основная навигация, включая `/books`;
- read-only safety banner и current-book link на `/books`;
- заголовки Dashboard / Accounts / Transactions;
- account-tree filter labels/statuses/empty states;
- dashboard/reporting limitation labels, report cards, drilldown helper copy, recent transactions, expenses by account, and cashflow labels;
- transaction filter/export copy, transaction detail/split metadata labels and empty states;
- страница `/books` для просмотра метаданных книг, без загрузки, удаления или редактирования данных GnuCash;
- страница `/scheduled`: safe metadata headings, URL-only filters/sorting, counts, labels, and empty states.

Это не полный перевод приложения. Backend/API ошибки, release-документы и большинство safety/security документов остаются на английском.

## English canonical docs

Основные документы:

- [README.md](README.md)
- [docs/GNUCASH_SAFETY.md](docs/GNUCASH_SAFETY.md)
- [docs/deployment/local-secure-deployment.md](docs/deployment/local-secure-deployment.md)
- [docs/operations/backup-and-recovery.md](docs/operations/backup-and-recovery.md)
- [docs/v0.2-controlled-writes.md](docs/v0.2-controlled-writes.md)
- [docs/localization.md](docs/localization.md)
- [CHANGELOG.md](CHANGELOG.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
