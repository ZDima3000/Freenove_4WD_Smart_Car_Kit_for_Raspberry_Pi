# First we need the asyncio library
import asyncio

# Then we need a loop to work with
loop = asyncio.get_event_loop()

# We also need something to run
async def main(level):
    for char in 'Hello, world!\n':
        print(char, end='', flush=True)
        if level == 1:
            #loop.create_task(main(2))
            await main(2)
        await asyncio.sleep(0.2)

# Then, we need to run the loop with a task
loop.run_until_complete(main(1))

#>>> process = subprocess.Popen(args, stdout=f)
#>>> process.send_signal(signal.SIGINT)
#f = open("/tmp/dima.txt", "w")
