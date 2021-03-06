# decimal_context_manager.py

import decimal

with decimal.localcontext() as c:
    c.prec = 2
    print('Precisione locale:', c.prec)
    print('3.14 / 3 =', (decimal.Decimal('3.14') / 3))

print()
print('Precisione predefinita:', decimal.getcontext().prec)
print('3.14 / 3 =', (decimal.Decimal('3.14') / 3))
