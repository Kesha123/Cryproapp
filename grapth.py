import asyncio


async def f():
    while True:
        print("f() func")
        await asyncio.sleep(1)


async def g():
    while True:
        print("g() func")
        await asyncio.sleep(1)


async def main():
    main_loop.create_task(f())
    main_loop.create_task(g())


main_loop = asyncio.get_event_loop()
main_loop.run_until_complete(main())
main_loop.run_forever()