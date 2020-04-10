int main(void)
{
    if (1 + 2) {
        return 0;
    }

    x = 10;

    while (1 + (2 + 3)) {
        return 1;
    }

    y = 20;

    if ((1 + 2) * (3 + 4)) {
        return 2;
    }

    z = 30;

    while (x && y || z) {
        return 3;
    }

    return 4 + x + y + z;

}