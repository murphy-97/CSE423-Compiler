int main(void)
{
    if (1 + 2) {
        return 0;
    }
    if (1 + (2 + 3)) {
        return 1;
    }
    if ((1 + 2) * (3 + 4)) {
        return 2;
    }
    return 3;
}