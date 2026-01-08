import subprocess
import os
import re

# List of tests: (assembly_filename, expected_top_of_stack)
tests = [
    ("test_push.asm", 10),
    ("test_pop.asm", 10),
    ("test_dup.asm", 10),
    ("test_halt.asm", 10),
    ("test_add.asm", 30),
    ("test_sub.asm", 20),
    ("test_mult.asm", 30),
    ("test_div.asm", 10),
    ("test_loop.asm", 0),
]

print(f"{'Test File':<20} | {'Expected':<10} | {'Actual':<10} | {'Status':<10}")
print("-" * 65)

passed_count = 0
failed_count = 0

for test_file, expected in tests:
    asm_path = os.path.join("test", test_file)
    bin_path = asm_path.replace(".asm", ".bin")
    
    test_passed = False
    
    try:
        # 1. Assemble the .asm file into .bin
        # We allow the assembler to print errors to stdout/stderr if it fails
        subprocess.check_call(
            ["python3", "assembler.py", asm_path, bin_path],
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # 2. Run the VM with the generated .bin file
        try:
            result = subprocess.check_output(["./vm", bin_path], stderr=subprocess.STDOUT).decode()
            
            # 3. Parse output for "Top of stack: <val>"
            match = re.search(r"Top of stack: (-?\d+)", result)
            if match:
                val = int(match.group(1))
                if val == expected:
                    status = "PASS"
                    passed_count += 1
                    test_passed = True
                else:
                    status = "FAIL"
                    failed_count += 1
                print(f"{test_file:<20} | {expected:<10} | {val:<10} | {status:<10}")
            else:
                print(f"{test_file:<20} | {expected:<10} | {'?':<10} | FAIL (Parse Error)")
                print(f"  Output: {result.strip()}")
                failed_count += 1

        except subprocess.CalledProcessError as e:
            # specialized error for VM runtime failure
            print(f"{test_file:<20} | {expected:<10} | {'ERROR':<10} | FAIL (Runtime Error)")
            print(f"  Error Output: {e.output.decode().strip()}")
            failed_count += 1
            
        finally:
            # 4. Cleanup: Remove the .bin file if it exists
            if os.path.exists(bin_path):
                os.remove(bin_path)

    except subprocess.CalledProcessError:
        # This catches errors from step 1 (assembler failure)
        print(f"{test_file:<20} | {expected:<10} | {'ERROR':<10} | FAIL (Assembly Error)")
        failed_count += 1
    except Exception as e:
        print(f"{test_file:<20} | {expected:<10} | {'ERROR':<10} | FAIL ({str(e)})")
        failed_count += 1

# Summary
total = passed_count + failed_count
percentage = (passed_count / total * 100) if total > 0 else 0

print("-" * 65)
print(f"Summary: {passed_count}/{total} passed ({percentage:.1f}%)")
if failed_count > 0:
    print(f"Failed: {failed_count} tests")
else:
    print("All tests passed!")
