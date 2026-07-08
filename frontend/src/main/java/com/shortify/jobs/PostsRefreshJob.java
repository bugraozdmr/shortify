package com.shortify.jobs;

import com.shortify.utils.GlobalState;

public class PostsRefreshJob implements Runnable {

    @Override
    public void run() {
        if (GlobalState.getInstance().isBackendOnline()) {
            GlobalState.getInstance().triggerPostsRefresh();
        }
    }
}
