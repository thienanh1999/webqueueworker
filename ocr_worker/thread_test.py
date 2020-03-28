from concurrent.futures import ThreadPoolExecutor

tasks = [1,2,3,4,5]

def do_task(t):
    print(t)
    return t+1


result = []
print("Starting ThreadPoolExecutor")
with ThreadPoolExecutor(max_workers=3) as executor:
   for t in tasks:
       result.append(executor.submit(do_task, (t)).result())
print("All tasks complete")
print(result)