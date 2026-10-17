#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <math.h>

int proof_by_intimidation(const char* proof) {
  if (!proof) return 1;
  puts("THE PROOF HAS COMPLETED. PLEASE DO NOT ASK ANY MORE QUESTIONS.");
  return 0;
}

int proof_by_confusion(const char* proof) {
  if (!proof) return 1;
  puts ("ough.. i don't know...");
  return 0;
}

int proof_by_invigilation(const char* proof) {
  if (!proof) return 1;
  puts("You must update Examena to view this proof.");
  return 0;
}

int (*proofs[4])(const char*) = {
  proof_by_intimidation,
  proof_by_confusion,
  proof_by_invigilation,
  puts
};

struct vtable {
  char lemma[0x200];
  unsigned long long left_operand;
  unsigned long long right_operand;
  int (*proof)(const char*);
};

int main(void) {
  unsigned int c;
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
 
  puts("[ THE INCREDIBLE PROOF MACHINE ]\n--------");

  while (1) {
    struct vtable *a = malloc(sizeof(*a));

    puts("[ OPERANDS ] ");
    printf("specify left operand > ");
    read(0, &(a->left_operand), sizeof(a->left_operand));

    puts("[ TYPES ] ");
    printf("specify right operand > ");
    read(0, &(a->right_operand), sizeof(a->right_operand));
    
    puts("[ PROOF ]\n (options: 1 - intimidation, 2 - confusion, 3 - invigilation, 4 - debug)");
    printf("specify proof method > ");
    c = getc(stdin) - 49; // ord('1')
    getchar(); // newline
    
    if (c > 4) exit(1);
    a->proof = proofs[c];
    
    puts("[ LEMMA ]");
    printf(" enter your lemma > ");
    read(0, a->lemma, sizeof(*a));

    puts("[ DETAILS ] ");
    printf("YOUR LEMMA: %s\n", a->lemma);
    printf("YOUR OPERANDS: %d %d\n", a->left_operand, a->right_operand);
    printf("press any key to formally prove your theorem... > ");
    getchar();

    a->proof(a->lemma);

    puts("[ DONE ! ]");
    puts("A TRULY MARVELLOUS PROOF... UNFORTUNATELY IT DOES NOT FIT WITHIN THE BOUNDS OF THIS TERMINAL.");
    puts("TRY AGAIN!");

    free(a);
  } 
}
