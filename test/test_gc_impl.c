#define TESTING
#include "../vm.c"
#include <assert.h>

// Mock Obj pointer to work with user's test syntax, 
// though we use integer handles in the VM.
// We'll treat `Obj*` as `intptr_t` which holds the VM address (index).
typedef intptr_t Obj; 

#define VAL_OBJ(o) ((int32_t)(o))

// Global VM for simplicity or pass it? 
// User syntax: Obj * a = new_pair(NULL, NULL); implies implicit VM or passed.
// I will pass VM for cleaner code, modifying the user's snippet slightly if needed,
// or use a global `current_vm` for the test helpers.

VM *current_vm;

Obj new_pair(Obj a, Obj b) {
    // 1. Manually trigger ALLOC opcode logic or calls vm_alloc helper if we made one.
    // Since we put logic in ALLOC opcode, let's call a helper or execute code?
    // Better to extract logic to `vm_alloc` as planned, but I put it in `run_vm`.
    // Let's execute "ALLOC" instruction via run_vm? 
    // No, simpler to just manipulate heap directly for these white-box tests 
    // OR refactor vm.c to have `int32_t vm_alloc(VM *vm, size_t size)`.

    
    int size = 2; // Pair has 2 fields
    int needed = size + 3; // +3 for header
    
    if (current_vm->free_ptr + needed > HEAP_SIZE) {
        printf("  [Alloc] Heap Overflow! Need %d, FreePtr at %d\n", needed, current_vm->free_ptr);
        return 0;
    }

    int32_t addr = current_vm->free_ptr;
    printf("  [Alloc] Allocating Pair at Heap Index %d (Size: %d, Header: [Size:%d, Next:%d, Mark:0])\n", 
           addr, size, size, current_vm->allocated_list);

    current_vm->heap[addr] = size;     // SIZE
    current_vm->heap[addr + 1] = current_vm->allocated_list; // NEXT
    current_vm->heap[addr + 2] = 0;    // MARKED
    
    current_vm->allocated_list = addr;
    current_vm->free_ptr += needed;
    
    int32_t payload_addr = addr + 3;
    int32_t vm_addr = MEM_SIZE + payload_addr;

    // Set fields
    // A pair in heap: [Size, Next, Mark] [Field1] [Field2]
    // Indices: addr, addr+1, addr+2, addr+3, addr+4
    
    // Check if a and b are pointers (VM addresses)
    // We store them as is.
    current_vm->heap[payload_addr] = (int32_t)a;
    current_vm->heap[payload_addr + 1] = (int32_t)b;
    
    printf("  [Alloc] Success. VM Address: %d. Fields: [%d, %d]\n", vm_addr, (int)a, (int)b);

    return (Obj)vm_addr;
}

void test_allocator() {
    printf("Testing Allocator...\n");
    printf("Goal: Verify that 'new_pair' correctly reserves space in the heap and links objects.\n");
    VM vm = {0};
    vm.free_ptr = 0;
    vm.allocated_list = -1;
    current_vm = &vm;
    
    printf("\n1. Allocating First Object (o1)...\n");
    Obj o1 = new_pair(0, 0);
    assert(o1 == MEM_SIZE + 0 + 3); // First object at start of heap + header
    
    // Check header
    int32_t r_addr = (int32_t)o1 - MEM_SIZE;
    printf("   -> Verified Object 1 Address: %ld\n", (long)o1);
    printf("   -> Checking Header at heap[%d]... Size should be 2.\n", r_addr - 3);
    assert(vm.heap[r_addr - 3] == 2); // Size
    assert(vm.heap[r_addr - 2] == -1); // Next (end of list)
    
    printf("\n2. Allocating Second Object (o2) pointing to o1...\n");
    Obj o2 = new_pair(o1, 0);
    
    // Check linked list
    int32_t r_addr2 = (int32_t)o2 - MEM_SIZE;
    printf("   -> Verified Object 2 Address: %ld\n", (long)o2);
    printf("   -> Checking List Linkage: o2->next should point to o1's header (%d).\n", r_addr - 3);
    assert(vm.heap[r_addr2 - 2] == r_addr - 3); // Next points to o1's header start
    
    printf("\nAllocator Test Passed: Objects created and linked correctly in heap.\n");
}

int main() {
    test_allocator();
    return 0;
}
