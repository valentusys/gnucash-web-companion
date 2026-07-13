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

export type Book = {
	id: number;
	name: string;
	storage_type: string;
	base_currency: string | null;
	is_default: boolean;
	is_archived: boolean;
	access_role: 'owner' | 'editor' | 'viewer' | null;
	access_role_label: string;
	access_role_description: string;
	read_only: boolean;
	status: string;
	status_severity: 'ok' | 'warning' | 'action_required' | string;
	access_status: string;
	can_open_read_only_views: boolean;
	storage_diagnostics: BookStorageDiagnostics;
	management_actions: Array<'set_default' | 'remove_from_registry' | string>;
	operator_guidance: BookOperatorGuidance;
};

export type Account = {
	id: string;
	name: string;
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
};

export type CommodityRef = {
	namespace: string;
	mnemonic: string;
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
	memo: string;
	reconcile_state?: string;
	amount: string;
	currency: string;
};

export type MoneyDTO = {
	amount: string;
	currency: string;
};

export type TransactionListItem = {
	id: string;
	date: string;
	description: string;
	amount: string;
	currency: string;
	account_id: string;
	account_name: string;
	counter_account_name: string;
	representative_amount?: MoneyDTO;
	representative_account?: { id: string; name: string } | null;
	matched_amount?: MoneyDTO | null;
	amount_basis?: 'selected_accounts' | 'income' | 'expense' | 'representative_split' | string;
	matched_account_ids?: string[];
	is_write_alpha_owned?: boolean;
};

export type TransactionDetail = {
	id: string;
	date: string;
	description: string;
	currency: string;
	splits: TransactionSplit[];
	is_write_alpha_owned?: boolean;
};

export type ScheduledTransactionRecurrence = {
	period_type: string;
	multiplier: number | null;
	period_start: string | null;
	weekend_adjust: string;
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

export type ReportSummary = {
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
};

export type DashboardDrilldownLinks = {
	recent: string;
	incomeThisMonth: string;
	expensesThisMonth: string;
	cashflowByMonth: Record<string, string>;
	expensesByAccount: Record<string, string>;
};

export type DashboardSectionErrors = {
	summary: boolean;
	expenses: boolean;
	cashflow: boolean;
	recentTransactions: boolean;
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

export type TransactionCreatePreview = {
	preview_only: boolean;
	writes_enabled_required_for_create: boolean;
	create_count: number;
	date: string;
	amount: string;
	currency: string;
	description: string;
	memo: string;
	debit_account: {
		id: string;
		name: string;
		full_name: string;
		currency: string;
	};
	credit_account: {
		id: string;
		name: string;
		full_name: string;
		currency: string;
	};
	splits: Array<{
		account_id: string;
		amount: string;
		currency: string;
		memo: string;
	}>;
	warnings: string[];
};

export type TransactionValidationResult = {
	valid: boolean;
	errors: string[];
	warnings: string[];
	summary: Record<string, unknown>;
};

export type TransactionWriteResult = {
	transaction_id: string;
	backup_path: string;
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
