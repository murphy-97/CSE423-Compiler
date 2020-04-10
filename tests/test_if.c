int main(void)
{
    if (1 + 2) {
        return 0;
    }
    while (1 + (2 + 3)) {
        return 1;
    }
    if ((1 + 2) * (3 + 4)) {
        return 2;
    }
    while (x && y || z) {
        return 3;
    }
    return 4;
}