package com.shortify.utils;

import com.shortify.models.Post;
import org.json.JSONArray;
import org.json.JSONObject;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public class PostService {

    private final HttpClient httpClient;

    public PostService() {
        this.httpClient = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(Duration.ofSeconds(5))
                .followRedirects(HttpClient.Redirect.ALWAYS)
                .build();
    }

    public CompletableFuture<com.shortify.models.PaginatedResult<Post>> getPosts(int skip, int limit, String status, String youtubeStatus, String sortBy) {
        String baseUrl = ConfigManager.getInstance().getApiUrl();
        if (baseUrl == null || baseUrl.isEmpty()) {
            return CompletableFuture.completedFuture(new com.shortify.models.PaginatedResult<>(0, new ArrayList<>()));
        }

        StringBuilder urlBuilder = new StringBuilder(baseUrl).append("/posts/?skip=").append(skip).append("&limit=").append(limit);
        
        if (status != null && !status.isEmpty() && !status.equalsIgnoreCase("all")) {
            urlBuilder.append("&status=").append(status);
        }
        if (youtubeStatus != null && !youtubeStatus.isEmpty() && !youtubeStatus.equalsIgnoreCase("all")) {
            urlBuilder.append("&youtube_status=").append(youtubeStatus);
        }
        if (sortBy != null && !sortBy.isEmpty()) {
            urlBuilder.append("&sort_by=").append(sortBy);
        }

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(urlBuilder.toString()))
                .GET()
                .build();

        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    List<Post> posts = new ArrayList<>();
                    int total = 0;
                    
                    if (response.statusCode() == 200) {
                        JSONObject jsonResponse = new JSONObject(response.body());
                        total = jsonResponse.optInt("total", 0);
                        JSONArray array = jsonResponse.optJSONArray("items");
                        
                        if (array != null) {
                            for (int i = 0; i < array.length(); i++) {
                                JSONObject obj = array.getJSONObject(i);
                                Post p = new Post();
                                p.setId(obj.optInt("id"));
                                p.setTitle(obj.optString("title"));
                                p.setStatus(obj.optString("status"));
                                p.setVideoPath(obj.optString("video_path", null));
                                p.setCreatedAt(obj.optString("created_at"));
                                p.setYoutubeTitle(obj.optString("youtube_title", null));
                                p.setYoutubeDescription(obj.optString("youtube_description", null));
                                p.setYoutubeTags(obj.optString("youtube_tags", null));
                                p.setYoutubeStatus(obj.optString("youtube_status", "pending"));
                                p.setYoutubeUrl(obj.optString("youtube_url", null));
                                p.setScheduledAt(obj.isNull("scheduled_at") ? null : obj.getString("scheduled_at"));
                                posts.add(p);
                            }
                        }
                    } else {
                        System.err.println("Failed to fetch posts: " + response.statusCode());
                    }
                    return new com.shortify.models.PaginatedResult<>(total, posts);
                });
    }

    public CompletableFuture<Boolean> updatePost(int id, String ytTitle, String ytDesc, String ytTags, String scheduledAt) {
        String baseUrl = ConfigManager.getInstance().getApiUrl();
        if (baseUrl == null || baseUrl.isEmpty()) return CompletableFuture.completedFuture(false);

        JSONObject json = new JSONObject();
        if (ytTitle != null) json.put("youtube_title", ytTitle);
        if (ytDesc != null) json.put("youtube_description", ytDesc);
        if (ytTags != null) json.put("youtube_tags", ytTags);
        json.put("scheduled_at", scheduledAt == null ? JSONObject.NULL : scheduledAt);

        String jsonString = json.toString();
        System.out.println("Giden İstek (PUT): " + baseUrl + "/posts/" + id);
        System.out.println("Giden Veri: " + jsonString);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/posts/" + id))
                .header("Content-Type", "application/json")
                .PUT(HttpRequest.BodyPublishers.ofString(jsonString))
                .build();

        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    System.out.println("Update Post Response Code: " + response.statusCode());
                    System.out.println("Update Post Response Body: " + response.body());
                    return response.statusCode() == 200;
                })
                .exceptionally(ex -> {
                    System.err.println("Exception in updatePost:");
                    ex.printStackTrace();
                    return false;
                });
    }

    public CompletableFuture<Boolean> deletePost(int id) {
        String baseUrl = ConfigManager.getInstance().getApiUrl();
        if (baseUrl == null || baseUrl.isEmpty()) return CompletableFuture.completedFuture(false);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/posts/" + id))
                .DELETE()
                .build();

        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> response.statusCode() == 200);
    }

    public CompletableFuture<Boolean> publishPost(int id) {
        String baseUrl = ConfigManager.getInstance().getApiUrl();
        if (baseUrl == null || baseUrl.isEmpty()) return CompletableFuture.completedFuture(false);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/posts/" + id + "/publish"))
                .POST(HttpRequest.BodyPublishers.noBody())
                .build();

        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> response.statusCode() == 200);
    }
}
