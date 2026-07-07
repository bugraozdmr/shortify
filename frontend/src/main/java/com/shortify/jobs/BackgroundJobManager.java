package com.shortify.jobs;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class BackgroundJobManager {
    private static BackgroundJobManager instance;
    private final ScheduledExecutorService scheduler;

    private BackgroundJobManager() {
        // Create a thread pool for background jobs.
        // Using daemon threads so they don't prevent the JVM from exiting.
        scheduler = Executors.newScheduledThreadPool(2, r -> {
            Thread t = new Thread(r);
            t.setDaemon(true);
            t.setName("Shortify-Background-Job-" + t.getId());
            return t;
        });
    }

    public static BackgroundJobManager getInstance() {
        if (instance == null) {
            instance = new BackgroundJobManager();
        }
        return instance;
    }

    /**
     * Schedulers a recurring job.
     */
    public void scheduleJob(Runnable task, long initialDelay, long period, TimeUnit unit) {
        scheduler.scheduleAtFixedRate(task, initialDelay, period, unit);
    }

    /**
     * Executes a job once immediately.
     */
    public void executeNow(Runnable task) {
        scheduler.execute(task);
    }

    public void shutdown() {
        if (scheduler != null && !scheduler.isShutdown()) {
            scheduler.shutdownNow();
        }
    }
}
