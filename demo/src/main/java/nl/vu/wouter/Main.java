package nl.vu.wouter;

import java.util.Random;

public class Main {
    public static void main(String[] args) {
        Demo[] demos = new Demo[] {new DemoA(), new DemoB(), new DemoC(), new DemoC(), new DemoC()};
        Random random = new Random();
        int total = 0;

        for (int i = 0; i < 10000; i++) {
            int index = random.nextInt(demos.length);
            int x = random.nextInt(225643);
            int y = random.nextInt(124512);
            total += demos[index].foo(x, y);
        }

        System.out.println("Total: " + total);
    }
}
