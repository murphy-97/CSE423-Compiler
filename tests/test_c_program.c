#include <stdio.h>

int main(void)
{
	printf("Hello, World!\n");

	int isPrime = 1;
	for (int i = 2; i < 100; i++) {
		isPrime = 1;
		for (int j = 2; j < i; j++) {
			if (i % j == 0) {
				isPrime = 0;
			}
		}
		if (isPrime) {
			printf("The Number %d is prime\n", i);
		}
	}
	
	return 0;
}
