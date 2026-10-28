import Big from 'big.js';

export const MoneyMath = {
    add: (a, b) => new Big(a).plus(new Big(b)).toFixed(2),
    subtract: (a, b) => new Big(a).minus(new Big(b)).toFixed(2),
    multiply: (a, b) => new Big(a).times(new Big(b)).toFixed(2),
    divide: (a, b) => new Big(a).div(new Big(b)).toFixed(2),

    format: (amount) => {
        return new Intl.NumberFormat('en-KE', {
            style: 'currency',
            currency: 'KES',
        }).format(amount);
    }
};