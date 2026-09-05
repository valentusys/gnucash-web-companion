export type BookOperatorGuidance = {
	metadata_source: string;
	data_access: string;
	read_only_default: boolean;
	private_path_redacted: boolean;
	storage_type_label: string;
	unsupported_management_actions: string[];
	message: string;
};

export type BookStorageDiagnostics = {
	status: 'available' | 'missing_file' | 'not_configured' | 'remote_or_unchecked' | string;
	configured: boolean;
	checked: boolean;
	safe_summary: string;
	safe_next_actions: string[];
};

export type CurrentUser = {
	id: number;
	username: string;
	display_name: string;
	is_admin: boolean;
};

export type AdminProblemCode =
	| 'username_invalid'
	| 'username_taken'
	| 'display_name_invalid'
	| 'password_policy'
	| 'user_not_found'
	| 'user_disabled'
	| 'session_changed'
	| 'self_disable_forbidden'
	| 'last_enabled_admin'
	| 'book_not_assignable'
	| 'admin_required'
	| 'api_unavailable'
	| 'unknown_admin_problem';

export type AdminUserStateFilter = 'all' | 'enabled' | 'disabled';

export type AdminBookAccessRole = 'owner' | 'editor' | 'viewer';

export type AdminUserSummary = {
	id: number;
	username: string;
	display_name: string;
	is_admin: boolean;
	is_enabled: boolean;
	assignment_count: number;
	created_at: string;
	updated_at: string;
};

export type AdminUserList = {
	items: AdminUserSummary[];
	total_count: number;
	limit: number;
	offset: number;
	has_next: boolean;
};

export type AdminBookOption = {
	id: number;
	name: string;
	is_default: boolean;
};

export type AdminBookOptionList = {
	items: AdminBookOption[];
	total_count: number;
	limit: number;
	offset: number;
	has_next: boolean;
};

export type AdminBookAccess = {
	book_id: number;
	book_name: string;
	is_default: boolean;
	role: AdminBookAccessRole;
};

export type AdminUserDetail = AdminUserSummary & {
	assignments: AdminBookAccess[];
};

export type AdminPasswordResetResult = {
	status: 'password_reset';
	subject_user_id: number;
	session_invalidated: boolean;
};

export type BookProblemCode =
	| 'admin_required'
	| 'preflight_required'
	| 'preflight_rejected'
	| 'preflight_token_invalid'
	| 'missing_preflight_token'
	| 'invalid_preflight_token'
	| 'preflight_request_mismatch'
	| 'preflight_source_mismatch'
	| 'invalid_path'
	| 'unsupported_source'
	| 'outside_allowed_roots'
	| 'symlink_forbidden'
	| 'missing_file'
	| 'not_regular_file'
	| 'permission_denied'
	| 'unsupported_format'
	| 'invalid_gnucash_schema'
	| 'source_changed'
	| 'open_failed'
	| 'duplicate_canonical_path'
	| 'book_not_enabled'
	| 'book_not_healthy'
	| 'book_health_not_checked'
	| 'api_unavailable'
	| 'book_registry_failed'
	| 'unknown_book_problem';

export type BookProblemDTO = {
	safe_code: BookProblemCode;
	safe_message?: string;
};

export type BookReadinessCode =
	| 'ready'
	| 'source_ready'
	| 'open_ready'
	| 'accounts_ready'
	| 'transactions_ready'
	| 'reports_ready'
	| 'registration_available'
	| 'already_registered'
	| string;

export type BookPreflightSafeCode = BookProblemCode | BookReadinessCode;

export type BookSectionStatusCode =
	| 'source_ready'
	| 'open_ready'
	| 'accounts_ready'
	| 'transactions_ready'
	| 'reports_ready'
	| 'registration_available'
	| 'already_registered'
	| 'duplicate_canonical_path'
	| string;

export type BookSectionStatus = {
	status: 'ready' | 'available' | 'ok' | 'warning' | 'rejected' | 'unavailable' | 'unknown' | string;
	safe_code: BookSectionStatusCode;
	message: string | null;
	retryable: boolean;
};

export type BookCapabilityFlags = {
	read_only?: boolean;
	can_register_metadata: boolean;
	can_open_accounts: boolean;
	can_open_transactions: boolean;
	can_open_reports: boolean;
	can_upload: false;
	can_edit: false;
	can_delete: false;
	can_edit_gnucash?: false;
	can_delete_source?: false;
};

export type BookHealth = {
	status: string;
	safe_code: string;
	checked_at: string | null;
	last_successful_at: string | null;
	source_status: string;
	open_status: string;
	accounts_status: string;
	transactions_status: string;
	reports_status: string;
};

export type BookPreflightRequest = {
	name: string;
	uri_or_path: string;
	storage_type: 'sqlite';
	base_currency: string;
	make_default: boolean;
};

export type BookPreflightResponse = {
	status: 'ready' | 'rejected';
	format: 'gnucash_sqlite' | string;
	preflight_token: string;
	registration_status: BookSectionStatus;
	source_status: BookSectionStatus;
	open_status: BookSectionStatus;
	accounts: BookSectionStatus;
	transactions: BookSectionStatus;
	reports: BookSectionStatus;
	capabilities: BookCapabilityFlags;
	checked_at: string;
	safe_code: BookPreflightSafeCode;
	message?: string | null;
	read_counters?: Record<string, number>;
};

export type Book = {
	id: number;
	name: string;
	storage_type: string;
	base_currency: string;
	is_default: boolean;
	is_enabled?: boolean;
	is_archived: boolean;
	created_at?: string;
	updated_at?: string;
	access_role: 'owner' | 'editor' | 'viewer' | null;
	access_role_label: string;
	access_role_description: string;
	read_only: boolean;
	status: string;
	status_severity: 'ok' | 'warning' | 'action_required' | string;
	access_status: string;
	can_open_read_only_views: boolean;
	health?: BookHealth;
	capabilities?: BookCapabilityFlags;
	storage_diagnostics: BookStorageDiagnostics;
	management_actions: Array<
		| 'set_default'
		| 'remove_from_registry'
		| 'rename'
		| 'disable'
		| 'enable'
		| 'recheck'
		| string
	>;
	operator_guidance: BookOperatorGuidance;
};

export type Account = {
	id: string;
	name: string;
	display_name?: string | null;
	full_name: string;
	type: string;
	currency: string;
	balance: string;
	placeholder: boolean;
	hidden: boolean;
	parent_id: string | null;
};

export type AccountTreeNode = Account & {
	children: AccountTreeNode[];
};

export type AccountExplorerPathSegment = {
	id: string;
	name: string;
	display_name?: string | null;
};

export type CommodityRef = {
	namespace: string;
	mnemonic: string;
};

export type AccountOptionsPurpose = 'transactions_filter' | 'transaction_create_preview';

export type AccountOption = {
	id: string;
	parent_id: string | null;
	name: string;
	display_name?: string | null;
	full_name: string;
	type: string;
	commodity: CommodityRef;
	currency: string;
	hidden: boolean;
	placeholder: boolean;
	selectable: boolean;
};

export type AccountOptionsScan = {
	candidate_accounts: number;
	matched_accounts: number;
	returned_items: number;
	query_count: number;
	serialized_bytes: number;
	exhausted: boolean;
	limits: Record<string, number>;
};

export type AccountOptionsResponse = {
	book_id: number;
	purpose: 'transactions_filter' | 'transaction_create_preview';
	normalized_filters: Record<string, unknown>;
	items: AccountOption[];
	limit: number;
	returned_count: number;
	next_cursor: string | null;
	partial_failure: boolean;
	error_code: string | null;
	scan: AccountOptionsScan;
	balance_basis: 'not_loaded';
	includes_currency_conversion: false;
	limitations: string[];
};

export type AccountCommodityAmount = {
	amount: string;
	commodity: CommodityRef;
};

export type AccountExplorerNode = {
	id: string;
	source_parent_id: string | null;
	parent_id: string | null;
	root_id: string;
	path: AccountExplorerPathSegment[];
	full_path: string;
	depth: number;
	name: string;
	display_name?: string | null;
	type: string;
	commodity: CommodityRef;
	hidden: boolean;
	placeholder: boolean;
	child_count: number;
	direct_balance: AccountCommodityAmount;
	recursive_balances: AccountCommodityAmount[];
	match_state: 'match' | 'ancestor_context' | string;
	structure_status: 'root' | 'normal' | 'orphan_promoted' | 'cycle_broken_root' | 'cycle_member' | string;
};

export type AccountExplorerScan = {
	candidate_accounts: number;
	returned_nodes: number;
	split_rows: number;
	split_aggregate_rows: number;
	query_count: number;
	rollup_bucket_cells: number;
	serialized_bytes: number;
	exhausted: boolean;
	limits: Record<string, number>;
};

export type AccountExplorerResponse = {
	book_id: number;
	mode: 'tree' | 'flat' | string;
	normalized_filters: Record<string, unknown>;
	root_ids: string[];
	nodes: AccountExplorerNode[];
	returned_count: number;
	scan: AccountExplorerScan;
	balance_basis: 'native_commodity_account_natural_sign' | string;
	includes_currency_conversion: boolean;
	limitations: string[];
};

export type AccountOverviewChild = Omit<AccountExplorerNode, 'match_state'>;

export type AccountOverview = Omit<AccountExplorerNode, 'match_state' | 'child_count'> & {
	breadcrumbs: AccountExplorerPathSegment[];
	subtree_account_count: number;
	child_count: number;
	children: AccountOverviewChild[];
	children_returned: number;
	children_truncated: boolean;
	scan: AccountExplorerScan;
	balance_basis: 'native_commodity_account_natural_sign' | string;
	includes_currency_conversion: boolean;
	limitations: string[];
};

export type AccountActivityRecentTransaction = {
	id: string;
	date: string;
	description: string;
	matched_quantity: AccountCommodityAmount;
	counter_account_name: string;
	direction?: TransactionDirection;
	is_write_alpha_owned: boolean;
};

export type AccountActivitySectionStatus = {
	section: 'change' | 'recent_transactions' | string;
	status: 'ok' | 'empty' | 'error' | string;
	detail: string | null;
};

export type AccountActivityScan = {
	selected_accounts: number;
	change_split_rows: number;
	recent_transaction_objects: number;
	recent_split_rows: number;
	query_count: number;
	serialized_bytes: number;
	limits: Record<string, number>;
};

export type AccountActivity = {
	book_id: number;
	account_id: string;
	date_from: string;
	date_to: string;
	scope: 'direct_account' | string;
	commodity: CommodityRef;
	change: AccountCommodityAmount | null;
	inflow: AccountCommodityAmount | null;
	outflow: AccountCommodityAmount | null;
	flow_status: 'not_applicable_for_generic_account' | string;
	recent_transactions: AccountActivityRecentTransaction[];
	limit: number;
	returned_count: number;
	has_more: boolean;
	transaction_explorer_compatible: boolean;
	partial_failure: boolean;
	section_statuses: AccountActivitySectionStatus[];
	scan: AccountActivityScan;
	limitations: string[];
};

export type TransactionSplit = {
	account_id: string;
	account_name: string;
	account_display_name?: string | null;
	memo: string;
	reconcile_state?: string;
	amount: string;
	currency: string;
};

export type MoneyDTO = {
	amount: string;
	currency: string;
};

export type TransactionDirectionEntry = {
	account_id: string;
	display_name: string;
	full_name: string;
	value: string;
	split_count: number;
};

export type TransactionDirection = {
	status: 'resolved' | 'composite' | 'ambiguous';
	reason:
		| 'balanced'
		| 'multiple_accounts'
		| 'no_nonzero_splits'
		| 'single_sided'
		| 'unbalanced'
		| 'account_on_both_sides';
	currency: string;
	from_accounts: TransactionDirectionEntry[];
	to_accounts: TransactionDirectionEntry[];
};

export type TransactionListItem = {
	id: string;
	date: string;
	description: string;
	amount: string;
	currency: string;
	account_id: string;
	account_name: string;
	account_display_name?: string | null;
	counter_account_name: string;
	direction?: TransactionDirection;
	representative_amount?: MoneyDTO;
	representative_account?: { id: string; name: string; display_name?: string | null; full_name?: string | null } | null;
	matched_amount?: MoneyDTO | null;
	amount_basis?: 'selected_accounts' | 'income' | 'expense' | 'representative_split' | string;
	matched_account_ids?: string[];
	is_write_alpha_owned?: boolean;
};

// The recent-report endpoint is NOT an explorer item. Do not accept explorer-only fields.
export type RecentTransaction = Pick<TransactionListItem,
    'id' | 'date' | 'description' | 'amount' | 'currency' | 'account_id' | 'account_name' |
    'account_display_name' | 'counter_account_name' | 'direction' | 'is_write_alpha_owned'
> & { amount_is_unambiguous: boolean };

export type TransactionDetail = {
	id: string;
	date: string;
	description: string;
	currency: string;
	splits: TransactionSplit[];
	is_write_alpha_owned?: boolean;
};

export type ReportingCurrencyCandidate = {
	currency: string;
	distinct_transaction_count: number;
	nonzero_split_count: number;
	active_leaf_account_count: number;
	eligible_leaf_account_count: number;
};

export type ReportingCurrencyResolution = {
	status: 'ready' | 'setup_required';
	source: 'configured' | 'detected' | 'none';
	reason: 'configured_valid' | 'dominant_detected' | 'no_eligible_currency' | 'dominance_tie';
	configured_currency: string | null;
	configured_currency_status: 'valid' | 'missing' | 'xxx' | 'absent' | 'template_only' | 'non_monetary' | 'inactive';
	selected_currency: string | null;
	candidates: ReportingCurrencyCandidate[];
	excluded_currencies: string[];
	non_currency_commodities_excluded: boolean;
};

export type ScheduledTransactionRecurrence = {
	period_type: string;
	multiplier: number | null;
	period_start: string | null;
	weekend_adjust: string;
};

export type ScheduledTransactionForecast = {
	status: 'ready' | 'disabled' | 'exhausted' | 'unavailable';
	reason: 'scheduled_recurrence_invalid_metadata' | null;
	as_of_date: string;
	next_due_date: string | null;
	is_overdue: boolean;
	upcoming_7_days: string[];
	upcoming_30_days: string[];
};

export type ScheduledTransactionAmountReason =
	| 'no_template_reference'
	| 'template_data_unavailable'
	| 'template_variables_unresolved'
	| 'template_shape_unsupported'
	| 'template_unbalanced'
	| 'currency_unavailable'
	| 'forecast_unavailable';

export type ScheduledTransactionAmount = {
	status: 'resolved' | 'unresolved' | 'not_available';
	amount: string | null;
	currency: string | null;
	unresolved_formula_count: number;
	reason: ScheduledTransactionAmountReason | null;
};

export type ScheduledTransaction = {
	id: string;
	name: string;
	enabled: boolean;
	start_date: string | null;
	end_date: string | null;
	last_occurred: string | null;
	num_occurrences: number | null;
	remaining_occurrences: number | null;
	auto_create: boolean;
	auto_notify: boolean;
	advance_create_days: number | null;
	advance_notify_days: number | null;
	instance_count: number | null;
	has_template_account: boolean;
	template_reference_status: string;
	recurrence: ScheduledTransactionRecurrence[];
	forecast: ScheduledTransactionForecast;
	amount: ScheduledTransactionAmount;
	new_transactions_created: 0;
	limitations: string[];
};

export type PaginatedTransactions = {
	items: TransactionListItem[];
	limit: number;
	offset: number;
	total: number;
};

export type TransactionExplorerSort = 'date_desc' | 'date_asc' | string;

export type TransactionExplorerScan = {
	candidate_rows: number;
	split_rows: number;
	query_count: number;
	scan_limited: boolean;
	exhausted: boolean;
};

export type TransactionExplorerPage = {
	items: TransactionListItem[];
	sort: TransactionExplorerSort;
	page_size: number;
	returned_count: number;
	has_more: boolean;
	has_previous: boolean;
	next_cursor: string | null;
	previous_cursor: string | null;
	scan: TransactionExplorerScan;
	limitations: string[];
};

export type ReportSummaryReady = {
	status: 'ready';
	currency: string;
	net_worth: string;
	assets: string;
	liabilities: string;
	income_this_month: string;
	expenses_this_month: string;
	as_of_date: string;
	reporting_basis: string;
	includes_currency_conversion: boolean;
	limitations: string[];
	reporting_currency: ReportingCurrencyResolution;
};

export type ReportSummarySetup = {
	status: 'setup_required';
	as_of_date: string;
	reporting_basis: string;
	includes_currency_conversion: false;
	limitations: string[];
	reporting_currency: ReportingCurrencyResolution;
};

export type ReportSummary = ReportSummaryReady | ReportSummarySetup;

export type DashboardDrilldownLinks = {
	recent: string;
	incomeThisMonth: string;
	expensesThisMonth: string;
	expensesAll: string;
	cashflowByMonth: Record<string, string>;
	expensesByAccount: Record<string, string>;
};

export type DashboardSectionErrors = {
	summary: boolean;
	expenses: boolean;
	cashflow: boolean;
	recentTransactions: boolean;
	changes: boolean;
	upcomingObligations: boolean;
};

export type DashboardExpenseChange = {
	account_id: string;
	account_name: string;
	delta: string;
	absolute_delta: string;
	currency: string;
};

export type DashboardUpcomingObligations = {
	enabled_count: number;
	unavailable_count: number;
};

export type ExpenseByAccount = {
	account_id: string;
	account_name: string;
	total: string;
	currency: string;
};

export type CashflowData = {
	date_from: string;
	date_to: string;
	currency: string;
	inflow: string;
	outflow: string;
	net: string;
};

export type CashflowPeriod = {
	month: string;
	inflow: string;
	outflow: string;
	net: string;
};

export type PeriodReportSummary = {
	currency: string;
	net_worth: string;
	assets: string;
	liabilities: string;
	as_of_date: string;
	reporting_basis: string;
	includes_currency_conversion: boolean;
	limitations: string[];
};

export type PeriodReportSectionStatus = {
	section: 'summary' | 'cashflow' | 'monthly_cashflow' | 'expenses_by_account' | string;
	status: 'ok' | 'empty' | 'error' | string;
	detail: string | null;
};

export type PeriodReport = {
	book_id: number;
	date_from: string;
	date_to: string;
	currency: string;
	reporting_basis: 'base_currency_only' | string;
	includes_currency_conversion: boolean;
	limitations: string[];
	partial_failure: boolean;
	empty: boolean;
	section_statuses: PeriodReportSectionStatus[];
	summary: PeriodReportSummary | null;
	cashflow: CashflowData | null;
	monthly_cashflow: CashflowPeriod[];
	expenses_by_account: ExpenseByAccount[];
};

export type ReportComparisonMode = 'previous_equivalent' | 'same_period_last_year' | 'custom';

export type DeltaSectionStatus = {
	section: 'summary' | 'cashflow' | 'expenses_by_account' | string;
	status: 'ok' | 'empty' | 'error' | 'not_comparable' | string;
	detail: string | null;
};

export type MoneyDelta = {
	primary: string;
	comparison: string;
	delta: string;
	absolute_delta: string;
	currency: string;
};

export type SummaryDelta = {
	currency: string;
	assets: MoneyDelta;
	liabilities: MoneyDelta;
	net_worth: MoneyDelta;
};

export type CashflowDelta = {
	currency: string;
	inflow: MoneyDelta;
	outflow: MoneyDelta;
	net: MoneyDelta;
};

export type ExpenseAccountComparison = {
	account_id: string;
	account_name: string;
	primary_total: string;
	comparison_total: string;
	delta: string | null;
	absolute_delta: string | null;
	currency: string;
	status: 'ok' | 'not_comparable' | string;
	detail: string | null;
};

export type PeriodReportComparison = {
	book_id: number;
	comparison_mode: ReportComparisonMode;
	primary: PeriodReport;
	comparison: PeriodReport;
	reporting_basis: 'base_currency_only' | string;
	includes_currency_conversion: boolean;
	limitations: string[];
	partial_failure: boolean;
	empty: boolean;
	comparable: boolean;
	delta_section_statuses: DeltaSectionStatus[];
	summary_delta: SummaryDelta | null;
	cashflow_delta: CashflowDelta | null;
	expense_changes: ExpenseAccountComparison[];
};

export type TransactionCreateSplitRequest = {
	account_id: string;
	amount: string;
	memo: string;
};

export type TransactionCreateRequest = {
	date: string;
	description: string;
	currency: string;
	splits: TransactionCreateSplitRequest[];
};

export type TransactionCreatePreviewAccount = {
	id: string;
	name: string;
	display_name?: string | null;
	full_name: string;
	type: string;
	currency: string;
};

export type TransactionCreateWarning = {
	code: string;
	message_key: string;
};

export type TransactionCreatePreviewSplit = {
	index: number;
	account: TransactionCreatePreviewAccount;
	amount: string;
	memo: string;
};

export type TransactionCreatePreviewResponse = {
	preview_only: true;
	confirm_allowed: boolean;
	create_count: 1;
	preview_token: string;
	expires_at: string;
	idempotency_key: string;
	create_generation: number;
	currency: string;
	date: string;
	description: string;
	splits: TransactionCreatePreviewSplit[];
	warnings: TransactionCreateWarning[];
};

export type TransactionCreatePreview = TransactionCreatePreviewResponse;

export type TransactionCreateConfirmReadback = {
	verified: boolean;
	transaction_present: boolean;
	split_count: number;
	balanced: boolean;
	currency_consistent: boolean;
};

export type TransactionCreateConfirmResult = {
	status: 'created' | 'already_created';
	transaction_id: string;
	audit_ref: string;
	backup_ref: string;
	readback: {
		verified: boolean;
		transaction_present: boolean;
		split_count: number;
		balanced: boolean;
		currency_consistent: boolean;
	};
	links: {
		transaction: string;
		explorer: string;
	};
};

export type TransactionCreateErrorEnvelope = {
	error: {
		code: string;
		message_key: string;
		field_path: string | null;
		retryable: boolean;
		recovery_ref: string | null;
		request_ref: string;
	};
};

export type TransactionCreateSettings = {
	known?: boolean;
	enabled: boolean;
	effective_enabled?: boolean;
	deployment_writes_enabled?: boolean;
	user_can_create?: boolean;
	create_generation: number;
	transaction_create_generation?: number;
	recovery_required: boolean;
	reason_key?: string;
	deployment?: {
		enabled?: boolean;
		writes_enabled?: boolean;
		code?: string;
	};
	generation?: number;
	recovery?: {
		required?: boolean;
		code?: string;
	};
	can_enable?: boolean;
	blocked_codes?: string[];
	effective?: {
		enabled?: boolean;
		confirm_allowed?: boolean;
	};
};

export type TransactionValidationResult = {
	valid: boolean;
	errors: string[];
	warnings: string[];
	summary: Record<string, unknown>;
};

export type TransactionWriteResult = {
	transaction_id: string;
	backup_ref?: string;
	audit_log_id: number | null;
};

export type WriteAlphaAuditSummaryItem = {
	id: number;
	action: string;
	result: string;
	timestamp: string;
	transaction_id_prefix: string | null;
	backup_present: boolean;
	backup_artifact_ref: string | null;
	error: string | null;
};

export type WriteAlphaAuditSummary = {
	book_id: number;
	items: WriteAlphaAuditSummaryItem[];
	total_count: number;
	returned_count: number;
	counts_by_action: Record<string, number>;
	counts_by_result: Record<string, number>;
	ownership_summary: Record<string, number | string | null>;
	filters: Record<string, string | number | null>;
	pagination: Record<string, number | boolean | null>;
	time_window: Record<string, string | null>;
	status_summary: string[];
	limitations: string[];
};

export type FirstRunCheckStatus = 'ok' | 'warning' | 'action_required' | string;

export type FirstRunCheck = {
	status: FirstRunCheckStatus;
	message: string;
	safe_next_actions?: string[];
};

export type FirstRunDiagnostics = {
	summary: string;
	action_required: string[];
	checks: Record<'jwt_secret' | 'admin_bootstrap' | 'default_book' | 'cors' | 'write_mode', FirstRunCheck>;
};

export type HealthPayload = {
	status: string;
	service: string;
	warnings: string[];
	first_run?: FirstRunDiagnostics;
};
