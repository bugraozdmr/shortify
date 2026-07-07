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
                .connectTimeout(Duration.ofSeconds(5))
                .followRedirects(HttpClient.Redirect.ALWAYS)
                .build();
    }

    public CompletableFuture<List<Post>> getPosts() {
        String url = ConfigManager.getInstance().getApiUrl();
        if (url == null || url.isEmpty()) {
            return CompletableFuture.completedFuture(new ArrayList<>());
        }

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url + "/posts/"))
                .GET()
                .build();

        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    List<Post> posts = new ArrayList<>();
                    if (response.statusCode() == 200) {
                        JSONArray array = new JSONArray(response.body());
                        for (int i = 0; i < array.length(); i++) {
                            JSONObject obj = array.getJSONObject(i);
                            Post p = new Post();
                            p.setId(obj.optInt("id"));
                            p.setTitle(obj.optString("title"));
                            p.setStatus(obj.optString("status"));
                            p.setVideoPath(obj.optString("video_path", null));
                            p.setCreatedAt(obj.optString("created_at"));
                            posts.add(p);
                        }
                    }
                    return posts;
                });
    }
}
