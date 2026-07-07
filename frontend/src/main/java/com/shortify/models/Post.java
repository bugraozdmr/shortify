package com.shortify.models;

public class Post {
    private int id;
    private String title;
    private String status;
    private String video_path;
    private String created_at;

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getVideoPath() { return video_path; }
    public void setVideoPath(String video_path) { this.video_path = video_path; }

    public String getCreatedAt() { return created_at; }
    public void setCreatedAt(String created_at) { this.created_at = created_at; }
}
