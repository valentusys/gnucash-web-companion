# gnucash-web-companion (RU)

> Статус: pre-alpha / v0.1 read-only опубликован. Английская документация в `README.md` остаётся канонической; этот русский файл — ограниченная справка и не является полным переводом.

`gnucash-web-companion` — self-hosted web companion для существующих GnuCash SQL books. Цель текущего MVP — безопасный read-only просмотр в браузере/на мобильном устройстве, пока GnuCash Desktop остаётся главным редактором.

## Что уже важно знать

- MVP v0.1 остаётся read-only by default.
- `GNUCASH_WRITES_ENABLED=false` — безопасный дефолт.
- Любой controlled-write код является experimental post-MVP и отключён по умолчанию.
- Не используйте pre-alpha сборку с единственной реальной книгой GnuCash: сначала тестовая копия или synthetic fixture.
- Не публикуйте early build напрямую в интернет.
- Английские safety/security тексты считаются источником правды; переводы требуют ручной проверки.

## Ограниченный русский UI

Русский язык включается вручную через переключатель языка в UI. Английский остаётся дефолтом.

Сейчас переведён только небольшой проверенный срез:

- экран входа;
- основная навигация, включая `/books`;
- read-only safety banner;
- заголовки Dashboard / Accounts / Transactions;
- страница `/books` для просмотра метаданных книг, без загрузки, удаления или редактирования данных GnuCash.

Это не полный перевод приложения. Backend/API ошибки, большая часть отчётных таблиц, release-документы и safety/security документы остаются на английском.

## Read-only смысл русских предупреждений

Русские предупреждения должны сохранять тот же смысл, что и английские:

- приложение по умолчанию только читает данные GnuCash;
- GnuCash Desktop остаётся главным редактором;
- web-записи требуют отдельного post-MVP feature flag;
- включать write mode против единственной реальной книги нельзя.

## English canonical docs

Основные документы:

- `README.md`
- `docs/GNUCASH_SAFETY.md`
- `docs/deployment/local-secure-deployment.md`
- `docs/operations/backup-and-recovery.md`
- `docs/v0.2-controlled-writes.md`
- `docs/localization.md`
