import webapp as web

app = web.create_app()

if __name__ == "__main__":
	app.run(debug = True) # Have to change it to False when in production
