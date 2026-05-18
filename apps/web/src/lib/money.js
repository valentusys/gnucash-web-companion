const DECIMAL_RE = /^([+-]?)(\d*)(?:\.(\d*))?$/;

/**
 * Parse the API's decimal-string money values without converting them to JS Number.
 * Invalid/empty values are treated as zero for display-only UI decisions.
 *
 * @param {string | number | null | undefined} value
 * @returns {{ negative: boolean; digits: bigint; scale: number }}
 */
function parseDecimalString(value) {
	const raw = String(value ?? '').trim();
	const match = DECIMAL_RE.exec(raw);
	if (!match) return { negative: false, digits: 0n, scale: 0 };

	const [, sign, integerPartRaw, fractionalPartRaw = ''] = match;
	const integerPart = integerPartRaw || '0';
	const fractionalPart = fractionalPartRaw;
	const normalized = `${integerPart}${fractionalPart}`.replace(/^0+/, '') || '0';
	const digits = BigInt(normalized);
	return {
		negative: sign === '-' && digits !== 0n,
		digits,
		scale: fractionalPart.length
	};
}

/**
 * Compare two decimal-string money values exactly enough for UI sign/range decisions.
 * Returns -1 when a < b, 0 when equal, and 1 when a > b.
 *
 * @param {string | number | null | undefined} a
 * @param {string | number | null | undefined} b
 * @returns {-1 | 0 | 1}
 */
export function compareDecimalStrings(a, b) {
	const left = parseDecimalString(a);
	const right = parseDecimalString(b);

	if (left.negative !== right.negative) {
		return left.negative ? -1 : 1;
	}

	const scale = Math.max(left.scale, right.scale);
	const leftScaled = left.digits * 10n ** BigInt(scale - left.scale);
	const rightScaled = right.digits * 10n ** BigInt(scale - right.scale);

	if (leftScaled === rightScaled) return 0;
	if (left.negative) {
		return leftScaled > rightScaled ? -1 : 1;
	}
	return leftScaled > rightScaled ? 1 : -1;
}

/**
 * @param {string | number | null | undefined} value
 * @returns {boolean}
 */
export function isNonNegativeDecimalString(value) {
	return compareDecimalStrings(value, '0') >= 0;
}

/**
 * Calculate a display-only percentage width from decimal-string money values without
 * using Number() on the money strings. Values are clamped to 0..100%.
 *
 * @param {string | number | null | undefined} value
 * @param {Array<string | number | null | undefined>} allValues
 * @returns {string}
 */
export function decimalBarWidthPercent(value, allValues) {
	const parsedValues = allValues.map(parseDecimalString);
	const maxScale = Math.max(parseDecimalString(value).scale, ...parsedValues.map((item) => item.scale), 0);
	const scaleToCommon = (/** @type {{ digits: bigint; scale: number }} */ item) =>
		item.digits * 10n ** BigInt(maxScale - item.scale);

	const numerator = scaleToCommon(parseDecimalString(value));
	const denominator = parsedValues.reduce((max, item) => {
		const scaled = scaleToCommon(item);
		return scaled > max ? scaled : max;
	}, 0n);

	if (numerator === 0n) return '0%';
	if (denominator === 0n) return '100%';

	const basisPoints = (numerator * 10000n) / denominator;
	const clamped = basisPoints > 10000n ? 10000n : basisPoints;
	const whole = clamped / 100n;
	const fractional = clamped % 100n;
	if (fractional === 0n) return `${whole}%`;
	return `${whole}.${fractional.toString().padStart(2, '0').replace(/0+$/, '')}%`;
}
