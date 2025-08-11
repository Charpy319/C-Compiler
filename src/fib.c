int fib(int n);

int main(void)
{
    return fib(12);   
}

int fib(int n)
{
    if (n == 0 || n == 1)
    return n;

    int i = 0;
    int j = 1;

    for (int count = 1; count < n; count++)
    {
        int next = i + j;
        i = j;
        j = next;
    }
    return j;
}