package com.shortify.models;

public class Post {
    private int id;
    private String title;
    private String status;
    private String video_path;
    private String created_at;
    private String youtubeTitle;
    private String youtubeDescription;
    private String youtubeTags;
    private String youtubeStatus;
    private String scheduledAt;
    private String youtubeUrl;

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

    public String getYoutubeTitle() { return youtubeTitle; }
    public void setYoutubeTitle(String youtubeTitle) { this.youtubeTitle = youtubeTitle; }

    public String getYoutubeDescription() { return youtubeDescription; }
    public void setYoutubeDescription(String youtubeDescription) { this.youtubeDescription = youtubeDescription; }

    public String getYoutubeTags() { return youtubeTags; }
    public void setYoutubeTags(String youtubeTags) { this.youtubeTags = youtubeTags; }

    public String getYoutubeStatus() { return youtubeStatus; }
    public void setYoutubeStatus(String youtubeStatus) { this.youtubeStatus = youtubeStatus; }

    public String getScheduledAt() { return scheduledAt; }
    public void setScheduledAt(String scheduledAt) { this.scheduledAt = scheduledAt; }

    public String getYoutubeUrl() { return youtubeUrl; }
    public void setYoutubeUrl(String youtubeUrl) { this.youtubeUrl = youtubeUrl; }
}
