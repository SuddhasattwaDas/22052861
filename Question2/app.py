from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

BASE_URL = "http://20.244.56.144/evaluation-service"


def fetch_data(endpoint):
    """Helper function to make API calls with error handling"""
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", timeout=1)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


@app.route('/users', methods=['GET'])
def get_top_users():
    """Fetch top 5 users with the highest number of posts"""
    users_data = fetch_data("users")
    
    if not users_data or "users" not in users_data:
        return jsonify({"error": "Failed to fetch users"}), 500

    users = users_data["users"]

    user_posts_count = {}
    for user_id in users.keys():
        posts_data = fetch_data(f"users/{user_id}/posts")
        if posts_data and "posts" in posts_data:
            user_posts_count[user_id] = len(posts_data["posts"])

    top_users = sorted(user_posts_count.items(), key=lambda x: x[1], reverse=True)[:5]
    top_user_ids = [uid for uid, _ in top_users]

    top_user_details = {uid: users[uid] for uid in top_user_ids}

    return jsonify({"top_users": top_user_details})


@app.route('/posts', methods=['GET'])
def get_posts():
    """Fetch either latest or popular posts based on query parameter"""
    post_type = request.args.get("type", "").lower()

    if post_type not in ["latest", "popular"]:
        return jsonify({"error": "Invalid type. Use 'latest' or 'popular'"}), 400

    users_data = fetch_data("users")
    if not users_data or "users" not in users_data:
        return jsonify({"error": "Failed to fetch users"}), 500

    all_posts = []
    
    for user_id in users_data["users"].keys():
        posts_data = fetch_data(f"users/{user_id}/posts")
        if posts_data and "posts" in posts_data:
            all_posts.extend(posts_data["posts"])

    if not all_posts:
        return jsonify({"error": "No posts found"}), 404

    if post_type == "latest":
        sorted_posts = sorted(all_posts, key=lambda x: x["id"], reverse=True)[:5]
    
    elif post_type == "popular":
        post_comment_counts = {}
        for post in all_posts:
            post_id = post["id"]
            comments_data = fetch_data(f"posts/{post_id}/comments")
            if comments_data and "comments" in comments_data:
                post_comment_counts[post_id] = len(comments_data["comments"])
            else:
                post_comment_counts[post_id] = 0
        
        sorted_posts = sorted(all_posts, key=lambda x: post_comment_counts.get(x["id"], 0), reverse=True)
        
        max_comments = post_comment_counts.get(sorted_posts[0]["id"], 0)
        sorted_posts = [post for post in sorted_posts if post_comment_counts.get(post["id"], 0) == max_comments]

    return jsonify({"posts": sorted_posts})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
