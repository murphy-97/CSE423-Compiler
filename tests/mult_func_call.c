int func_dec(int a)
{
  a = a + 2;
  return a;
}

int main(void)
{
  int x;
  int y;
  y = 3;
  x = func_dec(y);
  return 0;
}
