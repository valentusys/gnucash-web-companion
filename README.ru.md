# gnucash-web-companion (RU)

> Статус: pre-alpha / MVP in progress. Английская документация в `README.md` остаётся канонической;
> этот русский файл синхронизирует публичный статус, но не является полным переводом.

`gnucash-web-companion` — self-hosted web companion для существующих GnuCash SQL books. Цель
текущего MVP — безопасный read-only просмотр в браузере/на мобильном устройстве, пока GnuCash
Desktop остаётся главным редактором.

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

- Фазы 0–250 завершены.
- MVP v0.1 остаётся **read-only by default**.
- `GNUCASH_WRITES_ENABLED=false` — безопасный дефолт.
- Controlled-write код, если присутствует, является experimental post-MVP/write-alpha, отключён по
  умолчанию и дополнительно ограничен backend `APP_ENV=test` gate при явном включении.
- Текущий публичный read-only pre-alpha release:
  [`v0.1.7-readonly`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.7-readonly).
- Предыдущий публичный read-only pre-alpha release:
  [`v0.1.6-readonly`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.6-readonly).
- Предыдущие write-alpha pre-release:
  [`v0.2.5-writealpha`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.5-writealpha),
  [`v0.2.4-writealpha`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.4-writealpha),
  [`v0.2.3-writealpha`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.3-writealpha),
  [`v0.2.2-writealpha`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.2-writealpha),
  [`v0.2.1-writealpha`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.1-writealpha)
  и
  [`v0.2.0-writealpha`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.0-writealpha);
  они pre-alpha/experimental, disabled by default, не production-ready, не security-audited и не
  заявляют безопасность записей в real/private books.
- Текущий опубликованный write-alpha pre-release:
  [`v0.2.6-writealpha`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.6-writealpha),
  опубликован в Phase 241 после cycle-1 release gate, PM authorization и green exact-commit CI:
  [notes](docs/release/v0.2.6-writealpha-notes.md),
  [checklist](docs/release/v0.2.6-writealpha-checklist.md), [final
  gate](docs/release/v0.2.6-writealpha-final-gate.md), [publication
  evidence](docs/release/v0.2.6-writealpha-publication-evidence.md). Write-alpha нельзя использовать
  на real/private books или единственной копии книги; только synthetic/disposable или copied test
  books, которые можно восстановить или удалить.
- Phase 221 проверил `v0.2.5-writealpha` и зафиксировал explicit no-release verdict: Phase 220 нашёл
  DELETE backup-count anomaly в bounded write-alpha evidence. Phases 222–228 закрыли и
  smoke-verified blocker только как synthetic/disposable backup-audit evidence и default-disabled
  fresh-clone/upgrade evidence; Phase 229 обновил public status/release-doc drift guard после
  remediation; Phase 230 собрал green final release-candidate dogfood pack; Phase 231 опубликовал
  `v0.2.5-writealpha` только после final local gates и green exact release/status commit CI; Phase
  232 сверил public status/changelog wording после публикации; Phase 233 улучшил raw markdown
  readability README/README.ru/CHANGELOG/PROJECT_STATUS без изменения safety wording; Phase 234
  добавил conservative [copied-book write-alpha dogfood runbook](docs/write-alpha/copied-book-dogfood-runbook.md);
  Phase 235 добавил local-only redacted `scripts/write_alpha_preflight.py` target preflight CLI для
  будущего copied/disposable тестирования; Phase 236 добавил redacted dogfood evidence schema и
  `scripts/redact_dogfood_evidence.py`, чтобы будущие отчёты reject/redact path-like, amount-like,
  memo/account-name и payload-like data до commit; Phase 237 добавил явно unsafe-for-real-books
  `.env.writealpha.example` reference и [write-alpha environment guidance](docs/write-alpha/environment.md)
  для local-only operator testing без изменения default read-only config; Phase 238 добавил
  redacted non-mutating `scripts/write_alpha_readiness.py` readiness command для проверки
  write-alpha prerequisites; Phase 239 записал synthetic copied-book dry-run через Docker/Caddy по
  Phase 236 evidence schema; Phase 240 подготовил release-candidate docs для
  `v0.2.6-writealpha`; Phase 241 вызвал PM, повторил release gate, дождался green exact
  release/status commit CI и опубликовал `v0.2.6-writealpha` как conservative GitHub pre-release.
  Cycle 2 затем добавил ownership boundary: CREATE создаёт write-alpha-owned транзакции, PATCH/DELETE
  ограничены write-alpha-owned транзакциями, а historical/manual GnuCash transactions остаются
  read-only в этом app. Phase 249 зафиксировал эти operator warnings в write-alpha docs, а Phase
  250 подготовил `v0.2.7-writealpha` release-candidate notes/checklist/final-gate только для
  будущего Phase 251 release/no-release решения.
  Write-alpha остаётся
  pre-alpha/experimental, disabled by default, `APP_ENV=test` gated при явном включении и не безопасен
  для real/private или only-copy books.
- Compatibility matrix: [docs/gnucash-compatibility.md](docs/gnucash-compatibility.md). Текущие
  evidence boundaries — synthetic/disposable fixtures only; broad real GnuCash Desktop version
  support не заявлен.

## Последние post-release фазы

- Phase 143 — добавлен app-shell read-only/current-book status banner.
- Phase 144 — добавлен локальный read-only фильтр дерева счетов.
- Phase 145 — добавлена сводка текущего вида транзакций с filter/export parity и CSV cap.
- Phase 146 — улучшена читаемость transaction detail/split rows на mobile/desktop.
- Phase 147 — уточнены dashboard/reporting ограничения: base-currency-only, no conversion,
  mixed-currency/`XXX` edge cases.
- Phase 148 — улучшена `/books` self-hosting readiness без
  upload/delete/default-changing/registry-edit действий.
- Phase 149 — расширено Russian localization coverage для нового read-only UX через существующий
  catalog; перевод остаётся частичным, English остаётся canonical.
- Phase 150 — повторно пройден synthetic/disposable Docker/Caddy read-only API и headless browser
  dogfood с `GNUCASH_WRITES_ENABLED=false` после последних UX/localization изменений.
- Phase 159 — расширен release-critical Russian localization slice: dashboard report
  cards/drilldowns, recent/expense/cashflow widgets, `/scheduled` filters/metadata/empty states, and
  landing-page sign-in copy now use the English/Russian catalog; перевод всё ещё частичный, English
  остаётся canonical.
- Phase 169 — закрыт заметный RU/EN mismatch на release-critical login/error/operator paths: login
  validation/auth-configuration failures and global 403/404/API/network/5xx guidance now use the
  English/Russian catalog; перевод остаётся частичным, English остаётся canonical.
- Phase 170 — повторно пройден full cycle 2 synthetic/disposable Docker/Caddy API и browser dogfood
  с `GNUCASH_WRITES_ENABLED=false`.
- Phase 171 — опубликован `v0.1.7-readonly` как authorized GitHub pre-release после green final
  gates.
- Phase 172 — синхронизирован публичный статус README/README.ru/CHANGELOG/PROJECT_STATUS/release
  artifacts после публикаций `v0.1.7-readonly` и `v0.2.0-writealpha`; product code не менялся.
- Phase 173 — подготовлен local-only runbook для copied/disposable write-alpha dogfood.
- Phase 174 — реализован redacted preflight harness для copied-book write-alpha.
- Phase 175 — выполнен один controlled create dogfood на synthetic/disposable copied book с явным
  `APP_ENV=test` и local-only `GNUCASH_WRITES_ENABLED=true`.
- Phase 176 — disposable mutated book проверен через GnuCash CLI tooling во временном Debian
  container.
- Phase 177 — выполнен disposable backup/restore drill и read-only smoke с default disabled writes.
- Phase 178 — улучшены write-alpha UX guardrails и safe error handling для disposable/test-copy
  boundary.
- Phase 179 — усилена backend write-alpha обработка lock-contention/path-like errors без расширения
  write scope.
- Phase 180 — повторно пройден combined default-read-only Docker/Caddy dogfood и отдельный explicit
  disposable write-alpha smoke.
- Phase 181 — подготовлен unpublished `v0.2.1-writealpha` release-readiness gate; публикация
  остановлена до явной авторизации владельца.
- Phase 182 — fresh pre-publish gate пройден, `v0.2.1-writealpha` опубликован как authorized GitHub
  pre-release после clean `main`, `HEAD == origin/main`, отсутствия tag/release, зелёного GitHub
  Actions на exact release commit, local checks, write-disabled Compose defaults и sensitive
  tracked-file hygiene.
- Phase 183 — усилены stale/root-owned lock recovery evidence и safe operator guidance без automatic
  lock deletion.
- Phase 184 — выполнен bounded synthetic/disposable PATCH dogfood для существующего
  metadata/split-memo route.
- Phase 185 — выполнен bounded synthetic/disposable DELETE dogfood с restore proof.
- Phase 186 — добавлен read-only redacted write-alpha audit summary endpoint/UI для disposable runs.
- Phase 187 — усилены multi-book read-only access boundaries и selected-book recovery после
  write-alpha work.
- Phase 188 — улучшена reporting correctness для mixed-currency, unknown-base, zero-balance,
  signed-balance и drilldown edge cases.
- Phase 189 — fresh-clone Docker smokes пройдены для current read-only tag, current write-alpha tag
  и `main` с default disabled writes.
- Phase 190 — пройден combined cycle-2 release-candidate dogfood: default read-only API/browser plus
  separate explicit local-only create/PATCH/DELETE write-alpha evidence.
- Phase 191 — cycle-2 release-readiness gate пройден; `v0.2.2-writealpha` опубликован как authorized
  GitHub pre-release после green exact-commit CI.
- Phase 192 — убраны GitHub Actions Node.js 20 action deprecation warnings без изменения
  product/runtime defaults.
- Phase 193 — добавлен stopped-runtime-only cleanup/recovery helper для ignored root-owned runtime
  artifacts и stale/unreadable locks.
- Phase 194 — write-alpha smoke helpers стали устойчивыми к root-owned host-side artifacts без
  повторного запуска mutating routes.
- Phase 195 — усилен read-only write-alpha audit-summary operator UX с safe filters и redacted
  count/status metadata.
- Phase 196 — добавлены redacted first-run/read-only deployment diagnostics для
  JWT/admin/default-book/CORS/write-mode triage.
- Phase 197 — обновлён GnuCash Desktop fixture compatibility blocker evidence через disposable
  tooling probe и redaction/provenance tests.
- Phase 198 — усилены multi-book read-only registry diagnostics и selected-book recovery без raw
  paths и management/write controls.
- Phase 199 — пройден full default-read-only Docker/Caddy API/browser regression dogfood; disabled
  validate/create/PATCH/DELETE probes вернули 403.
- Phase 200 — пройден bounded write-alpha create/PATCH/DELETE disposable CRUD/restore dogfood, stack
  returned to default false, ignored runtime artifacts cleaned.
- Phase 201 — cycle-3 release-readiness gate пройден; `v0.2.3-writealpha` опубликован как authorized
  GitHub pre-release после green exact-commit CI.
- Phase 202 — усилены default read-only first-run diagnostics для health/login/books error states
  без включения writes.
- Phase 203 — обновлён safe disposable Desktop fixture capture path и зафиксирован blocker для
  noninteractive Desktop-generated SQLite fixture.
- Phase 204 — добавлены compatibility-matrix regression checks из redacted fixture metadata без
  broad backend/Desktop support claims.
- Phase 205 — улучшена multi-book read-only recovery для inaccessible/archived/missing/stale
  selected-book contexts.
- Phase 206 — усилены transaction/scheduled read-only edge cases и пройден synthetic mobile/desktop
  Docker/Caddy dogfood.
- Phase 207 — усилена redaction для read-only write-alpha audit-summary и bounded
  count/status/time-window metadata.
- Phase 208 — отполирована EN/RU operator safety copy для read-only/write-alpha warnings без full
  localization claim.
- Phase 209 — пройден full default-read-only Docker/Caddy API/browser dogfood; disabled
  validate/create/PATCH/DELETE probes вернули 403.
- Phase 210 — пройден bounded write-alpha create/PATCH/DELETE+restore dogfood на fresh ignored
  synthetic runtime copies, stack returned to default false, artifacts cleaned.
- Phase 211 — cycle-1 release gate пройден; `v0.2.4-writealpha` опубликован как authorized GitHub
  pre-release после green exact-commit CI.
- Phase 212 — синхронизирован stale public roadmap/status слой после `v0.2.4-writealpha` и добавлен
  public status drift guard для README/PROJECT_STATUS/CHANGELOG/docs/ROADMAP/release docs.
- Phase 213 — `v0.2.4-writealpha` проверен из fresh clone/tag path с synthetic fixture,
  default-disabled writes, API smoke, disabled validate/create/PATCH/DELETE probes и mobile/desktop
  browser dogfood.
- Phase 214 — добавлен и пройден synthetic local upgrade smoke от `v0.2.4-writealpha` runtime state
  к current `main`: dummy app metadata DB, default book, selected-book recovery, read-only routes,
  audit-summary и disabled writes сохранились.

## Как пробовать безопасно

- Сначала используйте test copy или synthetic/disposable fixture, а не единственную реальную книгу.
- Держите регулярные tested backups GnuCash files и `data/app/app.db`.
- Не коммитьте `.env`, app DB, GnuCash books, backups, private screenshots/exports, tokens, keys,
  certs или реальные финансовые данные.
- Не публикуйте early build напрямую в интернет; используйте local/LAN/VPN-only testing.
- Держите `GNUCASH_WRITES_ENABLED=false`, если только вы явно не тестируете post-MVP write-alpha на
  disposable fixture.

## Ограниченный русский UI

Русский язык включается вручную через переключатель языка в UI. Английский остаётся дефолтом и
каноническим источником для safety/release wording.

Сейчас переведён только небольшой проверенный срез:

- экран входа;
- основная навигация, включая `/books`;
- read-only safety banner и current-book link на `/books`;
- заголовки Dashboard / Accounts / Transactions;
- account-tree filter labels/statuses/empty states;
- dashboard/reporting limitation labels, report cards, drilldown helper copy, recent transactions,
  expenses by account, and cashflow labels;
- transaction filter/export copy, transaction detail/split metadata labels and empty states;
- страница `/books` для просмотра метаданных книг, без загрузки, удаления или редактирования данных
  GnuCash;
- страница `/scheduled`: safe metadata headings, URL-only filters/sorting, counts, labels, and empty
  states.
- login error states and global 403/404/API/network/5xx operator guidance for safe `/health`, local
  `.env`, and book-volume checks.

Это не полный перевод приложения. Backend/API payloads не переведены как полный слой;
release-документы и большинство safety/security документов остаются на английском.

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
