package com.shortify.utils;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

public class HttpClientUtil {
    
    // Uygulama geneli tek bir HttpClient örneği kullanmak performansı artırır.
    private static final HttpClient httpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    /**
     * Asenkron GET isteği atar.
     */
    public static CompletableFuture<HttpResponse<String>> getAsync(String url, Map<String, String> headers) {
        AppLogger.logRequest("GET", url, null);
        
        HttpRequest.Builder builder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET();
                
        applyHeaders(builder, headers);
        
        return sendAsync(builder.build());
    }

    /**
     * Asenkron POST isteği atar. JSON payload destekler.
     */
    public static CompletableFuture<HttpResponse<String>> postAsync(String url, String jsonPayload, Map<String, String> headers) {
        AppLogger.logRequest("POST", url, jsonPayload);
        
        HttpRequest.Builder builder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json") // Varsayılan olarak JSON
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload != null ? jsonPayload : ""));
                
        applyHeaders(builder, headers);
        
        return sendAsync(builder.build());
    }

    /**
     * Asenkron PUT isteği atar. JSON payload destekler.
     */
    public static CompletableFuture<HttpResponse<String>> putAsync(String url, String jsonPayload, Map<String, String> headers) {
        AppLogger.logRequest("PUT", url, jsonPayload);
        
        HttpRequest.Builder builder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .PUT(HttpRequest.BodyPublishers.ofString(jsonPayload != null ? jsonPayload : ""));
                
        applyHeaders(builder, headers);
        
        return sendAsync(builder.build());
    }
    
    /**
     * Asenkron DELETE isteği atar.
     */
    public static CompletableFuture<HttpResponse<String>> deleteAsync(String url, Map<String, String> headers) {
        AppLogger.logRequest("DELETE", url, null);
        
        HttpRequest.Builder builder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .DELETE();
                
        applyHeaders(builder, headers);
        
        return sendAsync(builder.build());
    }

    /**
     * İsteğe bağlı header'ları ekler.
     */
    private static void applyHeaders(HttpRequest.Builder builder, Map<String, String> headers) {
        if (headers != null && !headers.isEmpty()) {
            headers.forEach(builder::header);
        }
    }

    /**
     * İsteği gönderir ve yanıtı/hatayı AppLogger ile otomatik loglar.
     */
    private static CompletableFuture<HttpResponse<String>> sendAsync(HttpRequest request) {
        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .whenComplete((response, ex) -> {
                    if (ex != null) {
                        AppLogger.error("HTTP Ağ Hatası: " + request.uri(), ex);
                    } else {
                        AppLogger.logResponse(response.statusCode(), response.body());
                    }
                });
    }
}
