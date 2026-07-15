export const DEFAULT_LOCALE = 'en';
export const LOCALE_COOKIE = 'ui_locale';

export const supportedLocales = ['en', 'ru'] as const;

export type Locale = (typeof supportedLocales)[number];

export type MessageKey =
	| 'locale.english'
	| 'locale.russian'
	| 'locale.switcherLabel'
	| 'login.title'
	| 'login.subtitle'
	| 'login.username'
	| 'login.password'
	| 'login.submit'
	| 'login.error.missingCredentials'
	| 'login.error.serviceUnavailable'
	| 'login.error.invalidCredentials'
	| 'login.error.operatorConfiguration'
	| 'login.notice.sessionChanged'
	| 'login.firstRun.title'
	| 'login.firstRun.summary'
	| 'login.firstRun.safeDiagnostics'
	| 'login.firstRun.jwtSecret'
	| 'login.firstRun.adminBootstrap'
	| 'login.firstRun.defaultBook'
	| 'login.firstRun.cors'
	| 'login.firstRun.writeMode'
	| 'login.firstRun.status.ok'
	| 'login.firstRun.status.warning'
	| 'login.firstRun.status.actionRequired'
	| 'nav.dashboard'
	| 'nav.accounts'
	| 'nav.transactions'
	| 'nav.scheduled'
	| 'nav.reports'
	| 'nav.books'
	| 'nav.adminUsers'
	| 'nav.logout'
	| 'adminUsers.kicker'
	| 'adminUsers.title'
	| 'adminUsers.subtitle'
	| 'adminUsers.backToUsers'
	| 'adminUsers.createUser'
	| 'adminUsers.listTitle'
	| 'adminUsers.listHelp'
	| 'adminUsers.loading'
	| 'adminUsers.emptyTitle'
	| 'adminUsers.emptyMessage'
	| 'adminUsers.adminRequiredTitle'
	| 'adminUsers.adminRequiredMessage'
	| 'adminUsers.safeBoundaryBadge'
	| 'adminUsers.username'
	| 'adminUsers.displayName'
	| 'adminUsers.status'
	| 'adminUsers.enabled'
	| 'adminUsers.disabled'
	| 'adminUsers.adminBadge'
	| 'adminUsers.userBadge'
	| 'adminUsers.assignmentCount'
	| 'adminUsers.createdAt'
	| 'adminUsers.updatedAt'
	| 'adminUsers.actions'
	| 'adminUsers.viewDetails'
	| 'adminUsers.previousPage'
	| 'adminUsers.nextPage'
	| 'adminUsers.stateFilter'
	| 'adminUsers.stateAll'
	| 'adminUsers.stateEnabled'
	| 'adminUsers.stateDisabled'
	| 'adminUsers.applyFilter'
	| 'adminUsers.newTitle'
	| 'adminUsers.newSubtitle'
	| 'adminUsers.createTitle'
	| 'adminUsers.usernameHelp'
	| 'adminUsers.displayNameHelp'
	| 'adminUsers.initialPassword'
	| 'adminUsers.passwordHelp'
	| 'adminUsers.isAdminChoice'
	| 'adminUsers.isAdminHelp'
	| 'adminUsers.zeroAccessDefault'
	| 'adminUsers.createSubmit'
	| 'adminUsers.detailTitle'
	| 'adminUsers.detailSubtitle'
	| 'adminUsers.summaryTitle'
	| 'adminUsers.updateDisplayNameTitle'
	| 'adminUsers.updateDisplayNameHelp'
	| 'adminUsers.updateDisplayNameSubmit'
	| 'adminUsers.enableTitle'
	| 'adminUsers.enableHelp'
	| 'adminUsers.enableSubmit'
	| 'adminUsers.disableTitle'
	| 'adminUsers.disableHelp'
	| 'adminUsers.confirmDisableCopy'
	| 'adminUsers.disableSubmit'
	| 'adminUsers.resetPasswordTitle'
	| 'adminUsers.resetPasswordHelp'
	| 'adminUsers.newPassword'
	| 'adminUsers.confirmResetCopy'
	| 'adminUsers.resetPasswordSubmit'
	| 'adminUsers.accessTitle'
	| 'adminUsers.accessHelp'
	| 'adminUsers.book'
	| 'adminUsers.role'
	| 'adminUsers.grantSubmit'
	| 'adminUsers.revokeSubmit'
	| 'adminUsers.confirmRevokeCopy'
	| 'adminUsers.noBooksTitle'
	| 'adminUsers.noBooksMessage'
	| 'adminUsers.bookOptionsUnavailableTitle'
	| 'adminUsers.bookOptionsUnavailableMessage'
	| 'adminUsers.noAssignments'
	| 'adminUsers.limitedActionsNote'
	| 'adminUsers.passwordNotRepopulated'
	| 'adminUsers.role.viewer'
	| 'adminUsers.role.editor'
	| 'adminUsers.role.owner'
	| 'adminUsers.roleCopy.viewer'
	| 'adminUsers.roleCopy.editor'
	| 'adminUsers.roleCopy.owner'
	| 'adminUsers.roleBoundary'
	| 'adminUsers.problem.username_invalid'
	| 'adminUsers.problem.username_taken'
	| 'adminUsers.problem.display_name_invalid'
	| 'adminUsers.problem.password_policy'
	| 'adminUsers.problem.user_not_found'
	| 'adminUsers.problem.user_disabled'
	| 'adminUsers.problem.session_changed'
	| 'adminUsers.problem.self_disable_forbidden'
	| 'adminUsers.problem.last_enabled_admin'
	| 'adminUsers.problem.book_not_assignable'
	| 'adminUsers.problem.admin_required'
	| 'adminUsers.problem.api_unavailable'
	| 'adminUsers.problem.unknown_admin_problem'
	| 'adminUsers.success.user_created'
	| 'adminUsers.success.display_name_changed'
	| 'adminUsers.success.user_enabled'
	| 'adminUsers.success.user_disabled'
	| 'adminUsers.success.password_reset'
	| 'adminUsers.success.book_access_granted'
	| 'adminUsers.success.book_access_revoked'
	| 'safety.statusLabel'
	| 'safety.badge'
	| 'safety.message'
	| 'safety.releaseCritical'
	| 'safety.currentBook'
	| 'safety.noActiveBook'
	| 'safety.reviewBooks'
	| 'error.badgeWithCode'
	| 'error.badgeNetwork'
	| 'error.forbiddenTitle'
	| 'error.forbiddenMessage'
	| 'error.notFoundTitle'
	| 'error.notFoundMessage'
	| 'error.serviceTitle'
	| 'error.serviceMessage'
	| 'error.genericTitle'
	| 'error.genericMessage'
	| 'error.retry'
	| 'error.retryPage'
	| 'error.backDashboard'
	| 'error.reviewBooks'
	| 'dashboard.title'
	| 'accounts.kicker'
	| 'accounts.title'
	| 'accounts.bookLabel'
	| 'accounts.loading'
	| 'accounts.filter.label'
	| 'accounts.filter.placeholder'
	| 'accounts.filter.filteredStatus'
	| 'accounts.filter.allStatus'
	| 'accounts.filter.noMatchesTitle'
	| 'accounts.filter.noMatchesMessage'
	| 'accounts.column.name'
	| 'accounts.column.type'
	| 'accounts.column.balance'
	| 'accounts.column.currency'
	| 'accounts.emptyTitle'
	| 'accounts.emptyMessage'
	| 'accounts.emptyAction'
	| 'accounts.explorer.reset'
	| 'accounts.explorer.filtersTitle'
	| 'accounts.explorer.formHelp'
	| 'accounts.explorer.mode'
	| 'accounts.explorer.modeTree'
	| 'accounts.explorer.modeFlat'
	| 'accounts.explorer.query'
	| 'accounts.explorer.type'
	| 'accounts.explorer.hidden'
	| 'accounts.explorer.placeholder'
	| 'accounts.explorer.visibilityExclude'
	| 'accounts.explorer.visibilityInclude'
	| 'accounts.explorer.visibilityOnly'
	| 'accounts.explorer.typesLegend'
	| 'accounts.explorer.directBalance'
	| 'accounts.explorer.recursiveBuckets'
	| 'accounts.explorer.noRecursiveBuckets'
	| 'accounts.explorer.hiddenBadge'
	| 'accounts.explorer.placeholderBadge'
	| 'accounts.explorer.contextBadge'
	| 'accounts.explorer.repairedBadge'
	| 'accounts.explorer.readyTitle'
	| 'accounts.explorer.readyMessage'
	| 'accounts.explorer.noMatchesTitle'
	| 'accounts.explorer.noMatchesMessage'
	| 'accounts.explorer.invalidFilterTitle'
	| 'accounts.explorer.invalidFilterMessage'
	| 'accounts.explorer.narrowFiltersTitle'
	| 'accounts.explorer.narrowFiltersMessage'
	| 'accounts.explorer.loadFailedTitle'
	| 'accounts.explorer.loadFailedMessage'
	| 'accounts.explorer.unknownFailureTitle'
	| 'accounts.explorer.unknownFailureMessage'
	| 'accounts.explorer.statusCounts'
	| 'accounts.explorer.warningsTitle'
	| 'accounts.explorer.contextWarning'
	| 'accounts.explorer.hiddenWarning'
	| 'accounts.explorer.placeholderWarning'
	| 'accounts.explorer.repairedWarning'
	| 'accounts.explorer.mixedCommodityWarning'
	| 'accounts.explorer.resultsLabel'
	| 'accounts.detail.loading'
	| 'accounts.detail.kicker'
	| 'accounts.detail.breadcrumbAria'
	| 'accounts.detail.notAvailable'
	| 'accounts.detail.loadFailedTitle'
	| 'accounts.detail.loadFailedMessage'
	| 'accounts.detail.unknownFailureTitle'
	| 'accounts.detail.unknownFailureMessage'
	| 'accounts.detail.invalidFilterTitle'
	| 'accounts.detail.invalidFilterMessage'
	| 'accounts.detail.legacyNotice'
	| 'accounts.detail.overviewOnlyTitle'
	| 'accounts.detail.overviewOnlyMessage'
	| 'accounts.detail.activityLoadedTitle'
	| 'accounts.detail.activityLoadedMessage'
	| 'accounts.detail.activityEmptyTitle'
	| 'accounts.detail.activityEmptyMessage'
	| 'accounts.detail.partialActivityTitle'
	| 'accounts.detail.partialActivityMessage'
	| 'accounts.detail.backToExplorer'
	| 'accounts.detail.subtreeCount'
	| 'accounts.detail.childCount'
	| 'accounts.detail.childrenReturned'
	| 'accounts.detail.childrenTruncated'
	| 'accounts.detail.childrenTitle'
	| 'accounts.detail.childrenHelp'
	| 'accounts.detail.noChildren'
	| 'accounts.detail.activityTitle'
	| 'accounts.detail.activityHelp'
	| 'accounts.detail.resetActivity'
	| 'accounts.detail.activityFormHelp'
	| 'accounts.detail.limit'
	| 'accounts.detail.applyActivity'
	| 'accounts.detail.requestCounters'
	| 'accounts.detail.exactChange'
	| 'accounts.detail.flowNotApplicable'
	| 'accounts.detail.recentReturned'
	| 'accounts.detail.openTransactionExplorer'
	| 'accounts.detail.unavailableNoFxScope'
	| 'accounts.detail.openBaseReport'
	| 'accounts.detail.recentTitle'
	| 'accounts.detail.noRecentTransactions'
	| 'dashboard.loading'
	| 'dashboard.loadFailed'
	| 'dashboard.sectionError.title'
	| 'dashboard.sectionError.redacted'
	| 'dashboard.summary'
	| 'dashboard.conservativeTotals'
	| 'dashboard.reportingBasis'
	| 'dashboard.currencyConversion'
	| 'dashboard.currencyConversionIncluded'
	| 'dashboard.currencyConversionNotIncluded'
	| 'dashboard.netWorth'
	| 'dashboard.assets'
	| 'dashboard.liabilities'
	| 'dashboard.incomeThisMonth'
	| 'dashboard.expensesThisMonth'
	| 'dashboard.viewMonthlyFilter'
	| 'dashboard.drilldownSafety'
	| 'dashboard.recentTransactions'
	| 'dashboard.recentTransactionsHelp'
	| 'dashboard.viewTransactions'
	| 'dashboard.noRecentTransactions'
	| 'dashboard.expensesByAccount'
	| 'dashboard.expensesByAccountHelp'
	| 'dashboard.noExpenses'
	| 'dashboard.cashflow'
	| 'dashboard.cashflowHelp'
	| 'dashboard.noCashflow'
	| 'dashboard.cashflowIn'
	| 'dashboard.cashflowOut'
	| 'dashboard.cashflowNet'
	| 'reports.metaTitle'
	| 'reports.kicker'
	| 'reports.title'
	| 'reports.bookLabel'
	| 'reports.viewTransactionsPeriod'
	| 'reports.period.title'
	| 'reports.period.urlBackedHelp'
	| 'reports.period.presetsAria'
	| 'reports.period.customAria'
	| 'reports.period.dateFrom'
	| 'reports.period.dateTo'
	| 'reports.period.applyCustom'
	| 'reports.comparison.title'
	| 'reports.comparison.urlBackedHelp'
	| 'reports.comparison.modeAria'
	| 'reports.comparison.mode.previousEquivalent'
	| 'reports.comparison.mode.samePeriodLastYear'
	| 'reports.comparison.customAria'
	| 'reports.comparison.dateFrom'
	| 'reports.comparison.dateTo'
	| 'reports.comparison.applyCustom'
	| 'reports.comparison.validation.unsupportedMode'
	| 'reports.comparison.validation.invalidDateRange'
	| 'reports.comparison.validation.invalidRange'
	| 'reports.comparison.validation.inconsistentRange'
	| 'reports.comparison.deltaError'
	| 'reports.comparison.notComparable'
	| 'reports.comparison.rowNotComparable'
	| 'reports.comparison.emptyDelta'
	| 'reports.comparison.zeroHint'
	| 'reports.comparison.technicalLimitation'
	| 'reports.comparison.primarySide'
	| 'reports.comparison.comparisonSide'
	| 'reports.comparison.sourcePeriodsTitle'
	| 'reports.comparison.sourcePeriodsHelp'
	| 'reports.comparison.summaryDeltaTitle'
	| 'reports.comparison.cashflowDeltaTitle'
	| 'reports.comparison.expenseChangesTitle'
	| 'reports.comparison.expenseChangesHelp'
	| 'reports.comparison.unchanged'
	| 'reports.comparison.increase'
	| 'reports.comparison.decrease'
	| 'reports.comparison.absoluteChange'
	| 'reports.comparison.noExpenseChanges'
	| 'reports.preset.thisMonth'
	| 'reports.preset.lastMonth'
	| 'reports.preset.yearToDate'
	| 'reports.loading'
	| 'reports.validation.invalidDateRange'
	| 'reports.validation.unsupportedPreset'
	| 'reports.validation.invalidRange'
	| 'reports.validation.invalidTitle'
	| 'reports.validation.invalidNoRequest'
	| 'reports.error.title'
	| 'reports.error.redactedHelp'
	| 'reports.error.requestFailed'
	| 'reports.error.serviceUnavailable'
	| 'reports.error.forbidden'
	| 'reports.error.notFound'
	| 'reports.error.unknown'
	| 'reports.sectionError.redacted'
	| 'reports.empty.title'
	| 'reports.empty.message'
	| 'reports.empty.aria'
	| 'reports.empty.action'
	| 'reports.limitations.title'
	| 'reports.limitations.reportingBasis'
	| 'reports.limitations.none'
	| 'reports.partial.title'
	| 'reports.partial.help'
	| 'reports.summary.title'
	| 'reports.summary.help'
	| 'reports.summary.openFilter'
	| 'reports.summary.income'
	| 'reports.summary.expenses'
	| 'reports.summary.netPeriodResult'
	| 'reports.summary.netWorth'
	| 'reports.summary.assets'
	| 'reports.summary.liabilities'
	| 'reports.summary.noTotals'
	| 'reports.cashflow.title'
	| 'reports.cashflow.monthlyTitle'
	| 'reports.cashflow.monthlyHelp'
	| 'reports.cashflow.inflow'
	| 'reports.cashflow.outflow'
	| 'reports.cashflow.net'
	| 'reports.cashflow.noTotals'
	| 'reports.cashflow.noMonthly'
	| 'reports.expenses.title'
	| 'reports.expenses.help'
	| 'reports.expenses.allPeriod'
	| 'reports.expenses.noRows'
	| 'reports.localizationNotice'
	| 'home.subtitle'
	| 'transactions.kicker'
	| 'transactions.title'
	| 'transactionDetail.back'
	| 'transactionDetail.kicker'
	| 'transactionDetail.noDescription'
	| 'transactionDetail.helper'
	| 'transactionDetail.date'
	| 'transactionDetail.currency'
	| 'transactionDetail.splits'
	| 'transactionDetail.id'
	| 'transactionDetail.splitSingular'
	| 'transactionDetail.splitPlural'
	| 'transactionDetail.writeAlphaHistoryTitle'
	| 'transactionDetail.writeAlphaHistoryHelper'
	| 'transactionDetail.nonOwnedTitle'
	| 'transactionDetail.nonOwnedHelper'
	| 'transactionDetail.deleteTitle'
	| 'transactionDetail.deleteHelper'
	| 'transactionDetail.deleteAcknowledgement'
	| 'transactionDetail.deleteButton'
	| 'transactionDetail.deleteConfirm'
	| 'transactionSplits.title'
	| 'transactionSplits.helper'
	| 'transactionSplits.empty'
	| 'transactionSplits.splitAccount'
	| 'transactionSplits.memo'
	| 'transactionSplits.noMemo'
	| 'transactionSplits.reconciliation'
	| 'transactionSplits.accountId'
	| 'transactionSplits.caption'
	| 'transactionSplits.stateNotProvided'
	| 'transactionSplits.stateUnknown'
	| 'books.kicker'
	| 'books.title'
	| 'books.subtitle'
	| 'books.activeDefault'
	| 'books.configuredTitle'
	| 'books.hiddenPolicy'
	| 'books.noMutationBadge'
	| 'books.currentBook'
	| 'books.defaultBook'
	| 'books.readOnlyBadge'
	| 'books.accessibleBadge'
	| 'books.baseCurrency'
	| 'books.storageType'
	| 'books.readonlyStatus'
	| 'books.safetyNote'
	| 'books.noBooks'
	| 'books.emptyTitle'
	| 'books.emptyMessage'
	| 'books.notConfigured'
	| 'books.unknown'
	| 'books.accessRole'
	| 'books.status'
	| 'books.storageDiagnostics'
	| 'books.safeNextActions'
	| 'books.privatePathRedacted'
	| 'books.openSafeViews'
	| 'books.unavailableViews'
	| 'books.viewAccounts'
	| 'books.browseTransactions'
	| 'books.viewScheduled'
	| 'books.dashboardSummary'
	| 'books.settingsLink'
	| 'books.lastSuccessfulAt'
	| 'books.capabilitiesTitle'
	| 'books.capabilityReadOnly'
	| 'books.capabilityAccounts'
	| 'books.capabilityTransactions'
	| 'books.capabilityReports'
	| 'books.capabilityUpload'
	| 'books.capabilityEdit'
	| 'books.capabilityDelete'
	| 'books.yes'
	| 'books.no'
	| 'books.noManagementActions'
	| 'books.registryManagement'
	| 'books.registryManagementSafety'
	| 'books.setDefaultAction'
	| 'books.removeRegistryAction'
	| 'books.operatorGuidanceTitle'
	| 'books.metadataSource'
	| 'books.dataAccess'
	| 'books.readOnlyDefault'
	| 'books.unsupportedActions'
	| 'books.noUnsupportedActions'
	| 'books.currentDefaultExplanation'
	| 'books.safeOperatorGuidance'
	| 'books.contextRecoveryTitle'
	| 'books.contextRecoveryStale'
	| 'books.contextRecoveryUnavailable'
	| 'books.contextRecoveryNoBooks'
	| 'books.auditEvidence'
	| 'books.registerTitle'
	| 'books.registerIntro'
	| 'books.adminOnlyBadge'
	| 'books.registerName'
	| 'books.registerCurrency'
	| 'books.registerPath'
	| 'books.registerMakeDefault'
	| 'books.registerSafety'
	| 'books.registerSubmit'
	| 'books.loading'
	| 'books.addBookAction'
	| 'books.firstRunAdminTitle'
	| 'books.firstRunAdminMessage'
	| 'books.firstRunUserTitle'
	| 'books.firstRunUserMessage'
	| 'books.enabledBook'
	| 'books.disabledBook'
	| 'books.notChecked'
	| 'books.statusUnknown'
	| 'books.status.ready'
	| 'books.status.available'
	| 'books.status.ok'
	| 'books.status.warning'
	| 'books.status.rejected'
	| 'books.status.unavailable'
	| 'books.status.unknown'
	| 'books.status.missing_file'
	| 'books.status.not_configured'
	| 'books.status.remote_or_unchecked'
	| 'books.status.invalid_gnucash_schema'
	| 'books.status.action_required'
	| 'books.status.not_checked'
	| 'books.status.disabled'
	| 'books.status.failed'
	| 'books.status.empty'
	| 'books.status.blocked'
	| 'books.status.unsupported'
	| 'books.problem.admin_required'
	| 'books.problem.preflight_required'
	| 'books.problem.preflight_rejected'
	| 'books.problem.preflight_token_invalid'
	| 'books.problem.missing_preflight_token'
	| 'books.problem.invalid_preflight_token'
	| 'books.problem.preflight_request_mismatch'
	| 'books.problem.preflight_source_mismatch'
	| 'books.problem.invalid_path'
	| 'books.problem.unsupported_source'
	| 'books.problem.outside_allowed_roots'
	| 'books.problem.symlink_forbidden'
	| 'books.problem.missing_file'
	| 'books.problem.not_regular_file'
	| 'books.problem.permission_denied'
	| 'books.problem.unsupported_format'
	| 'books.problem.invalid_gnucash_schema'
	| 'books.problem.source_changed'
	| 'books.problem.open_failed'
	| 'books.problem.duplicate_canonical_path'
	| 'books.problem.book_not_enabled'
	| 'books.problem.book_not_healthy'
	| 'books.problem.book_health_not_checked'
	| 'books.problem.api_unavailable'
	| 'books.problem.book_registry_failed'
	| 'books.problem.unknown_book_problem'
	| 'books.manageSuccessSetDefault'
	| 'books.manageSuccessRemoveRegistry'
	| 'books.manageSuccessRecheck'
	| 'books.manageSuccessRename'
	| 'books.manageSuccessDisable'
	| 'books.manageSuccessEnable'
	| 'books.removeMetadataConfirm'
	| 'books.reportsLink'
	| 'books.statusDetailsTitle'
	| 'books.statusDetailsHelp'
	| 'books.renameFuture'
	| 'books.disableFuture'
	| 'books.recheckFuture'
	| 'books.backToBooks'
	| 'books.newTitle'
	| 'books.newSubtitle'
	| 'books.adminRequiredTitle'
	| 'books.newStep1Title'
	| 'books.newStep2Title'
	| 'books.newStep3Title'
	| 'books.newStep4Title'
	| 'books.supportedFormat'
	| 'books.unsupportedFormatWarning'
	| 'books.preflightSubmit'
	| 'books.preflightReady'
	| 'books.preflightRejected'
	| 'books.preflightFormat'
	| 'books.preflightCheckedAt'
	| 'books.preflightTokenOpaque'
	| 'books.confirmRegisterHelp'
	| 'books.confirmRegisterSubmit'
	| 'books.registrationSuccessTitle'
	| 'books.registrationSuccessMessage'
	| 'books.settingsTitle'
	| 'books.settingsSubtitle'
	| 'books.settingsSummaryTitle'
	| 'books.healthTitle'
	| 'books.healthHelp'
	| 'books.healthSafeCode'
	| 'books.healthSourceStatus'
	| 'books.healthOpenStatus'
	| 'books.healthAccountsStatus'
	| 'books.healthTransactionsStatus'
	| 'books.healthReportsStatus'
	| 'books.adminLifecycleTitle'
	| 'books.adminLifecycleSafety'
	| 'books.renameTitle'
	| 'books.renameHelp'
	| 'books.renameAction'
	| 'books.recheckTitle'
	| 'books.recheckHelp'
	| 'books.recheckAction'
	| 'books.disableTitle'
	| 'books.disableHelp'
	| 'books.disableMetadataConfirm'
	| 'books.disableAction'
	| 'books.enableTitle'
	| 'books.enablePreflightHelp'
	| 'books.enablePath'
	| 'books.enablePreflightSubmit'
	| 'books.enablePreviewTitle'
	| 'books.enableConfirmHelp'
	| 'books.enableConfirmSubmit'
	| 'books.unregisterTitle'
	| 'books.unregisterHelp'
	| 'books.section.source'
	| 'books.section.open'
	| 'books.section.accounts'
	| 'books.section.transactions'
	| 'books.section.reports'
	| 'books.statusCode.source_ready'
	| 'books.statusCode.open_ready'
	| 'books.statusCode.accounts_ready'
	| 'books.statusCode.transactions_ready'
	| 'books.statusCode.reports_ready'
	| 'books.statusCode.registration_available'
	| 'books.statusCode.already_registered'
	| 'books.registrationStatus.available'
	| 'books.registrationStatus.alreadyRegistered'
	| 'books.registrationStatus.unavailable'
	| 'books.sectionStatus.source.ready'
	| 'books.sectionStatus.source.rejected'
	| 'books.sectionStatus.source.unavailable'
	| 'books.sectionStatus.open.ready'
	| 'books.sectionStatus.open.rejected'
	| 'books.sectionStatus.open.unavailable'
	| 'books.sectionStatus.accounts.ready'
	| 'books.sectionStatus.accounts.rejected'
	| 'books.sectionStatus.accounts.unavailable'
	| 'books.sectionStatus.transactions.ready'
	| 'books.sectionStatus.transactions.rejected'
	| 'books.sectionStatus.transactions.unavailable'
	| 'books.sectionStatus.reports.ready'
	| 'books.sectionStatus.reports.rejected'
	| 'books.sectionStatus.reports.unavailable'
	| 'audit.title'
	| 'audit.bannerTitle'
	| 'audit.bannerMessage'
	| 'audit.redactionMessage'
	| 'audit.activeBook'
	| 'audit.noAccessibleBook'
	| 'audit.reviewBooks'
	| 'audit.filtersLabel'
	| 'audit.allActions'
	| 'audit.create'
	| 'audit.patch'
	| 'audit.delete'
	| 'audit.allResults'
	| 'audit.success'
	| 'audit.failed'
	| 'audit.started'
	| 'audit.unknown'
	| 'audit.action'
	| 'audit.result'
	| 'audit.sinceIso'
	| 'audit.untilIso'
	| 'audit.applyFilters'
	| 'audit.clearFilters'
	| 'audit.limit'
	| 'audit.countsLabel'
	| 'audit.filteredRows'
	| 'audit.returnedCount'
	| 'audit.actions'
	| 'audit.results'
	| 'audit.window'
	| 'audit.ownership'
	| 'audit.ownedCreated'
	| 'audit.nonOwnedRejected'
	| 'audit.lastMutation'
	| 'audit.requestedWindow'
	| 'audit.returnedWindow'
	| 'audit.noStart'
	| 'audit.noEnd'
	| 'audit.none'
	| 'audit.emptyTitle'
	| 'audit.emptyMessage'
	| 'audit.browseTransactions'
	| 'audit.showingEntries'
	| 'audit.pageStatus'
	| 'audit.paginationLabel'
	| 'audit.paginationSummary'
	| 'audit.previousPage'
	| 'audit.nextPage'
	| 'audit.timestamp'
	| 'audit.txnPrefix'
	| 'audit.backupSafeError'
	| 'audit.backupPresent'
	| 'audit.backupMissing'
	| 'audit.backupRef'
	| 'audit.limitations'
	| 'writeMode.title'
	| 'writeMode.message'
	| 'writeMode.desktop'
	| 'writeMode.disposableOnly'
	| 'writeMode.createOnlyDogfood'
	| 'writeMode.evidence'
	| 'writeMode.staleLock'
	| 'writeMode.neverRealBook'
	| 'writeMode.finalConfirm'
	| 'writeMode.acknowledgement'
	| 'writeMode.kicker'
	| 'writeMode.newTransactionTitle'
	| 'writeMode.newTransactionHelp'
	| 'transactions.filters.title'
	| 'transactions.filters.subtitle'
	| 'transactions.filters.filteredView'
	| 'transactions.filters.datePresets'
	| 'transactions.filters.datePresetAria'
	| 'transactions.filters.datePresetHelp'
	| 'transactions.filters.activeSummaryTitle'
	| 'transactions.filters.search'
	| 'transactions.filters.searchPlaceholder'
	| 'transactions.filters.account'
	| 'transactions.filters.accountScope'
	| 'transactions.filters.accountId'
	| 'transactions.filters.lockedAccountHelp'
	| 'transactions.filters.allAccounts'
	| 'transactions.filters.customDateRange'
	| 'transactions.filters.from'
	| 'transactions.filters.to'
	| 'transactions.filters.startDateError'
	| 'transactions.filters.state'
	| 'transactions.filters.anyState'
	| 'transactions.filters.stateUnreconciled'
	| 'transactions.filters.stateCleared'
	| 'transactions.filters.stateReconciled'
	| 'transactions.filters.stateVoided'
	| 'transactions.filters.stateHelp'
	| 'transactions.filters.minAmount'
	| 'transactions.filters.maxAmount'
	| 'transactions.filters.amountError'
	| 'transactions.filters.submit'
	| 'transactions.filters.clear'
	| 'transactions.filters.summary.search'
	| 'transactions.filters.summary.account'
	| 'transactions.filters.summary.dates'
	| 'transactions.filters.summary.from'
	| 'transactions.filters.summary.to'
	| 'transactions.filters.summary.amount'
	| 'transactions.filters.summary.minAmount'
	| 'transactions.filters.summary.maxAmount'
	| 'transactions.filters.summary.state'
	| 'transactions.listStatus.title'
	| 'transactions.listStatus.order'
	| 'transactions.listStatus.pageRange'
	| 'transactions.listStatus.emptyPage'
	| 'transactions.listStatus.filtersApplied'
	| 'transactions.listStatus.noFilters'
	| 'transactions.listStatus.exportParity'
	| 'transactions.explorer.formHelp'
	| 'transactions.explorer.datePresetHelp'
	| 'transactions.explorer.dateTextLegend'
	| 'transactions.explorer.scopeLegend'
	| 'transactions.explorer.scopeHelp'
	| 'transactions.explorer.accountIds'
	| 'transactions.explorer.accountIdsHelp'
	| 'transactions.explorer.accountOptionsLimited'
	| 'transactions.explorer.accountsDisabledByType'
	| 'transactions.explorer.type'
	| 'transactions.explorer.typeAny'
	| 'transactions.explorer.typeIncome'
	| 'transactions.explorer.typeExpense'
	| 'transactions.explorer.direction'
	| 'transactions.explorer.directionAny'
	| 'transactions.explorer.directionIncrease'
	| 'transactions.explorer.directionDecrease'
	| 'transactions.explorer.directionHelp'
	| 'transactions.explorer.amountPagingLegend'
	| 'transactions.explorer.amountPagingHelp'
	| 'transactions.explorer.sort'
	| 'transactions.explorer.sortDateDesc'
	| 'transactions.explorer.sortDateAsc'
	| 'transactions.explorer.pageSize'
	| 'transactions.explorer.reset'
	| 'transactions.explorer.removeFilter'
	| 'transactions.explorer.cursorChip'
	| 'transactions.explorer.dateRangeRequiredTitle'
	| 'transactions.explorer.dateRangeRequiredMessage'
	| 'transactions.explorer.readyTitle'
	| 'transactions.explorer.readyMessage'
	| 'transactions.explorer.trueEmptyTitle'
	| 'transactions.explorer.trueEmptyMessage'
	| 'transactions.explorer.scanWindowEmptyTitle'
	| 'transactions.explorer.scanWindowEmptyMessage'
	| 'transactions.explorer.scanLimitedTitle'
	| 'transactions.explorer.scanLimitedMessage'
	| 'transactions.explorer.endTitle'
	| 'transactions.explorer.endMessage'
	| 'transactions.explorer.invalidFilterTitle'
	| 'transactions.explorer.invalidFilterMessage'
	| 'transactions.explorer.staleCursorTitle'
	| 'transactions.explorer.staleCursorMessage'
	| 'transactions.explorer.loadFailedTitle'
	| 'transactions.explorer.loadFailedMessage'
	| 'transactions.explorer.unknownFailureTitle'
	| 'transactions.explorer.unknownFailureMessage'
	| 'transactions.explorer.legacyCompatibility'
	| 'transactions.explorer.legacyOffsetConflict'
	| 'transactions.explorer.returnedStatus'
	| 'transactions.explorer.filtersApplied'
	| 'transactions.explorer.noFilters'
	| 'transactions.explorer.order'
	| 'transactions.explorer.noTotal'
	| 'transactions.explorer.limitationsTitle'
	| 'transactions.explorer.resetPagination'
	| 'transactions.explorer.paginationLabel'
	| 'transactions.explorer.cursorPagination'
	| 'transactions.explorer.previous'
	| 'transactions.explorer.next'
	| 'transactions.explorer.continue'
	| 'transactions.writeAlphaHistoryBadge'
	| 'transactions.writeAlphaHistoryTitle'
	| 'transactions.listStatus.writeAlphaHint'
	| 'transactions.listStatus.writeAlphaFollowupTitle'
	| 'transactions.listStatus.writeAlphaFollowupHelp'
	| 'transactions.listStatus.writeAlphaAuditLink'
	| 'transactions.export.button'
	| 'transactions.export.buttonWithFilters'
	| 'transactions.export.statusFiltered'
	| 'transactions.export.statusUnfiltered'
	| 'transactions.export.emptyStatus'
	| 'transactions.export.countStatus'
	| 'transactions.export.truncatedStatus'
	| 'transactions.export.accountButton'
	| 'transactions.export.accountButtonWithFilters'
	| 'transactions.export.accountStatus'
	| 'transactions.export.explorerDisabled'
	| 'transactions.export.explorerHonesty'
	| 'scheduled.title'
	| 'scheduled.kicker'
	| 'scheduled.subtitle'
	| 'scheduled.activeBook'
	| 'scheduled.recurringMetadata'
	| 'scheduled.metadataHelp'
	| 'scheduled.readOnlyBadge'
	| 'scheduled.statusFilter'
	| 'scheduled.templateFilter'
	| 'scheduled.sortDisplay'
	| 'scheduled.all'
	| 'scheduled.enabled'
	| 'scheduled.disabled'
	| 'scheduled.templatePresent'
	| 'scheduled.noTemplateReference'
	| 'scheduled.startDate'
	| 'scheduled.endDate'
	| 'scheduled.lastOccurred'
	| 'scheduled.name'
	| 'scheduled.enabledFirst'
	| 'scheduled.shownStatus'
	| 'scheduled.clearFilters'
	| 'scheduled.unnamed'
	| 'scheduled.templateAccount'
	| 'scheduled.templateReferenceStatus'
	| 'scheduled.templatePresentRedacted'
	| 'scheduled.templateNotPresentRedacted'
	| 'scheduled.occurrences'
	| 'scheduled.occurrencesValue'
	| 'scheduled.autoCreateNotify'
	| 'scheduled.advanceDays'
	| 'scheduled.advanceDaysValue'
	| 'scheduled.recurrenceMetadata'
	| 'scheduled.noRecurrenceMetadata'
	| 'scheduled.noMatchesTitle'
	| 'scheduled.noMatchesMessage'
	| 'scheduled.noMatchesAria'
	| 'scheduled.emptyTitle'
	| 'scheduled.emptyMessage'
	| 'scheduled.emptyAria'
	| 'scheduled.browseTransactions'
	| 'scheduled.reviewBooks'
	| 'scheduled.notConfigured'
	| 'scheduled.yes'
	| 'scheduled.no'
	| 'scheduled.recurrenceEvery'
	| 'scheduled.recurrenceFrom'
	| 'scheduled.recurrenceWeekend'
	| 'scheduled.recurrenceUnavailable';

export const messages: Record<Locale, Record<MessageKey, string>> = {
	en: {
		'locale.english': 'English',
		'locale.russian': 'Russian',
		'locale.switcherLabel': 'Language',
		'login.title': 'Sign in',
		'login.subtitle': 'Use the configured admin account to continue.',
		'login.username': 'Username',
		'login.password': 'Password',
		'login.submit': 'Sign in',
		'login.error.missingCredentials': 'Enter username and password.',
		'login.error.serviceUnavailable': 'Authentication service is unavailable.',
		'login.error.invalidCredentials': 'Invalid username or password.',
		'login.error.operatorConfiguration':
			'Login is not fully configured. Check JWT_SECRET and APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD in your local .env/deployment environment, restart the service, and keep GnuCash data read-only.',
		'login.notice.sessionChanged': 'Session changed. Sign in again to continue.',
		'login.firstRun.title': 'First-run read-only deployment checks',
		'login.firstRun.summary': 'Safe redacted /health diagnostics help distinguish placeholder JWT secret, admin bootstrap, mounted book, CORS, and write-disabled status before login.',
		'login.firstRun.safeDiagnostics': 'No secrets, full paths, tokens, app DB contents, or book data are shown here.',
		'login.firstRun.jwtSecret': 'JWT secret',
		'login.firstRun.adminBootstrap': 'Admin bootstrap',
		'login.firstRun.defaultBook': 'Default book',
		'login.firstRun.cors': 'CORS origins',
		'login.firstRun.writeMode': 'Write mode',
		'login.firstRun.status.ok': 'OK',
		'login.firstRun.status.warning': 'Warning',
		'login.firstRun.status.actionRequired': 'Action required',
		'nav.dashboard': 'Dashboard',
		'nav.accounts': 'Accounts',
		'nav.transactions': 'Transactions',
		'nav.scheduled': 'Scheduled',
		'nav.reports': 'Reports',
		'nav.books': 'Books',
		'nav.adminUsers': 'Admin users',
		'nav.logout': 'Logout',
		'adminUsers.kicker': 'Admin foundation',
		'adminUsers.title': 'User and book access administration',
		'adminUsers.subtitle': 'Server-rendered local-user management for self-hosted installs. The backend remains authoritative and GnuCash data stays read-only.',
		'adminUsers.backToUsers': 'Back to admin users',
		'adminUsers.createUser': 'Create user',
		'adminUsers.listTitle': 'Local users',
		'adminUsers.listHelp': 'Bounded list from /admin/users. Normal users do not receive user or access payloads from SSR.',
		'adminUsers.loading': 'Loading admin user data…',
		'adminUsers.emptyTitle': 'No local users returned',
		'adminUsers.emptyMessage': 'The bounded admin API returned an empty page. Create a user or adjust the enabled/disabled filter.',
		'adminUsers.adminRequiredTitle': 'Administrator account required',
		'adminUsers.adminRequiredMessage': 'This page intentionally withholds admin user and access payloads unless /auth/me reports is_admin=true. Backend authorization is still authoritative.',
		'adminUsers.safeBoundaryBadge': 'App metadata only — no GnuCash writes',
		'adminUsers.username': 'Username',
		'adminUsers.displayName': 'Display name',
		'adminUsers.status': 'Status',
		'adminUsers.enabled': 'Enabled',
		'adminUsers.disabled': 'Disabled',
		'adminUsers.adminBadge': 'Admin',
		'adminUsers.userBadge': 'User',
		'adminUsers.assignmentCount': 'Book assignments',
		'adminUsers.createdAt': 'Created',
		'adminUsers.updatedAt': 'Updated',
		'adminUsers.actions': 'Actions',
		'adminUsers.viewDetails': 'Manage user',
		'adminUsers.previousPage': 'Previous page',
		'adminUsers.nextPage': 'Next page',
		'adminUsers.stateFilter': 'Enabled state',
		'adminUsers.stateAll': 'All users',
		'adminUsers.stateEnabled': 'Enabled only',
		'adminUsers.stateDisabled': 'Disabled only',
		'adminUsers.applyFilter': 'Apply filter',
		'adminUsers.newTitle': 'Create local user',
		'adminUsers.newSubtitle': 'Create one local account. Username and admin choice are immutable in this milestone; book access starts empty unless an admin grants it later.',
		'adminUsers.createTitle': 'User credentials',
		'adminUsers.usernameHelp': 'Lowercase ASCII username, 3–64 characters, starting with a letter. It cannot be edited later.',
		'adminUsers.displayNameHelp': '1–100 visible characters. This is the only editable profile label in #57.',
		'adminUsers.initialPassword': 'Initial password',
		'adminUsers.passwordHelp': 'Password is sent only to the server action and never repopulated after errors.',
		'adminUsers.isAdminChoice': 'Create as global admin',
		'adminUsers.isAdminHelp': 'Admins can manage local users and book assignments. Book owner/editor/viewer roles do not grant global admin.',
		'adminUsers.zeroAccessDefault': 'New users start with zero book access by default; the default book never grants access by itself.',
		'adminUsers.createSubmit': 'Create user',
		'adminUsers.detailTitle': 'User detail',
		'adminUsers.detailSubtitle': 'Manage display name, enabled state, password reset, and explicit active-book assignments.',
		'adminUsers.summaryTitle': 'Safe user summary',
		'adminUsers.updateDisplayNameTitle': 'Display name update',
		'adminUsers.updateDisplayNameHelp': 'Only display name can be edited here. Username and admin role are intentionally not editable.',
		'adminUsers.updateDisplayNameSubmit': 'Update display name',
		'adminUsers.enableTitle': 'Enable account',
		'adminUsers.enableHelp': 'Enabling lets the user sign in again with current credentials or after a reset.',
		'adminUsers.enableSubmit': 'Enable user',
		'adminUsers.disableTitle': 'Disable account',
		'adminUsers.disableHelp': 'Disable blocks the next authenticated request after backend auth-version enforcement; self-disable and last-admin checks remain backend enforced.',
		'adminUsers.confirmDisableCopy': 'I understand this disables the local account only; it does not delete users, books, audit rows, or GnuCash data.',
		'adminUsers.disableSubmit': 'Disable user',
		'adminUsers.resetPasswordTitle': 'Password reset',
		'adminUsers.resetPasswordHelp': 'Reset replaces only the server-side secret and invalidates existing sessions on the next request. The new value is never shown again.',
		'adminUsers.newPassword': 'New password',
		'adminUsers.confirmResetCopy': 'I understand this reset invalidates existing sessions and the password field will not be repopulated.',
		'adminUsers.resetPasswordSubmit': 'Reset password',
		'adminUsers.accessTitle': 'Book access matrix',
		'adminUsers.accessHelp': 'Grant only active, non-archived books. New grants default to viewer; owner/editor labels do not enable GnuCash writes or global admin.',
		'adminUsers.book': 'Book',
		'adminUsers.role': 'Role',
		'adminUsers.grantSubmit': 'Grant or update access',
		'adminUsers.revokeSubmit': 'Revoke access',
		'adminUsers.confirmRevokeCopy': 'I understand revoke removes this app access on the next request and does not modify the GnuCash book.',
		'adminUsers.noBooksTitle': 'No assignable active books',
		'adminUsers.noBooksMessage': 'No active non-archived book options were returned. Users can remain with zero access safely.',
		'adminUsers.bookOptionsUnavailableTitle': 'Book options are temporarily unavailable',
		'adminUsers.bookOptionsUnavailableMessage': 'Existing assignments remain visible, but new grants are disabled until the fixed options list loads successfully.',
		'adminUsers.noAssignments': 'No book assignments for this user.',
		'adminUsers.limitedActionsNote': 'This milestone exposes only display-name update, enable/disable, password reset, and explicit book grants.',
		'adminUsers.passwordNotRepopulated': 'Password fields use autocomplete=new-password and never reuse submitted values.',
		'adminUsers.role.viewer': 'Viewer',
		'adminUsers.role.editor': 'Editor',
		'adminUsers.role.owner': 'Owner',
		'adminUsers.roleCopy.viewer': 'Viewer: read-only views only.',
		'adminUsers.roleCopy.editor': 'Editor: preserves existing edit-authorization label, but no GnuCash writes are enabled by this UI.',
		'adminUsers.roleCopy.owner': 'Owner: same book-level effective access label as editor here; it is not global admin.',
		'adminUsers.roleBoundary': 'Roles affect app metadata access only. GNUCASH_WRITES_ENABLED=false and backend write gates remain independent.',
		'adminUsers.problem.username_invalid': 'Username does not match the allowed local-account policy.',
		'adminUsers.problem.username_taken': 'A user with that normalized username already exists.',
		'adminUsers.problem.display_name_invalid': 'Display name is missing or outside the allowed length/character policy.',
		'adminUsers.problem.password_policy': 'Password does not meet the local policy.',
		'adminUsers.problem.user_not_found': 'The requested user was not found.',
		'adminUsers.problem.user_disabled': 'This user is disabled or the session changed. Sign in again if needed.',
		'adminUsers.problem.session_changed': 'Session changed. Sign in again to continue.',
		'adminUsers.problem.self_disable_forbidden': 'Self-disable is not allowed from the web UI.',
		'adminUsers.problem.last_enabled_admin': 'At least one enabled admin must remain.',
		'adminUsers.problem.book_not_assignable': 'That book is not active and assignable.',
		'adminUsers.problem.admin_required': 'Administrator privileges are required.',
		'adminUsers.problem.api_unavailable': 'Admin API is unavailable. No raw backend details were shown.',
		'adminUsers.problem.unknown_admin_problem': 'The admin action failed safely. Unknown backend details were redacted.',
		'adminUsers.success.user_created': 'User created with zero book access by default.',
		'adminUsers.success.display_name_changed': 'Display name updated.',
		'adminUsers.success.user_enabled': 'User enabled.',
		'adminUsers.success.user_disabled': 'User disabled.',
		'adminUsers.success.password_reset': 'Password reset; existing sessions are invalidated on the next request.',
		'adminUsers.success.book_access_granted': 'Book access granted or updated.',
		'adminUsers.success.book_access_revoked': 'Book access revoked.',
		'safety.statusLabel': 'Read-only safety status',
		'safety.badge': 'Read-only by default',
		'safety.message':
			'Pre-alpha read-only MVP by default. GNUCASH_WRITES_ENABLED=false is the safe default; GnuCash Desktop remains the authoritative editor.',
		'safety.releaseCritical':
			'Not production-ready or security-audited. Experimental write-alpha flows are hidden by default and, when explicitly enabled, are only for outside-git copied/restorable test books with originals untouched.',
		'safety.currentBook': 'Current book',
		'safety.noActiveBook': 'No active book selected',
		'safety.reviewBooks': 'Review books',
		'error.badgeWithCode': 'Error {statusCode}',
		'error.badgeNetwork': 'API/network error',
		'error.forbiddenTitle': 'Access denied',
		'error.forbiddenMessage': 'Your account cannot access this read-only view or book. Check the selected book or sign in with an account that has access.',
		'error.notFoundTitle': 'Page or book not found',
		'error.notFoundMessage': 'The requested page, book, account, or transaction was not found. It may be unavailable, archived, or hidden by access rules.',
		'error.serviceTitle': 'Service temporarily unavailable',
		'error.serviceMessage':
			'The API or network request failed while loading this read-only view. Verify the service is running, check /health for redacted first-run diagnostics, then review local .env and book volume settings before trying again.',
		'error.genericTitle': 'Something went wrong',
		'error.genericMessage': 'An unexpected API or network error occurred. Please try again or return to a safe read-only page.',
		'error.retry': 'Retry',
		'error.retryPage': 'Retry this page',
		'error.backDashboard': 'Back to dashboard',
		'error.reviewBooks': 'Review books and storage diagnostics',
		'dashboard.title': 'Dashboard',
		'accounts.kicker': 'Accounts',
		'accounts.title': 'Account tree',
		'accounts.bookLabel': 'Book',
		'accounts.loading': 'Loading account tree for the selected read-only book…',
		'accounts.filter.label': 'Filter accounts',
		'accounts.filter.placeholder': 'Search by account name, full path, type, or currency',
		'accounts.filter.filteredStatus': 'Showing {filtered} of {total} accounts. Matching descendants stay grouped with their parent path.',
		'accounts.filter.allStatus': 'Showing all {total} accounts. Use the filter to narrow large read-only account trees without changing the book.',
		'accounts.filter.noMatchesTitle': 'No accounts match this filter.',
		'accounts.filter.noMatchesMessage': 'Clear the account filter to return to the full read-only account tree.',
		'accounts.column.name': 'Name',
		'accounts.column.type': 'Type',
		'accounts.column.balance': 'Balance',
		'accounts.column.currency': 'Currency',
		'accounts.emptyTitle': 'No accounts found',
		'accounts.emptyMessage': 'The selected read-only book did not return any accounts. Verify the active test-copy book and accessible book metadata before relying on this view.',
		'accounts.emptyAction': 'Review available books',
		'accounts.explorer.reset': 'Reset account explorer',
		'accounts.explorer.filtersTitle': 'Account explorer filters',
		'accounts.explorer.formHelp':
			'URL is the source of truth. The form submits a read-only GET request to /accounts; the server validates filters before calling the bounded account explorer API.',
		'accounts.explorer.mode': 'Display mode',
		'accounts.explorer.modeTree': 'Tree with ancestor context',
		'accounts.explorer.modeFlat': 'Flat matching rows',
		'accounts.explorer.query': 'Search',
		'accounts.explorer.type': 'Account type',
		'accounts.explorer.hidden': 'Hidden accounts',
		'accounts.explorer.placeholder': 'Placeholder accounts',
		'accounts.explorer.visibilityExclude': 'Exclude',
		'accounts.explorer.visibilityInclude': 'Include',
		'accounts.explorer.visibilityOnly': 'Only',
		'accounts.explorer.typesLegend': 'Type filters',
		'accounts.explorer.directBalance': 'Direct native balance',
		'accounts.explorer.recursiveBuckets': 'Recursive native-commodity buckets',
		'accounts.explorer.noRecursiveBuckets': 'No native balance buckets returned.',
		'accounts.explorer.hiddenBadge': 'Hidden',
		'accounts.explorer.placeholderBadge': 'Placeholder',
		'accounts.explorer.contextBadge': 'Ancestor context',
		'accounts.explorer.repairedBadge': 'Repaired hierarchy',
		'accounts.explorer.readyTitle': 'Account explorer loaded',
		'accounts.explorer.readyMessage': 'The bounded account explorer returned server-filtered account rows for this URL.',
		'accounts.explorer.noMatchesTitle': 'No accounts match these filters',
		'accounts.explorer.noMatchesMessage': 'The server-filtered account explorer returned no rows. Clear filters or broaden search/type/visibility controls.',
		'accounts.explorer.invalidFilterTitle': 'Invalid account explorer filters',
		'accounts.explorer.invalidFilterMessage': 'The account explorer URL was rejected before any account explorer API call was made. Fix the URL or reset filters.',
		'accounts.explorer.narrowFiltersTitle': 'Narrow account filters',
		'accounts.explorer.narrowFiltersMessage': 'The bounded account explorer refused this result as too large or complex. Narrow query/type/visibility filters and retry.',
		'accounts.explorer.loadFailedTitle': 'Account explorer failed',
		'accounts.explorer.loadFailedMessage': 'The read-only account explorer request failed safely. Backend details, paths, and private sentinels were redacted.',
		'accounts.explorer.unknownFailureTitle': 'Account explorer unavailable',
		'accounts.explorer.unknownFailureMessage': 'The API returned an unsupported account explorer failure shape. Unknown backend details were redacted.',
		'accounts.explorer.statusCounts': 'Returned {returned} account row(s) from {candidates} bounded candidates.',
		'accounts.explorer.warningsTitle': 'Account explorer warnings',
		'accounts.explorer.contextWarning': 'Some rows are ancestors included only to preserve search/filter context.',
		'accounts.explorer.hiddenWarning': 'Hidden accounts are visible because the current URL explicitly includes or selects them.',
		'accounts.explorer.placeholderWarning': 'Placeholder accounts are shown as metadata rows, not transaction-bearing totals.',
		'accounts.explorer.repairedWarning': 'The hierarchy contained orphan or cycle repairs; source parent IDs are preserved where reported.',
		'accounts.explorer.mixedCommodityWarning': 'Recursive balances are separate native-commodity buckets. No FX conversion or cross-commodity total is implied.',
		'accounts.explorer.resultsLabel': 'Server-filtered account explorer results',
		'accounts.detail.loading': 'Loading account overview for the selected read-only book…',
		'accounts.detail.kicker': 'Account detail',
		'accounts.detail.breadcrumbAria': 'Account breadcrumb',
		'accounts.detail.notAvailable': 'Not available',
		'accounts.detail.loadFailedTitle': 'Account detail failed',
		'accounts.detail.loadFailedMessage': 'The read-only account overview or activity request failed safely. Backend details, paths, and private sentinels were redacted.',
		'accounts.detail.unknownFailureTitle': 'Account detail unavailable',
		'accounts.detail.unknownFailureMessage': 'The API returned an unsupported account detail failure shape. Unknown backend details were redacted.',
		'accounts.detail.invalidFilterTitle': 'Invalid account detail URL',
		'accounts.detail.invalidFilterMessage': 'Account id, date_from/date_to, limit, or return_to validation failed before any activity API call was made.',
		'accounts.detail.legacyNotice': 'Legacy account-detail transaction query keys were ignored. This migrated page uses only paired date_from/date_to, limit, and safe account explorer return_to; it never calls the old unbounded account-transactions API.',
		'accounts.detail.overviewOnlyTitle': 'Overview only',
		'accounts.detail.overviewOnlyMessage': 'No date range is selected, so only the bounded account overview endpoint was called and no activity request was made.',
		'accounts.detail.activityLoadedTitle': 'Account activity loaded',
		'accounts.detail.activityLoadedMessage': 'The bounded direct-account activity endpoint returned exact change and recent direct rows for this date range.',
		'accounts.detail.activityEmptyTitle': 'No direct activity in this date range',
		'accounts.detail.activityEmptyMessage': 'The bounded direct-account activity endpoint returned empty change/recent sections for the selected account and dates.',
		'accounts.detail.partialActivityTitle': 'Partial account activity',
		'accounts.detail.partialActivityMessage': 'One activity section failed safely; unaffected sections remain visible and backend details were redacted.',
		'accounts.detail.backToExplorer': 'Back to account explorer',
		'accounts.detail.subtreeCount': 'Subtree accounts',
		'accounts.detail.childCount': 'Immediate children',
		'accounts.detail.childrenReturned': 'Children returned',
		'accounts.detail.childrenTruncated': 'Only the bounded first child rows are shown; child_count reports the full bounded graph count.',
		'accounts.detail.childrenTitle': 'Children',
		'accounts.detail.childrenHelp': 'Immediate child summaries come from the bounded overview response; no transaction pages are aggregated in the browser.',
		'accounts.detail.noChildren': 'No immediate children were returned for this account.',
		'accounts.detail.activityTitle': 'Direct account activity',
		'accounts.detail.activityHelp': 'Activity is scoped to direct splits in this account for a paired date range up to 366 days.',
		'accounts.detail.resetActivity': 'Reset activity',
		'accounts.detail.activityFormHelp': 'Set both dates to call the bounded activity endpoint. Reset removes date/limit and preserves the safe account explorer return link.',
		'accounts.detail.limit': 'Recent row limit',
		'accounts.detail.applyActivity': 'Load activity',
		'accounts.detail.requestCounters': 'SSR request counters: overview={overview}, activity={activity}.',
		'accounts.detail.exactChange': 'Exact direct change',
		'accounts.detail.flowNotApplicable': 'Generic inflow/outflow classification is not applicable for account activity; exact direct change is shown instead.',
		'accounts.detail.recentReturned': 'Recent rows returned',
		'accounts.detail.openTransactionExplorer': 'Open exact /transactions drilldown',
		'accounts.detail.unavailableNoFxScope': 'unavailable_no_fx_scope: non-base or non-currency account has no exact #54 explorer drilldown; no FX conversion is performed.',
		'accounts.detail.openBaseReport': 'Open base-currency book report',
		'accounts.detail.recentTitle': 'Recent direct transactions',
		'accounts.detail.noRecentTransactions': 'No recent direct transactions were returned for this bounded date range.',
		'dashboard.loading': 'Loading dashboard summary for the selected read-only book…',
		'dashboard.loadFailed': 'Failed to load dashboard data',
		'dashboard.sectionError.title': 'Dashboard section unavailable',
		'dashboard.sectionError.redacted':
			'This dashboard section could not be loaded. Other sections are still shown when available. Backend details were redacted.',
		'dashboard.summary': 'Summary',
		'dashboard.conservativeTotals': 'Conservative dashboard totals',
		'dashboard.reportingBasis': 'Reporting basis',
		'dashboard.currencyConversion': 'Currency conversion',
		'dashboard.currencyConversionIncluded': 'included',
		'dashboard.currencyConversionNotIncluded': 'not included',
		'dashboard.netWorth': 'Net Worth',
		'dashboard.assets': 'Assets',
		'dashboard.liabilities': 'Liabilities',
		'dashboard.incomeThisMonth': 'Income This Month',
		'dashboard.expensesThisMonth': 'Expenses This Month',
		'dashboard.viewMonthlyFilter': "View this month's transaction filter",
		'dashboard.drilldownSafety':
			'Drilldowns preserve the active book and use existing read-only transaction URL filters. Dashboard totals remain base-currency-only with no FX conversion; transaction filter views are evidence for the same period/account context, not invented recomputations.',
		'dashboard.recentTransactions': 'Recent Transactions',
		'dashboard.recentTransactionsHelp': 'Same read-only transaction list, newest first; CSV export uses matching filters.',
		'dashboard.viewTransactions': 'View transactions',
		'dashboard.noRecentTransactions': 'No transactions found.',
		'dashboard.expensesByAccount': 'Expenses by Account',
		'dashboard.expensesByAccountHelp': 'Base-currency-only reporting; account links open the same read-only date/account filter used for CSV parity.',
		'dashboard.noExpenses': 'No expenses found for the selected period.',
		'dashboard.cashflow': 'Cashflow',
		'dashboard.cashflowHelp': 'Monthly drilldowns use date_from/date_to transaction filters for the active book. No FX conversion is inferred.',
		'dashboard.noCashflow': 'No cashflow data for the selected period.',
		'dashboard.cashflowIn': 'In',
		'dashboard.cashflowOut': 'Out',
		'dashboard.cashflowNet': 'Net',
		'reports.metaTitle': 'Period reports',
		'reports.kicker': 'Read-only reports',
		'reports.title': 'Period reports explorer',
		'reports.bookLabel': 'Book: {name}',
		'reports.viewTransactionsPeriod': 'View /transactions for this period',
		'reports.period.title': 'Report period',
		'reports.period.urlBackedHelp':
			'URL-backed range: {dateFrom} to {dateTo}. Presets and custom dates only change read-only query parameters.',
		'reports.period.presetsAria': 'Report period presets',
		'reports.period.customAria': 'Custom report period',
		'reports.period.dateFrom': 'Date from',
		'reports.period.dateTo': 'Date to',
		'reports.period.applyCustom': 'Apply custom range',
		'reports.comparison.title': 'Comparison period',
		'reports.comparison.urlBackedHelp':
			'URL-backed comparison: {dateFrom} to {dateTo}. The comparison endpoint receives primary and comparison dates in one read-only GET request.',
		'reports.comparison.modeAria': 'Comparison period modes',
		'reports.comparison.mode.previousEquivalent': 'Previous equivalent',
		'reports.comparison.mode.samePeriodLastYear': 'Same period last year',
		'reports.comparison.customAria': 'Custom comparison period',
		'reports.comparison.dateFrom': 'Comparison date from',
		'reports.comparison.dateTo': 'Comparison date to',
		'reports.comparison.applyCustom': 'Apply comparison',
		'reports.comparison.validation.unsupportedMode': 'Choose a supported comparison mode.',
		'reports.comparison.validation.invalidDateRange':
			'Enter valid comparison_date_from/comparison_date_to values using YYYY-MM-DD dates.',
		'reports.comparison.validation.invalidRange': 'Invalid comparison range: comparison_date_from must be on or before comparison_date_to.',
		'reports.comparison.validation.inconsistentRange':
			'This comparison mode requires comparison_date_from={dateFrom} and comparison_date_to={dateTo}. No reports API request was made.',
		'reports.comparison.deltaError': 'Comparison delta is unavailable because one source section returned an explicit error. Backend details were redacted.',
		'reports.comparison.notComparable':
			'Comparison is not comparable for this section. Unknown or mismatched currency/no-FX limitations are preserved below as technical backend limitation text.',
		'reports.comparison.rowNotComparable':
			'This account row is not comparable. Side totals and exact drilldowns are shown, but the backend row detail is redacted and no delta is calculated.',
		'reports.comparison.emptyDelta': 'No comparable delta rows were returned for this section.',
		'reports.comparison.zeroHint':
			'Exact 0.00 values are genuine data and unchanged deltas remain visible; one-sided successful zero values are not treated as missing.',
		'reports.comparison.technicalLimitation': 'Backend limitation: {limitation}',
		'reports.comparison.primarySide': 'Primary period',
		'reports.comparison.comparisonSide': 'Comparison period',
		'reports.comparison.sourcePeriodsTitle': 'Primary and comparison totals',
		'reports.comparison.sourcePeriodsHelp':
			'Each side links to /transactions with its exact date_from/date_to. Balance totals remain as-of each side date_to.',
		'reports.comparison.summaryDeltaTitle': 'Balance change',
		'reports.comparison.cashflowDeltaTitle': 'Cashflow change',
		'reports.comparison.expenseChangesTitle': 'Spending changes by account',
		'reports.comparison.expenseChangesHelp':
			'Rows preserve the backend-ranked account union. Each side opens /transactions with the side dates and account_id.',
		'reports.comparison.unchanged': 'Unchanged',
		'reports.comparison.increase': 'Increase',
		'reports.comparison.decrease': 'Decrease',
		'reports.comparison.absoluteChange': 'Absolute change',
		'reports.comparison.noExpenseChanges': 'No expense-account comparison rows were returned.',
		'reports.preset.thisMonth': 'This month',
		'reports.preset.lastMonth': 'Last month',
		'reports.preset.yearToDate': 'Year to date',
		'reports.loading': 'Loading read-only period reports…',
		'reports.validation.invalidDateRange': 'Enter a valid custom date_from/date_to range using YYYY-MM-DD dates.',
		'reports.validation.unsupportedPreset': 'Choose a supported report period preset.',
		'reports.validation.invalidRange': 'Invalid range: date_from must be on or before date_to.',
		'reports.validation.invalidTitle': 'Invalid range',
		'reports.validation.invalidNoRequest': 'No reports API request was made for this invalid range.',
		'reports.error.title': 'Report request failed',
		'reports.error.redactedHelp':
			'Unknown API details are redacted; genuine empty report sections are shown separately below when available.',
		'reports.error.requestFailed': 'Reports API request failed safely.',
		'reports.error.serviceUnavailable': 'Reports API is unavailable. Backend details are redacted.',
		'reports.error.forbidden': 'You do not have access to this read-only reports view.',
		'reports.error.notFound': 'Requested report data was not found.',
		'reports.error.unknown': 'Reports API is unavailable or returned an unsupported response. Unknown backend details are redacted.',
		'reports.sectionError.redacted': 'Reports API returned a section error. Backend details are redacted.',
		'reports.empty.title': 'No report data',
		'reports.empty.message':
			'The reports API returned no summary, cashflow, monthly, or expense rows for this read-only period. Try another date range or inspect transactions for the same filters.',
		'reports.empty.aria': 'No report data for the selected period',
		'reports.empty.action': 'Open matching /transactions filter',
		'reports.limitations.title': 'Reporting limitations',
		'reports.limitations.reportingBasis':
			'Reporting basis: {reportingBasis}. No FX conversion is performed; totals are base_currency_only and should not be interpreted as converted multi-currency totals.',
		'reports.limitations.none':
			'No additional limitations were reported by the API; keep treating this as base_currency_only with No FX conversion.',
		'reports.partial.title': 'Partial report',
		'reports.partial.help': 'One or more sections returned an explicit error state; unaffected sections remain visible.',
		'reports.summary.title': 'Summary totals',
		'reports.summary.help': 'Period income/expenses/net come from cashflow for {dateFrom} through {dateTo}; balance totals are as of date_to.',
		'reports.summary.openFilter': 'Open matching transaction filter',
		'reports.summary.income': 'Income',
		'reports.summary.expenses': 'Expenses',
		'reports.summary.netPeriodResult': 'Net period result',
		'reports.summary.netWorth': 'Net worth',
		'reports.summary.assets': 'Assets',
		'reports.summary.liabilities': 'Liabilities',
		'reports.summary.noTotals': 'No summary totals were returned for this period.',
		'reports.cashflow.title': 'Cashflow totals',
		'reports.cashflow.monthlyTitle': 'Monthly cashflow',
		'reports.cashflow.monthlyHelp': 'Each month links to /transactions with matching date_from/date_to filters.',
		'reports.cashflow.inflow': 'Inflow',
		'reports.cashflow.outflow': 'Outflow',
		'reports.cashflow.net': 'Net',
		'reports.cashflow.noTotals': 'No cashflow totals were returned for this period.',
		'reports.cashflow.noMonthly': 'No monthly cashflow rows were returned for this period.',
		'reports.expenses.title': 'Expenses by account',
		'reports.expenses.help': 'Account rows link to exact /transactions filters for the selected date range and account_id.',
		'reports.expenses.allPeriod': 'All period transactions',
		'reports.expenses.noRows': 'No expense account rows were returned for this period.',
		'reports.localizationNotice':
			'Release-critical safety copy is localized in English/Russian; backend report values remain as returned by the read-only API.',
		'home.subtitle': 'Modern self-hosted read-only companion for existing GnuCash books.',
		'transactions.kicker': 'Transactions',
		'transactions.title': 'Browse transactions',
		'transactionDetail.back': 'Back to transactions',
		'transactionDetail.kicker': 'Transaction detail',
		'transactionDetail.noDescription': 'No description',
		'transactionDetail.helper': 'Read-only view of the selected GnuCash transaction. Split rows below show memo and reconciliation metadata when available.',
		'transactionDetail.date': 'Date',
		'transactionDetail.currency': 'Currency',
		'transactionDetail.splits': 'Splits',
		'transactionDetail.id': 'ID',
		'transactionDetail.splitSingular': 'split',
		'transactionDetail.splitPlural': 'splits',
		'transactionDetail.writeAlphaHistoryTitle': 'Created through write-alpha app metadata',
		'transactionDetail.writeAlphaHistoryHelper':
			'This read-only history provenance means the transaction GUID matches a safe app-metadata marker from a write-alpha run. Synthetic/disposable history hint only; backend ownership guards remain authoritative and default writes remain disabled.',
		'transactionDetail.nonOwnedTitle': 'Historical/manual transaction remains read-only',
		'transactionDetail.nonOwnedHelper':
			'Edit/delete controls are hidden because this transaction is not marked as write-alpha-owned in app metadata. Backend ownership guards remain authoritative. Experimental controls appear only for write-alpha-owned synthetic/disposable transactions when write mode is explicitly enabled in APP_ENV=test.',
		'transactionDetail.deleteTitle': 'Experimental delete transaction',
		'transactionDetail.deleteHelper': 'This button is hidden unless write mode is explicitly enabled and the transaction is write-alpha-owned in app metadata. Use only ignored copied/disposable test books in APP_ENV=test; GnuCash Desktop remains the authoritative editor.',
		'transactionDetail.deleteAcknowledgement': 'I acknowledge this experimental DELETE is for ignored disposable/test copies only and requires backup, audit, and lock-release checks.',
		'transactionDetail.deleteButton': 'Delete transaction',
		'transactionDetail.deleteConfirm': 'Delete this transaction from the disposable/test GnuCash book? This experimental write-alpha action creates a backup first and cannot be undone here.',
		'transactionSplits.title': 'Splits',
		'transactionSplits.helper': 'Read-only split metadata from GnuCash: account, memo, reconciliation state, and amount.',
		'transactionSplits.empty': 'No split rows were returned for this transaction. The read-only detail view does not invent balancing data.',
		'transactionSplits.splitAccount': 'Split {index} account',
		'transactionSplits.memo': 'Memo',
		'transactionSplits.noMemo': 'No memo',
		'transactionSplits.reconciliation': 'Reconciliation',
		'transactionSplits.accountId': 'Account ID',
		'transactionSplits.caption': 'Transaction split rows with account, memo, reconciliation state, and amount',
		'transactionSplits.stateNotProvided': 'Not provided',
		'transactionSplits.stateUnknown': 'State {state}',
		'books.kicker': 'Books',
		'books.title': 'Book metadata',
		'books.subtitle':
			'Read-only book metadata only. This page shows already configured books that your account can access; it does not provide book data editing workflows.',
		'books.activeDefault': 'Active/default book',
		'books.configuredTitle': 'Configured books',
		'books.hiddenPolicy': 'Archived and unauthorized books are hidden or blocked by the API.',
		'books.noMutationBadge': 'No upload, deletion, or GnuCash data editing here',
		'books.currentBook': 'Current book',
		'books.defaultBook': 'Active/default book',
		'books.readOnlyBadge': 'Read-only',
		'books.accessibleBadge': 'Access status: Accessible',
		'books.baseCurrency': 'Base currency',
		'books.storageType': 'Storage type',
		'books.readonlyStatus': 'Read-only status',
		'books.safetyNote': 'GnuCash Desktop remains the authoritative editor.',
		'books.auditEvidence': 'Write-alpha audit evidence',
		'books.noBooks': 'No accessible configured books are available for this account.',
		'books.emptyTitle': 'No accessible books found',
		'books.emptyMessage':
			'No configured books are available to this account. Confirm the book registry and access metadata, then sign in again or ask the administrator to grant read-only access. For first run, also verify GNUCASH_DEFAULT_BOOK_PATH points to a mounted readable test-copy book and check /health for redacted diagnostics.',
		'books.notConfigured': 'Not configured',
		'books.unknown': 'Unknown',
		'books.accessRole': 'Access role',
		'books.status': 'Metadata status',
		'books.storageDiagnostics': 'Storage diagnostics',
		'books.safeNextActions': 'Safe next actions',
		'books.privatePathRedacted': 'Private filesystem path is intentionally not shown.',
		'books.openSafeViews': 'Open safe views',
		'books.unavailableViews':
			'Read-only data views are withheld until this book is available from the runtime; use the safe diagnostics above instead of exposing private paths.',
		'books.viewAccounts': 'View accounts',
		'books.browseTransactions': 'Browse transactions',
		'books.viewScheduled': 'View scheduled metadata',
		'books.dashboardSummary': 'Dashboard summary',
		'books.settingsLink': 'Settings and health',
		'books.lastSuccessfulAt': 'Last successful check',
		'books.capabilitiesTitle': 'Read-only capabilities',
		'books.capabilityReadOnly': 'Read-only mode',
		'books.capabilityAccounts': 'Accounts',
		'books.capabilityTransactions': 'Transactions',
		'books.capabilityReports': 'Reports',
		'books.capabilityUpload': 'Browser upload',
		'books.capabilityEdit': 'GnuCash edits',
		'books.capabilityDelete': 'Underlying file removal',
		'books.yes': 'Yes',
		'books.no': 'No',
		'books.noManagementActions': 'No registry management actions are available on this read-only page.',
		'books.registryManagement': 'Registry management',
		'books.registryManagementSafety':
			'Admin-only metadata actions. They change the app registry/default only and never delete or edit the underlying GnuCash file.',
		'books.setDefaultAction': 'Set as default',
		'books.removeRegistryAction': 'Remove from registry',
		'books.operatorGuidanceTitle': 'Self-hosting operator guidance',
		'books.metadataSource': 'Metadata source',
		'books.dataAccess': 'Listing data access',
		'books.readOnlyDefault': 'Read-only default',
		'books.unsupportedActions': 'Unsupported MVP management actions',
		'books.noUnsupportedActions': 'No management actions are exposed for this book.',
		'books.currentDefaultExplanation':
			'Current marks the book selected for this browser session; default marks the configured fallback book. Both are read-only context labels, not management controls.',
		'books.safeOperatorGuidance':
			'Use the host configuration and app metadata database to change registered books. This page intentionally does not expose upload, delete, default-changing, or registry-edit actions in the MVP.',
		'books.contextRecoveryTitle': 'Book context reviewed',
		'books.contextRecoveryStale':
			'The selected-book cookie was invalid or no longer accessible, so this browser session was safely moved to an accessible read-only book. Review the current/default labels before opening a view.',
		'books.contextRecoveryUnavailable':
			'The selected book is accessible in metadata but currently unavailable for read-only data views. This browser session was safely moved to an available read-only book when one exists; review storage diagnostics and safe next actions without exposing private paths.',
		'books.contextRecoveryNoBooks':
			'No accessible configured books are available for this account. The selected-book cookie was cleared; archived and unauthorized books remain hidden or blocked.',
		'books.registerTitle': 'Register mounted book metadata',
		'books.registerIntro':
			'Admin-only app metadata flow for an already-mounted local copied/test SQLite book. The web UI does not upload, copy, open, or mutate GnuCash accounting data.',
		'books.adminOnlyBadge': 'Admin metadata only',
		'books.registerName': 'Display name',
		'books.registerCurrency': 'Base currency',
		'books.registerPath': 'Mounted local SQLite path',
		'books.registerMakeDefault': 'Make this the default fallback book for this installation',
		'books.registerSafety':
			'Use only host-mounted copied/test books. Private filesystem paths are sent to the API for metadata registration but are never rendered back in the book list, and no accounts, transactions, memos, amounts, uploads, or screenshots are collected.',
		'books.registerSubmit': 'Register metadata',
		'books.loading': 'Loading accessible read-only books…',
		'books.addBookAction': 'Add book',
		'books.firstRunAdminTitle': 'No books are registered yet',
		'books.firstRunAdminMessage':
			'Register an existing server-mounted GnuCash SQL SQLite book to start. The web UI records app metadata only and keeps GnuCash Desktop as the authoritative editor.',
		'books.firstRunUserTitle': 'No book is assigned to this account',
		'books.firstRunUserMessage':
			'An administrator must register or assign a book before this account can open read-only views. No server path fields, environment guidance, or management actions are shown for this role.',
		'books.enabledBook': 'Enabled',
		'books.disabledBook': 'Disabled',
		'books.notChecked': 'Not checked',
		'books.statusUnknown': 'Unknown',
		'books.status.ready': 'Ready',
		'books.status.available': 'Available',
		'books.status.ok': 'OK',
		'books.status.warning': 'Warning',
		'books.status.rejected': 'Rejected',
		'books.status.unavailable': 'Unavailable',
		'books.status.unknown': 'Unknown',
		'books.status.missing_file': 'Source unavailable',
		'books.status.not_configured': 'Not configured',
		'books.status.remote_or_unchecked': 'Unchecked source',
		'books.status.invalid_gnucash_schema': 'Invalid GnuCash SQL book',
		'books.status.action_required': 'Action required',
		'books.status.not_checked': 'Not checked',
		'books.status.disabled': 'Disabled',
		'books.status.failed': 'Failed',
		'books.status.empty': 'Empty',
		'books.status.blocked': 'Blocked',
		'books.status.unsupported': 'Unsupported',
		'books.problem.admin_required': 'Administrator privileges are required for book registry management.',
		'books.problem.preflight_required': 'Run a successful preflight and confirm the metadata-only action before registration.',
		'books.problem.preflight_rejected': 'Preflight rejected this source. The book was not registered.',
		'books.problem.preflight_token_invalid': 'The preflight token is missing, expired, or does not match the form values. Run preflight again.',
		'books.problem.missing_preflight_token': 'A fresh preflight token is required for this metadata lifecycle action. Run preflight again.',
		'books.problem.invalid_preflight_token': 'The preflight token is invalid, expired, or tampered. Run preflight again.',
		'books.problem.preflight_request_mismatch': 'The form no longer matches the preflight token. Run preflight again with the same display name, base currency, and default choice.',
		'books.problem.preflight_source_mismatch': 'The source changed after preflight. Re-enter the mounted server-side path and run preflight again.',
		'books.problem.invalid_path': 'The mounted server path is invalid. No book registry metadata was changed.',
		'books.problem.unsupported_source': 'Only a supported server-side SQLite source under the allowed roots may be registered here.',
		'books.problem.outside_allowed_roots': 'The source is outside the allowed server-side book roots.',
		'books.problem.symlink_forbidden': 'The source path uses a symlink component that is not allowed for registration.',
		'books.problem.missing_file': 'The configured server-side source was not found by the API runtime.',
		'books.problem.not_regular_file': 'The configured server-side source is not a regular file.',
		'books.problem.permission_denied': 'The API runtime does not have permission to read this source.',
		'books.problem.unsupported_format': 'Only existing server-side GnuCash SQL SQLite books are supported here.',
		'books.problem.invalid_gnucash_schema': 'The configured SQLite database does not match the expected GnuCash SQL schema.',
		'books.problem.source_changed': 'The source changed after preflight. Run preflight again before confirming registration.',
		'books.problem.open_failed': 'The API could not open the source in read-only mode.',
		'books.problem.duplicate_canonical_path': 'This canonical book source is already registered in app metadata.',
		'books.problem.book_not_enabled': 'This book metadata entry is disabled. Enable it with a fresh preflight before opening or making it default.',
		'books.problem.book_not_healthy': 'Cached health is not ready. Recheck health successfully before opening or making this book default.',
		'books.problem.book_health_not_checked': 'Cached health has not been checked yet. Run a health recheck first.',
		'books.problem.api_unavailable': 'The API service is unavailable. No book registry metadata was changed.',
		'books.problem.book_registry_failed': 'Book registry metadata update failed. No GnuCash source file was changed.',
		'books.problem.unknown_book_problem': 'The API returned an unsupported book status. Private backend details are hidden.',
		'books.manageSuccessSetDefault': 'Updated the default app metadata entry. No GnuCash accounting data was changed.',
		'books.manageSuccessRemoveRegistry': 'Removed the book from the app registry only. The source GnuCash file is not deleted or modified.',
		'books.manageSuccessRecheck': 'Refreshed cached health from a bounded read-only recheck. No GnuCash accounting data was changed.',
		'books.manageSuccessRename': 'Updated display metadata only. No GnuCash source file was changed.',
		'books.manageSuccessDisable': 'Disabled this app registration. The source GnuCash file remains present and unmodified.',
		'books.manageSuccessEnable': 'Enabled this app registration after a fresh matching preflight. No GnuCash accounting data was changed.',
		'books.removeMetadataConfirm':
			'I understand this removes only app registration/access metadata. The source GnuCash file is not deleted or modified.',
		'books.reportsLink': 'View reports',
		'books.statusDetailsTitle': 'Status details and lifecycle route',
		'books.statusDetailsHelp': 'Open Settings and health for path-redacted rename, disable/enable, unregister, and recheck actions.',
		'books.renameFuture': 'Rename updates display metadata only.',
		'books.disableFuture': 'Disable/enable controls app availability without touching the underlying file.',
		'books.recheckFuture': 'Recheck refreshes typed health/status without registering a new book.',
		'books.backToBooks': 'Back to books',
		'books.newTitle': 'Add a GnuCash SQL SQLite book',
		'books.newSubtitle': 'SSR-first admin flow: explain support, preflight the mounted source, then explicitly confirm metadata registration.',
		'books.adminRequiredTitle': 'Administrator-only book registration',
		'books.newStep1Title': 'Step 1 — supported source format',
		'books.newStep2Title': 'Step 2 — mounted source metadata',
		'books.newStep3Title': 'Step 3 — typed preflight checklist',
		'books.newStep4Title': 'Step 4 — confirm registration',
		'books.supportedFormat': 'Existing server-side GnuCash SQL SQLite only. The file must already be mounted where the API runtime can read it.',
		'books.unsupportedFormatWarning':
			'No browser upload, copy, import, XML, compressed XML, conversion, filesystem discovery, or source delete is available in this flow.',
		'books.preflightSubmit': 'Run preflight',
		'books.preflightReady': 'Preflight is ready. Registration has not happened yet.',
		'books.preflightRejected': 'Preflight rejected this source. Registration has not happened.',
		'books.preflightFormat': 'Detected format',
		'books.preflightCheckedAt': 'Checked at',
		'books.preflightTokenOpaque': 'The preflight token is opaque and never placed in the URL. It is sent only by the explicit confirmation form.',
		'books.confirmRegisterHelp': 'Confirm only if the checklist matches the source you intended. This stores app registry metadata only.',
		'books.confirmRegisterSubmit': 'Confirm metadata registration',
		'books.registrationSuccessTitle': 'Book metadata registered',
		'books.registrationSuccessMessage': 'The app registry was updated only. The source GnuCash file was not deleted, modified, copied, or converted.',
		'books.settingsTitle': 'Book settings and health',
		'books.settingsSubtitle': 'Path-redacted read-only status for one registered book. Admin lifecycle actions affect app metadata/availability only.',
		'books.settingsSummaryTitle': 'Registration summary',
		'books.healthTitle': 'Cached health',
		'books.healthHelp': 'Health fields are typed backend status codes mapped to local copy; backend messages, private paths, and arbitrary payloads are not rendered.',
		'books.healthSafeCode': 'Safe code',
		'books.healthSourceStatus': 'Source status',
		'books.healthOpenStatus': 'Read-only open status',
		'books.healthAccountsStatus': 'Accounts status',
		'books.healthTransactionsStatus': 'Transactions status',
		'books.healthReportsStatus': 'Reports status',
		'books.adminLifecycleTitle': 'Admin lifecycle controls',
		'books.adminLifecycleSafety': 'These controls call only the accepted app metadata lifecycle routes. They never upload, copy, edit, or remove the source GnuCash file.',
		'books.renameTitle': 'Display metadata',
		'books.renameHelp': 'Change only the app display name and base currency metadata.',
		'books.renameAction': 'Save metadata',
		'books.recheckTitle': 'Health recheck',
		'books.recheckHelp': 'Run a bounded read-only health probe and update cached typed status fields.',
		'books.recheckAction': 'Recheck health',
		'books.disableTitle': 'Disable app availability',
		'books.disableHelp': 'Disable this app registration and hide read-only open links. The source GnuCash file remains present and unmodified.',
		'books.disableMetadataConfirm': 'I understand this changes only app registration/availability metadata. The source GnuCash file remains present, unmodified, and not deleted.',
		'books.disableAction': 'Disable registration',
		'books.enableTitle': 'Enable with fresh preflight',
		'books.enablePreflightHelp': 'Enter the mounted server-side path again. The stored raw path is never shown; the preflight preview remains path-redacted and must be confirmed separately with an opaque token.',
		'books.enablePath': 'Mounted server-side path for this registered book',
		'books.enablePreflightSubmit': 'Run enable preflight',
		'books.enablePreviewTitle': 'Path-redacted enable preflight preview',
		'books.enableConfirmHelp': 'Confirm enable only if this preview matches the registered display name, base currency, and intended default choice.',
		'books.enableConfirmSubmit': 'Confirm enable',
		'books.unregisterTitle': 'Unregister app metadata',
		'books.unregisterHelp': 'Remove this app registration/access metadata only. The source GnuCash file remains present, unmodified, and not deleted.',
		'books.section.source': 'Source',
		'books.section.open': 'Read-only open',
		'books.section.accounts': 'Accounts',
		'books.section.transactions': 'Transactions',
		'books.section.reports': 'Reports',
		'books.statusCode.source_ready': 'Source ready',
		'books.statusCode.open_ready': 'Read-only open ready',
		'books.statusCode.accounts_ready': 'Accounts ready',
		'books.statusCode.transactions_ready': 'Transactions ready',
		'books.statusCode.reports_ready': 'Reports ready',
		'books.statusCode.registration_available': 'Registration available',
		'books.statusCode.already_registered': 'Already registered',
		'books.registrationStatus.available': 'Metadata registration is available for this preflight token.',
		'books.registrationStatus.alreadyRegistered': 'This canonical source is already registered, so confirmation is disabled.',
		'books.registrationStatus.unavailable': 'Metadata registration is not available for this preflight result.',
		'books.sectionStatus.source.ready': 'The server-side source passed preflight without rendering the private path back to the browser.',
		'books.sectionStatus.source.rejected': 'The server-side source was rejected. Fix host-side storage and rerun preflight.',
		'books.sectionStatus.source.unavailable': 'The server-side source is not ready. Verify host-side storage and rerun preflight.',
		'books.sectionStatus.open.ready': 'The API can open this source in read-only mode for validation.',
		'books.sectionStatus.open.rejected': 'The API rejected the read-only open check. No registration was performed.',
		'books.sectionStatus.open.unavailable': 'The read-only open check is not available for this preflight result.',
		'books.sectionStatus.accounts.ready': 'The accounts adapter is ready for read-only views.',
		'books.sectionStatus.accounts.rejected': 'The accounts readiness check was rejected. No account data is rendered here.',
		'books.sectionStatus.accounts.unavailable': 'The accounts readiness check is not available for this preflight result.',
		'books.sectionStatus.transactions.ready': 'The transactions adapter is ready for read-only views.',
		'books.sectionStatus.transactions.rejected': 'The transactions readiness check was rejected. No transaction data is rendered here.',
		'books.sectionStatus.transactions.unavailable': 'The transactions readiness check is not available for this preflight result.',
		'books.sectionStatus.reports.ready': 'The reports adapter is ready for read-only views.',
		'books.sectionStatus.reports.rejected': 'The reports readiness check was rejected. No report data is rendered here.',
		'books.sectionStatus.reports.unavailable': 'The reports readiness check is not available for this preflight result.',
		'audit.title': 'Write-alpha audit evidence',
		'audit.bannerTitle': 'Write-alpha audit evidence for disposable runs',
		'audit.bannerMessage':
			'Read-only app metadata summary for the active book. This pre-alpha operator view is for synthetic/disposable write-alpha runs only; it is not production-ready, not security-audited, and not a production audit log product.',
		'audit.redactionMessage':
			'Raw request payloads, backup paths, private file paths, account names, memos, and amounts are not shown.',
		'audit.activeBook': 'Active book',
		'audit.noAccessibleBook': 'No accessible book',
		'audit.reviewBooks': 'Review books',
		'audit.filtersLabel': 'Audit summary filters',
		'audit.allActions': 'All actions',
		'audit.create': 'Create',
		'audit.patch': 'PATCH',
		'audit.delete': 'DELETE',
		'audit.allResults': 'All results',
		'audit.success': 'Success',
		'audit.failed': 'Failed',
		'audit.started': 'Started',
		'audit.unknown': 'Unknown',
		'audit.action': 'Action',
		'audit.result': 'Result',
		'audit.sinceIso': 'Since ISO',
		'audit.untilIso': 'Until ISO',
		'audit.applyFilters': 'Apply filters',
		'audit.clearFilters': 'Clear filters',
		'audit.limit': 'Rows per page',
		'audit.countsLabel': 'Audit summary counts',
		'audit.filteredRows': 'Filtered rows',
		'audit.returnedCount': 'Returned: {count}',
		'audit.actions': 'Actions',
		'audit.results': 'Results',
		'audit.window': 'Window',
		'audit.ownership': 'Ownership',
		'audit.ownedCreated': 'write-alpha-created',
		'audit.nonOwnedRejected': 'non-owned rejected',
		'audit.lastMutation': 'Last mutation',
		'audit.requestedWindow': 'Requested: {since} → {until}',
		'audit.returnedWindow': 'Returned: {oldest} → {newest}',
		'audit.noStart': 'No start',
		'audit.noEnd': 'No end',
		'audit.none': 'none',
		'audit.emptyTitle': 'No write-alpha audit rows',
		'audit.emptyMessage':
			'No create/PATCH/DELETE write-alpha app-metadata audit entries match the current filters for the active book. Run only explicit disposable APP_ENV=test write-alpha smokes before expecting evidence here.',
		'audit.browseTransactions': 'Browse transactions',
		'audit.showingEntries':
			'Showing {returned} of {total} redacted audit entries. Backup is represented only as present/missing.',
		'audit.pageStatus': 'Page offset {offset}; bounded page size {limit}.',
		'audit.paginationLabel': 'Audit summary pagination',
		'audit.paginationSummary': 'Review page offset {offset}, limit {limit}. Filters stay in the URL only.',
		'audit.previousPage': 'Previous page',
		'audit.nextPage': 'Next page',
		'audit.timestamp': 'Timestamp',
		'audit.txnPrefix': 'Txn prefix',
		'audit.backupSafeError': 'Backup / safe error',
		'audit.backupPresent': 'Backup: present',
		'audit.backupMissing': 'Backup: not recorded',
		'audit.backupRef': 'Backup ref',
		'audit.limitations': 'Limitations',
		'writeMode.title': 'Experimental controlled write mode — not part of MVP v0.1',
		'writeMode.message':
			'MVP v0.1 remains read-only by default and GNUCASH_WRITES_ENABLED=false is the safe default. This write form is experimental post-MVP functionality only, not production-ready or security-audited, and should be reachable only in an explicit APP_ENV=test disposable run.',
		'writeMode.desktop': 'GnuCash Desktop remains the authoritative editor.',
		'writeMode.disposableOnly':
			'Use only an outside-git copied/restorable test book in ignored runtime storage; never point this at the original/source book or the only existing copy.',
		'writeMode.createOnlyDogfood':
			'For copied-book dogfood, stop after dry-run unless explicitly continuing to one small CREATE test transaction. Do not use this form for production entries, PATCH, or DELETE.',
		'writeMode.evidence': 'Confirm an independent backup, restore plan, audit row, app backup evidence, and lock-release evidence before treating a write-alpha CREATE run as complete.',
		'writeMode.staleLock':
			'If a stale lock file remains, stop the runtime first and follow the recovery runbook; never assume a host permission error means an active writer.',
		'writeMode.neverRealBook': 'Never use this experimental path with your only real financial book.',
		'writeMode.finalConfirm':
			'Final warning: this experimental post-MVP action will write one test transaction to a copied/restorable GnuCash book. Continue only in APP_ENV=test with the original untouched, an outside-git copied test book, independent backup, restore plan, audit, app backup, and lock-release checks. Never use a source/original, only copy, or production book. Continue?',
		'writeMode.acknowledgement':
			'I acknowledge that controlled writes are experimental post-MVP functionality, MVP v0.1 remains read-only by default, GNUCASH_WRITES_ENABLED=false is the safe default, GnuCash Desktop remains the authoritative editor, and I am using only an outside-git copied/restorable test book with the original untouched, one CREATE test transaction, independent backup, restore plan, audit, app backup, and lock-release checks. This is not for production use.',
		'writeMode.kicker': 'Controlled write',
		'writeMode.newTransactionTitle': 'New transaction',
		'writeMode.newTransactionHelp': 'Creates one simple two-split test transaction only for copied-book dogfood. It is not for production entries; verify backup/restore evidence before and after the final write.',
		'transactions.filters.title': 'Transaction filters',
		'transactions.filters.subtitle':
			'Narrow the read-only transaction list and CSV export; filters never modify your GnuCash book.',
		'transactions.filters.filteredView': 'Filtered view',
		'transactions.filters.datePresets': 'Date presets',
		'transactions.filters.datePresetAria': 'Transaction date range presets',
		'transactions.filters.datePresetHelp':
			'Presets update only the ordinary date_from/date_to filters; the list and CSV export stay read-only and use the same filtered view.',
		'transactions.filters.activeSummaryTitle': 'Active filters applied to list and CSV export',
		'transactions.filters.search': 'Search',
		'transactions.filters.searchPlaceholder': 'Description, notes, or split memo...',
		'transactions.filters.account': 'Account',
		'transactions.filters.accountScope': 'Account scope',
		'transactions.filters.accountId': 'Account ID',
		'transactions.filters.lockedAccountHelp':
			"This account detail view is fixed to this account; other filters narrow only this account's transactions.",
		'transactions.filters.allAccounts': 'All accounts',
		'transactions.filters.customDateRange': 'Custom date range',
		'transactions.filters.from': 'From',
		'transactions.filters.to': 'To',
		'transactions.filters.startDateError': 'Start date must be earlier than or equal to end date.',
		'transactions.filters.state': 'State',
		'transactions.filters.anyState': 'Any state',
		'transactions.filters.stateUnreconciled': 'Unreconciled',
		'transactions.filters.stateCleared': 'Cleared',
		'transactions.filters.stateReconciled': 'Reconciled',
		'transactions.filters.stateVoided': 'Voided',
		'transactions.filters.stateHelp':
			'Filters by the GnuCash split reconciliation state; it does not edit transactions.',
		'transactions.filters.minAmount': 'Min amount',
		'transactions.filters.maxAmount': 'Max amount',
		'transactions.filters.amountError': 'Minimum amount must be less than or equal to maximum amount.',
		'transactions.filters.submit': 'Filter',
		'transactions.filters.clear': 'Clear filters',
		'transactions.filters.summary.search': 'Search',
		'transactions.filters.summary.account': 'Account',
		'transactions.filters.summary.dates': 'Dates',
		'transactions.filters.summary.from': 'From',
		'transactions.filters.summary.to': 'To',
		'transactions.filters.summary.amount': 'Amount',
		'transactions.filters.summary.minAmount': 'Min amount',
		'transactions.filters.summary.maxAmount': 'Max amount',
		'transactions.filters.summary.state': 'State',
		'transactions.listStatus.title': 'Current read-only view',
		'transactions.listStatus.order': 'Sorted newest first by transaction date.',
		'transactions.listStatus.pageRange': 'Showing {start}–{end} of {total} matching transactions on this page.',
		'transactions.listStatus.emptyPage': 'No matching transactions on this page.',
		'transactions.listStatus.filtersApplied': '{count} active {filterLabel}; the list, pagination, and CSV export use the same URL filters.',
		'transactions.listStatus.noFilters': 'No transaction filters are active; CSV export uses the current unfiltered read-only view.',
		'transactions.listStatus.exportParity': 'CSV export ignores page offset, starts from the first matching row, and is capped at 10,000 rows.',
		'transactions.explorer.formHelp':
			'URL is the source of truth. The form submits a real GET request to /transactions; changing filters, sort, or page_size clears any cursor.',
		'transactions.explorer.datePresetHelp': 'Presets set paired date_from/date_to values and keep the canonical explorer cursor cleared.',
		'transactions.explorer.dateTextLegend': 'Dates, text, and state',
		'transactions.explorer.scopeLegend': 'Account or type scope',
		'transactions.explorer.scopeHelp': 'Choose up to 20 accounts, or choose income/expense type mode. These modes are mutually exclusive.',
		'transactions.explorer.accountIds': 'Accounts (up to 20)',
		'transactions.explorer.accountIdsHelp': 'Hold Ctrl/Cmd to select multiple accounts. Amount and direction use the exact selected-account split sum.',
		'transactions.explorer.accountOptionsLimited': 'Only the first bounded account options are shown; paste a canonical account_ids URL for rarer accounts.',
		'transactions.explorer.accountsDisabledByType': 'Account selection is disabled while income/expense type mode is active.',
		'transactions.explorer.type': 'Type mode',
		'transactions.explorer.typeAny': 'No type mode',
		'transactions.explorer.typeIncome': 'Income',
		'transactions.explorer.typeExpense': 'Expense',
		'transactions.explorer.direction': 'Direction',
		'transactions.explorer.directionAny': 'Any direction',
		'transactions.explorer.directionIncrease': 'Increase selected accounts',
		'transactions.explorer.directionDecrease': 'Decrease selected accounts',
		'transactions.explorer.directionHelp': 'Direction is available only with account_ids; it is not combined with income/expense type mode.',
		'transactions.explorer.amountPagingLegend': 'Exact amount and pagination controls',
		'transactions.explorer.amountPagingHelp': 'Amount filters require account_ids or type mode, use canonical Decimal strings, and never use float arithmetic. page_size accepts 1–100.',
		'transactions.explorer.sort': 'Sort',
		'transactions.explorer.sortDateDesc': 'Newest first',
		'transactions.explorer.sortDateAsc': 'Oldest first',
		'transactions.explorer.pageSize': 'Page size',
		'transactions.explorer.reset': 'Reset explorer',
		'transactions.explorer.removeFilter': 'Remove filter',
		'transactions.explorer.cursorChip': 'Pagination cursor active',
		'transactions.explorer.dateRangeRequiredTitle': 'Choose a bounded date range',
		'transactions.explorer.dateRangeRequiredMessage':
			'Set both date_from and date_to (up to 366 days) before loading the read-only explorer. The reset/default route does not request an unbounded transaction page.',
		'transactions.explorer.readyTitle': 'Explorer page loaded',
		'transactions.explorer.readyMessage': 'The explorer returned a bounded cursor page for the active filters.',
		'transactions.explorer.trueEmptyTitle': 'No transactions match these exact filters',
		'transactions.explorer.trueEmptyMessage': 'The explorer reached a true empty result for this URL. Clear filters or broaden the date/account/type/search scope.',
		'transactions.explorer.scanWindowEmptyTitle': 'No rows in this scan window',
		'transactions.explorer.scanWindowEmptyMessage': 'The backend stopped at a bounded scan window before proving the full result set. Continue pagination or narrow filters.',
		'transactions.explorer.scanLimitedTitle': 'Partial bounded scan',
		'transactions.explorer.scanLimitedMessage': 'This page is valid but scan-limited. Continue with the opaque cursor or narrow filters for a tighter window.',
		'transactions.explorer.endTitle': 'End of cursor results',
		'transactions.explorer.endMessage': 'No additional rows were returned for this cursor. Reset pagination to the first page or change filters.',
		'transactions.explorer.invalidFilterTitle': 'Invalid explorer filters',
		'transactions.explorer.invalidFilterMessage': 'The explorer rejected this filter combination before any transaction page was rendered. Fix the URL or reset filters.',
		'transactions.explorer.staleCursorTitle': 'Pagination cursor is stale',
		'transactions.explorer.staleCursorMessage': 'The opaque cursor no longer matches the filters or signing window. Reset pagination and retry.',
		'transactions.explorer.loadFailedTitle': 'Transactions explorer failed',
		'transactions.explorer.loadFailedMessage': 'The read-only explorer request failed safely. Backend details, paths, and private sentinels were redacted.',
		'transactions.explorer.unknownFailureTitle': 'Transactions explorer unavailable',
		'transactions.explorer.unknownFailureMessage': 'The API returned an unsupported failure shape. Unknown backend details were redacted.',
		'transactions.explorer.legacyCompatibility': 'Legacy /transactions URL compatibility mode is active for account_id, limit/offset, or one-sided date parameters. New explorer links use account_ids, page_size, and cursor.',
		'transactions.explorer.legacyOffsetConflict': 'Legacy offset pagination cannot be mixed with advanced explorer fields. Remove offset or reset to the canonical explorer URL.',
		'transactions.explorer.returnedStatus': 'Returned {count} row(s) on this cursor page; requested page_size={pageSize}.',
		'transactions.explorer.filtersApplied': '{count} active {filterLabel}; the URL, form, detail return link, and cursor pagination all preserve them.',
		'transactions.explorer.noFilters': 'No advanced explorer filters are active; the URL still records sort and page_size.',
		'transactions.explorer.order': 'Sorted by {sort}; transaction date plus GUID is the stable cursor key.',
		'transactions.explorer.noTotal': 'No total count or page number is fabricated; navigation uses opaque Previous/Next/Continue cursors only.',
		'transactions.explorer.limitationsTitle': 'Explorer limitations',
		'transactions.explorer.resetPagination': 'Reset pagination',
		'transactions.explorer.paginationLabel': 'Transactions explorer cursor pagination',
		'transactions.explorer.cursorPagination': 'Cursor pagination: no page numbers or fabricated totals.',
		'transactions.explorer.previous': 'Previous',
		'transactions.explorer.next': 'Next',
		'transactions.explorer.continue': 'Continue',
		'transactions.writeAlphaHistoryBadge': 'write-alpha-created',
		'transactions.writeAlphaHistoryTitle':
			'Created by write-alpha app metadata. Synthetic/disposable history hint only; backend ownership guards remain authoritative.',
		'transactions.listStatus.writeAlphaHint':
			'{count} transaction(s) on this page are marked write-alpha-created in app metadata; treat this only as a synthetic/disposable history hint. Backend ownership guards remain authoritative and default writes stay disabled.',
		'transactions.listStatus.writeAlphaFollowupTitle': 'New synthetic CREATE follow-up',
		'transactions.listStatus.writeAlphaFollowupHelp':
			'After a synthetic/disposable CREATE is read back, the newly created synthetic/disposable transaction appears in the normal newest-first history only after the read-only API returns it and app metadata marks its GUID. It is not pinned above filters; if the badge is absent, clear filters or review redacted audit evidence. The badge is not a permission to write.',
		'transactions.listStatus.writeAlphaAuditLink': 'Review redacted write-alpha audit evidence',
		'transactions.export.button': 'Export CSV',
		'transactions.export.buttonWithFilters': 'Export CSV ({count} {filterLabel})',
		'transactions.export.statusFiltered':
			'Exports the current read-only filtered view, capped at 10,000 rows. Large exports run synchronously; narrow filters if the request times out or the export is truncated.',
		'transactions.export.statusUnfiltered':
			'Exports this read-only transaction list, capped at 10,000 rows. Large exports run synchronously; narrow filters if the request times out or the export is truncated.',
		'transactions.export.emptyStatus':
			'The current export would contain only the CSV header because no matching transactions are visible.',
		'transactions.export.countStatus':
			'Current matching rows before the cap: {total}. CSV amounts stay string values; no currency conversion is performed.',
		'transactions.export.truncatedStatus':
			'Current matching rows before the cap: {total}; export will include only the first 10,000 rows. Narrow filters for a complete subset.',
		'transactions.export.accountButton': 'Export account CSV',
		'transactions.export.accountButtonWithFilters': 'Export account CSV ({count} {filterLabel})',
		'transactions.export.accountStatus':
			'Exports this account-scoped read-only filtered view with the same search/date/amount/state filters.',
		'transactions.export.explorerDisabled':
			'CSV export is disabled for advanced explorer filters because exact legacy CSV parity is not proved for account_ids, type, direction, query, cursor, and scan-limited pages.',
		'transactions.export.explorerHonesty':
			'Use legacy account_id/limit URLs for the existing CSV endpoint; advanced explorer CSV remains disabled until exact parity is implemented.',
		'scheduled.title': 'Scheduled transactions',
		'scheduled.kicker': 'Read-only scheduled transaction awareness',
		'scheduled.subtitle':
			'Safe summary metadata from the active GnuCash book. This pre-alpha page does not create, edit, delete, or calculate upcoming schedule predictions for scheduled transactions. Use GnuCash Desktop as the authoritative editor.',
		'scheduled.activeBook': 'Active book',
		'scheduled.recurringMetadata': 'Recurring metadata',
		'scheduled.metadataHelp':
			'Only safe schedule fields are shown. Template split details and private raw SQL are not exposed. Filters and sorting are URL-only display controls; they do not save scheduled metadata in browser storage.',
		'scheduled.readOnlyBadge': 'Read-only · no scheduling editor',
		'scheduled.statusFilter': 'Status filter',
		'scheduled.templateFilter': 'Template metadata filter',
		'scheduled.sortDisplay': 'Sort display',
		'scheduled.all': 'All',
		'scheduled.enabled': 'Enabled',
		'scheduled.disabled': 'Disabled',
		'scheduled.templatePresent': 'Template present',
		'scheduled.noTemplateReference': 'No template reference',
		'scheduled.startDate': 'Start date',
		'scheduled.endDate': 'End date',
		'scheduled.lastOccurred': 'Last occurred',
		'scheduled.name': 'Name',
		'scheduled.enabledFirst': 'Enabled first',
		'scheduled.shownStatus':
			'Showing {shown} of {total} safe scheduled metadata rows. No template split amounts, accounts, memos, transaction descriptions, or raw SQL are exposed.',
		'scheduled.clearFilters': 'Clear scheduled filters',
		'scheduled.unnamed': 'Unnamed scheduled transaction',
		'scheduled.templateAccount': 'Template account',
		'scheduled.templateReferenceStatus': 'Template reference status',
		'scheduled.templatePresentRedacted': 'Present; split details redacted',
		'scheduled.templateNotPresentRedacted': 'No template reference reported; no split details inferred',
		'scheduled.occurrences': 'Occurrences',
		'scheduled.occurrencesValue': 'total {total} · remaining {remaining}',
		'scheduled.autoCreateNotify': 'Auto-create / notify',
		'scheduled.advanceDays': 'Advance days',
		'scheduled.advanceDaysValue': 'create {create} · notify {notify}',
		'scheduled.recurrenceMetadata': 'Recurrence metadata',
		'scheduled.noRecurrenceMetadata': 'No safe recurrence metadata is available through the adapter.',
		'scheduled.noMatchesTitle': 'No scheduled transactions match these display filters',
		'scheduled.noMatchesMessage':
			'The active book has scheduled metadata, but the current URL-only scheduled filters hide every row. Clear filters to return to the full safe read-only metadata view.',
		'scheduled.noMatchesAria': 'No scheduled transactions match display filters',
		'scheduled.emptyTitle': 'No scheduled transactions found',
		'scheduled.emptyMessage':
			'No scheduled transactions are available through the safe read-only adapter for this book. If the book uses scheduled transactions, manage and review them in GnuCash Desktop.',
		'scheduled.emptyAria': 'No scheduled transactions found',
		'scheduled.browseTransactions': 'Browse transactions',
		'scheduled.reviewBooks': 'Review books',
		'scheduled.notConfigured': 'Not configured',
		'scheduled.yes': 'Yes',
		'scheduled.no': 'No',
		'scheduled.recurrenceEvery': 'every {count}',
		'scheduled.recurrenceFrom': 'from {date}',
		'scheduled.recurrenceWeekend': 'weekend: {value}',
		'scheduled.recurrenceUnavailable': 'Raw recurrence metadata unavailable'
	},
	ru: {
		'locale.english': 'Английский',
		'locale.russian': 'Русский',
		'locale.switcherLabel': 'Язык',
		'login.title': 'Вход',
		'login.subtitle': 'Используйте настроенную учётную запись администратора.',
		'login.username': 'Имя пользователя',
		'login.password': 'Пароль',
		'login.submit': 'Войти',
		'login.error.missingCredentials': 'Введите имя пользователя и пароль.',
		'login.error.serviceUnavailable': 'Сервис аутентификации недоступен.',
		'login.error.invalidCredentials': 'Неверное имя пользователя или пароль.',
		'login.error.operatorConfiguration':
			'Вход настроен не полностью. Проверьте JWT_SECRET и APP_ADMIN_PASSWORD_HASH или APP_ADMIN_PASSWORD в локальном .env/deployment окружении, перезапустите сервис и оставьте данные GnuCash в read-only режиме.',
		'login.notice.sessionChanged': 'Сессия изменилась. Войдите заново, чтобы продолжить.',
		'login.firstRun.title': 'Проверки first-run read-only deployment',
		'login.firstRun.summary': 'Безопасная redacted диагностика /health помогает отличить placeholder JWT secret, admin bootstrap, смонтированную книгу, CORS и write-disabled статус до входа.',
		'login.firstRun.safeDiagnostics': 'Здесь не показываются secrets, полные пути, tokens, содержимое app DB или данные книги.',
		'login.firstRun.jwtSecret': 'JWT secret',
		'login.firstRun.adminBootstrap': 'Admin bootstrap',
		'login.firstRun.defaultBook': 'Основная книга',
		'login.firstRun.cors': 'CORS origins',
		'login.firstRun.writeMode': 'Write mode',
		'login.firstRun.status.ok': 'OK',
		'login.firstRun.status.warning': 'Предупреждение',
		'login.firstRun.status.actionRequired': 'Требуется действие',
		'nav.dashboard': 'Обзор',
		'nav.accounts': 'Счета',
		'nav.transactions': 'Транзакции',
		'nav.scheduled': 'Плановые',
		'nav.reports': 'Отчёты',
		'nav.books': 'Книги',
		'nav.adminUsers': 'Админ users',
		'nav.logout': 'Выйти',
		'adminUsers.kicker': 'Админ foundation',
		'adminUsers.title': 'Управление users и доступом к книгам',
		'adminUsers.subtitle': 'Server-rendered управление локальными пользователями для self-hosted установки. Backend остаётся authoritative, данные GnuCash остаются read-only.',
		'adminUsers.backToUsers': 'Назад к admin users',
		'adminUsers.createUser': 'Создать user',
		'adminUsers.listTitle': 'Локальные users',
		'adminUsers.listHelp': 'Bounded список из /admin/users. Обычные users не получают user/access payloads через SSR.',
		'adminUsers.loading': 'Загрузка admin user data…',
		'adminUsers.emptyTitle': 'Локальные users не вернулись',
		'adminUsers.emptyMessage': 'Bounded admin API вернул пустую страницу. Создайте user или измените фильтр enabled/disabled.',
		'adminUsers.adminRequiredTitle': 'Нужна учётная запись администратора',
		'adminUsers.adminRequiredMessage': 'Эта страница намеренно не отдаёт admin user/access payloads, пока /auth/me не вернёт is_admin=true. Backend authorization всё равно authoritative.',
		'adminUsers.safeBoundaryBadge': 'Только app metadata — без GnuCash writes',
		'adminUsers.username': 'Username',
		'adminUsers.displayName': 'Display name',
		'adminUsers.status': 'Статус',
		'adminUsers.enabled': 'Enabled',
		'adminUsers.disabled': 'Disabled',
		'adminUsers.adminBadge': 'Admin',
		'adminUsers.userBadge': 'User',
		'adminUsers.assignmentCount': 'Назначения книг',
		'adminUsers.createdAt': 'Создан',
		'adminUsers.updatedAt': 'Обновлён',
		'adminUsers.actions': 'Действия',
		'adminUsers.viewDetails': 'Управлять user',
		'adminUsers.previousPage': 'Предыдущая страница',
		'adminUsers.nextPage': 'Следующая страница',
		'adminUsers.stateFilter': 'Состояние enabled',
		'adminUsers.stateAll': 'Все users',
		'adminUsers.stateEnabled': 'Только enabled',
		'adminUsers.stateDisabled': 'Только disabled',
		'adminUsers.applyFilter': 'Применить фильтр',
		'adminUsers.newTitle': 'Создать локального user',
		'adminUsers.newSubtitle': 'Создаёт одну локальную учётку. Username и admin choice immutable в этом milestone; доступ к книгам пустой, пока admin не выдаст его позже.',
		'adminUsers.createTitle': 'Учётные данные user',
		'adminUsers.usernameHelp': 'Lowercase ASCII username, 3–64 символа, начинается с буквы. Позже не редактируется.',
		'adminUsers.displayNameHelp': '1–100 видимых символов. Это единственная editable profile label в #57.',
		'adminUsers.initialPassword': 'Initial password',
		'adminUsers.passwordHelp': 'Password отправляется только в server action и никогда не repopulate после ошибок.',
		'adminUsers.isAdminChoice': 'Создать как global admin',
		'adminUsers.isAdminHelp': 'Admins управляют локальными users и book assignments. Роли owner/editor/viewer по книге не дают global admin.',
		'adminUsers.zeroAccessDefault': 'Новые users начинают с нулевым доступом к книгам; default book сама по себе доступ не даёт.',
		'adminUsers.createSubmit': 'Создать user',
		'adminUsers.detailTitle': 'Детали user',
		'adminUsers.detailSubtitle': 'Управление display name, enabled state, password reset и явными active-book assignments.',
		'adminUsers.summaryTitle': 'Safe user summary',
		'adminUsers.updateDisplayNameTitle': 'Обновление display name',
		'adminUsers.updateDisplayNameHelp': 'Здесь редактируется только display name. Username и admin role намеренно не редактируются.',
		'adminUsers.updateDisplayNameSubmit': 'Обновить display name',
		'adminUsers.enableTitle': 'Enable account',
		'adminUsers.enableHelp': 'Enable снова позволяет user войти с текущими credentials или после reset.',
		'adminUsers.enableSubmit': 'Enable user',
		'adminUsers.disableTitle': 'Disable account',
		'adminUsers.disableHelp': 'Disable блокирует следующий authenticated request после backend auth-version enforcement; self-disable и last-admin checks остаются на backend.',
		'adminUsers.confirmDisableCopy': 'Я понимаю, что это disable только локальную учётку; users, books, audit rows и GnuCash data не удаляются.',
		'adminUsers.disableSubmit': 'Disable user',
		'adminUsers.resetPasswordTitle': 'Password reset',
		'adminUsers.resetPasswordHelp': 'Reset заменяет только server-side secret и invalidates existing sessions на следующем request. Новое значение больше не показывается.',
		'adminUsers.newPassword': 'New password',
		'adminUsers.confirmResetCopy': 'Я понимаю, что reset invalidates existing sessions, а password field не будет repopulated.',
		'adminUsers.resetPasswordSubmit': 'Reset password',
		'adminUsers.accessTitle': 'Матрица доступа к книгам',
		'adminUsers.accessHelp': 'Grant только active, non-archived books. Новые grants default to viewer; owner/editor labels не включают GnuCash writes или global admin.',
		'adminUsers.book': 'Книга',
		'adminUsers.role': 'Роль',
		'adminUsers.grantSubmit': 'Grant/update access',
		'adminUsers.revokeSubmit': 'Revoke access',
		'adminUsers.confirmRevokeCopy': 'Я понимаю, что revoke убирает app access на следующем request и не меняет GnuCash book.',
		'adminUsers.noBooksTitle': 'Нет assignable active books',
		'adminUsers.noBooksMessage': 'API не вернул active non-archived book options. Users могут безопасно оставаться с zero access.',
		'adminUsers.bookOptionsUnavailableTitle': 'Book options временно недоступны',
		'adminUsers.bookOptionsUnavailableMessage': 'Existing assignments остаются видимыми, но новые grants отключены, пока fixed options list не загрузится успешно.',
		'adminUsers.noAssignments': 'У этого user нет book assignments.',
		'adminUsers.limitedActionsNote': 'В этом milestone доступны только display-name update, enable/disable, password reset и явные book grants.',
		'adminUsers.passwordNotRepopulated': 'Password fields используют autocomplete=new-password и никогда не reuse submitted values.',
		'adminUsers.role.viewer': 'Viewer',
		'adminUsers.role.editor': 'Editor',
		'adminUsers.role.owner': 'Owner',
		'adminUsers.roleCopy.viewer': 'Viewer: только read-only views.',
		'adminUsers.roleCopy.editor': 'Editor: сохраняет existing edit-authorization label, но этот UI не включает GnuCash writes.',
		'adminUsers.roleCopy.owner': 'Owner: здесь тот же book-level effective access label, что editor; это не global admin.',
		'adminUsers.roleBoundary': 'Roles влияют только на app metadata access. GNUCASH_WRITES_ENABLED=false и backend write gates остаются независимыми.',
		'adminUsers.problem.username_invalid': 'Username не соответствует local-account policy.',
		'adminUsers.problem.username_taken': 'User с таким normalized username уже существует.',
		'adminUsers.problem.display_name_invalid': 'Display name отсутствует или вне разрешённой длины/символов.',
		'adminUsers.problem.password_policy': 'Password не соответствует local policy.',
		'adminUsers.problem.user_not_found': 'User не найден.',
		'adminUsers.problem.user_disabled': 'Этот user disabled или session changed. При необходимости войдите заново.',
		'adminUsers.problem.session_changed': 'Сессия изменилась. Войдите заново, чтобы продолжить.',
		'adminUsers.problem.self_disable_forbidden': 'Self-disable не разрешён через web UI.',
		'adminUsers.problem.last_enabled_admin': 'Должен остаться хотя бы один enabled admin.',
		'adminUsers.problem.book_not_assignable': 'Эта book не active/assignable.',
		'adminUsers.problem.admin_required': 'Нужны права администратора.',
		'adminUsers.problem.api_unavailable': 'Admin API недоступен. Raw backend details не показаны.',
		'adminUsers.problem.unknown_admin_problem': 'Admin action safely failed. Unknown backend details скрыты.',
		'adminUsers.success.user_created': 'User создан с zero book access по умолчанию.',
		'adminUsers.success.display_name_changed': 'Display name обновлён.',
		'adminUsers.success.user_enabled': 'User enabled.',
		'adminUsers.success.user_disabled': 'User disabled.',
		'adminUsers.success.password_reset': 'Password reset; existing sessions invalidated на следующем request.',
		'adminUsers.success.book_access_granted': 'Book access granted или updated.',
		'adminUsers.success.book_access_revoked': 'Book access revoked.',
		'safety.statusLabel': 'Статус безопасности read-only режима',
		'safety.badge': 'Read-only по умолчанию',
		'safety.message':
			'Pre-alpha MVP по умолчанию работает только на чтение. GNUCASH_WRITES_ENABLED=false — безопасное значение по умолчанию; GnuCash Desktop остаётся главным редактором.',
		'safety.releaseCritical':
			'Не production-ready и не проходило security audit. Экспериментальные write-alpha flows скрыты по умолчанию и при явном включении предназначены только для outside-git copied/restorable test books с untouched originals.',
		'safety.currentBook': 'Текущая книга',
		'safety.noActiveBook': 'Активная книга не выбрана',
		'safety.reviewBooks': 'Проверить книги',
		'error.badgeWithCode': 'Ошибка {statusCode}',
		'error.badgeNetwork': 'Ошибка API/сети',
		'error.forbiddenTitle': 'Доступ запрещён',
		'error.forbiddenMessage': 'Эта учётная запись не может открыть этот read-only раздел или книгу. Проверьте выбранную книгу или войдите под учётной записью с доступом.',
		'error.notFoundTitle': 'Страница или книга не найдена',
		'error.notFoundMessage': 'Запрошенная страница, книга, счёт или транзакция не найдены. Объект может быть недоступен, архивирован или скрыт правилами доступа.',
		'error.serviceTitle': 'Сервис временно недоступен',
		'error.serviceMessage':
			'API или сетевой запрос не сработал при загрузке этого read-only раздела. Убедитесь, что сервис запущен, проверьте /health для редактированной first-run диагностики, затем проверьте локальный .env и volume с книгой перед повторной попыткой.',
		'error.genericTitle': 'Что-то пошло не так',
		'error.genericMessage': 'Произошла неожиданная ошибка API или сети. Повторите попытку или вернитесь к безопасной read-only странице.',
		'error.retry': 'Повторить',
		'error.retryPage': 'Повторить эту страницу',
		'error.backDashboard': 'Назад к обзору',
		'error.reviewBooks': 'Проверить книги и storage diagnostics',
		'dashboard.title': 'Обзор',
		'accounts.kicker': 'Счета',
		'accounts.title': 'Дерево счетов',
		'accounts.bookLabel': 'Книга',
		'accounts.loading': 'Загрузка дерева счетов для выбранной read-only книги…',
		'accounts.filter.label': 'Фильтр счетов',
		'accounts.filter.placeholder': 'Поиск по названию счёта, полному пути, типу или валюте',
		'accounts.filter.filteredStatus': 'Показано {filtered} из {total} счетов. Совпадающие дочерние счета остаются вместе с родительским путём.',
		'accounts.filter.allStatus': 'Показаны все счета: {total}. Используйте фильтр, чтобы сузить большое read-only дерево счетов без изменения книги.',
		'accounts.filter.noMatchesTitle': 'Нет счетов по этому фильтру.',
		'accounts.filter.noMatchesMessage': 'Очистите фильтр счетов, чтобы вернуться к полному read-only дереву счетов.',
		'accounts.column.name': 'Название',
		'accounts.column.type': 'Тип',
		'accounts.column.balance': 'Баланс',
		'accounts.column.currency': 'Валюта',
		'accounts.emptyTitle': 'Счета не найдены',
		'accounts.emptyMessage': 'Выбранная read-only книга не вернула счета. Проверьте активную test-copy книгу и доступные метаданные книги, прежде чем полагаться на этот вид.',
		'accounts.emptyAction': 'Проверить доступные книги',
		'accounts.explorer.reset': 'Сбросить account explorer',
		'accounts.explorer.filtersTitle': 'Фильтры account explorer',
		'accounts.explorer.formHelp':
			'URL — источник истины. Форма отправляет read-only GET в /accounts; сервер валидирует фильтры до вызова bounded account explorer API.',
		'accounts.explorer.mode': 'Режим отображения',
		'accounts.explorer.modeTree': 'Дерево с ancestor context',
		'accounts.explorer.modeFlat': 'Плоские matching rows',
		'accounts.explorer.query': 'Поиск',
		'accounts.explorer.type': 'Тип счёта',
		'accounts.explorer.hidden': 'Hidden счета',
		'accounts.explorer.placeholder': 'Placeholder счета',
		'accounts.explorer.visibilityExclude': 'Исключить',
		'accounts.explorer.visibilityInclude': 'Включить',
		'accounts.explorer.visibilityOnly': 'Только',
		'accounts.explorer.typesLegend': 'Фильтры типов',
		'accounts.explorer.directBalance': 'Прямой native balance',
		'accounts.explorer.recursiveBuckets': 'Recursive native-commodity buckets',
		'accounts.explorer.noRecursiveBuckets': 'Native balance buckets не вернулись.',
		'accounts.explorer.hiddenBadge': 'Hidden',
		'accounts.explorer.placeholderBadge': 'Placeholder',
		'accounts.explorer.contextBadge': 'Ancestor context',
		'accounts.explorer.repairedBadge': 'Repaired hierarchy',
		'accounts.explorer.readyTitle': 'Account explorer загружен',
		'accounts.explorer.readyMessage': 'Bounded account explorer вернул server-filtered строки счетов для этого URL.',
		'accounts.explorer.noMatchesTitle': 'Нет счетов по этим фильтрам',
		'accounts.explorer.noMatchesMessage': 'Server-filtered account explorer не вернул строк. Сбросьте фильтры или расширьте search/type/visibility.',
		'accounts.explorer.invalidFilterTitle': 'Некорректные фильтры account explorer',
		'accounts.explorer.invalidFilterMessage': 'URL account explorer отклонён до любого API-вызова explorer. Исправьте URL или сбросьте фильтры.',
		'accounts.explorer.narrowFiltersTitle': 'Сузьте фильтры счетов',
		'accounts.explorer.narrowFiltersMessage': 'Bounded account explorer отказался от результата как слишком большого/сложного. Сузьте query/type/visibility и повторите.',
		'accounts.explorer.loadFailedTitle': 'Account explorer не загрузился',
		'accounts.explorer.loadFailedMessage': 'Read-only запрос account explorer безопасно завершился ошибкой. Backend details, paths и private sentinels скрыты.',
		'accounts.explorer.unknownFailureTitle': 'Account explorer недоступен',
		'accounts.explorer.unknownFailureMessage': 'API вернул неподдерживаемую форму ошибки account explorer. Unknown backend details скрыты.',
		'accounts.explorer.statusCounts': 'Вернулось {returned} строк(и) счетов из {candidates} bounded candidates.',
		'accounts.explorer.warningsTitle': 'Предупреждения account explorer',
		'accounts.explorer.contextWarning': 'Некоторые строки — ancestors, добавленные только для сохранения search/filter context.',
		'accounts.explorer.hiddenWarning': 'Hidden счета видны, потому что текущий URL явно включает или выбирает их.',
		'accounts.explorer.placeholderWarning': 'Placeholder счета показаны как metadata rows, а не как transaction-bearing totals.',
		'accounts.explorer.repairedWarning': 'В иерархии были orphan/cycle repairs; source parent IDs сохранены там, где API их сообщил.',
		'accounts.explorer.mixedCommodityWarning': 'Recursive balances — отдельные native-commodity buckets. FX conversion и cross-commodity total не подразумеваются.',
		'accounts.explorer.resultsLabel': 'Server-filtered результаты account explorer',
		'accounts.detail.loading': 'Загрузка account overview для выбранной read-only книги…',
		'accounts.detail.kicker': 'Детали счёта',
		'accounts.detail.breadcrumbAria': 'Breadcrumb счёта',
		'accounts.detail.notAvailable': 'Недоступно',
		'accounts.detail.loadFailedTitle': 'Account detail не загрузился',
		'accounts.detail.loadFailedMessage': 'Read-only account overview или activity request безопасно завершился ошибкой. Backend details, paths и private sentinels скрыты.',
		'accounts.detail.unknownFailureTitle': 'Account detail недоступен',
		'accounts.detail.unknownFailureMessage': 'API вернул неподдерживаемую форму ошибки account detail. Unknown backend details скрыты.',
		'accounts.detail.invalidFilterTitle': 'Некорректный account detail URL',
		'accounts.detail.invalidFilterMessage': 'Account id, date_from/date_to, limit или return_to не прошли validation до любого activity API-вызова.',
		'accounts.detail.legacyNotice': 'Legacy account-detail transaction query keys проигнорированы. Эта migrated page использует только paired date_from/date_to, limit и safe account explorer return_to; old unbounded account-transactions API не вызывается.',
		'accounts.detail.overviewOnlyTitle': 'Только overview',
		'accounts.detail.overviewOnlyMessage': 'Date range не выбран, поэтому вызван только bounded account overview endpoint; activity request не выполнялся.',
		'accounts.detail.activityLoadedTitle': 'Account activity загружена',
		'accounts.detail.activityLoadedMessage': 'Bounded direct-account activity endpoint вернул exact change и recent direct rows для этого date range.',
		'accounts.detail.activityEmptyTitle': 'Нет direct activity в этом date range',
		'accounts.detail.activityEmptyMessage': 'Bounded direct-account activity endpoint вернул empty change/recent sections для выбранного счёта и дат.',
		'accounts.detail.partialActivityTitle': 'Частичная account activity',
		'accounts.detail.partialActivityMessage': 'Одна activity section безопасно упала; остальные секции видны, backend details скрыты.',
		'accounts.detail.backToExplorer': 'Назад к account explorer',
		'accounts.detail.subtreeCount': 'Счетов в subtree',
		'accounts.detail.childCount': 'Immediate children',
		'accounts.detail.childrenReturned': 'Children returned',
		'accounts.detail.childrenTruncated': 'Показаны только bounded первые child rows; child_count сообщает полный bounded graph count.',
		'accounts.detail.childrenTitle': 'Children',
		'accounts.detail.childrenHelp': 'Immediate child summaries приходят из bounded overview response; transaction pages в браузере не агрегируются.',
		'accounts.detail.noChildren': 'Для этого счёта immediate children не вернулись.',
		'accounts.detail.activityTitle': 'Direct account activity',
		'accounts.detail.activityHelp': 'Activity ограничена direct splits этого счёта для paired date range до 366 дней.',
		'accounts.detail.resetActivity': 'Сбросить activity',
		'accounts.detail.activityFormHelp': 'Укажите обе даты для вызова bounded activity endpoint. Reset удаляет date/limit и сохраняет safe account explorer return link.',
		'accounts.detail.limit': 'Лимит recent rows',
		'accounts.detail.applyActivity': 'Загрузить activity',
		'accounts.detail.requestCounters': 'SSR request counters: overview={overview}, activity={activity}.',
		'accounts.detail.exactChange': 'Exact direct change',
		'accounts.detail.flowNotApplicable': 'Generic inflow/outflow classification неприменима для account activity; вместо неё показан exact direct change.',
		'accounts.detail.recentReturned': 'Recent rows returned',
		'accounts.detail.openTransactionExplorer': 'Открыть точный /transactions drilldown',
		'accounts.detail.unavailableNoFxScope': 'unavailable_no_fx_scope: non-base или non-currency счёт не имеет точного #54 explorer drilldown; FX conversion не выполняется.',
		'accounts.detail.openBaseReport': 'Открыть base-currency book report',
		'accounts.detail.recentTitle': 'Recent direct transactions',
		'accounts.detail.noRecentTransactions': 'Recent direct transactions для этого bounded date range не вернулись.',
		'dashboard.loading': 'Загрузка dashboard summary для выбранной read-only книги…',
		'dashboard.loadFailed': 'Не удалось загрузить данные обзора',
		'dashboard.sectionError.title': 'Секция dashboard недоступна',
		'dashboard.sectionError.redacted':
			'Эту секцию dashboard не удалось загрузить. Другие секции всё ещё показываются, когда доступны. Backend details скрыты.',
		'dashboard.summary': 'Сводка',
		'dashboard.conservativeTotals': 'Консервативные итоги dashboard',
		'dashboard.reportingBasis': 'База отчёта',
		'dashboard.currencyConversion': 'Конвертация валют',
		'dashboard.currencyConversionIncluded': 'включена',
		'dashboard.currencyConversionNotIncluded': 'не включена',
		'dashboard.netWorth': 'Чистая стоимость',
		'dashboard.assets': 'Активы',
		'dashboard.liabilities': 'Обязательства',
		'dashboard.incomeThisMonth': 'Доходы за месяц',
		'dashboard.expensesThisMonth': 'Расходы за месяц',
		'dashboard.viewMonthlyFilter': 'Открыть фильтр транзакций за месяц',
		'dashboard.drilldownSafety':
			'Drilldown-ссылки сохраняют активную книгу и используют существующие read-only URL-фильтры транзакций. Итоги обзора остаются только в базовой валюте без FX-конвертации; виды транзакций — это evidence для того же периода/счёта, а не заново рассчитанные итоги.',
		'dashboard.recentTransactions': 'Последние транзакции',
		'dashboard.recentTransactionsHelp': 'Тот же read-only список транзакций, новые сначала; CSV export использует совпадающие фильтры.',
		'dashboard.viewTransactions': 'Открыть транзакции',
		'dashboard.noRecentTransactions': 'Транзакции не найдены.',
		'dashboard.expensesByAccount': 'Расходы по счетам',
		'dashboard.expensesByAccountHelp': 'Отчёт только в базовой валюте; ссылки по счетам открывают тот же read-only фильтр даты/счёта для parity с CSV.',
		'dashboard.noExpenses': 'За выбранный период расходы не найдены.',
		'dashboard.cashflow': 'Денежный поток',
		'dashboard.cashflowHelp': 'Месячные drilldown-ссылки используют фильтры транзакций date_from/date_to для активной книги. FX-конвертация не предполагается.',
		'dashboard.noCashflow': 'За выбранный период нет данных денежного потока.',
		'dashboard.cashflowIn': 'Вход',
		'dashboard.cashflowOut': 'Выход',
		'dashboard.cashflowNet': 'Итого',
		'reports.metaTitle': 'Отчёты за период',
		'reports.kicker': 'Read-only отчёты',
		'reports.title': 'Просмотр отчётов за период',
		'reports.bookLabel': 'Книга: {name}',
		'reports.viewTransactionsPeriod': 'Открыть /transactions за этот период',
		'reports.period.title': 'Период отчёта',
		'reports.period.urlBackedHelp':
			'URL-диапазон: {dateFrom} — {dateTo}. Быстрые периоды и свои даты меняют только read-only query parameters.',
		'reports.period.presetsAria': 'Быстрые периоды отчёта',
		'reports.period.customAria': 'Свой период отчёта',
		'reports.period.dateFrom': 'Дата с',
		'reports.period.dateTo': 'Дата по',
		'reports.period.applyCustom': 'Применить свой диапазон',
		'reports.comparison.title': 'Период сравнения',
		'reports.comparison.urlBackedHelp':
			'URL-сравнение: {dateFrom} — {dateTo}. Comparison endpoint получает primary и comparison dates одним read-only GET request.',
		'reports.comparison.modeAria': 'Режимы периода сравнения',
		'reports.comparison.mode.previousEquivalent': 'Предыдущий равный период',
		'reports.comparison.mode.samePeriodLastYear': 'Тот же период год назад',
		'reports.comparison.customAria': 'Свой период сравнения',
		'reports.comparison.dateFrom': 'Дата сравнения с',
		'reports.comparison.dateTo': 'Дата сравнения по',
		'reports.comparison.applyCustom': 'Применить сравнение',
		'reports.comparison.validation.unsupportedMode': 'Выберите поддерживаемый comparison mode.',
		'reports.comparison.validation.invalidDateRange':
			'Введите корректные comparison_date_from/comparison_date_to в формате YYYY-MM-DD.',
		'reports.comparison.validation.invalidRange': 'Некорректный диапазон сравнения: comparison_date_from должен быть не позже comparison_date_to.',
		'reports.comparison.validation.inconsistentRange':
			'Этот comparison mode требует comparison_date_from={dateFrom} и comparison_date_to={dateTo}. Запрос к reports API не выполнялся.',
		'reports.comparison.deltaError': 'Comparison delta недоступна, потому что одна source section вернула явную ошибку. Backend details скрыты.',
		'reports.comparison.notComparable':
			'Эту секцию нельзя корректно сравнить. Unknown or mismatched currency/no-FX limitations сохранены ниже как technical backend limitation text.',
		'reports.comparison.rowNotComparable':
			'Эту строку счёта нельзя корректно сравнить. Итоги сторон и точные drilldown-ссылки показаны, но detail строки от backend скрыт и delta не рассчитывается.',
		'reports.comparison.emptyDelta': 'Для этой секции не вернулись сравнимые delta rows.',
		'reports.comparison.zeroHint':
			'Точные значения 0.00 — реальные данные; unchanged deltas остаются видимыми, а one-sided successful zero не считается missing.',
		'reports.comparison.technicalLimitation': 'Backend limitation: {limitation}',
		'reports.comparison.primarySide': 'Основной период',
		'reports.comparison.comparisonSide': 'Период сравнения',
		'reports.comparison.sourcePeriodsTitle': 'Итоги основного периода и сравнения',
		'reports.comparison.sourcePeriodsHelp':
			'Каждая сторона ведёт в /transactions с точными date_from/date_to. Балансовые итоги остаются as-of date_to каждой стороны.',
		'reports.comparison.summaryDeltaTitle': 'Изменение баланса',
		'reports.comparison.cashflowDeltaTitle': 'Изменение cashflow',
		'reports.comparison.expenseChangesTitle': 'Изменения расходов по счетам',
		'reports.comparison.expenseChangesHelp':
			'Строки сохраняют backend-ranked account union. Каждая сторона открывает /transactions с датами стороны и account_id.',
		'reports.comparison.unchanged': 'Без изменений',
		'reports.comparison.increase': 'Рост',
		'reports.comparison.decrease': 'Снижение',
		'reports.comparison.absoluteChange': 'Абсолютное изменение',
		'reports.comparison.noExpenseChanges': 'Expense-account comparison rows не вернулись.',
		'reports.preset.thisMonth': 'Этот месяц',
		'reports.preset.lastMonth': 'Прошлый месяц',
		'reports.preset.yearToDate': 'С начала года',
		'reports.loading': 'Загрузка read-only отчётов за период…',
		'reports.validation.invalidDateRange': 'Введите корректный custom date_from/date_to диапазон в формате YYYY-MM-DD.',
		'reports.validation.unsupportedPreset': 'Выберите поддерживаемый быстрый период отчёта.',
		'reports.validation.invalidRange': 'Некорректный диапазон: date_from должен быть не позже date_to.',
		'reports.validation.invalidTitle': 'Некорректный диапазон',
		'reports.validation.invalidNoRequest': 'Для этого некорректного диапазона запрос к reports API не выполнялся.',
		'reports.error.title': 'Запрос отчёта не удался',
		'reports.error.redactedHelp':
			'Неизвестные детали API скрыты; настоящие пустые секции отчёта показываются отдельно, когда доступны.',
		'reports.error.requestFailed': 'Запрос к reports API безопасно завершился ошибкой.',
		'reports.error.serviceUnavailable': 'Reports API недоступен. Детали backend скрыты.',
		'reports.error.forbidden': 'Нет доступа к этому read-only разделу отчётов.',
		'reports.error.notFound': 'Запрошенные данные отчёта не найдены.',
		'reports.error.unknown': 'Reports API недоступен или вернул неподдержанный ответ. Неизвестные backend details скрыты.',
		'reports.sectionError.redacted': 'Reports API вернул ошибку секции. Backend details скрыты.',
		'reports.empty.title': 'Нет данных отчёта',
		'reports.empty.message':
			'Reports API не вернул summary, cashflow, monthly или expense rows для этого read-only периода. Попробуйте другой диапазон дат или откройте транзакции с теми же фильтрами.',
		'reports.empty.aria': 'Нет данных отчёта за выбранный период',
		'reports.empty.action': 'Открыть matching /transactions filter',
		'reports.limitations.title': 'Ограничения отчёта',
		'reports.limitations.reportingBasis':
			'База отчёта: {reportingBasis}. No FX conversion не выполняется; итоги base_currency_only не являются сконвертированными мультивалютными итогами.',
		'reports.limitations.none':
			'API не сообщил дополнительных ограничений; продолжайте считать отчёт base_currency_only без FX-конвертации.',
		'reports.partial.title': 'Частичный отчёт',
		'reports.partial.help': 'Одна или несколько секций вернули явную ошибку; остальные секции остаются видимыми.',
		'reports.summary.title': 'Итоги summary',
		'reports.summary.help': 'Доходы/расходы/итог берутся из cashflow за {dateFrom} — {dateTo}; балансовые итоги показаны на date_to.',
		'reports.summary.openFilter': 'Открыть matching transaction filter',
		'reports.summary.income': 'Доходы',
		'reports.summary.expenses': 'Расходы',
		'reports.summary.netPeriodResult': 'Итог периода',
		'reports.summary.netWorth': 'Чистая стоимость',
		'reports.summary.assets': 'Активы',
		'reports.summary.liabilities': 'Обязательства',
		'reports.summary.noTotals': 'За этот период summary totals не вернулись.',
		'reports.cashflow.title': 'Итоги cashflow',
		'reports.cashflow.monthlyTitle': 'Cashflow по месяцам',
		'reports.cashflow.monthlyHelp': 'Каждый месяц ведёт в /transactions с соответствующими фильтрами date_from/date_to.',
		'reports.cashflow.inflow': 'Вход',
		'reports.cashflow.outflow': 'Выход',
		'reports.cashflow.net': 'Итого',
		'reports.cashflow.noTotals': 'За этот период cashflow totals не вернулись.',
		'reports.cashflow.noMonthly': 'За этот период monthly cashflow rows не вернулись.',
		'reports.expenses.title': 'Расходы по счетам',
		'reports.expenses.help': 'Строки счетов ведут к точным фильтрам /transactions для выбранного date range и account_id.',
		'reports.expenses.allPeriod': 'Все транзакции периода',
		'reports.expenses.noRows': 'За этот период expense account rows не вернулись.',
		'reports.localizationNotice':
			'Release-critical safety copy локализована на английский/русский; значения отчёта остаются ровно такими, как их вернул read-only API.',
		'home.subtitle': 'Современный self-hosted read-only companion для существующих книг GnuCash.',
		'transactions.kicker': 'Транзакции',
		'transactions.title': 'Просмотр транзакций',
		'transactionDetail.back': 'Назад к транзакциям',
		'transactionDetail.kicker': 'Детали транзакции',
		'transactionDetail.noDescription': 'Без описания',
		'transactionDetail.helper': 'Read-only просмотр выбранной транзакции GnuCash. Строки split ниже показывают memo и metadata сверки, если они доступны.',
		'transactionDetail.date': 'Дата',
		'transactionDetail.currency': 'Валюта',
		'transactionDetail.splits': 'Splits',
		'transactionDetail.id': 'ID',
		'transactionDetail.splitSingular': 'split',
		'transactionDetail.splitPlural': 'splits',
		'transactionDetail.writeAlphaHistoryTitle': 'Создано через app metadata write-alpha',
		'transactionDetail.writeAlphaHistoryHelper':
			'Эта read-only provenance истории означает, что GUID транзакции совпадает с безопасным app-metadata marker из write-alpha запуска. Это только synthetic/disposable подсказка истории; backend ownership guards остаются главным enforcement, а writes по умолчанию отключены.',
		'transactionDetail.nonOwnedTitle': 'Историческая/manual транзакция остаётся read-only',
		'transactionDetail.nonOwnedHelper':
			'Edit/delete controls скрыты, потому что эта транзакция не отмечена в app metadata как write-alpha-owned. Backend ownership guards остаются главным enforcement. Экспериментальные controls появляются только для write-alpha-owned synthetic/disposable транзакций при явном write mode в APP_ENV=test.',
		'transactionDetail.deleteTitle': 'Экспериментальное удаление транзакции',
		'transactionDetail.deleteHelper': 'Эта кнопка скрыта, если write mode явно не включён и транзакция не write-alpha-owned в app metadata. Используйте только ignored скопированные/disposable тестовые книги в APP_ENV=test; GnuCash Desktop остаётся главным редактором.',
		'transactionDetail.deleteAcknowledgement': 'Я понимаю, что экспериментальный DELETE предназначен только для ignored disposable/test копий и требует backup, audit и lock-release checks.',
		'transactionDetail.deleteButton': 'Удалить транзакцию',
		'transactionDetail.deleteConfirm': 'Удалить эту транзакцию из disposable/test книги GnuCash? Это экспериментальное write-alpha действие сначала создаёт backup и не может быть отменено здесь.',
		'transactionSplits.title': 'Splits',
		'transactionSplits.helper': 'Read-only metadata split из GnuCash: счёт, memo, состояние сверки и сумма.',
		'transactionSplits.empty': 'Для этой транзакции не вернулись строки split. Read-only просмотр деталей не придумывает балансирующие данные.',
		'transactionSplits.splitAccount': 'Split {index}: счёт',
		'transactionSplits.memo': 'Memo',
		'transactionSplits.noMemo': 'Нет memo',
		'transactionSplits.reconciliation': 'Сверка',
		'transactionSplits.accountId': 'ID счёта',
		'transactionSplits.caption': 'Строки split транзакции со счётом, memo, состоянием сверки и суммой',
		'transactionSplits.stateNotProvided': 'Не указано',
		'transactionSplits.stateUnknown': 'Состояние {state}',
		'books.kicker': 'Книги',
		'books.title': 'Метаданные книг',
		'books.subtitle':
			'Только read-only метаданные книг. Эта страница показывает уже настроенные книги, доступные вашей учётной записи; разделов редактирования данных книги здесь нет.',
		'books.activeDefault': 'Активная/основная книга',
		'books.configuredTitle': 'Настроенные книги',
		'books.hiddenPolicy': 'Архивные и недоступные книги скрываются или блокируются API.',
		'books.noMutationBadge': 'Без загрузки, удаления и редактирования данных GnuCash',
		'books.currentBook': 'Текущая книга',
		'books.defaultBook': 'Активная/основная книга',
		'books.readOnlyBadge': 'Только чтение',
		'books.accessibleBadge': 'Статус доступа: доступна',
		'books.baseCurrency': 'Базовая валюта',
		'books.storageType': 'Тип хранения',
		'books.readonlyStatus': 'Read-only статус',
		'books.safetyNote': 'GnuCash Desktop остаётся главным редактором.',
		'books.auditEvidence': 'Write-alpha audit evidence',
		'books.noBooks': 'Для этой учётной записи нет доступных настроенных книг.',
		'books.emptyTitle': 'Нет доступных книг',
		'books.emptyMessage':
			'Для этой учётной записи нет настроенных доступных книг. Проверьте реестр книг и права доступа, затем войдите снова или попросите администратора выдать read-only доступ. При первом запуске также проверьте, что GNUCASH_DEFAULT_BOOK_PATH указывает на смонтированную читаемую test-copy книгу, и используйте /health для redacted diagnostics.',
		'books.notConfigured': 'Не настроено',
		'books.unknown': 'Неизвестно',
		'books.accessRole': 'Роль доступа',
		'books.status': 'Статус метаданных',
		'books.storageDiagnostics': 'Диагностика хранения',
		'books.safeNextActions': 'Безопасные следующие действия',
		'books.privatePathRedacted': 'Приватный путь файловой системы намеренно не показан.',
		'books.openSafeViews': 'Открыть безопасные разделы',
		'books.unavailableViews':
			'Read-only разделы с данными скрыты, пока книга недоступна из runtime; используйте безопасную диагностику выше без раскрытия приватных путей.',
		'books.viewAccounts': 'Открыть счета',
		'books.browseTransactions': 'Открыть транзакции',
		'books.viewScheduled': 'Открыть scheduled metadata',
		'books.dashboardSummary': 'Сводка dashboard',
		'books.settingsLink': 'Настройки и health',
		'books.lastSuccessfulAt': 'Последняя успешная проверка',
		'books.capabilitiesTitle': 'Read-only возможности',
		'books.capabilityReadOnly': 'Read-only режим',
		'books.capabilityAccounts': 'Счета',
		'books.capabilityTransactions': 'Транзакции',
		'books.capabilityReports': 'Отчёты',
		'books.capabilityUpload': 'Browser upload',
		'books.capabilityEdit': 'Редактирование GnuCash',
		'books.capabilityDelete': 'Удаление underlying file',
		'books.yes': 'Да',
		'books.no': 'Нет',
		'books.noManagementActions': 'На этой read-only странице нет доступных действий управления реестром.',
		'books.registryManagement': 'Управление реестром',
		'books.registryManagementSafety':
			'Admin-only действия с метаданными. Они меняют только реестр/основную книгу приложения и никогда не удаляют и не редактируют файл GnuCash.',
		'books.setDefaultAction': 'Сделать основной',
		'books.removeRegistryAction': 'Убрать из реестра',
		'books.operatorGuidanceTitle': 'Подсказки для self-hosting оператора',
		'books.metadataSource': 'Источник метаданных',
		'books.dataAccess': 'Доступ к данным при списке',
		'books.readOnlyDefault': 'Read-only по умолчанию',
		'books.unsupportedActions': 'Неподдерживаемые действия управления в MVP',
		'books.noUnsupportedActions': 'Для этой книги не показаны действия управления.',
		'books.currentDefaultExplanation':
			'Текущая книга выбрана для этой браузерной сессии; основная книга — настроенный fallback. Оба статуса являются read-only метками контекста, а не элементами управления.',
		'books.safeOperatorGuidance':
			'Меняйте зарегистрированные книги через конфигурацию хоста и app metadata database. Эта MVP-страница намеренно не даёт загрузку, удаление, смену основной книги или редактирование реестра.',
		'books.contextRecoveryTitle': 'Контекст книги проверен',
		'books.contextRecoveryStale':
			'Cookie выбранной книги был некорректным или больше недоступен, поэтому браузерная сессия безопасно переключена на доступную read-only книгу. Проверьте метки текущей/основной книги перед открытием разделов.',
		'books.contextRecoveryUnavailable':
			'Выбранная книга доступна в метаданных, но сейчас недоступна для read-only разделов с данными. Браузерная сессия безопасно переключена на доступную read-only книгу, если она есть; проверьте диагностику хранения и безопасные действия без раскрытия приватных путей.',
		'books.contextRecoveryNoBooks':
			'Для этой учётной записи нет доступных настроенных книг. Cookie выбранной книги очищен; архивные и неавторизованные книги остаются скрыты или заблокированы.',
		'books.registerTitle': 'Регистрация метаданных смонтированной книги',
		'books.registerIntro':
			'Admin-only поток app metadata для уже смонтированной локальной copied/test SQLite книги. Web UI не загружает, не копирует, не открывает и не изменяет бухгалтерские данные GnuCash.',
		'books.adminOnlyBadge': 'Только admin metadata',
		'books.registerName': 'Название',
		'books.registerCurrency': 'Базовая валюта',
		'books.registerPath': 'Смонтированный локальный SQLite путь',
		'books.registerMakeDefault': 'Сделать fallback книгой по умолчанию для этой установки',
		'books.registerSafety':
			'Используйте только host-mounted copied/test books. Приватные пути отправляются в API для регистрации метаданных, но не отображаются обратно в списке книг; счета, транзакции, memos, amounts, uploads и screenshots не собираются.',
		'books.registerSubmit': 'Зарегистрировать метаданные',
		'books.loading': 'Загрузка доступных read-only книг…',
		'books.addBookAction': 'Добавить книгу',
		'books.firstRunAdminTitle': 'Книги ещё не зарегистрированы',
		'books.firstRunAdminMessage':
			'Зарегистрируйте существующую server-mounted GnuCash SQL SQLite книгу, чтобы начать. Web UI сохраняет только app metadata, а GnuCash Desktop остаётся главным редактором.',
		'books.firstRunUserTitle': 'Этой учётной записи книга не назначена',
		'books.firstRunUserMessage':
			'Администратор должен зарегистрировать или назначить книгу, прежде чем эта учётная запись сможет открыть read-only разделы. Для этой роли не показываются поля server path, environment guidance или действия управления.',
		'books.enabledBook': 'Включена',
		'books.disabledBook': 'Отключена',
		'books.notChecked': 'Не проверено',
		'books.statusUnknown': 'Неизвестно',
		'books.status.ready': 'Готово',
		'books.status.available': 'Доступно',
		'books.status.ok': 'OK',
		'books.status.warning': 'Предупреждение',
		'books.status.rejected': 'Отклонено',
		'books.status.unavailable': 'Недоступно',
		'books.status.unknown': 'Неизвестно',
		'books.status.missing_file': 'Источник недоступен',
		'books.status.not_configured': 'Не настроено',
		'books.status.remote_or_unchecked': 'Источник не проверен',
		'books.status.invalid_gnucash_schema': 'Некорректная GnuCash SQL книга',
		'books.status.action_required': 'Требуется действие',
		'books.status.not_checked': 'Не проверено',
		'books.status.disabled': 'Отключено',
		'books.status.failed': 'Ошибка',
		'books.status.empty': 'Пусто',
		'books.status.blocked': 'Заблокировано',
		'books.status.unsupported': 'Не поддерживается',
		'books.problem.admin_required': 'Для управления реестром книг нужны права администратора.',
		'books.problem.preflight_required': 'Сначала выполните успешный preflight и подтвердите metadata-only действие регистрации.',
		'books.problem.preflight_rejected': 'Preflight отклонил этот источник. Книга не зарегистрирована.',
		'books.problem.preflight_token_invalid': 'Preflight token отсутствует, истёк или не соответствует значениям формы. Запустите preflight снова.',
		'books.problem.missing_preflight_token': 'Для этого metadata lifecycle действия нужен свежий preflight token. Запустите preflight снова.',
		'books.problem.invalid_preflight_token': 'Preflight token некорректен, истёк или изменён. Запустите preflight снова.',
		'books.problem.preflight_request_mismatch': 'Форма больше не соответствует preflight token. Запустите preflight снова с тем же названием, базовой валютой и выбором default.',
		'books.problem.preflight_source_mismatch': 'Источник изменился после preflight. Введите смонтированный server-side путь заново и запустите preflight снова.',
		'books.problem.invalid_path': 'Смонтированный server path некорректен. Метаданные реестра книг не изменены.',
		'books.problem.unsupported_source': 'Здесь можно регистрировать только поддержанный server-side SQLite источник внутри разрешённых roots.',
		'books.problem.outside_allowed_roots': 'Источник находится вне разрешённых server-side roots для книг.',
		'books.problem.symlink_forbidden': 'В пути источника есть symlink-компонент, запрещённый для регистрации.',
		'books.problem.missing_file': 'API runtime не нашёл настроенный server-side источник.',
		'books.problem.not_regular_file': 'Настроенный server-side источник не является обычным файлом.',
		'books.problem.permission_denied': 'У API runtime нет прав на чтение этого источника.',
		'books.problem.unsupported_format': 'Здесь поддерживается только существующая server-side GnuCash SQL SQLite книга.',
		'books.problem.invalid_gnucash_schema': 'Настроенная SQLite database не соответствует ожидаемой схеме GnuCash SQL.',
		'books.problem.source_changed': 'Источник изменился после preflight. Запустите preflight снова перед подтверждением регистрации.',
		'books.problem.open_failed': 'API не смог открыть источник в read-only режиме.',
		'books.problem.duplicate_canonical_path': 'Этот canonical source книги уже зарегистрирован в app metadata.',
		'books.problem.book_not_enabled': 'Эта запись metadata отключена. Включите её через свежий preflight перед открытием или назначением default.',
		'books.problem.book_not_healthy': 'Cached health не готов. Сначала успешно выполните health recheck.',
		'books.problem.book_health_not_checked': 'Cached health ещё не проверен. Сначала запустите health recheck.',
		'books.problem.api_unavailable': 'API service недоступен. Метаданные реестра книг не изменены.',
		'books.problem.book_registry_failed': 'Обновление метаданных реестра книг не удалось. Файл GnuCash не изменён.',
		'books.problem.unknown_book_problem': 'API вернул неподдержанный статус книги. Private backend details скрыты.',
		'books.manageSuccessSetDefault': 'Обновлена основная запись app metadata. Бухгалтерские данные GnuCash не изменены.',
		'books.manageSuccessRemoveRegistry': 'Книга удалена только из реестра приложения. Файл GnuCash не удаляется и не изменяется.',
		'books.manageSuccessRecheck': 'Cached health обновлён bounded read-only проверкой. Бухгалтерские данные GnuCash не изменены.',
		'books.manageSuccessRename': 'Обновлены только display metadata. Source file GnuCash не изменён.',
		'books.manageSuccessDisable': 'Эта app registration отключена. Source file GnuCash остаётся на месте и не изменён.',
		'books.manageSuccessEnable': 'App registration включена после свежего matching preflight. Бухгалтерские данные GnuCash не изменены.',
		'books.removeMetadataConfirm':
			'Я понимаю, что удаляется только регистрация/доступ в app metadata. Файл GnuCash не удаляется и не изменяется.',
		'books.reportsLink': 'Открыть отчёты',
		'books.statusDetailsTitle': 'Детали статуса и lifecycle route',
		'books.statusDetailsHelp': 'Откройте Settings and health для path-redacted rename, disable/enable, unregister и recheck действий.',
		'books.renameFuture': 'Rename меняет только display metadata.',
		'books.disableFuture': 'Disable/enable управляет app availability без изменения underlying file.',
		'books.recheckFuture': 'Recheck обновляет typed health/status без регистрации новой книги.',
		'books.backToBooks': 'Назад к книгам',
		'books.newTitle': 'Добавить GnuCash SQL SQLite книгу',
		'books.newSubtitle': 'SSR-first admin flow: объяснить поддержку, выполнить preflight смонтированного источника, затем явно подтвердить регистрацию метаданных.',
		'books.adminRequiredTitle': 'Регистрация книг только для администратора',
		'books.newStep1Title': 'Шаг 1 — поддерживаемый формат источника',
		'books.newStep2Title': 'Шаг 2 — метаданные смонтированного источника',
		'books.newStep3Title': 'Шаг 3 — typed preflight checklist',
		'books.newStep4Title': 'Шаг 4 — подтверждение регистрации',
		'books.supportedFormat': 'Существующая server-side GnuCash SQL SQLite книга только. Файл уже должен быть смонтирован там, где API runtime может его читать.',
		'books.unsupportedFormatWarning':
			'В этом flow нет browser upload, copy, import, XML, compressed XML, conversion, filesystem discovery или source delete.',
		'books.preflightSubmit': 'Запустить preflight',
		'books.preflightReady': 'Preflight готов. Регистрация ещё не выполнена.',
		'books.preflightRejected': 'Preflight отклонил этот источник. Регистрация не выполнена.',
		'books.preflightFormat': 'Определённый формат',
		'books.preflightCheckedAt': 'Время проверки',
		'books.preflightTokenOpaque': 'Preflight token opaque и никогда не помещается в URL. Он отправляется только явной формой подтверждения.',
		'books.confirmRegisterHelp': 'Подтверждайте только если checklist соответствует нужному источнику. Это сохраняет только app registry metadata.',
		'books.confirmRegisterSubmit': 'Подтвердить регистрацию метаданных',
		'books.registrationSuccessTitle': 'Метаданные книги зарегистрированы',
		'books.registrationSuccessMessage': 'App registry обновлён только metadata-only. Source GnuCash file не был удалён, изменён, скопирован или converted.',
		'books.settingsTitle': 'Настройки и health книги',
		'books.settingsSubtitle': 'Path-redacted read-only статус одной зарегистрированной книги. Admin lifecycle actions меняют только app metadata/availability.',
		'books.settingsSummaryTitle': 'Сводка регистрации',
		'books.healthTitle': 'Cached health',
		'books.healthHelp': 'Health fields — typed backend status codes, показанные через локальные тексты; backend messages, private paths и arbitrary payloads не отображаются.',
		'books.healthSafeCode': 'Safe code',
		'books.healthSourceStatus': 'Статус source',
		'books.healthOpenStatus': 'Статус read-only open',
		'books.healthAccountsStatus': 'Статус счетов',
		'books.healthTransactionsStatus': 'Статус транзакций',
		'books.healthReportsStatus': 'Статус отчётов',
		'books.adminLifecycleTitle': 'Admin lifecycle controls',
		'books.adminLifecycleSafety': 'Эти controls вызывают только accepted app metadata lifecycle routes. Они никогда не upload/copy/edit/remove source GnuCash file.',
		'books.renameTitle': 'Display metadata',
		'books.renameHelp': 'Изменить только app display name и base currency metadata.',
		'books.renameAction': 'Сохранить metadata',
		'books.recheckTitle': 'Health recheck',
		'books.recheckHelp': 'Запустить bounded read-only health probe и обновить cached typed status fields.',
		'books.recheckAction': 'Проверить health',
		'books.disableTitle': 'Отключить app availability',
		'books.disableHelp': 'Отключить эту app registration и скрыть read-only open links. Source file GnuCash остаётся на месте и не изменяется.',
		'books.disableMetadataConfirm': 'Я понимаю, что меняется только app registration/availability metadata. Source file GnuCash остаётся на месте, не изменяется и не удаляется.',
		'books.disableAction': 'Отключить registration',
		'books.enableTitle': 'Включить через fresh preflight',
		'books.enablePreflightHelp': 'Введите смонтированный server-side path заново. Сохранённый raw path никогда не показывается; preflight preview остаётся path-redacted и подтверждается отдельно opaque token.',
		'books.enablePath': 'Смонтированный server-side path для этой зарегистрированной книги',
		'books.enablePreflightSubmit': 'Запустить enable preflight',
		'books.enablePreviewTitle': 'Path-redacted preview для enable preflight',
		'books.enableConfirmHelp': 'Подтверждайте enable только если preview соответствует registered display name, base currency и нужному default choice.',
		'books.enableConfirmSubmit': 'Подтвердить enable',
		'books.unregisterTitle': 'Unregister app metadata',
		'books.unregisterHelp': 'Удалить только app registration/access metadata. Source file GnuCash остаётся на месте, не изменяется и не удаляется.',
		'books.section.source': 'Источник',
		'books.section.open': 'Read-only open',
		'books.section.accounts': 'Счета',
		'books.section.transactions': 'Транзакции',
		'books.section.reports': 'Отчёты',
		'books.statusCode.source_ready': 'Источник готов',
		'books.statusCode.open_ready': 'Read-only open готов',
		'books.statusCode.accounts_ready': 'Счета готовы',
		'books.statusCode.transactions_ready': 'Транзакции готовы',
		'books.statusCode.reports_ready': 'Отчёты готовы',
		'books.statusCode.registration_available': 'Регистрация доступна',
		'books.statusCode.already_registered': 'Уже зарегистрировано',
		'books.registrationStatus.available': 'Регистрация metadata доступна для этого preflight token.',
		'books.registrationStatus.alreadyRegistered': 'Этот canonical source уже зарегистрирован, поэтому подтверждение отключено.',
		'books.registrationStatus.unavailable': 'Регистрация metadata недоступна для этого результата preflight.',
		'books.sectionStatus.source.ready': 'Server-side источник прошёл preflight без возврата private path в browser.',
		'books.sectionStatus.source.rejected': 'Server-side источник отклонён. Исправьте host-side storage и запустите preflight снова.',
		'books.sectionStatus.source.unavailable': 'Server-side источник не готов. Проверьте host-side storage и запустите preflight снова.',
		'books.sectionStatus.open.ready': 'API может открыть этот источник в read-only режиме для проверки.',
		'books.sectionStatus.open.rejected': 'API отклонил read-only open check. Регистрация не выполнялась.',
		'books.sectionStatus.open.unavailable': 'Read-only open check недоступен для этого результата preflight.',
		'books.sectionStatus.accounts.ready': 'Accounts adapter готов для read-only views.',
		'books.sectionStatus.accounts.rejected': 'Accounts readiness check отклонён. Данные счетов здесь не показываются.',
		'books.sectionStatus.accounts.unavailable': 'Accounts readiness check недоступен для этого результата preflight.',
		'books.sectionStatus.transactions.ready': 'Transactions adapter готов для read-only views.',
		'books.sectionStatus.transactions.rejected': 'Transactions readiness check отклонён. Данные транзакций здесь не показываются.',
		'books.sectionStatus.transactions.unavailable': 'Transactions readiness check недоступен для этого результата preflight.',
		'books.sectionStatus.reports.ready': 'Reports adapter готов для read-only views.',
		'books.sectionStatus.reports.rejected': 'Reports readiness check отклонён. Данные отчётов здесь не показываются.',
		'books.sectionStatus.reports.unavailable': 'Reports readiness check недоступен для этого результата preflight.',
		'audit.title': 'Write-alpha audit evidence',
		'audit.bannerTitle': 'Write-alpha audit evidence для disposable запусков',
		'audit.bannerMessage':
			'Read-only summary из app metadata для активной книги. Этот pre-alpha операторский вид предназначен только для synthetic/disposable write-alpha запусков; он не production-ready, не security-audited и не является production audit log product.',
		'audit.redactionMessage':
			'Raw request payloads, backup paths, private file paths, account names, memos и amounts не показываются.',
		'audit.activeBook': 'Активная книга',
		'audit.noAccessibleBook': 'Нет доступной книги',
		'audit.reviewBooks': 'Проверить книги',
		'audit.filtersLabel': 'Фильтры audit summary',
		'audit.allActions': 'Все действия',
		'audit.create': 'Create',
		'audit.patch': 'PATCH',
		'audit.delete': 'DELETE',
		'audit.allResults': 'Все результаты',
		'audit.success': 'Success',
		'audit.failed': 'Failed',
		'audit.started': 'Started',
		'audit.unknown': 'Unknown',
		'audit.action': 'Action',
		'audit.result': 'Result',
		'audit.sinceIso': 'Since ISO',
		'audit.untilIso': 'Until ISO',
		'audit.applyFilters': 'Применить фильтры',
		'audit.clearFilters': 'Сбросить фильтры',
		'audit.limit': 'Строк на странице',
		'audit.countsLabel': 'Счётчики audit summary',
		'audit.filteredRows': 'Отфильтрованные строки',
		'audit.returnedCount': 'Вернулось: {count}',
		'audit.actions': 'Действия',
		'audit.results': 'Результаты',
		'audit.window': 'Окно времени',
		'audit.ownership': 'Ownership',
		'audit.ownedCreated': 'write-alpha-created',
		'audit.nonOwnedRejected': 'non-owned rejected',
		'audit.lastMutation': 'Последняя mutation',
		'audit.requestedWindow': 'Запрошено: {since} → {until}',
		'audit.returnedWindow': 'Вернулось: {oldest} → {newest}',
		'audit.noStart': 'Без начала',
		'audit.noEnd': 'Без окончания',
		'audit.none': 'нет',
		'audit.emptyTitle': 'Нет write-alpha audit rows',
		'audit.emptyMessage':
			'Нет create/PATCH/DELETE write-alpha записей app-metadata audit, подходящих под текущие фильтры активной книги. Ожидайте evidence здесь только после явных disposable APP_ENV=test write-alpha smoke-запусков.',
		'audit.browseTransactions': 'Открыть транзакции',
		'audit.showingEntries':
			'Показано {returned} из {total} redacted audit entries. Backup представлен только как present/missing.',
		'audit.pageStatus': 'Offset страницы {offset}; ограниченный размер страницы {limit}.',
		'audit.paginationLabel': 'Пагинация audit summary',
		'audit.paginationSummary': 'Страница review: offset {offset}, limit {limit}. Фильтры остаются только в URL.',
		'audit.previousPage': 'Предыдущая страница',
		'audit.nextPage': 'Следующая страница',
		'audit.timestamp': 'Timestamp',
		'audit.txnPrefix': 'Txn prefix',
		'audit.backupSafeError': 'Backup / safe error',
		'audit.backupPresent': 'Backup: present',
		'audit.backupMissing': 'Backup: not recorded',
		'audit.backupRef': 'Backup ref',
		'audit.limitations': 'Ограничения',
		'writeMode.title': 'Экспериментальный controlled write mode — не часть MVP v0.1',
		'writeMode.message':
			'MVP v0.1 по умолчанию остаётся read-only, а GNUCASH_WRITES_ENABLED=false — безопасное значение по умолчанию. Эта write form — только экспериментальная post-MVP функциональность, не production-ready и не security-audited; она должна быть доступна только при явном APP_ENV=test disposable запуске.',
		'writeMode.desktop': 'GnuCash Desktop остаётся главным редактором.',
		'writeMode.disposableOnly':
			'Используйте только outside-git copied/restorable test book в ignored runtime storage; никогда не указывайте original/source book или единственную существующую копию.',
		'writeMode.createOnlyDogfood':
			'Для copied-book dogfood остановитесь после dry-run, если нет явного решения продолжить с одной небольшой CREATE test transaction. Не используйте эту форму для production entries, PATCH или DELETE.',
		'writeMode.evidence': 'Проверьте independent backup, restore plan, audit row, app backup evidence и lock-release evidence перед тем, как считать write-alpha CREATE запуск завершённым.',
		'writeMode.staleLock':
			'Если остался stale lock file, сначала остановите runtime и следуйте recovery runbook; не считайте host permission error признаком активного writer.',
		'writeMode.neverRealBook': 'Никогда не используйте этот экспериментальный path с единственной реальной финансовой книгой.',
		'writeMode.finalConfirm':
			'Последнее предупреждение: это experimental post-MVP действие запишет одну test transaction в copied/restorable книгу GnuCash. Продолжайте только в APP_ENV=test, когда original untouched, используется outside-git copied test book, есть independent backup, restore plan, audit, app backup и lock-release checks. Никогда не используйте source/original, only copy или production book. Продолжить?',
		'writeMode.acknowledgement':
			'Я понимаю, что controlled writes — экспериментальная post-MVP функциональность, MVP v0.1 остаётся read-only по умолчанию, GNUCASH_WRITES_ENABLED=false — безопасное значение по умолчанию, GnuCash Desktop остаётся главным редактором, и я использую только outside-git copied/restorable test book, original untouched, одну CREATE test transaction, independent backup, restore plan, audit, app backup и lock-release checks. Это не для production use.',
		'writeMode.kicker': 'Controlled write',
		'writeMode.newTransactionTitle': 'Новая транзакция',
		'writeMode.newTransactionHelp': 'Создаёт только одну простую two-split test transaction для copied-book dogfood. Это не для production entries; проверьте backup/restore evidence до и после финальной записи.',
		'transactions.filters.title': 'Фильтры транзакций',
		'transactions.filters.subtitle':
			'Сужают read-only список транзакций и CSV export; фильтры никогда не изменяют вашу книгу GnuCash.',
		'transactions.filters.filteredView': 'Отфильтрованный вид',
		'transactions.filters.datePresets': 'Быстрые даты',
		'transactions.filters.datePresetAria': 'Быстрые диапазоны дат транзакций',
		'transactions.filters.datePresetHelp':
			'Быстрые даты меняют только обычные фильтры date_from/date_to; список и CSV export остаются read-only и используют тот же отфильтрованный вид.',
		'transactions.filters.activeSummaryTitle': 'Активные фильтры применяются к списку и CSV export',
		'transactions.filters.search': 'Поиск',
		'transactions.filters.searchPlaceholder': 'Описание, notes или split memo...',
		'transactions.filters.account': 'Счёт',
		'transactions.filters.accountScope': 'Область счёта',
		'transactions.filters.accountId': 'ID счёта',
		'transactions.filters.lockedAccountHelp':
			'Детальная страница счёта зафиксирована на этом счёте; остальные фильтры сужают только транзакции этого счёта.',
		'transactions.filters.allAccounts': 'Все счета',
		'transactions.filters.customDateRange': 'Свой диапазон дат',
		'transactions.filters.from': 'С',
		'transactions.filters.to': 'По',
		'transactions.filters.startDateError': 'Дата начала должна быть раньше даты окончания или равна ей.',
		'transactions.filters.state': 'Состояние',
		'transactions.filters.anyState': 'Любое состояние',
		'transactions.filters.stateUnreconciled': 'Не сверено',
		'transactions.filters.stateCleared': 'Очищено',
		'transactions.filters.stateReconciled': 'Сверено',
		'transactions.filters.stateVoided': 'Аннулировано',
		'transactions.filters.stateHelp':
			'Фильтрует по состоянию сверки split в GnuCash; транзакции не редактируются.',
		'transactions.filters.minAmount': 'Мин. сумма',
		'transactions.filters.maxAmount': 'Макс. сумма',
		'transactions.filters.amountError': 'Минимальная сумма должна быть меньше максимальной или равна ей.',
		'transactions.filters.submit': 'Фильтровать',
		'transactions.filters.clear': 'Сбросить фильтры',
		'transactions.filters.summary.search': 'Поиск',
		'transactions.filters.summary.account': 'Счёт',
		'transactions.filters.summary.dates': 'Даты',
		'transactions.filters.summary.from': 'С',
		'transactions.filters.summary.to': 'По',
		'transactions.filters.summary.amount': 'Сумма',
		'transactions.filters.summary.minAmount': 'Мин. сумма',
		'transactions.filters.summary.maxAmount': 'Макс. сумма',
		'transactions.filters.summary.state': 'Состояние',
		'transactions.listStatus.title': 'Текущий read-only вид',
		'transactions.listStatus.order': 'Сортировка: новые транзакции сначала по дате.',
		'transactions.listStatus.pageRange': 'Показаны {start}–{end} из {total} подходящих транзакций на этой странице.',
		'transactions.listStatus.emptyPage': 'На этой странице нет подходящих транзакций.',
		'transactions.listStatus.filtersApplied': '{count} активных {filterLabel}; список, пагинация и CSV export используют те же URL-фильтры.',
		'transactions.listStatus.noFilters': 'Активных фильтров транзакций нет; CSV export использует текущий нефильтрованный read-only вид.',
		'transactions.listStatus.exportParity': 'CSV export игнорирует page offset, начинает с первой подходящей строки и ограничен 10 000 строк.',
		'transactions.explorer.formHelp':
			'URL — источник истины. Форма отправляет настоящий GET на /transactions; изменение фильтров, sort или page_size сбрасывает cursor.',
		'transactions.explorer.datePresetHelp': 'Быстрые даты задают парные date_from/date_to и сбрасывают cursor canonical explorer.',
		'transactions.explorer.dateTextLegend': 'Даты, текст и состояние',
		'transactions.explorer.scopeLegend': 'Счета или type scope',
		'transactions.explorer.scopeHelp': 'Выберите до 20 счетов или режим income/expense. Эти режимы взаимоисключающие.',
		'transactions.explorer.accountIds': 'Счета (до 20)',
		'transactions.explorer.accountIdsHelp': 'Ctrl/Cmd выбирает несколько счетов. Amount и direction используют точную сумму split выбранных счетов.',
		'transactions.explorer.accountOptionsLimited': 'Показан только ограниченный список счетов; для редких счетов используйте canonical URL с account_ids.',
		'transactions.explorer.accountsDisabledByType': 'Выбор счетов отключён, пока активен режим income/expense.',
		'transactions.explorer.type': 'Type mode',
		'transactions.explorer.typeAny': 'Без type mode',
		'transactions.explorer.typeIncome': 'Доходы',
		'transactions.explorer.typeExpense': 'Расходы',
		'transactions.explorer.direction': 'Direction',
		'transactions.explorer.directionAny': 'Любое направление',
		'transactions.explorer.directionIncrease': 'Увеличение выбранных счетов',
		'transactions.explorer.directionDecrease': 'Уменьшение выбранных счетов',
		'transactions.explorer.directionHelp': 'Direction доступен только с account_ids; он не совмещается с income/expense type mode.',
		'transactions.explorer.amountPagingLegend': 'Точная сумма и pagination controls',
		'transactions.explorer.amountPagingHelp': 'Amount filters требуют account_ids или type mode, используют canonical Decimal strings и не используют float arithmetic. page_size принимает 1–100.',
		'transactions.explorer.sort': 'Сортировка',
		'transactions.explorer.sortDateDesc': 'Новые сначала',
		'transactions.explorer.sortDateAsc': 'Старые сначала',
		'transactions.explorer.pageSize': 'Размер страницы',
		'transactions.explorer.reset': 'Сбросить explorer',
		'transactions.explorer.removeFilter': 'Убрать фильтр',
		'transactions.explorer.cursorChip': 'Активен cursor пагинации',
		'transactions.explorer.dateRangeRequiredTitle': 'Выберите ограниченный диапазон дат',
		'transactions.explorer.dateRangeRequiredMessage':
			'Задайте date_from и date_to (до 366 дней), прежде чем загружать read-only explorer. Reset/default route не запрашивает unbounded список транзакций.',
		'transactions.explorer.readyTitle': 'Страница explorer загружена',
		'transactions.explorer.readyMessage': 'Explorer вернул ограниченную cursor page для активных фильтров.',
		'transactions.explorer.trueEmptyTitle': 'Нет транзакций для этих точных фильтров',
		'transactions.explorer.trueEmptyMessage': 'Explorer доказал пустой результат для этого URL. Сбросьте фильтры или расширьте даты/счета/type/search.',
		'transactions.explorer.scanWindowEmptyTitle': 'В этом scan window нет строк',
		'transactions.explorer.scanWindowEmptyMessage': 'Backend остановился на bounded scan window до полного доказательства результата. Продолжите pagination или сузьте фильтры.',
		'transactions.explorer.scanLimitedTitle': 'Частичный bounded scan',
		'transactions.explorer.scanLimitedMessage': 'Эта страница валидна, но scan-limited. Продолжите opaque cursor или сузьте фильтры.',
		'transactions.explorer.endTitle': 'Конец cursor results',
		'transactions.explorer.endMessage': 'Для этого cursor дополнительных строк не вернулось. Сбросьте pagination на первую страницу или измените фильтры.',
		'transactions.explorer.invalidFilterTitle': 'Некорректные фильтры explorer',
		'transactions.explorer.invalidFilterMessage': 'Explorer отклонил комбинацию фильтров до рендера страницы транзакций. Исправьте URL или сбросьте фильтры.',
		'transactions.explorer.staleCursorTitle': 'Cursor пагинации устарел',
		'transactions.explorer.staleCursorMessage': 'Opaque cursor больше не соответствует фильтрам или signing window. Сбросьте pagination и повторите.',
		'transactions.explorer.loadFailedTitle': 'Transactions explorer завершился ошибкой',
		'transactions.explorer.loadFailedMessage': 'Read-only explorer request безопасно завершился ошибкой. Backend details, paths и private sentinels скрыты.',
		'transactions.explorer.unknownFailureTitle': 'Transactions explorer недоступен',
		'transactions.explorer.unknownFailureMessage': 'API вернул неподдержанную форму ошибки. Неизвестные backend details скрыты.',
		'transactions.explorer.legacyCompatibility': 'Активен legacy compatibility mode для /transactions URL с account_id, limit/offset или one-sided date параметрами. Новые explorer ссылки используют account_ids, page_size и cursor.',
		'transactions.explorer.legacyOffsetConflict': 'Legacy offset pagination нельзя смешивать с advanced explorer fields. Уберите offset или сбросьте canonical explorer URL.',
		'transactions.explorer.returnedStatus': 'Вернулось {count} строк(и) на этой cursor page; запрошено page_size={pageSize}.',
		'transactions.explorer.filtersApplied': '{count} активных {filterLabel}; URL, форма, return link деталей и cursor pagination сохраняют их.',
		'transactions.explorer.noFilters': 'Advanced explorer filters не активны; URL всё равно фиксирует sort и page_size.',
		'transactions.explorer.order': 'Сортировка {sort}; date транзакции плюс GUID — стабильный cursor key.',
		'transactions.explorer.noTotal': 'Total count и номер страницы не придумываются; навигация использует только opaque Previous/Next/Continue cursors.',
		'transactions.explorer.limitationsTitle': 'Ограничения explorer',
		'transactions.explorer.resetPagination': 'Сбросить pagination',
		'transactions.explorer.paginationLabel': 'Cursor pagination transactions explorer',
		'transactions.explorer.cursorPagination': 'Cursor pagination: без page numbers и fabricated totals.',
		'transactions.explorer.previous': 'Назад',
		'transactions.explorer.next': 'Вперёд',
		'transactions.explorer.continue': 'Продолжить',
		'transactions.writeAlphaHistoryBadge': 'write-alpha-created',
		'transactions.writeAlphaHistoryTitle':
			'Создано по app metadata write-alpha. Это только synthetic/disposable подсказка истории; backend ownership guards остаются главным enforcement.',
		'transactions.listStatus.writeAlphaHint':
			'{count} строк(и) на этой странице отмечены app metadata как write-alpha-created; это только synthetic/disposable подсказка истории. Backend ownership guards остаются главным enforcement, а writes по умолчанию отключены.',
		'transactions.listStatus.writeAlphaFollowupTitle': 'Новая synthetic CREATE follow-up',
		'transactions.listStatus.writeAlphaFollowupHelp':
			'После read-back synthetic/disposable CREATE новая synthetic/disposable транзакция появляется в обычной истории только когда read-only API вернул строку, а app metadata пометила GUID. Она не закрепляется поверх фильтров; если badge не виден, сбросьте фильтры или проверьте redacted audit evidence. Сам badge не даёт разрешение на запись.',
		'transactions.listStatus.writeAlphaAuditLink': 'Открыть redacted write-alpha audit evidence',
		'transactions.export.button': 'Экспорт CSV',
		'transactions.export.buttonWithFilters': 'Экспорт CSV ({count} {filterLabel})',
		'transactions.export.statusFiltered':
			'Экспортирует текущий read-only отфильтрованный вид, максимум 10 000 строк. Большие экспорты выполняются синхронно; сузьте фильтры, если запрос истёк по времени или export был обрезан.',
		'transactions.export.statusUnfiltered':
			'Экспортирует этот read-only список транзакций, максимум 10 000 строк. Большие экспорты выполняются синхронно; сузьте фильтры, если запрос истёк по времени или export был обрезан.',
		'transactions.export.emptyStatus':
			'Текущий export содержал бы только CSV header, потому что подходящие транзакции не видны.',
		'transactions.export.countStatus':
			'Текущих подходящих строк до ограничения: {total}. CSV amounts остаются string values; currency conversion не выполняется.',
		'transactions.export.truncatedStatus':
			'Текущих подходящих строк до ограничения: {total}; export включит только первые 10 000 строк. Сузьте фильтры для полного поднабора.',
		'transactions.export.accountButton': 'Экспорт CSV по счёту',
		'transactions.export.accountButtonWithFilters': 'Экспорт CSV по счёту ({count} {filterLabel})',
		'transactions.export.accountStatus':
			'Экспортирует read-only отфильтрованный вид в рамках этого счёта с теми же фильтрами поиска/дат/сумм/состояния.',
		'transactions.export.explorerDisabled':
			'CSV export отключён для advanced explorer filters, потому что exact legacy CSV parity не доказана для account_ids, type, direction, query, cursor и scan-limited pages.',
		'transactions.export.explorerHonesty':
			'Используйте legacy account_id/limit URLs для существующего CSV endpoint; advanced explorer CSV остаётся отключённым до exact parity.',
		'scheduled.title': 'Плановые транзакции',
		'scheduled.kicker': 'Read-only просмотр плановых транзакций',
		'scheduled.subtitle':
			'Безопасные сводные метаданные из активной книги GnuCash. Эта pre-alpha страница не создаёт, не редактирует, не удаляет и не рассчитывает будущие выполнения плановых транзакций. GnuCash Desktop остаётся главным редактором.',
		'scheduled.activeBook': 'Активная книга',
		'scheduled.recurringMetadata': 'Recurring metadata',
		'scheduled.metadataHelp':
			'Показываются только безопасные поля расписаний. Детали template split и приватный raw SQL не раскрываются. Фильтры и сортировка — только URL display controls; они не сохраняют scheduled metadata в browser storage.',
		'scheduled.readOnlyBadge': 'Read-only · без редактора расписаний',
		'scheduled.statusFilter': 'Фильтр статуса',
		'scheduled.templateFilter': 'Фильтр template metadata',
		'scheduled.sortDisplay': 'Сортировка отображения',
		'scheduled.all': 'Все',
		'scheduled.enabled': 'Включено',
		'scheduled.disabled': 'Выключено',
		'scheduled.templatePresent': 'Template есть',
		'scheduled.noTemplateReference': 'Без ссылки на template',
		'scheduled.startDate': 'Дата начала',
		'scheduled.endDate': 'Дата окончания',
		'scheduled.lastOccurred': 'Последнее выполнение',
		'scheduled.name': 'Название',
		'scheduled.enabledFirst': 'Включённые первыми',
		'scheduled.shownStatus':
			'Показано {shown} из {total} безопасных строк scheduled metadata. Template split amounts, accounts, memos, transaction descriptions и raw SQL не раскрываются.',
		'scheduled.clearFilters': 'Сбросить фильтры плановых',
		'scheduled.unnamed': 'Плановая транзакция без названия',
		'scheduled.templateAccount': 'Template account',
		'scheduled.templateReferenceStatus': 'Статус template reference',
		'scheduled.templatePresentRedacted': 'Есть; детали split скрыты',
		'scheduled.templateNotPresentRedacted': 'Template reference не найден; split-детали не выводятся',
		'scheduled.occurrences': 'Повторы',
		'scheduled.occurrencesValue': 'всего {total} · осталось {remaining}',
		'scheduled.autoCreateNotify': 'Auto-create / notify',
		'scheduled.advanceDays': 'Advance days',
		'scheduled.advanceDaysValue': 'создать {create} · уведомить {notify}',
		'scheduled.recurrenceMetadata': 'Recurrence metadata',
		'scheduled.noRecurrenceMetadata': 'Безопасные recurrence metadata недоступны через adapter.',
		'scheduled.noMatchesTitle': 'Плановые транзакции не подходят под эти display filters',
		'scheduled.noMatchesMessage':
			'В активной книге есть scheduled metadata, но текущие URL-only фильтры скрывают все строки. Сбросьте фильтры, чтобы вернуться к полному безопасному read-only виду метаданных.',
		'scheduled.noMatchesAria': 'Плановые транзакции не подходят под display filters',
		'scheduled.emptyTitle': 'Плановые транзакции не найдены',
		'scheduled.emptyMessage':
			'Для этой книги через безопасный read-only adapter не доступны плановые транзакции. Если книга использует плановые транзакции, управляйте ими и проверяйте их в GnuCash Desktop.',
		'scheduled.emptyAria': 'Плановые транзакции не найдены',
		'scheduled.browseTransactions': 'Открыть транзакции',
		'scheduled.reviewBooks': 'Проверить книги',
		'scheduled.notConfigured': 'Не настроено',
		'scheduled.yes': 'Да',
		'scheduled.no': 'Нет',
		'scheduled.recurrenceEvery': 'каждые {count}',
		'scheduled.recurrenceFrom': 'с {date}',
		'scheduled.recurrenceWeekend': 'выходные: {value}',
		'scheduled.recurrenceUnavailable': 'Raw recurrence metadata недоступны'
	}
};
