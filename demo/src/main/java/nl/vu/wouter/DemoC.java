package nl.vu.wouter;

public class DemoC extends DemoB {
    @Override
    public int foo(int x, int y) {
        return super.foo(x, y) % 102;
    }
}
