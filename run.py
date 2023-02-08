from kollekt import create_app

# import gunicorn

app = create_app()

if __name__ == "__main__":
    app.run(use_reloader=False)
