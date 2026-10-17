#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void arbread(void) {
  unsigned char* loc;
  printf("[?] address > ");
  read(0, &loc, sizeof(loc));
  printf("[!] arbread: ");
  for (int i = 0; i < 8; i++) {
    printf("%02x", loc[i]);
  }
}

void arbwrite(void) {
  unsigned char* loc;
  printf("[?] address > ");
  read(0, &loc, 8);
  printf("[?] write > ");
  read(0, loc, 8);
  puts("arbwrite done!");
}

void menu(void) {
  char c;
  puts("[1] arbread");
  puts("[2] arbwrite");
  puts("[anything else] quit");
  printf("option > ");
  c = getc(stdin);
  getchar(); // exhaust newline
  switch (c) {
    case '1':
      arbread();
      break;
    case '2':
      arbwrite();
      break;
  }
}
int main(void) {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);

  puts("welcome to the great primitivizatinator [TAKE TWO]!");
  while (1) menu();
}
