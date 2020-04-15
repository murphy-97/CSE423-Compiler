int func_dec(int a, int b, int c)
{
  a = a + b + c;
  return a;
}

int main(void)
{
  int a = 2 + 1;
  int x;
  int y;
  x = 2;
  y = 3;
  x = func_dec(x, y, 5);
  return 0;
}
