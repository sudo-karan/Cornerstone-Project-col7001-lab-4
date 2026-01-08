import subprocess
import os
import re

tests = [
    ("test_push.bin", 10),
    ("test_pop.bin", 10),
    ("test_dup.bin", 10),
    ("test_halt.bin", 10),
    ("test_add.bin", 30),
    ("test_sub.bin", 20),
    ("test_mult.bin", 30),
    ("test_div.bin", 10),
]

print(f"{'Test File':<20} | {'Expected':<10} | {'Actual':<10} | {'Status':<10}")
print("-" * 60)

for test_file, expected in tests:
    path = os.path.join("test", test_file)
    try:
        # Run the VM
        result = subprocess.check_output(["./vm", path], stderr=subprocess.STDOUT).decode()
        
        # Parse output for "Top of stack: <val>"
        match = re.search(r"Top of stack: (-?\d+)", result)
        if match:
            val = int(match.group(1))
            status = "PASS" if val == expected else "FAIL"
            print(f"{test_file:<20} | {expected:<10} | {val:<10} | {status:<10}")
        else:
            print(f"{test_file:<20} | {expected:<10} | {'?':<10} | FAIL (Parse Error)")
            print(f"  Output: {result.strip()}")
            
    except subprocess.CalledProcessError as e:
        print(f"{test_file:<20} | {expected:<10} | {'ERROR':<10} | FAIL")
        print(f"  Error Output: {e.output.decode().strip()}")
    except Exception as e:
        print(f"{test_file:<20} | {expected:<10} | {'ERROR':<10} | FAIL ({str(e)})")
