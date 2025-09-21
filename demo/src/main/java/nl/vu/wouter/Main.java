package nl.vu.wouter;

import java.util.Random;

public class Main {
    public static void main(String[] args) throws Exception {
        Demo[] demos = new Demo[] {
            new DemoA(),
            new DemoB(),
            new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(),
            new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(),
            new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(), new DemoC(),
        };
        Random random = new Random(0);
        int y = random.nextInt(124512);
        int total = 0;

        total += demos[new Random().nextInt(demos.length)].foo("sdiofasd", 3);

        for (int i = 0; i < 1_000_000_000; i++) {
            Demo demo = demos[i % demos.length];
            total += demo.foo(args[0], y + i % y);
        }

        System.out.println("Total: " + total);
    }
}
