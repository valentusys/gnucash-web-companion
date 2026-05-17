# gnucash-web-companion (RU)

> Статус: pre-alpha / MVP в разработке. Английская документация в `README.md` остаётся канонической; этот русский файл — начальная справочная заглушка и может отставать.

`gnucash-web-companion` — self-hosted web companion для существующих GnuCash SQL books. Цель MVP — безопасный read-only просмотр в браузере/на мобильном устройстве, пока GnuCash Desktop остаётся главным редактором.

## Что уже важно знать

- MVP v0.1 остаётся read-only by default.
- `GNUCASH_WRITES_ENABLED=false` — безопасный дефолт.
- Любой controlled-write код является experimental post-MVP и отключён по умолчанию.
- Не используйте pre-alpha сборку с единственной реальной книгой GnuCash: сначала тестовая копия или synthetic fixture.
- Не публикуйте early build напрямую в интернет.
- Английские safety/security тексты считаются источником правды; переводы требуют ручной проверки.

## Phase 52 localization scope

В Phase 52 добавлена только i18n-основа и небольшой набор русских UI-строк:

- экран входа;
- базовая навигация;
- read-only safety banner;
- заголовки Dashboard / Accounts / Transactions.

Русский язык не является дефолтом и не блокирует v0.1. Подробности: `docs/localization.md`.

## English canonical docs

Основные документы:

- `README.md`
- `docs/GNUCASH_SAFETY.md`
- `docs/deployment/local-secure-deployment.md`
- `docs/operations/backup-and-recovery.md`
- `docs/v0.2-controlled-writes.md`
