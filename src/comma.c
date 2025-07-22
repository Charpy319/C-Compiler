int main()
{
    int x;
    int y = 5;
    x = (y += 4, ~3);
    return x %= y;
}