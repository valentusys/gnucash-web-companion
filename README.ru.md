# gnucash-web-companion (RU)

> Статус: pre-alpha / MVP in progress. Английская документация в `README.md` остаётся канонической;
> этот русский файл синхронизирует публичный статус, но не является полным переводом.

`gnucash-web-companion` — self-hosted web companion для существующих GnuCash SQL books. Цель
текущего MVP — безопасный read-only просмотр в браузере/на мобильном устройстве, пока GnuCash
Desktop остаётся главным редактором. `/transactions` теперь включает bounded read-only explorer, а
`/reports` включает period reports и read-only сравнение периодов без FX-конвертации.

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

Короткая версия для review в терминале: README.ru держит только текущую публичную
позицию и ссылки. Длинная фазовая история остаётся в `PROJECT_STATUS.md`,
release docs и handoff-файлах, чтобы этот файл не становился статус-логом.

- Фазы 0–830 завершены; детали и evidence см. в
  [PROJECT_STATUS.md](PROJECT_STATUS.md).
- Текущий public read-only beta остаётся
  [`v0.5.0-public-readonly-beta`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.5.0-public-readonly-beta).
- `v0.5.1-public-readonly-beta` не опубликован.
- `v0.4.0-owner-writebeta` отложен; публичной write beta нет.
- Текущий опубликованный write-alpha pre-release остаётся
  [`v0.2.8-writealpha`](https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.8-writealpha),
  опубликованный после Phase 261 cycle-3 release gate.
- MVP/read-only доступ остаётся **read-only by default**.
- `GNUCASH_WRITES_ENABLED=false` остаётся безопасным дефолтом.
- #59 закрыта как completed: corrected product/docs head
  `694d6695c7f74b410d1770f1575c65af6eb94bbb` интегрирован и pushed FF-only для post-MVP controlled
  general transaction CREATE. Фича остаётся default-off: нужны deployment write enablement, отдельный
  per-book CREATE enablement и owner/editor assignment. Exact-head CI
  [29630743491](https://github.com/valentusys/gnucash-web-companion/actions/runs/29630743491),
  attempt 1, succeeded; final acceptance comment
  [#issuecomment-5009945433](https://github.com/valentusys/gnucash-web-companion/issues/59#issuecomment-5009945433)
  recorded, issue closed as completed at `2026-07-18T04:45:00Z`.
- Controlled-write код, если присутствует, является experimental post-MVP/write-alpha,
  отключён по умолчанию и дополнительно ограничен backend `APP_ENV=test` gate при явном включении.
- real/private/original/only-copy books не являются безопасной write-целью.
- #36 controlled-write readiness закрыта как `CLOSE_36_AS_MAINTENANCE_BOUNDARY`; это historical
  maintenance evidence only, не approval для real-book mutation.
- #44 Owner real-book trial safety model закрыта после одного успешного owner-approved real-book
  CREATE trial и manual Desktop verification; это не ongoing mutation approval.
- Read-only accounts/reports/transactions: #52 закрыта после принятого period reports explorer. #53
  добавляет URL-backed comparisons и точные paired transaction drilldowns. #54 закрыта как completed
  на exact head `0d9381544118a64795827b24d787d1a8e7d998c0` после bounded, URL-backed read-only
  transaction explorer с paired dates, account/type/direction/exact-amount/text filters, cursor
  pagination, safe detail back links, report/dashboard drilldowns и EN/RU mobile/browser coverage.
  Exact-head GitHub Actions CI run
  [29197662815](https://github.com/valentusys/gnucash-web-companion/actions/runs/29197662815)
  succeeded for Backend, Frontend, Docker Compose, and Foundation; final closeout comment
  [#issuecomment-4951703096](https://github.com/valentusys/gnucash-web-companion/issues/54#issuecomment-4951703096)
  recorded. #55 закрыта как completed на exact head
  `3dfd60604d78e329284979442b959aea4b6763a2` после hierarchical account explorer, bounded overview
  and activity, native commodity exact amounts, deterministic repair/partial semantics, SSR account
  navigation, transaction/report drilldowns и EN/RU desktop/mobile browser coverage. Exact-head
  GitHub Actions run
  [29297230998](https://github.com/valentusys/gnucash-web-companion/actions/runs/29297230998)
  succeeded for Backend tests, Frontend checks, Foundation checks, and Docker Compose validation;
  final acceptance comment
  [#issuecomment-4964411655](https://github.com/valentusys/gnucash-web-companion/issues/55#issuecomment-4964411655)
  recorded. Reporting/account views остаются без FX conversion.
- Book onboarding/health/lifecycle: #56 закрыта как completed на exact head
  `6928a2ae5f66f2ad16fdffdc26d1e8022ac5d706` и tree
  `9ab4a5239505c112dc1956459b60d643324af0ac`. Администратор может выполнить явный read-only
  preflight и token-bound подтверждение для существующей server-side GnuCash SQL SQLite book, после
  чего доступны cached health и app-metadata-only rename/base-currency/default/recheck/disable/enable/
  unregister controls. Upload/client file chooser отсутствует; XML/compressed XML не поддерживаются;
  unregister никогда не удаляет source; обычный пользователь видит только назначенные книги и
  path-safe diagnostics; GnuCash Desktop остаётся authoritative. Exact-head GitHub Actions run
  [29382943117](https://github.com/valentusys/gnucash-web-companion/actions/runs/29382943117),
  attempt 2, succeeded for Frontend checks, Backend tests, Foundation checks и Docker Compose
  validation. Final acceptance comment
  [#issuecomment-4976179921](https://github.com/valentusys/gnucash-web-companion/issues/56#issuecomment-4976179921)
  recorded. Это не release, production-readiness, security-audit или broad compatibility claim;
  `GNUCASH_WRITES_ENABLED=false` остаётся дефолтом.
- Admin users и app-metadata recovery: #57 и #58 закрыты как completed после independent PM/QA review
  и exact-head CI. Admin может управлять локальными пользователями и явным доступом к книгам без
  implicit default/new-book grants; disable/reset/revoke инвалидируют доступ до открытия source. #58
  добавляет app-metadata-only backup, verify, disposable restore rehearsal и synthetic upgrade
  rehearsal tooling. Это не backup/restore GnuCash source books, не browser DB backup/restore/download,
  не release и не production/security-audited claim.
- Controlled-write trackers #45–#50 остаются отдельными experimental post-MVP boundaries. Они не
  разрешают owner/private DELETE или batch, release publication или public write beta.
  `GNUCASH_WRITES_ENABLED=false` остаётся дефолтом.
- Недавно завершены: #51 disposable copied-book UI rehearsal, #52 read-only period reports, #22
  compatibility fixtures, #28 markdown readability, #13, #41, #42 и #43.

## Карта текущих статусов

- #59: закрыта как completed после corrected product/docs head
  `694d6695c7f74b410d1770f1575c65af6eb94bbb` / tree
  `4f8246ddd0a5f90d314c9d80a7e819efec6fde77` был integrated и pushed FF-only. Exact-head CI
  [29630743491](https://github.com/valentusys/gnucash-web-companion/actions/runs/29630743491),
  attempt 1, succeeded for Foundation, Frontend, Backend и Docker Compose; final acceptance comment
  [#issuecomment-5009945433](https://github.com/valentusys/gnucash-web-companion/issues/59#issuecomment-5009945433)
  recorded, issue closed as completed at `2026-07-18T04:45:00Z`. Accepted fixed-seed
  generated/disposable evidence покрывает expense, income, 3-split, Unicode CREATEs, same-GUID
  idempotency, typed safety rejections, verified backup, lock, close/reopen/read-back, ownership и
  audit controls. FX/trading не поддерживаются, PATCH/DELETE не являются normal product functions,
  owner/private vector равен zero. Evidence:
  [docs/handoff/hermes-kanban-product-run-9-write-create.md](docs/handoff/hermes-kanban-product-run-9-write-create.md).
- #56: закрыта как completed для onboarding существующей server-side SQLite book, cached health и
  admin-only app-metadata lifecycle controls на exact head
  `6928a2ae5f66f2ad16fdffdc26d1e8022ac5d706`; exact-head GitHub Actions run
  [29382943117](https://github.com/valentusys/gnucash-web-companion/actions/runs/29382943117),
  attempt 2, succeeded, final acceptance comment
  [#issuecomment-4976179921](https://github.com/valentusys/gnucash-web-companion/issues/56#issuecomment-4976179921)
  recorded. Нет upload, source delete, default GnuCash writes, production claim или broad
  format/version/backend claim.
- #55: закрыта как completed для advanced read-only account explorer на exact head
  `3dfd60604d78e329284979442b959aea4b6763a2`; exact-head GitHub Actions run
  [29297230998](https://github.com/valentusys/gnucash-web-companion/actions/runs/29297230998)
  succeeded, final acceptance comment
  [#issuecomment-4964411655](https://github.com/valentusys/gnucash-web-companion/issues/55#issuecomment-4964411655)
  recorded.
- #54: закрыта как completed для bounded read-only transaction explorer на exact head
  `0d9381544118a64795827b24d787d1a8e7d998c0`; exact-head GitHub Actions run
  [29197662815](https://github.com/valentusys/gnucash-web-companion/actions/runs/29197662815)
  succeeded, final closeout comment
  [#issuecomment-4951703096](https://github.com/valentusys/gnucash-web-companion/issues/54#issuecomment-4951703096)
  recorded.
- #53: закрыта как completed для accepted read-only comparison milestone после independent acceptance,
  exact-product-head CI и final documentation/issue closeout.
- #51 и #52 закрыты после принятого disposable UI rehearsal и read-only period reports explorer.
- #36 закрыта как maintenance boundary. #45–#50 остаются отдельной experimental controlled-write
  историей; CREATE/PATCH требуют fresh same-context owner/PM approval с точными counts, а DELETE,
  batch, release, public write beta и broad write-safety claims остаются запрещены.
- #22: compatibility fixtures закрыта narrowly for isolated Desktop-generated synthetic SQLite fixture
  read-only evidence only; future Desktop/backend/version fixture expansion остаётся separate work.
- #28: raw Markdown readability закрыта после terminal-readability/status guard cleanup без whole-repo reflow.

## Где смотреть подробности

- Подробный статус и длинная история: [PROJECT_STATUS.md](PROJECT_STATUS.md).
- Handoff/evidence docs: [docs/handoff/](docs/handoff/).
- Current public beta notes:
  [docs/release/v0.5.0-public-readonly-beta-notes.md](docs/release/v0.5.0-public-readonly-beta-notes.md)
  ([checklist](docs/release/v0.5.0-public-readonly-beta-checklist.md),
  [final gate](docs/release/v0.5.0-public-readonly-beta-final-gate.md),
  [publication evidence](docs/release/v0.5.0-public-readonly-beta-publication-evidence.md)).
- Current copied-book write-alpha posture:
  [docs/write-alpha/copied-book-write-alpha-posture.md](docs/write-alpha/copied-book-write-alpha-posture.md).
- Compatibility matrix and evidence boundaries:
  [docs/gnucash-compatibility.md](docs/gnucash-compatibility.md).
- Older read-only/write-alpha releases are historical pre-alpha references, not production or
  security-audited guarantees.

## Последние post-release фазы

- Phase 143 — добавлен app-shell read-only/current-book status banner.
- Phase 144 — добавлен локальный read-only фильтр дерева счетов.
- Phase 145 — добавлена сводка текущего вида транзакций с filter/export parity и CSV cap.
- Phase 146 — улучшена читаемость transaction detail/split rows на mobile/desktop.
- Phase 147 — уточнены dashboard/reporting ограничения: base-currency-only, no conversion,
  mixed-currency/`XXX` edge cases.
- Phase 148 — улучшена `/books` self-hosting readiness. Current #56 теперь добавляет admin-only app
  metadata registry lifecycle controls, сохраняя отсутствие upload, source delete, default accounting
  writes и private path rendering.
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
