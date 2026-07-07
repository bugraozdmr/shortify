import pytest
from pipeline.fetcher import fetch_best_posts

@pytest.mark.asyncio
async def test_fetch_best_posts():
    """
    Test that fetch_best_posts successfully scrapes at least one post from a subreddit.
    """
    # Fetch 1 post from an active subreddit like tifu
    posts = await fetch_best_posts(subreddit_name="tifu", limit=1)
    
    # Assert we got results
    assert len(posts) > 0, "No posts were fetched from the subreddit."
    
    # Check the structure of the first post
    first_post = posts[0]
    assert "reddit_id" in first_post
    assert "title" in first_post
    assert "text" in first_post
    
    # Check that title and text are not empty
    assert len(first_post["title"]) > 0, "Post title is empty"
    assert len(first_post["text"]) > 0, "Post text is empty"
    
    print("\n" + "="*50)
    print("✅ TEST SUCCESSFUL! FETCHED POST:")
    print("="*50)
    print(f"Reddit ID: {first_post['reddit_id']}")
    print(f"Title:     {first_post['title']}")
    print(f"Text:      {first_post['text'][:200]}...") # Print first 200 chars
    print("="*50 + "\n")
