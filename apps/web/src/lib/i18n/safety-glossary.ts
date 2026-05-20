import type { MessageKey } from './messages';

export type SafetyGlossaryTerm = {
	id: string;
	canonicalEnglish: string;
	preferredRussian: string;
	notes: string;
	messageKeys: MessageKey[];
};

export const safetyGlossaryTerms: SafetyGlossaryTerm[] = [
	{
		id: 'read-only-default',
		canonicalEnglish: 'read-only by default; GNUCASH_WRITES_ENABLED=false',
		preferredRussian: 'read-only по умолчанию; GNUCASH_WRITES_ENABLED=false',
		notes: 'Visible safety copy must keep the default-disabled read-only boundary explicit.',
		messageKeys: ['safety.badge', 'safety.message', 'books.readOnlyDefault', 'writeMode.message', 'writeMode.acknowledgement']
	},
	{
		id: 'write-alpha-disposable-test-boundary',
		canonicalEnglish: 'write-alpha is experimental and disposable/test-copy only',
		preferredRussian: 'write-alpha экспериментален и только для disposable/test copies',
		notes: 'Do not imply normal editing, source-book writes, only-copy writes, or real/private-book readiness.',
		messageKeys: [
			'safety.releaseCritical',
			'audit.bannerTitle',
			'audit.bannerMessage',
			'audit.emptyMessage',
			'writeMode.message',
			'writeMode.disposableOnly',
			'writeMode.neverRealBook',
			'writeMode.finalConfirm',
			'writeMode.acknowledgement',
			'transactionDetail.deleteHelper',
			'transactionDetail.deleteAcknowledgement',
			'transactionDetail.deleteConfirm'
		]
	},
	{
		id: 'not-production-ready',
		canonicalEnglish: 'not production-ready',
		preferredRussian: 'не production-ready',
		notes: 'Keep explicit in release-critical operator copy; never soften into production readiness.',
		messageKeys: ['safety.releaseCritical', 'audit.bannerMessage', 'writeMode.message']
	},
	{
		id: 'not-security-audited',
		canonicalEnglish: 'not security-audited',
		preferredRussian: 'не security-audited / не проходило security audit',
		notes: 'Do not imply a completed audit, certification, or production-grade security.',
		messageKeys: ['safety.releaseCritical', 'audit.bannerMessage', 'writeMode.message']
	},
	{
		id: 'no-currency-conversion',
		canonicalEnglish: 'no currency conversion / no FX conversion',
		preferredRussian: 'без конвертации валют / без FX-конвертации',
		notes: 'Dashboard, transaction drilldowns, and CSV/export copy must not imply FX conversion.',
		messageKeys: [
			'dashboard.drilldownSafety',
			'dashboard.currencyConversion',
			'dashboard.currencyConversionNotIncluded',
			'dashboard.cashflowHelp',
			'transactions.export.countStatus'
		]
	},
	{
		id: 'desktop-authoritative-editor',
		canonicalEnglish: 'GnuCash Desktop remains the authoritative editor',
		preferredRussian: 'GnuCash Desktop остаётся главным редактором',
		notes: 'Use for all write-boundary warnings; do not present the web app as the authoritative editor.',
		messageKeys: ['safety.message', 'books.safetyNote', 'scheduled.subtitle', 'writeMode.desktop', 'writeMode.acknowledgement']
	}
];
