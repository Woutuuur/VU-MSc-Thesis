package nl.vu.wouter;

public class DemoA extends Demo {

    @Override
    public int foo(Object x, int y) {
        if (x instanceof String s) {
            return s.isEmpty() ? y : s.length() * y;
        }

        return y + x.hashCode() * 2 % 1234;
    }

}
