int func_dec(int a, int b, int c, int d)
{
  int ef = a / b + c + d;
  return ef;
}

int func_dec_2(int a, int b, int c, int aa, int ba, int ca, int as, int bs, int cs)
{
	return 0;
}

int func_dec_3()
{
  return 0;
}

int main(void)
{
  int a = 2 + 1;
  int x;
  int y;
  a = func_dec(1, 2, 3, 4);
  a = func_dec_2(1, 2, 3, 4, 5, 6, 7, 8, 9);
  x = 2;
  y = 3;
  a = func_dec_3();
  return 0;
}
