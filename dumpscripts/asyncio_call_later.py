# asyncio_call_later.py

import asyncio


def callback(n):
    print('callback {} invocato'.format(n))


async def main(loop):
    print('registrazione callbacks')
    loop.call_later(0.2, callback, 1)
    loop.call_later(0.1, callback, 2)
    loop.call_soon(callback, 3)

    await asyncio.sleep(0.4)


event_loop = asyncio.get_event_loop()
try:
    print('entrata nel ciclo di eventi')
    event_loop.run_until_complete(main(event_loop))
finally:
    print('chiusura del ciclo di eventi')
    event_loop.close()
