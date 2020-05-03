int foo(int a, int b) {
    int c;
    c = a + b;
    c = c + 1 + 2;
    return c;
}

int main() {
    int x = foo(1, 2);
    return 0;
}