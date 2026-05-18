import assert from 'node:assert/strict';

import {
	compareDecimalStrings,
	decimalBarWidthPercent,
	isNonNegativeDecimalString
} from '../src/lib/money.js';

assert.equal(compareDecimalStrings('10', '2'), 1);
assert.equal(compareDecimalStrings('2', '10'), -1);
assert.equal(compareDecimalStrings('001.2300', '1.23'), 0);
assert.equal(compareDecimalStrings('-0.01', '0'), -1);
assert.equal(compareDecimalStrings('-10.00', '-2.00'), -1);
assert.equal(compareDecimalStrings('-2.00', '-10.00'), 1);
assert.equal(compareDecimalStrings('12345678901234567890.123456789', '12345678901234567890.123456788'), 1);

assert.equal(isNonNegativeDecimalString('0'), true);
assert.equal(isNonNegativeDecimalString('0.00'), true);
assert.equal(isNonNegativeDecimalString('42.10'), true);
assert.equal(isNonNegativeDecimalString('-0.01'), false);

assert.equal(decimalBarWidthPercent('-50.00', ['-100.00', '-50.00']), '50%');
assert.equal(decimalBarWidthPercent('2.5', ['2.5', '10.0']), '25%');
assert.equal(decimalBarWidthPercent('1', ['3']), '33.33%');
assert.equal(decimalBarWidthPercent('0', ['0', '0.00']), '0%');
assert.equal(decimalBarWidthPercent('100', ['0']), '100%');
assert.equal(decimalBarWidthPercent('150', ['100']), '100%');

console.log('money string checks passed');
