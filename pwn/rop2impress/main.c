#include <stdio.h>
#include <unistd.h>

void gift(void) {
  __asm__("pop %rbx; ret");
  __asm__("pop %rsp; ret");
}

void rop(void) {
  char buf[0x50];
  read(0, buf, 0x60);
  if (!buf[0]) rop();
  return;
}

int main(void) {
  rop(); 
}
