from beluga import app


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,
            port=app.config.PORT,
            workers=app.config.WORKERS)
