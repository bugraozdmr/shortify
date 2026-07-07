package com.shortify.jobs;

import com.shortify.utils.ConfigManager;
import com.shortify.utils.GlobalState;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public class BackendHealthJob implements Runnable {

    private final HttpClient httpClient;

    public BackendHealthJob() {
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(3))
                .build();
    }

    @Override
    public void run() {
        checkHealth();
    }

    public void checkHealth() {
        String url = ConfigManager.getInstance().getApiUrl();
        if (url == null || url.isEmpty() || (!url.startsWith("http://") && !url.startsWith("https://"))) {
            GlobalState.getInstance().setBackendOnline(false);
            return;
        }

        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url + "/health"))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200 && response.body().contains("success")) {
                GlobalState.getInstance().setBackendOnline(true);
            } else {
                GlobalState.getInstance().setBackendOnline(false);
            }
        } catch (Exception e) {
            GlobalState.getInstance().setBackendOnline(false);
        }
    }
}
