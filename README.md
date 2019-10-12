## Komments

A Flask Web App to manage comments for a blog.

## Basics

#### Installation

1. Create a personal app in your Dropbox.
2. Create an `ACCESS TOKEN` for your app. (Don't share it with anyone!)
3. Clone this repository locally, install all the pip dependencies and adjust the `SITE_NAME` variable in the `app.py` file to your blog site.
4. Deploy the web app on any Python hosting platform like Heroku.
5. Create a `DROPBOX_ACCESS_TOKEN` environment key on your platform and add your Dropbox access token to this key.
6. You are ready to go.

#### Adding comments

From your app, send a **POST** request to `<site.url>/add` URL with `name`, `content`, `blog` as parameters. The comments are saved to the `comments.json` file in your Dropbox app.

#### Getting comments

From your app, send a **POST** request to `<site.url>/get` URL with `blog` as a parameter. The comments are then fetched from the `comments.json` file in your Dropbox app.

## Support

In case of any anomalies, please file an issue [here](https://github.com/ravgeetdhillon/komments/issues).
