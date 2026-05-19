# Analyst Roadmap — 2026-05-19

## 1. Краткая оценка текущего состояния

**Проект:** gnucash-web-companion (valentusys/gnucash-web-companion)
**Текущий HEAD:** `85d7781` — `docs: mark v0.2.0 writealpha release authorized`
**Ветка:** `main`, синхронизирован с `origin/main`
**Последний релиз:** `v0.2.0-writealpha` (pre-release, опубликован 2026-05-19)

### Состояние кодовой базы

| Метрика | Значение |
|---|---|
| Всего коммитов | 192 |
| Завершённых фаз | 0–132 |
| Backend-тесты | 377 passed (targeted checks: health/auth/models 28 passed, write-gating 8 passed) |
| Frontend svelte-check | 0 errors, 0 warnings |
| Auth-route checks | passed |
| Docker Compose config | valid |
| GitHub CI (последние 5) | all success |

### Что сделано

- Полностью реализован read-only MVP: дашборд, счета, транзакции, фильтры, CSV-экспорт, расписание, мультикнижность, мультивалютные ограничения
- Реализован write-alpha слой (create/PATCH/DELETE транзакций) — полностью disabled by default (`GNUCASH_WRITES_ENABLED=false`), требует `APP_ENV=test`, покрыт тестами только на synthetic/disposable fixtures
- Опубликовано 7 релизов (от v0.0.1-prealpha до v0.2.0-writealpha)
- Документация: 132 handoff-файлов, changelog, roadmap, compatibility matrix, security docs, localization glossary
- Открытых issues: 6 (#13, #17, #22, #28, #29, #36)

### Текущий статус безопасности

- `GNUCASH_WRITES_ENABLED=false` — default во всех конфигах
- Write-routes требуют `GNUCASH_WRITES_ENABLED=true` + `APP_ENV=test`
- Нет реальных книг/секретов/скриншотов с реальными данными в репозитории
- CI зелёный, чувствительные файлы под .gitignore

## 2. Процент read-only готовности

**Текущая read-only готовность: ~95%**

Read-only функциональность практически завершена. Оставшиеся ~5% — это:
- Мелкие UX-полировки (пустые состояния, edge cases)
- Расширение compatibility matrix для реальных версий GnuCash Desktop
- Покрытие дополнительных edge cases в фильтрации

**100% read-only готовность будет достигнута к Фазе 8** (после финального synthetic dogfood и закрытия оставшихся read-only UX gaps).

## 3. Когда начинается write-alpha

Write-alpha **уже начат и частично завершён** в фазах 123–132:

- Phase 123: write-alpha safety foundation
- Phase 124: create transaction hardening
- Phase 128: concurrency/error-path expansion
- Phase 129: recovery docs
- Phase 130: PATCH transaction hardening
- Phase 131: DELETE transaction hardening
- Phase 132: v0.2.0-writealpha release gate

**Write-alpha НЕ входит в следующие 10 фаз.** Следующие 10 фаз — это read-only полировка, UX, документация и подготовка к следующему maintenance release. Write-alpha продолжится только после явного запроса Валентина как отдельный блок работ.

## 4. Нужен ли PM

**PM НЕ нужен для следующих 10 фаз.**

Обоснование:
- Приоритеты не конфликтуют: все 10 фаз — read-only полировка и документация, чётко упорядоченные
- Нет выбора now/defer: фазы идут последовательно, каждая строится на предыдущей
- Нет решения release/no-release: Фаза 10 — это release-gate артефакты, публикация требует отдельной авторизации Валентина
- Риск «улучшательства» ограничен: scope каждой фазы узкий, non-goals явно указаны
- Нет риска приватных данных: работа ведётся только с synthetic fixtures
- Нет публикации релиза без авторизации: Фаза 10 производит только артефакты, тег/релиз — отдельным шагом

**PM подключать если:**
- Валентин захочет изменить приоритеты или scope
- Появится необходимость в write-mode работах
- Потребуется решение о публикации релиза
- Возникнет конфликт между улучшательством и стабильностью

## 5. Roadmap на 10 фаз

---

### Фаза 1 — Полировка read-only UX: пустые состояния и edge cases

**Goal:** Улучшить пользовательский опыт для edge cases: пустые списки, нет результатов поиска, недоступные книги, ошибки загрузки.

**Scope:**
- Компонент `EmptyState.svelte` — проверить/расширить все пустые состояния (нет счетов, нет транзакций, нет расписаний, нет доступных книг)
- Компонент `ErrorState.svelte` — проверить/расширить все состояния ошибок (ошибка API, сеть, 403, 404)
- Страница `/books` — пустое состояние когда нет доступных книг
- Страница `/scheduled` — пустое состояние когда нет расписаний
- Страница `/transactions` — пустое состояние когда нет транзакций или фильтры не дали результатов
- Страница `/accounts` — пустое состояние когда нет счетов
- Проверить доступность (aria-labels, keyboard navigation) для новых empty/error states

**Non-goals:**
- Не добавлять новые страницы или маршруты
- Не менять backend API
- Не добавлять новые фильтры или поиск
- Не трогать write-mode код
- Не публиковать релиз

**Acceptance criteria:**
- Все страницы имеют информативные пустые состояния с понятным текстом
- Все состояния ошибок имеют понятный текст и действие (retry/назад)
- Frontend svelte-check: 0 errors, 0 warnings
- Frontend route checks: passed
- Backend tests: без изменений (377 passed)

**Safety checks:**
- `GNUCASH_WRITES_ENABLED=false` не меняется
- Write endpoints не трогаются
- Нет реальных книг/экспортов/скриншотов с реальными данными
- Docker Compose config validation: passed

**Verification:**
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/api && pytest tests/test_health.py tests/test_auth.py -q`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

**Expected artifacts:**
- Обновлённые `.svelte` компоненты (EmptyState, ErrorState, страницы)
- `docs/handoff/phase-133.md`
- Обновлённый `PROJECT_STATUS.md`

---

### Фаза 2 — Полировка read-only UX: загрузка и скелетоны

**Goal:** Добавить состояния загрузки (skeleton screens) для улучшения perceived performance.

**Scope:**
- Компонент `LoadingState.svelte` — проверить/расширить
- Скелетон-загрузка для страницы `/dashboard` (summary cards, charts placeholders)
- Скелетон-загрузка для страницы `/accounts` (tree placeholders)
- Скелетон-загрузка для страницы `/transactions` (table/card placeholders)
- Скелетон-загрузка для страницы `/books` (list placeholders)
- Убедиться что loading states корректно показываются при переключении книг

**Non-goals:**
- Не менять backend API или добавлять новые endpoints
- Не добавлять реальные графики/чарты (только плейсхолдеры)
- Не трогать write-mode код
- Не публиковать релиз

**Acceptance criteria:**
- Все основные страницы показывают скелетон при загрузке данных
- Скелетоны визуально похожи на реальный контент (правильная структура)
- Нет layout shift при переходе от скелетона к контенту
- Frontend svelte-check: 0 errors, 0 warnings

**Safety checks:**
- `GNUCASH_WRITES_ENABLED=false` не меняется
- Write endpoints не трогаются
- Нет реальных данных в скриншотах/артефактах

**Verification:**
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

**Expected artifacts:**
- Обновлённые `.svelte` компоненты (LoadingState, страницы)
- `docs/handoff/phase-134.md`
- Обновлённый `PROJECT_STATUS.md`

---

### Фаза 3 — Полировка read-only UX: мобильная навигация

**Goal:** Улучшить мобильную навигацию и UX на маленьких экранах.

**Scope:**
- `MobileNav.svelte` — проверить/улучшить мобильное меню
- `DesktopNav.svelte` — проверить корректное переключение между mobile/desktop
- Проверить все страницы на мобильных breakpoints (320px–768px)
- Убедиться что touch targets ≥ 44px
- Проверить что горизонтальный скролл отсутствует на мобильных
- Проверить что модальные окна/дропдауны корректно работают на touch

**Non-goals:**
- Не добавлять новые страницы или маршруты
- Не менять backend API
- Не трогать write-mode код
- Не публиковать релиз

**Acceptance criteria:**
- Все страницы корректно отображаются на 320px–768px
- Нет горизонтального скролла на мобильных
- Touch targets ≥ 44px для всех интерактивных элементов
- Мобильное меню корректно открывается/закрывается
- Frontend svelte-check: 0 errors, 0 warnings

**Safety checks:**
- `GNUCASH_WRITES_ENABLED=false` не меняется
- Write endpoints не трогаются
- Нет реальных данных в артефактах

**Verification:**
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

**Expected artifacts:**
- Обновлённые `.svelte` компоненты (MobileNav, DesktopNav, страницы)
- `docs/handoff/phase-135.md`
- Обновлённый `PROJECT_STATUS.md`

---

### Фаза 4 — Документация: обновление compatibility matrix

**Goal:** Обновить матрицу совместимости GnuCash с учётом текущего состояния.

**Scope:**
- `docs/gnucash-compatibility.md` — обновить матрицу
- `docs/gnucash-version-fixture-plan.md` — обновить план
- Проверить что все synthetic fixtures корректно задокументированы
- Добавить явное указание какие версии GnuCash Desktop протестированы (synthetic only)
- Обновить `README.md` ссылку на compatibility docs если нужно

**Non-goals:**
- Не генерировать новые fixtures (только документация)
- Не тестировать реальные версии GnuCash Desktop
- Не менять backend/frontend код
- Не публиковать релиз

**Acceptance criteria:**
- Матрица совместимости актуальна и честна
- Явно указано что compatibility evidence основан на synthetic fixtures
- Нет ложных утверждений о поддержке версий
- Backend tests: 377 passed (без изменений)

**Safety checks:**
- Нет реальных книг в репозитории
- Нет ложных compatibility claims

**Verification:**
- `cd apps/api && pytest tests/test_gnucash_compatibility.py -q`
- `cd apps/api && pytest tests/test_gnucash_compatibility_metadata.py -q`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

**Expected artifacts:**
- Обновлённые docs (`gnucash-compatibility.md`, `gnucash-version-fixture-plan.md`)
- `docs/handoff/phase-136.md`
- Обновлённый `PROJECT_STATUS.md`

---

### Фаза 5 — Документация: deployment hardening guide

**Goal:** Обновить и расширить руководство по безопасному deployment.

**Scope:**
- `docs/deployment/local-secure-deployment.md` — обновить/расширить
- Добавить раздел о рекомендуемых `CORS_ORIGINS` для LAN/VPN
- Добавить раздел о настройке `JWT_SECRET` (генерация, ротация)
- Добавить раздел о бэкапах app metadata DB
- Добавить чеклист pre-deployment для самохостинга
- Обновить `.env.example` комментарии если нужно

**Non-goals:**
- Не менять backend/frontend код
- Не добавлять новые endpoints
- Не публиковать релиз
- Не делать production-readiness claims

**Acceptance criteria:**
- Deployment guide покрывает основные сценарии (localhost, LAN, VPN)
- Чеклист pre-deployment проверяем и конкретен
- Нет production-readiness claims
- Backend tests: 377 passed (без изменений)

**Safety checks:**
- Нет реальных секретов/путей в документации
- Нет production-readiness claims

**Verification:**
- `cd apps/api && pytest tests/test_health.py -q`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

**Expected artifacts:**
- Обновлённые docs (`local-secure-deployment.md`, `.env.example`)
- `docs/handoff/phase-137.md`
- Обновлённый `PROJECT_STATUS.md`

---

### Фаза 6 — Документация: обновление README и CHANGELOG

**Goal:** Синхронизировать README, CHANGELOG и публичный статус после фаз 1–5.

**Scope:**
- `README.md` — обновить текущий статус, скриншоты (если изменился UI), ссылки
- `CHANGELOG.md` — добавить записи для фаз 133–137
- `README.ru.md` — синхронизировать с английским README
- `docs/ROADMAP.md` — обновить статус
- Проверить что все ссылки в README работают

**Non-goals:**
- Не менять backend/frontend код
- Не добавлять новые функции
- Не публиковать релиз

**Acceptance criteria:**
- README актуален и корректен
- CHANGELOG содержит записи для всех завершённых фаз
- Все ссылки работают
- Нет production-readiness claims

**Safety checks:**
- Нет реальных скриншотов с приватными данными
- Нет production-readiness claims

**Verification:**
- `cd apps/api && pytest tests/test_health.py -q`
- `cd apps/web && npm run check`

**Expected artifacts:**
- Обновлённые `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`
- `docs/handoff/phase-138.md`
- Обновлённый `PROJECT_STATUS.md`

---

### Фаза 7 — Synthetic dogfood refresh

**Goal:** Провести полный synthetic dogfood проход после всех изменений из фаз 1–6.

**Scope:**
- Запустить локальный Docker/Caddy с `GNUCASH_WRITES_ENABLED=false`
- Запустить `scripts/smoke/read-only-api-smoke.py` — полный проход
- Запустить `scripts/smoke/read-only-browser-dogfood.py` — полный проход
- Проверить все основные UI пути: login, dashboard, accounts, books, scheduled, transactions, filters, account detail, transaction detail, CSV export
- Проверить что write UI скрыт/отключён
- Записать redacted evidence

**Non-goals:**
- Не использовать реальные/приватные книги
- Не менять код (только dogfood)
- Не публиковать релиз

**Acceptance criteria:**
- Все smoke checks проходят
- Все browser dogfood checks проходят
- Write UI скрыт/отключён
- Evidence задокументирована

**Safety checks:**
- Только synthetic/disposable data
- Нет реальных книг/скриншотов/экспортов в git
- `GNUCASH_WRITES_ENABLED=false`

**Verification:**
- Smoke script: all checks passed
- Browser dogfood: all checks passed
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

**Expected artifacts:**
- `docs/dogfood/phase-139-synthetic-dogfood.md`
- `docs/handoff/phase-139.md`
- Обновлённый `PROJECT_STATUS.md`

---

### Фаза 8 — Аудит готовности к maintenance release

**Goal:** Провести независимый аудит готовности к `v0.1.4-readonly` maintenance release.

**Scope:**
- Проверить что все изменения из фаз 1–3 задокументированы и протестированы
- Проверить что `GNUCASH_WRITES_ENABLED=false` остаётся default
- Проверить что write-gating тесты проходят
- Проверить что нет реальных книг/секретов в репозитории
- Проверить что README/CHANGELOG/PROJECT_STATUS синхронизированы
- Проверить что GitHub CI зелёный
- Проверить что Docker Compose config valid
- Записать вердикт: ready / not ready

**Non-goals:**
- Не менять код (только аудит)
- Не публиковать релиз
- Не создавать тег

**Acceptance criteria:**
- Аудит-отчёт создан
- Вердикт записан (ready / not ready)
- Все проверки задокументированы

**Safety checks:**
- Read-only только
- Нет реальных данных

**Verification:**
- `cd apps/api && pytest tests/test_transaction_writes.py::TestWritesDisabledByDefault -q`
- `cd apps/web && npm run test:auth-routes`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `gh run list --limit 5` — all success

**Expected artifacts:**
- `docs/audits/2026-05-19-phase-139-audit.md`
- `docs/handoff/phase-140.md`
- Обновлённый `PROJECT_STATUS.md`

---

### Фаза 9 — Подготовка release артефактов для v0.1.4-readonly

**Goal:** Подготовить артефакты для возможного `v0.1.4-readonly` maintenance release.

**Scope:**
- Создать `docs/release/v0.1.4-readonly-notes.md`
- Создать `docs/release/v0.1.4-readonly-checklist.md`
- Создать `docs/release/v0.1.4-readonly-final-gate.md`
- Обновить `CHANGELOG.md` секцию `[0.1.4-readonly]`
- Обновить `README.md` ссылку на текущий релиз
- Обновить `PROJECT_STATUS.md`

**Non-goals:**
- Не создавать git tag
- Не создавать GitHub release
- Не публиковать пакеты
- Не менять `GNUCASH_WRITES_ENABLED=false` default

**Acceptance criteria:**
- Release notes честны: pre-alpha, read-only, not production-ready
- Checklist полон и проверяем
- Final-gate содержит вердикт
- Нет production-readiness claims

**Safety checks:**
- Нет тега, релиза, пакета
- `GNUCASH_WRITES_ENABLED=false` остаётся default
- Нет реальных данных

**Verification:**
- `cd apps/api && pytest tests/test_health.py tests/test_auth.py -q`
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

**Expected artifacts:**
- `docs/release/v0.1.4-readonly-notes.md`
- `docs/release/v0.1.4-readonly-checklist.md`
- `docs/release/v0.1.4-readonly-final-gate.md`
- Обновлённые `CHANGELOG.md`, `README.md`, `PROJECT_STATUS.md`
- `docs/handoff/phase-141.md`

---

### Фаза 10 — Release gate и публикация v0.1.4-readonly (при авторизации)

**Goal:** Провести финальный release gate и, при наличии авторизации Валентина, опубликовать `v0.1.4-readonly`.

**Scope:**
- Проверить clean `main`, `HEAD == origin/main`
- Проверить что все release артефакты на месте
- Проверить что GitHub CI зелёный
- Проверить что Docker Compose config valid
- Проверить что нет реальных книг/секретов в репозитории
- Проверить что `GNUCASH_WRITES_ENABLED=false` остаётся default
- **При наличии авторизации Валентина:**
  - Создать git tag `v0.1.4-readonly`
  - Создать GitHub pre-release
  - Записать publication evidence
- **При отсутствии авторизации:**
  - Записать вердикт «Ready for authorized publish»
  - Не создавать тег/релиз

**Non-goals:**
- Не публиковать без авторизации Валентина
- Не менять `GNUCASH_WRITES_ENABLED=false` default
- Не ослаблять `APP_ENV=test` gate для write-alpha
- Не добавлять новые функции

**Acceptance criteria:**
- Release gate пройден и задокументирован
- Если авторизован: tag создан, GitHub pre-release опубликован
- Если не авторизован: вердикт «Ready for authorized publish», тег/релиз не созданы
- Нет production-readiness claims

**Safety checks:**
- `GNUCASH_WRITES_ENABLED=false` остаётся default
- Write-alpha остаётся disabled
- Нет реальных книг/секретов/приватных данных в git
- Publication только при явной авторизации

**Verification:**
- `cd apps/api && pytest tests/test_transaction_writes.py::TestWritesDisabledByDefault -q`
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `gh run list --limit 5` — all success
- `git diff --check` — passed

**Expected artifacts:**
- `docs/release/v0.1.4-readonly-publication-evidence.md` (если опубликован)
- `docs/handoff/phase-142.md`
- Обновлённые `PROJECT_STATUS.md`, `CHANGELOG.md`, `README.md`
- Git tag + GitHub pre-release (только при авторизации)

---

## Сводка roadmap

| Фаза | Тип | Результат |
|---|---|---|
| 1 | UX | Пустые состояния и edge cases |
| 2 | UX | Скелетоны загрузки |
| 3 | UX | Мобильная навигация |
| 4 | Docs | Compatibility matrix update |
| 5 | Docs | Deployment hardening guide |
| 6 | Docs | README/CHANGELOG sync |
| 7 | QA | Synthetic dogfood refresh |
| 8 | Audit | Release readiness audit |
| 9 | Release | Release артефакты v0.1.4-readonly |
| 10 | Release | Release gate + публикация (при авторизации) |

**Ключевые принципы:**
- Все 10 фаз — read-only only
- Write-alpha не трогается
- `GNUCASH_WRITES_ENABLED=false` не меняется
- Публикация только при авторизации Валентина
- PM не нужен — scope узкий, приоритеты не конфликтуют
