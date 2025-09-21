package nl.vu.wouter;

public class DemoC extends DemoB {

    @Override
    public int foo(Object x, int y) {
        // if (x instanceof Integer s) {
        //     return s + y;
        // }

        // if (x == null) {
        //     return 0;
        // }

        // if (x instanceof Demo d) {
        //     return d.foo("abc", y + 15);
        // }

        if (x instanceof String s) {
            return s.isEmpty() ? y : s.length() * y;
        }

        return y + x.hashCode() * 14 % 2151;
    }

}
